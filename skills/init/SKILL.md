---
name: init
description: "Initialize the OntoShip entry point in a project: create or update the managed block in AGENTS.md and add the three .gitignore lines the KB requires. Idempotent; writes only AGENTS.md and .gitignore, and in AGENTS.md only between the ontoship markers. Use after the core is installed, when the user asks to initialize or set up OntoShip in this project."
---

# Init

Set up the entry point of an OntoShip project. Run this once per project, after the core
is installed. It is **idempotent**: a second run changes nothing, and `git diff` after it
is empty.

**What init owns.** Two files, nothing else:

- `AGENTS.md` — a managed block between `<!-- BEGIN ontoship -->` and
  `<!-- END ontoship -->`. Everything outside the markers is project text: never edit
  it, never move it, never rewrite the file wholesale.
- `.gitignore` — the three lines the KB requires: `.gitmark/`, `*-map.html`,
  `.scratch/`.

Init writes these two files and nothing else: it does not create a command index or
generated tables, it does not write `docs/`, `.dsh/`, `.gitmark/` or any other file, and
it does not run `index`, `lint` or `map`. If it cannot write one of the two files, it
reports that and stops — it never substitutes a different location.

## 1. Find the project root

Run `git rev-parse --show-toplevel` from the project root; fall back to the current
directory when the project is not a git repository. Write both files at that root.

DSH loads `AGENTS.md` from the user-global roots (`~/.dsh/AGENTS.md`,
`~/.agents/AGENTS.md`) and then from each directory between the project root (the first
ancestor with `.git`) and the session's working directory. A subdirectory file is loaded
only when a file under it is touched, so the project root is where the entry point
belongs. Do not write `~/.dsh/AGENTS.md` or a nested `AGENTS.md`.

## 2. Update AGENTS.md

Read the file **without normalizing its bytes** — binary I/O, or text I/O with
`newline=''`. Determine the newline style from the first line (`\r\n` or `\n`) and use it
for the inserted lines. A marker is present only when a whole line, ignoring a trailing
`\r`, equals the marker string. Then apply exactly one of five cases:

| case | action |
|---|---|
| `AGENTS.md` is missing | create it containing exactly the block below |
| file exists, neither marker string appears | append one blank line, then the block; every existing line stays |
| one BEGIN and one END, in that order, and the inner text equals the template | change nothing; the file is already current |
| one BEGIN and one END, in that order, and the inner text differs | replace only the inner text, keep the marker lines and everything outside them; report `[WARN]` |
| any marker string appears but the pair is not exactly one BEGIN then one END | change nothing, report `[FAIL]`, stop — do not touch `.gitignore` either |

The last case covers a lone marker, a reversed pair, a duplicate pair, and a marker that
is not on its own line. Fail closed: guessing which pair is "the" block risks destroying
project text.

The block is **verbatim**; do not reflow, retitle, add or drop lines:

````markdown
<!-- BEGIN ontoship -->
## Knowledge base (OntoShip)

- Entry point: [`docs/README.md`](docs/README.md) — the KB master index; every folder has
  a `README.md` index.
- Search before answering or writing: load the `kb-search` skill. The engine is at
  `.dsh/skills/kb-search/gitmark.py` for direct use.
- New or updated docs: load the `kb-curate` skill — search first, never duplicate.
- Maintain after editing docs:

  ```sh
  python3 .dsh/skills/kb-search/gitmark.py index
  python3 .dsh/skills/kb-search/gitmark.py lint --strict
  python3 .dsh/skills/kb-search/gitmark.py map -o docs-map.html
  ```

- The KB is markdown + git: `.gitmark/`, `*-map.html` and `.scratch/` are derived or
  ephemeral — never committed.
<!-- END ontoship -->
````

The block is generated content. Project-specific instructions belong outside the markers.
An edit inside the block is lost on the next init; say so when the block is replaced.

Compare the inner text after normalizing line endings (`\r\n` to `\n`) on both sides, so a
CRLF file with an otherwise current block is not rewritten. When writing, keep every
byte outside the block as it was; do not add a trailing newline that the file did not
have.

## 3. Update .gitignore

Create the file when it is missing. Otherwise append only the lines that are not already
present as a line (compare the trimmed line). Leave every existing line, its order and
its comments alone — never remove a duplicate, a broader pattern or a comment. Append the
missing lines in this order:

```text
.gitmark/
*-map.html
.scratch/
```

If the file is non-empty and does not end with a newline, add one before appending.
Finish with a newline after the last appended line. If all three lines are already
present, change nothing.

## 4. Verify

From the project root:

```sh
git diff -- AGENTS.md .gitignore
git status --short
```

The first run shows the block and the missing lines. A second run must show **no diff at
all** — that is the idempotence check, not a claim. If the second run shows a diff, the
block text or the line comparison is not stable: fix the skill, do not paper over it.

Check that the marker pair is exactly one pair:

```sh
grep -c '^<!-- BEGIN ontoship -->$' AGENTS.md   # 1
grep -c '^<!-- END ontoship -->$' AGENTS.md     # 1
```

## 5. Report

Name each file and what happened: `created`, `appended` (name the lines), `updated inside
markers`, or `unchanged`. On an update, warn that edits inside the block do not survive.
On `[FAIL]`, quote the marker problem and state that nothing was changed.

Then hand over: the next step is building the KB. `docs/README.md` is the master index;
new docs go through `kb-curate`; the maintain commands are in the block. Do not run them
as part of init.