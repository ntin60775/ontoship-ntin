# Перенос: карта изменения (тикет 05, база 9fc1c21)

## Team-репо (`/home/prog7/home/dev/contrib/forks/ontoship-team`, коммит 03969fa)

| путь | происхождение |
|---|---|
| `docs/plans/team-profiles.md` | спека из ядра; нормативное содержание сохранено; форма ссылок в ядро — адреса-проза, информация frontmatter relates_to — проза-абзац, updated поднят, финальный newline добавлен (spec-link-form.diff) |
| `tickets/team-profiles/07-live-proof.md` | побайтово из ядра (sha256 e992dc4c…) |
| `tickets/team-profiles/08-suite-kb-08-protocol.md` | побайтово из ядра (sha256 60649c08…) |
| `docs/plans/README.md` | новый индекс планов team |
| `tickets/README.md` | новый индекс тикетов team (открытые 07/08; закрытые — адрес-проза в ядро) |
| `tickets/team-profiles/dag.md` | вид team: полный граф юнита (14 узлов), 07 pending / 08 waiting |
| `tickets/team-profiles/kanban.md` | вид team: полная таблица, 07 ready (проба остановлена оператором — проза), 08 blocked |
| `README.md` | «Состав» + секция «Спека и тикеты»: индексы, владелец, пробел KB-бутстрапа |

Линк тикетов 07/08 на спеку `../../docs/plans/team-profiles.md` резолвится
внутри team — правка не потребовалась.

## Ядро (worktree ctb05-spec-move)

Снято (перенесено): `docs/plans/team-profiles.md`,
`tickets/team-profiles/07-live-proof.md`,
`tickets/team-profiles/08-suite-kb-08-protocol.md`.

Носители правок:

- `docs/plans/README.md` — стаб-указатель вместо строки спеки; frontmatter
  `relates_to` без team-profiles.md; `updated` 2026-11-17.
- `docs/plans/core-team-boundaries.md` — frontmatter `relates_to` без
  team-profiles.md (тело не тронуто: упоминания — проза).
- `docs/plans/standards-autoship.md` — две приписки решения 14: линк →
  адрес-проза.
- `docs/ops/continue.md` — два линка → адреса-проза («Где мы», абзац
  юнита); абзац юнита «Порядка тикетов»: запись переноса, статус 07
  (проба остановлена оператором 2026-11-16) и счётчик 12 закрытых
  вместо устаревших «в работе / 11» (тривиальная правка согласованности).
- `tickets/README.md` — шапка юнита, строки 07/08, заметка переноса,
  заморозка sa08: линки → адреса-проза.
- 16 закрытых тикетов и progress-файлов `tickets/team-profiles/` —
  шапка «Спека»: линк → адрес-проза (механическая замена, критерии и
  доказательства тикетов не тронуты).
- `tickets/team-profiles/dag.md`, `kanban.md` — перегенерированы без
  07/08 (12 закрытых узлов, транзитивная редукция рёбер); шапки несут
  запись переноса и адрес видов team.
- `tickets/team-profiles/leads.md` — запись переноса в шапке; реестр
  остаётся в ядре.

Маркеры traceability (4):

- `tests/test_canon_sync.py::test_triviality_override_in_canon_and_mirror`,
  `tests/test_skill_grilling.py::test_triviality_filter_contract` —
  `docs/decisions/ontoship-core.md#три фазы` (носитель нормы тривиальности
  после переноса — канон; core-team-boundaries норму не несёт, указатель
  на него был бы ложным маркером). Провенанс «team-profiles 14, решение 23»
  сохранён в маркере.
- `tests/test_skill_init.py::test_team_bundle_is_named_by_reference`,
  `test_team_reference_contract_can_fail` —
  `docs/plans/core-team-boundaries.md#готово` («Готово» 3 инкорпорирует
  решение 15 team-profiles: ссылка init на team-бандл в §5/отчёте).

Размещение — на носителях нормы, решение оператора ask 2026-11-17
(приёмка 05): формулировка «Готово» 5 ревизована (аннотация 2026-11-17
спеки), критерий 3 тикета приведён к ней; тесты остались в ядре
(сторожат канон, зеркало, grilling, init). Отклонений и костылей нет.

## Названные пробелы (не делались по скоупу оператора)

- KB-бутстрап team (онтология, индекс, lint) — следующий шаг (онто-док);
  `lint --strict` исполнен только в ядре.
- Новые тесты team не писались (скоуп оператора 2026-11-16); набор team
  не запускался (docs-only изменение, тесты team читают манифест/патч).
- Team-релиз v0.3.0 и активация в живом профиле отложены (решение 6).
- PR-путь team-репо: remote нет — локальный коммит в main.

## Правки панели одним проходом (2026-11-17)

Отчёт — [04-panel.md](04-panel.md): 18 сырых → 17 групп (2 P2 / 15 P3),
оба P2 и правимые P3 закрыты; P3-a закрыт решением оператора
ask 2026-11-17 (маркеры на носителях нормы, «Готово» 5 ревизовано);
P3-k (синхронизация
шапки 07 с агрегацией блокеров) — зацепка оператору в leads юнита.
Team: коммит правок `e9f1854` поверх `03969fa` (адрес allowlist-справочника,
форма адресов спеки, метки ссылок, newline, агрегация в шапках видов).
Ядро: отдельный коммит правок поверх среза `23dae29` (обёртка шапок и
абзаца continue.md, updated, статус 07 в tickets/README, докстринг init,
секции тикета, leads юнита, evidence).