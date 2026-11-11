"""redact_lite at the output boundary: lint messages and .gitignore warnings.

The matrix pins each rule with a positive case and honest negatives. It has a
negative/mutation probe: removing any single rule lets a secret through at
least one case, so the matrix can fail when a rule is disabled.

Traceability: ``invariant: secrets at the output boundary are redacted``;
E2E cases also verify ``spec: docs/plans/core-kb.md#готово-2`` (lint output).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ENGINE


# (should_mask, name, input, secret substring that must not survive)
REDACT_CASES = [
    # ── rule traps (removing a rule leaves the secret in the output) ──
    (True, "whole eyJ JWS (rule 1)",
     "токен eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.FAKESIG123456 в логе", "FAKESIG123456"),
    (True, "bearer literal without a dictionary key (rule 2)",
     "hdr bearer FAKEabc123-def456=", "FAKEabc123-def456="),
    (True, "JSON form with quotes (rule 3)", '{"password": "FAKEhunter2x"}', "FAKEhunter2x"),
    (True, "YAML: quoted value, bare key (rule 4)",
     'password: "FAKEkey12345"', "FAKEkey12345"),
    (True, "password equals, bare (rule 5)", "password=FAKEabcdef123456", "FAKEabcdef123456"),
    (True, "vendor ghp_ without dictionary context (rule 6)",
     "see ghp_FAKETOKEN12 end", "ghp_FAKETOKEN12"),
    # ── other positives ──
    (True, "password with colon", "конфиг: password: FAKEcolonsecret", "FAKEcolonsecret"),
    (True, "JSON api_key", '{"api_key": "FAKEv1.abc123def456"}', "FAKEv1.abc123def456"),
    (True, "JSON client_secret (affix)",
     '{"client_secret": "FAKEcl13ntsec"}', "FAKEcl13ntsec"),
    (True, "python-repr client_secret", "{'client_secret': 'FAKEpysec99'}", "FAKEpysec99"),
    (True, "JSON: escaped quote in the value",
     '{"password": "abcd\\"EFSECRET9tail"}', "EFSECRET9tail"),
    (True, "JSON with backslashes before quotes",
     '\\"password\\": \\"FAKEesc9secret99\\"', "FAKEesc9secret99"),
    (True, "python-repr with single quotes",
     "{'password': 'FAKEpysecret99'}", "FAKEpysecret99"),
    (True, "key with a digit suffix (affix)", "password1=FAKEp1secret", "FAKEp1secret"),
    (True, "key with _key suffix", "secret_key=FAKEsk22key", "FAKEsk22key"),
    (True, "plural key — one letter after KEY",
     "secrets: FAKEplural123", "FAKEplural123"),
    (True, "plural tokens", "tokens: FAKEplural456", "FAKEplural456"),
    # live I9 format: the middle token is the engine's word "значение"
    (True, "I9: card field value outside the list",
     "поле token: значение 'FAKEprobe1' вне списка", "FAKEprobe1"),
    (True, "I9: 64-char middle token (long path)",
     "password: " + "p" * 64 + " 'FAKElongtail9'", "FAKElongtail9"),
    # quotes in values by quote type: raw double inside single is legal (I9)
    (True, "I9: raw double quote inside a single-quoted value",
     "поле token: значение 'ab\"cd' вне списка", "ab\"cd"),
    (True, "YAML: escaped quote in a double-quoted value",
     'password: "se\\"cret123"', "cret123"),
    (True, "basic read/write — /-lookahead, documented FP trade-off",
     "basic read/write", ""),
    (True, "basic literal with valid padding =",
     "basic RkFLRXVzZXI6RkFLRXBhc3N3b3I=", "RkFLRXVzZXI6RkFLRXBhc3N3b3I="),
    (True, "basic literal with an inner digit",
     "basic RkFLRXVzZXI6RkFLRXBhc3N3b3Jk", "RkFLRXVzZXI6RkFLRXBhc3N3b3Jk"),
    (True, "vendor sk-", "ключ sk-FAKEa1b2c3d4e5f6", "FAKEa1b2c3d4e5f6"),
    (True, "vendor AKIA", "aws AKIAFAKE12345678 key", "AKIAFAKE12345678"),
    # live I2/I4 formats
    (True, "I2: service value outside the vocabulary",
     "service='eyJhbGciOiJIUzI1NiJ9.eyJFAKEsubIn0.FAKESIG99' вне словаря", "FAKESIG99"),
    (True, "I4: broken link with a token",
     "битая ссылка → ./nope.md?token=ghp_FAKETOKEN12345", "FAKETOKEN12345"),
    # negatives: honest strings are not distorted
    (False, "short value — skip", "token=abc", ""),
    (False, "auth in prose (short value) — skip", "заголовок auth: см. документацию", ""),
    (False, "author is an honest word (KEY boundary)", "author: Пушкин", ""),
    (False, "authorized — KEY + 2+ letters, boundary holds", "authorized: client-id-12345", ""),
    (False, "camelCase key — documented skip (KEY + 2+ letters)",
     "tokenValue: значение 'abc12345def' вне списка", ""),
    (False, "authKey — documented skip", "authKey: s3cr3tv4lue", ""),
    (False, "letters-only bearer token — lookahead trade-off",
     "bearer Zxqwvutsrqponm", ""),
    (False, "authorization: bearer <letters> — marker does not mimic masking",
     "authorization: bearer abcdefgh", ""),
    (False, "multiline: a quote below the key is not eaten",
     "password: x\n\n'FAKEquote99 не тронуто'", ""),
    (False, "unclosed quote — skip (broken format)",
     "password: 'FAKEunclosed9", ""),
    (False, "quoted value <4 chars — lite threshold",
     'password = "abc"', ""),
    (False, "basic authentication — prose, not a token",
     "схема basic authentication запрещена", ""),
    (False, "Cyrillic key — outside the lite dictionary (documented skip)",
     "токен стенда: hunter2go99", ""),
    (False, "a path with token in the name",
     "docs/plans/token-guide.md — нет frontmatter с node_type", ""),
    (False, "counters", "5 файлов · I2×2 · I4×1 · 200 KB", ""),
    (False, "Russian prose without dictionary keys",
     "Пароль забыт — восстановление через поддержку", ""),
    (False, "service outside the vocabulary without a secret shape (I2 honest)",
     "service='demo' вне словаря", ""),
]


@pytest.mark.parametrize("should_mask,name,inp,secret", REDACT_CASES)
def test_redact_matrix(gm, should_mask, name, inp, secret):
    """invariant: secrets at the output boundary are redacted, honest text survives."""
    out = gm.redact_lite(inp)
    assert (out != inp) == should_mask, f"[{name}] => {out!r}"
    if should_mask:
        if secret:
            assert secret not in out, f"LEAK [{name}]: secret survived"
        assert "[REDACTED]" in out, f"[{name}]: marker missing"
        assert re.sub(r"\[REDACTED\]|\s", "", out), f"[{name}]: over-redacted"
    assert gm.redact_lite(out) == out, f"NOT IDEMPOTENT [{name}]"


def test_middle_token_cap_pins_upper_bound(gm):
    """invariant: the 64-char bridge cap is a documented boundary, not unbounded."""
    out = gm.redact_lite("password: " + "p" * 65 + " 'FAKEover64x'")
    assert "FAKEover64x" in out
    assert "p" * 65 not in out


def test_c0_control_chars_stripped(gm):
    """invariant: C0/DEL from untrusted messages never reaches the terminal."""
    out = gm.redact_lite("node_type='x\x1b[2Jy' вне словаря")
    assert "\x1b" not in out
    assert "[2J" in out


def test_no_quadratic_hang(gm):
    """invariant: a 100 KB field does not trigger quadratic backtracking."""
    import time
    payload = "y" * 50000 + "token" + "y" * 50000
    t0 = time.monotonic()
    gm.redact_lite(payload)
    assert time.monotonic() - t0 < 10


def test_mutation_every_rule_has_a_trap(gm, monkeypatch):
    """invariant/mutation probe: removing one rule leaks a secret in some case, so the
    matrix fails when a rule is disabled."""
    orig = list(gm._REDACT_RULES)
    positives = [c for c in REDACT_CASES if c[0]]
    for i in range(len(orig)):
        monkeypatch.setattr(gm, "_REDACT_RULES", orig[:i] + orig[i + 1:])
        traps = [
            name for _, name, inp, secret in positives
            if secret and secret in gm.redact_lite(inp)
        ]
        monkeypatch.setattr(gm, "_REDACT_RULES", orig)
        assert traps, (
            f"rule #{i} has no trap: without it no case leaks — "
            "the matrix does not test this rule"
        )


# ── E2E: the three live channels of lint output ────────────────────────────
CARDS_MD = """---
node_type: card
token: sk-FAKEprobe12345
links:
  relates_to: [../README.md]
---
# Карточка
"""
SCHEMA_MD = """---
node_type: schema
card_type: card
required: [token]
values: token: free|locked
links:
  relates_to: [../README.md]
---
# Схема
"""
SERVICE_MD = """---
node_type: service
service: eyJhbGciOiJIUzI1NiJ9.eyJFAKEsubIn0.FAKESIG99
status: active
links:
  relates_to: [../../README.md]
---
# Demo
"""
REFS_MD = """---
node_type: reference
service: _platform
status: active
links:
  relates_to: [../README.md]
---
# Ссылки
Смотри [вестку](./nope.md?token=ghp_FAKETOKEN12345).
"""


@pytest.fixture()
def probe_kb(tmp_path):
    (tmp_path / "docs" / "services" / "demo").mkdir(parents=True)
    (tmp_path / "docs" / "reference").mkdir(parents=True)
    (tmp_path / "docs" / "services" / "cards.md").write_text(CARDS_MD, "utf-8")
    (tmp_path / "docs" / "services" / "_schema.md").write_text(SCHEMA_MD, "utf-8")
    (tmp_path / "docs" / "services" / "demo" / "README.md").write_text(SERVICE_MD, "utf-8")
    (tmp_path / "docs" / "reference" / "refs.md").write_text(REFS_MD, "utf-8")
    (tmp_path / "docs" / "README.md").write_text("# Docs\n\n- [services](services/)\n", "utf-8")
    return tmp_path


def test_lint_stdout_redacted(probe_kb):
    """spec: docs/plans/core-kb.md#готово-2 — I2/I4/I9 messages are redacted, format survives."""
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(probe_kb), "lint"],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    assert r.returncode == 0, f"gitmark упал: {r.stderr[-500:]}"
    out = r.stdout + r.stderr
    for secret in ("FAKEprobe12345", "FAKETOKEN12345", "FAKESIG99", "eyJhbGci"):
        assert secret not in out, f"секрет {secret!r} утёк в вывод lint"
    assert out.count("[REDACTED]") >= 3
    assert "docs/services/cards.md" in out
    assert "поле token: [REDACTED] вне списка" in out
    assert "service='[REDACTED]' вне словаря" in out
    assert "./nope.md?token=[REDACTED]" in out


def test_gitignore_warning_redacted(tmp_path):
    """invariant: a .gitignore rule is untrusted text and is redacted in stderr."""
    (tmp_path / "drafts").mkdir()
    (tmp_path / "drafts" / "a.md").write_text("# a\n", "utf-8")
    (tmp_path / ".gitignore").write_text("!secret=FAKEkey456789.md\n", "utf-8")
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(tmp_path), "lint"],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    assert r.returncode == 0, f"gitmark упал: {r.stderr[-500:]}"
    combined = r.stdout + r.stderr
    assert "FAKEkey456789" not in combined
    assert "[REDACTED]" in combined