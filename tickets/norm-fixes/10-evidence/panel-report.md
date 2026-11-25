# Ревью-панель nf10 — отчёт и триаж

Прогон один, четыре роли параллельно, маршрут
`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` / `max`. Паков нет.

Вердикты: reviewer-spec — вернуть; reviewer-code — не приёмка;
reviewer-kb — на правку; reviewer-tests — тесты принять, изменение
вернуть.

24 сырых находки → 13 групп: 3 P1 / 3 P2 / 7 P3. Все закрыты одним
проходом правок (P3 тоже — дёшево и в рамках тикета). Снятых нет.

## Закрытые правки

| # | приоритет | находка (роли) | правка |
|---|---|---|---|
| 1 | P1 | архив сливает одноимённые бандлы разных корней, знание форка теряется (spec, code; воспроизведено исполнителем) | путь архива `$archive_dir/$root/$name`, PID в имени каталога (коллизия epoch); target-тест двух корней; после фикса оба форка раздельно (p1-after-fix.txt) |
| 2 | P1 | шапка install.sh:11–13 «real directories are never touched» против нормы (tests, spec, code) | шапка переписана |
| 3 | P1 | приписка nf08 harness-agnostic противоречит legacy-2 (kb, spec, code, tests) | клауза сужена («вне legacy-корней», «ревизованы припиской legacy-2»), --check → legacy-записи |
| 4 | P2 | «Ограничения» harness-agnostic запрещают запись в ~/.dsh, архив пишет (spec) | исключение для state-архива legacy |
| 5 | P2 | tickets/README без строк 09/10 (kb, tests) | строки добавлены |
| 6 | P2 | отказ архивации не запинен тестом (tests, spec, code) | test_install_refuses_when_archive_cannot_be_written (HOME/state файлом): exit≠0, именованный отказ, дерево цело |
| 7 | P3 | хвост deliver.md: заголовок, --check wording, карта носителей, ссылка тикета 10, «Решения 76–77» (kb, spec, code) | хвост переписан, ссылки добавлены, указатель назван |
| 8 | P3 | протокол 3 deliver.md сужен до симлинков (kb) | «legacy-записи чистятся: симлинки — снос, реальные копии — архив» |
| 9 | P3 | copy-нога не сверяет байты архива (tests) | ассерт байтов архива для copy |
| 10 | P3 | check/dry-run только .dsh; HOME read-only не доказан (tests) | три корня в check-тесте, ассерт отсутствия архива в HOME |
| 11 | P3 | HOME unset — голый bash-выход (code, tests) | `[[ -n ${HOME:-} ]] || die`, target-тест |
| 12 | P3 | date/basename вне preflight инструментов (spec, code) | добавлены в tool loop |
| 13 | P3 | тестовый артефакт в реальном HOME (tests) | project-1795608646 снесён (проверен: ship/note.md теста) |

## Прогоны после правок

- Набор: **844 passed** (final-suite.txt).
- lint --strict: чисто (lint-strict.txt).
- Красная проба базы ddc051e: 6 failed (red-probe-base.txt).
- P1-воспроизведение после фикса: оба форка раздельно (p1-after-fix.txt).
- Демо: demo.txt; prod: prod-checks.txt (selfhost relink + чистая copy).

## Зацепки

Открытых зацепок нет.