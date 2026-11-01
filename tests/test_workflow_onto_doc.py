"""Contract for the onto-doc run workflow (onto-doc ticket 02, decision 8).

The saved workflow is the only run mechanics of the doc part: it lives in the
repository (``.zcode/workflows/onto-doc.dwf.ts``), takes the KB root, the
decomposition plan and the assigned model as arguments, fans one curator out
per plan piece and prints the assigned model into the log. The file answers
for its arguments (all three required), rejects a plan that could pull a
curator outside the root or double-book an area, carries no placeholders, and
curators follow kb-curate writing only inside the root. The model and the
level themselves are the launch contract of the skill, not of the file.

spec: docs/plans/onto-doc.md#готово — сохранённый workflow по решению 8:
      аргументы root/plan, отсутствие плейсхолдеров, печать назначенной
      модели в log
invariant: docs/plans/onto-doc.md#ограничения — прогон пишет только внутри
      root
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".zcode" / "workflows" / "onto-doc.dwf.ts"
REQUIRED_ARGS = ("root", "plan", "model")
FORBIDDEN_PLACEHOLDERS = (
    "${CLAUDE_PLUGIN_ROOT}",
    "$ARGUMENTS",
    "TODO",
    "FIXME",
    "<MODEL>",
)


def _split(text: str) -> tuple[str, str]:
    """Split a saved workflow file into metadata and script body."""
    match = re.match(r"^/\* zcode-workflow\n(.*?)\*/\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("the saved workflow must open with a zcode-workflow "
                         "metadata block")
    return match.group(1), match.group(2)


def _args_from(meta: str) -> dict[str, dict[str, str]]:
    """Parse argument declarations (name → their key: value lines)."""
    args: dict[str, dict[str, str]] = {}
    in_args = False
    for line in meta.splitlines():
        if line.startswith("args:"):
            in_args = True
        elif in_args and re.match(r"^  ([\w-]+):\s*$", line):
            args[line.strip()[:-1]] = {}
        elif in_args and re.match(r"^    ([\w-]+):\s*(.*)$", line) and args:
            key, value = re.match(r"^    ([\w-]+):\s*(.*)$", line).groups()
            list(args.values())[-1][key] = value.strip()
    return args


def _placeholder_hits(text: str) -> list[str]:
    """Every forbidden placeholder present in the file."""
    return [marker for marker in FORBIDDEN_PLACEHOLDERS if marker in text]


def test_workflow_file_is_committed_with_metadata_and_args():
    """spec: docs/plans/onto-doc.md#готово — файл прогона отвечает за
    аргументы root и plan (решение 8) и несёт модель для печати в log;
    все три аргумента обязательны."""
    assert WORKFLOW.is_file(), "the onto-doc run workflow is missing"
    text = WORKFLOW.read_text("utf-8")
    meta, _ = _split(text)
    args = _args_from(meta)
    for name in REQUIRED_ARGS:
        assert name in args, f"argument {name!r} is not declared"
        assert args[name].get("required") == "true", \
            f"argument {name!r} must be required"

    # The model argument is declared last; dropping the last required line
    # must hit exactly its own declaration.
    head, sep, tail = text.rpartition("    required: true\n")
    assert sep, "the file declares no required argument"
    meta_dropped, _ = _split(head + tail)
    assert _args_from(meta_dropped)["model"].get("required") != "true", \
        "the mutation must hit the model declaration"


def test_body_prints_the_assigned_model_into_the_log():
    """spec: docs/plans/onto-doc.md#готово — файл печатает назначенную модель
    в log: значением аргумента model, не чем-то другим под этой меткой;
    модель и уровень проверяются контрактом запуска, не файлом."""
    _, body = _split(WORKFLOW.read_text("utf-8"))
    assert "const assigned = String(args.model)" in body, \
        "the assigned model must come from the model argument"
    log_lines = [line for line in body.splitlines()
                 if "log(" in line and "назначенную модель" in line]
    assert log_lines, "no log line prints the assigned model"
    assert any("${assigned}" in line for line in log_lines), \
        "the log line must print the assigned model value"

    muted = body.replace("${assigned}", "${root}", 1)
    assert muted != body
    muted_lines = [line for line in muted.splitlines()
                   if "log(" in line and "назначенную модель" in line]
    assert not any("${assigned}" in line for line in muted_lines)


def test_plan_guards_keep_curators_inside_root():
    """invariant: docs/plans/onto-doc.md#ограничения — прогон пишет только
    внутри root: план отвергает абсолютные пути и '..', дубли областей и
    пустой план."""
    _, body = _split(WORKFLOW.read_text("utf-8"))
    assert "includes(\"..\")" in body
    assert "startsWith(\"/\")" in body
    assert "duplicate doc area" in body
    assert "plan is empty" in body
    assert "внутри корня KB, за его пределы не выходи" in body

    unguarded = body.replace('path.split("/").includes("..")', "True", 1)
    assert unguarded != body
    assert "includes(\"..\")" not in unguarded


def test_curators_follow_kb_curate_inside_the_root():
    """invariant: docs/plans/onto-doc.md#ограничения — куратор ведёт срез по
    скиллу kb-curate: путь установленного бандла, а при его отсутствии —
    путь репозитория; ответ — объект строки области."""
    _, body = _split(WORKFLOW.read_text("utf-8"))
    assert ".agents/skills/kb-curate/SKILL.md" in body, \
        "the installed bundle path must be tried first"
    assert "skills/kb-curate/SKILL.md" in body
    for field in ("path", "curator", "files", "refusal"):
        assert field in body, f"the row field {field!r} must be in the ask"

    no_skill = body.replace(".agents/skills/kb-curate/SKILL.md", "x")
    assert ".agents/skills/kb-curate/SKILL.md" not in no_skill


def test_curator_row_comes_from_a_typed_answer_never_silently_empty():
    """invariant: docs/plans/onto-doc.md#готово — карточка прогона несёт строку
    на область (куратор, файлы, отказ). Живой прогон dwfrun-5efcd1d0 поймал
    сбой транспорта: нетипизированный ответ с прозой вокруг JSON молча
    превращался в files: [] при девяти правках в worktree. Ответ куратора
    типизирован, промпт требует только JSON, а ответ не по схеме — именованный
    отказ строки, не пустой список."""
    _, body = _split(WORKFLOW.read_text("utf-8"))
    assert "ask<CuratorRow>" in body, \
        "the curator answer must be typed: the row comes from a schema"
    assert "только JSON" in body, \
        "the ask must demand a JSON-only answer"
    assert "ответил не по схеме" in body, \
        "an off-schema answer must become a named refusal of the row"
    for silent_default in ("map(String) : [];",
                           'String(shape?.refusal ?? "")'):
        assert silent_default not in body, \
            f"silent default {silent_default!r} masks an off-schema answer"

    untyped = body.replace("ask<CuratorRow>", "ask", 1)
    assert untyped != body and "ask<CuratorRow>" not in untyped, \
        "the mutation must drop the typed ask"

    loose = body.replace("только JSON", "JSON", 1)
    assert loose != body and "только JSON" not in loose, \
        "the mutation must drop the JSON-only demand"

    muted = body.replace("ответил не по схеме", "ответил пустым списком", 1)
    assert muted != body and "ответил не по схеме" not in muted, \
        "the mutation must drop the named refusal"


def test_no_placeholders():
    """spec: docs/plans/onto-doc.md#готово — файл не несёт плейсхолдеров;
    проверка умеет падать: испорченный текст ловится той же функцией."""
    text = WORKFLOW.read_text("utf-8")
    assert _placeholder_hits(text) == []
    for marker in FORBIDDEN_PLACEHOLDERS:
        poisoned = text + f"\n// fallback: {marker}\n"
        assert _placeholder_hits(poisoned) == [marker]
