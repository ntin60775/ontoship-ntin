---
name: kb-search
description: "Search this repository's markdown knowledge base with the GitMark engine: find where something is documented, get file paths with snippets, rebuild the derived index after docs change, and inspect KB stats or the HTML map. Use before reading files at random, before answering where something lives, and before writing a new doc."
---

# KB search

Use this skill to find where something is documented in this repository's knowledge
base (KB), before opening files at random, and before writing a new document. The KB is
markdown plus git; the engine searches a deterministic index over it. A search result is
a lead, not proof: open the file before you rely on it.

## When to use

- The user asks where something is documented, or which document covers a topic.
- You are about to read files at random to understand the repository.
- You are about to write a new doc: first check whether the KB already covers it.
- You need a short, citable path and snippet for an answer.

Do not use this skill as a substitute for reading the document it returns.

## Run the engine

The engine is `gitmark.py`, beside this `SKILL.md`. Run it with Python 3 from the
repository root. In this source checkout:

```sh
python3 skills/kb-search/gitmark.py <command>
```

After a project-local install, the same file is at `.dsh/skills/kb-search/gitmark.py`:

```sh
python3 .dsh/skills/kb-search/gitmark.py <command>
```

No dependencies beyond the Python 3 standard library.

## Commands

### `index` — build the search index

```sh
python3 skills/kb-search/gitmark.py index
```

Rebuild after adding or editing docs. It writes `.gitmark/index.db` and prints file,
chunk and link counts. `--force` is accepted; the command rebuilds the whole index either
way.

### `search` — find documents

```sh
python3 skills/kb-search/gitmark.py search "canon"
python3 skills/kb-search/gitmark.py search "ticket acceptance criteria" -k 5
```

Searches the index with BM25 and trigram matching. Results are ranked and printed as
`path:line`, a heading, the match source in brackets, and a snippet. Use a few
distinctive words; a long natural-language question is usually worse than its key terms.

### `search --json` — machine-readable results

```sh
python3 skills/kb-search/gitmark.py search "canon" --json
```

Prints a JSON array of objects with `path`, `heading`, `line`, `snippet`, `score`, and
`via`. Parse it when you need to filter or sort results yourself.

### `map` — optional HTML overview

```sh
python3 skills/kb-search/gitmark.py map -o docs-map.html
```

Writes a self-contained HTML tree and link graph. It is a reading aid, not a source of
truth. The default output is `docs/docs-map.html`; the map is derived and never
committed.

### `stat` — index statistics

```sh
python3 skills/kb-search/gitmark.py stat
python3 skills/kb-search/gitmark.py stat --json
```

Reports whether the index exists and how many files, chunks, links and areas it covers.
`stat --json` always prints valid JSON; before the first index it returns
`{"indexed": false}`.

### `version` — engine version

```sh
python3 skills/kb-search/gitmark.py version
```

Prints `gitmark <version>`.

## How to search

1. **Check the index** when you are unsure it is current. `stat --json` returns
   `indexed: false` if there is none. Run `index`, then search.
2. **Search with key terms.** Start with two to five distinctive words from the topic.
   Use `-k` to widen or narrow the candidate list.
3. **Read the hits.** Open each promising path and read enough context to confirm it
   answers the question. The `line` value is the start of the matching chunk, not a
   guarantee that the exact sentence is on that line.
4. **Answer with evidence.** Cite the repository-relative path (and line or heading when
   useful) and a short snippet. If several docs cover different parts, name them all.

## Degradation: say what happened

The skill is honest about missing state. Never fill a gap with a plausible document.

- **No index.** `search` refuses with a message naming `gitmark index`. Run that command
  and retry. If you cannot run it, tell the user the exact command to run; do not guess
  at the KB contents.
- **No matches.** The engine prints `ничего не найдено`. Say that there are no matches
  for the query, name the terms you searched, and try synonyms or a broader query.
  Do not invent a document, path, or snippet.
- **Engine or path failure.** Quote the command and the error. Report the gap; do not
  substitute a hand-written summary of what the KB "probably" says.
- **No document opened.** If you have not opened a file, do not claim what it contains.
  A snippet is evidence of a match, not of the document's full answer.

## Before writing a new document

1. Search the KB for the topic and for likely synonyms.
2. If a document already covers it, update that document instead of creating a
   duplicate.
3. If nothing covers it, say which terms you searched and that you found no coverage.
   Then create the doc under `docs/`, give it the required frontmatter, and link it from
   its folder's `README.md` so it is not orphaned.
4. Rebuild the index after the change (`index`).

## `.gitmark/` is derived

`.gitmark/` and every HTML map are generated from the markdown. They are ignored by git
and are never the source of truth: do not edit them by hand, do not commit them, and do
not cite them as documentation. The source is the markdown; the index is rebuilt from it
at any time.
