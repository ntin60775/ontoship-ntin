"""Shared engine fixture.

The suite talks to the shipped engine at skills/kb-search/gitmark.py and needs
no Node: everything is Python stdlib plus pytest.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "skills" / "kb-search" / "gitmark.py"


def load_engine(path: Path = ENGINE, name: str = "gitmark"):
    """Import an engine file by path (the shipped one or a .dsh copy)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def gm():
    return load_engine()