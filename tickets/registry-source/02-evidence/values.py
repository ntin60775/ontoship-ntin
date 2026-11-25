"""Ticket 02 evidence: the pool values live in the config.

Run from the repo root:
    python3 tickets/registry-source/02-evidence/values.py
"""
import tomllib
from pathlib import Path

data = tomllib.loads(Path(".agents/config.toml").read_text("utf-8"))
pool = data["validation"]["pool"]
print("pool entries:", [(entry["model"], entry["level"]) for entry in pool])
parts = [entry["model"].split("/", 1)[1] for entry in pool]
print("model parts:", parts)
print("distinct model parts:", len(parts) == len(set(parts)))
print("pool size:", len(pool))
print("agent sections:", list(data["agents"]))
print("critic:", data["agents"]["critic"])
