# 05: документы, матрица и legacy-регрессия

**Спека:** [docs/plans/dsh-adaptation.md](../../docs/plans/dsh-adaptation.md)

**Что построить:** последний срез юнита — DSH первым классом в
`docs/reference/harnesses.md` (скиллы, панель, онто-док; без «DSH вне
плана»), запись живых проб в `docs/ops/continue.md`, приписки в
`docs/plans/review-config.md` (решение 6 — для ZCode) и
`docs/plans/onto-doc.md` (DSH-прогон через `subagent`), обновление
`README.md`, `skills/README.md`, `docs/README.md`,
`docs/reference/README.md` и `docs/plans/README.md`; проверка, что
`gen_agents.py`, `.zcode/agents/`, `.zcode/workflows/` и `deploy.json`
не сломаны, а DSH-бандла и глобальной установки нет. Старые записи о DSH
в runbook получают приписку «снято» — история не стирается.

**Блокируется:** 01, 02, 03, 04.

**Демо-путь:** открыть `docs/reference/harnesses.md` и
`docs/ops/continue.md` — DSH назван первым классом, живые пробы
записаны; `grep -n "DSH — пробел окружения" docs/reference/harnesses.md`
пуст, `grep -n "DSH и Qoder — вне плана"` по `harnesses.md`,
`review-panel.md`, `ontodoc-run.md` пуст для DSH; `pytest` и
`lint --strict` зелёные; `git diff` по ZCode-файлам пуст; DSH-бандла и
следов установки в `~/.dsh`/`~/.agents` нет.

**Критерии приёмки**:

- [ ] матрица — артефакт: `docs/reference/harnesses.md`,
      `tests/test_review_roles.py`; ожидание: DSH первый класс для
      скиллов, панели и онто-дока; фраз «DSH вне плана» и «пробел
      окружения» для DSH нет; Qoder остаётся названным пробелом;
      строка о безусловном запуске генератора под DSH исправлена —
      DSH-ветка генератор не зовёт; ZCode-разделы сохранены; сторож
      DSH-пробела обновлён, мутации краснеют (спека, «Готово» 1)
- [ ] runbook — артефакт: `docs/ops/continue.md`, выписка каталога
      DSH-сессии; ожидание: живой каталог (восемь модельных скиллов,
      `ship` user-invocable), `/ship`, `install.sh --check`, базовая
      цифра 452 passed (2026-11-06) и текущая цифра среза, маршруты
      живых проб, пути артефактов; старые записи о DSH помечены «снято»
      (спека, «Готово» 1, 9)
- [ ] legacy-поправки — артефакт: `docs/plans/review-config.md`,
      `docs/plans/onto-doc.md`; ожидание: приписки про ZCode-legacy и
      DSH-прогон через `subagent` на месте, история не переписана
      (спека, «Решения», техническое следствие 7)
- [ ] индексы — артефакт: `README.md`, `skills/README.md`,
      `docs/README.md`, `docs/reference/README.md`,
      `docs/plans/README.md`; ожидание: DSH-первый-класс и юнит
      названы, спека связана, сирот нет, `gitmark.py lint --strict`
      чист (спека, «Готово» 7)
- [ ] ZCode legacy — артефакт: `git diff` по
      `skills/init/gen_agents.py`, `.zcode/workflows/`, `deploy.json`;
      прогон генератора на временном ZCode-конфиге;
      `tests/test_gen_agents.py`, `tests/test_workflow_onto_doc.py`;
      ожидание: diff по отслеживаемым файлам пуст, генератор пишет шесть
      определений на ZCode-маршрутах (`.zcode/agents/` в `.gitignore`,
      `git diff` по нему вакуумен), тесты зелёные (спека, «Готово» 6)
- [ ] без плагина — артефакт: дерево файлов, `git status`, listing
      `~/.dsh` и `~/.agents/skills`; ожидание: нет `cordis.patch.yml`/
      DSH-бандла, нет следов установки юнита в профиле и глобальных
      скиллах, `--check` — 0 (спека, «Готово» 8)
- [ ] охранник — артефакт: `python3 -m pytest tests/ -q`,
      `python3 skills/kb-search/gitmark.py lint --strict`,
      `gitmark.py index`; ожидание: зелёные, индекс пересобран, поиск
      находит DSH-раздел (спека, «Готово» 7, 9)

## Доказательства

Заполняются при ship: вывод `grep`, `pytest`, `lint`, `install.sh
--check`, `git diff` по ZCode-файлам, запись живых проб.
