# Init с паком — отчёт (шаг 2 пробы sa08)

Проект: /tmp/sa08-smoke/proj (git, main). Повторный прогон после утери
первой попытки внешним клинером /tmp (инцидент назван в отчёте пробы).

## Файлы

- AGENTS.md — created: файл отсутствовал, создан ровно управляемый блок
  (шаблон скилла init, случай 1). Расхождение ожидание/факт: инструмент
  записи срезал завершающий newline; канон блока по BLOCK_FENCE
  tests/test_skill_init.py кончается `<!-- END ontoship -->\n`;
  исправлено допиской одного байта, сверка block == template — True
  (лог 06-init-newline-fix.log).
- .gitignore — created: пять строк (.gitmark/, *-map.html, .scratch/,
  .agents/skills/, .agents/packs/).
- .agents/config.toml — created: бутстрап. Шесть ролей ядра стандартной
  раскладкой без ask (все маршруты и уровни сверены с живым
  list_subagent_models 2026-11-17): reviewer-spec/tests/code/kb —
  qwen-token-plan-deepseek/deepseek-v4.1-flash-1017, max; critic —
  qwen-token-plan-max/qwen4-max-preview, xhigh; curator — тот же
  deepseek-маршрут, high. Пул [validation]: deepseek-account/deepseek-flash
  max, qwen-token-plan/qwen3.8-flash xhigh — оба живы, записаны без ask.
  Роль пака reviewer-reference-code — бутстрап-вопрос оператору
  (ask 2026-11-17): выбран ближайший к раскладке ядра маршрут
  qwen-token-plan-deepseek/deepseek-v4.1-flash-1017, max.
- docs/ops/continue.md — created: скелет дословно, updated: 2026-11-17.

## Паки стандартов

- .agents/packs/ обнаружен; пак reference-pack проверен валидатором
  бандла pack: «✓ пак reference-pack (team, 1.0.0) валиден», exit 0.
- Роль пака reviewer-reference-code зарегистрирована в реестре
  бутстрап-вопросом (модель назначает реестр, не пак).

## Роли команды

Бандл профиля ontoship-team 0.3.0 установлен (link-канал, поколение
модулей активного GUI); init бандл не устанавливает и ролей команды в
реестр не пишет. Факт среды: в паузе пробы операторский GUI перезапущен
(скилл chain появился в каталоге сессии) — проба профиль не трогала.

## Проверь (шаг 6)

- Маркеры: BEGIN=1, END=1.
- git status после первого прогона: ?? AGENTS.md, .gitignore, .agents/,
  docs/ (созданные файлы).
- Идемпотентность: второй прогон init — блок равен шаблону (не меняется),
  пять строк .gitignore на месте (не меняется), конфиг существует
  (не трогается), continue.md существует (не трогается); sha256 четырёх
  файлов совпали между проходами (логи 04/05; хэш AGENTS.md изменён
  только допиской newline до фиксации).
- Файлы init закоммичены в toy-репо: 0ea80b1.