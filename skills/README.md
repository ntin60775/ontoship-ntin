---
node_type: index
title: Скиллы — бандлы установщика
service: _platform
status: active
updated: 2026-11-02
tags: [index, skills, installer]
links:
  part_of: [../README.md]
  relates_to: [../docs/ops/continue.md]
---

# Скиллы

Состав скиллов ведут два машинных носителя под взаимным паритетом:
массив `SKILLS` установщика `scripts/install.sh` — канал
`<project>/.agents/skills` — и маппинги `deploy.json` плагина маркета —
канал `<project>/.zcode/skills`. Ядро KB — `kb-search`,
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

Новый скилл появляется бандлом в `scripts/install.sh` и строкой здесь — одним
коммитом; строка «Раскладки» в `AGENTS.md` ведёт сюда.
