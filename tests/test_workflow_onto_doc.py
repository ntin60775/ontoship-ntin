"""Contract for the onto-doc run workflow (onto-doc ticket 02, decision 8).

The saved workflow is the only run mechanics of the doc part: it lives in the
repository (``.zcode/workflows/onto-doc.dwf.ts``), takes the KB root and the
decomposition plan as arguments, fans one curator out per plan piece and
prints the assigned model into the log. The file answers for its arguments
``root`` and ``plan``, carries no placeholders, and curators follow kb-curate
writing only inside the root. The model and the level themselves are the
launch contract of the skill, not of the file.

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


def test_workflow_file_is_committed_with_metadata_and_args():
    """spec: docs/plans/onto-doc.md#готово — файл прогона отвечает за
    аргументы root и plan (решение 8) и несёт модель для печати в log."""
    assert WORKFLOW.is_file(), "the onto-doc run workflow is missing"
    meta, _ = _split(WORKFLOW.read_text("utf-8"))
    args = _args_from(meta)
    for name in REQUIRED_ARGS:
        assert name in args, f"argument {name!r} is not declared"
    for name in ("root", "plan"):
        assert args[name].get("required") == "true", \
            f"argument {name!r} must be required"


def test_body_prints_the_assigned_model_into_the_log():
    """spec: docs/plans/onto-doc.md#готово — файл печатает назначенную модель
    в log; модель и уровень проверяются контрактом запуска, не файлом."""
    _, body = _split(WORKFLOW.read_text("utf-8"))
    assert "args.model" in body, "the assigned model must come from arguments"
    log_lines = [line for line in body.splitlines()
                 if "log(" in line and "назначенную модель" in line]
    assert log_lines, "no log line prints the assigned model"

    muted = body.replace("назначенную модель", "модель")
    assert muted != body
    assert not [line for line in muted.splitlines()
                if "log(" in line and "назначенную модель" in line]


def test_curators_follow_kb_curate_inside_the_root():
    """invariant: docs/plans/onto-doc.md#ограничения — прогон пишет только
    внутри root; каждый куратор ведёт срез по скиллу kb-curate."""
    _, body = _split(WORKFLOW.read_text("utf-8"))
    assert "skills/kb-curate/SKILL.md" in body
    assert "только внутри" in body
    assert "Promise.all" in body and "plan.map" in body, \
        "one curator per plan piece, independent areas in parallel"

    no_skill = body.replace("skills/kb-curate/SKILL.md", "skills/curate.md")
    assert no_skill != body
    assert "skills/kb-curate/SKILL.md" not in no_skill


def test_no_placeholders():
    """spec: docs/plans/onto-doc.md#готово — файл не несёт плейсхолдеров."""
    text = WORKFLOW.read_text("utf-8")
    for marker in FORBIDDEN_PLACEHOLDERS:
        assert marker not in text, f"placeholder {marker!r} found"
        leaked = text + f"\n// fallback: {marker}\n"
        assert marker in leaked


def test_args_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    file's args contract rejects a droppable root argument."""
    text = WORKFLOW.read_text("utf-8")
    unrequired = text.replace("    required: true\n", "", 1)
    assert unrequired != text, "the mutation must hit a required declaration"
    meta, _ = _split(unrequired)
    args = _args_from(meta)
    assert "required" not in args["root"], \
        "the first dropped declaration must be root's"
