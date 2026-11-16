# Init-отчёт — проба core-team-boundaries (тикет 04)

Дата: 2026-11-17. Корень проекта: `/tmp/ctb04-project` (`git rev-parse --show-toplevel`).
Харнесс: DSH — инструменты `list_subagent_models` и `subagent` присутствуют.

## Файлы (первый прогон)

| файл | итог |
|---|---|
| `AGENTS.md` | `created` — файл отсутствовал, создан содержащим ровно блок ontoship |
| `.gitignore` | `created` — строки: `.gitmark/`, `*-map.html`, `.scratch/`, `.agents/skills/`, `.agents/packs/` |
| `.agents/config.toml` | `created` — бутстрап стандартной раскладкой (ниже) |
| `docs/ops/continue.md` | `created` — скелет, `updated: 2026-11-17` |

Проверка: `git status --short` → `?? .agents/`, `?? .gitignore`, `?? AGENTS.md`,
`?? docs/ops/`; diff по новым файлам пуст (не в индексе). Маркеры:
`grep -c '^<!-- BEGIN ontoship -->$'` = 1, `grep -c '^<!-- END ontoship -->$'` = 1.

## Реестр ролей (.agents/config.toml)

Конфига не было — бутстрап. Источник моделей — живой `list_subagent_models`;
все шесть маршрутов стандартной раскладки и их уровни доступны → записано без ask.

| роль | model | level |
|---|---|---|
| `reviewer-spec` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `max` |
| `reviewer-tests` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `max` |
| `reviewer-code` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `max` |
| `reviewer-kb` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `max` |
| `critic` | `qwen-token-plan-max/qwen4-max-preview` | `xhigh` |
| `curator` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `high` (дефолт модели) |

Пул валидации `[validation]` (маршруты и уровни сверены с живым каталогом, все живы):
- `deepseek-account/deepseek-flash`, уровень `max`
- `qwen-token-plan/qwen3.8-flash`, уровень `xhigh` (дефолт модели)

Модель сессии (runtime-контекст «powered by …»): `qwen4-max-preview`.
Ревью-роли на модели, отличной от сессионной — норма независимости соблюдена.
Совпадение: модель роли `critic` (`qwen4-max-preview`) совпадает с моделью сессии —
допустимо по скиллу, названо здесь; отказом не является.

Пропусков ролей ядра и секции пула нет. Незнакомых секций/ключей нет.

## Идемпотентность (второй прогон)

Повторное применение процедуры init: блок AGENTS.md равен шаблону (побайтово,
нормализация CRLF) → `unchanged`; все 5 строк .gitignore присутствуют → `unchanged`;
`docs/ops/continue.md` существует → `unchanged` (не читался); конфиг существует →
не тронут, все 6 секций ядра и `[validation]` на месте.
SHA-256 четырёх файлов после второго прогона идентичны первому
(`02-init-hashes-run1.txt` = `02-init-hashes-run2.txt`), новых строк в
`git status --short` и `git diff` нет. Идемпотентность подтверждена фактом.

## Паки и роли команды

Каталога `.agents/packs/` нет — паков нет. Team-бандл пресетов в профиле
отсутствует (сверено перечнем бандлов `plugin_manager`).

## Дальше

Следующий шаг метода — построить KB (`docs/README.md` — главный индекс,
документы через `kb-curate`, команды сопровождения — в блоке). В рамках init
не запускался.