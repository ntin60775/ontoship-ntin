"""Shared engine fixture.

The suite talks to the shipped engine at skills/kb-search/gitmark.py and needs
no Node: everything is Python stdlib plus pytest.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "skills" / "kb-search" / "gitmark.py"


def load_engine(path: Path = ENGINE, name: str = "gitmark"):
    """Import an engine file by path (the shipped one or an install copy)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def gm():
    return load_engine()

def make_git_repo(tmp_path: Path, files: dict) -> Path:
    """Временный git-репозиторий с перечисленными файлами.

    Файлы добавляются в индекс (`git add -A`) без коммита: `git ls-files -c -o`
    их видит, поэтому корпус движка совпадает с тем, что видит git. Фикстура
    заведена тикетом 01 юнита `kb-scope` — до неё `git init` повторялся инлайн
    в трёх местах `tests/test_engine.py`.
    """
    for rel, body in files.items():
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path
