---
node_type: index
title: Скиллы — бандлы метода
service: _platform
status: active
updated: 2026-11-02
tags: [index, skills, bundles]
links:
  part_of: [../README.md]
  relates_to: [../docs/ops/continue.md]
---

# Скиллы

Состав скиллов ведут два машинных носителя под взаимным паритетом:
массив `SKILLS` установщика `scripts/install.sh` — канал
`<project>/.agents/skills` — и маппинги `deploy.json` плагина маркета
(рядом лежит манифест `.zcode-plugin/plugin.json`) — канал
`<project>/.zcode/skills`. Ядро KB — `kb-search`,
`kb-curate`, `init`; фазы метода — `grilling`, `to-tickets`, `ship`;
правило качества — `testing`; ревью плана — `critic`; док-часть — `onto-doc`.

- [kb-search/](kb-search/SKILL.md) — движок GitMark и поиск по KB.
- [kb-curate/](kb-curate/SKILL.md) — CREATE, UPDATE, DEPRECATE, LINK,
  REINDEX; модель онтологии.
- [init/](init/SKILL.md) — управляемый блок, `.gitignore`, конфиг ролей,
  машинный источник перечня ролей `roles.py`, генератор `gen_agents.py`.
- [grilling/](grilling/SKILL.md) — интервью по фронтиру, выход в спеку
  на план-гейт.
- [to-tickets/](to-tickets/SKILL.md) — нарезка спеки на tracer-bullet
  тикеты.
- [ship/](ship/SKILL.md) — один проход: worktree, тесты, ревью-панель,
  merge.
- [testing/](testing/SKILL.md) — классы тестов и планка качества.
- [critic/](critic/SKILL.md) — критика плана до первого ship.
- [onto-doc/](onto-doc/SKILL.md) — тяжёлая док-часть: fan-out кураторов
  по плану.

Новый скилл появляется бандлом в `scripts/install.sh`, маппингом в
`deploy.json` плагина маркета, строкой здесь и кортежем в
`tests/test_install.py` — одним коммитом; паритет держит тот же тест.
Строка «Раскладки» в `AGENTS.md` ведёт сюда.
