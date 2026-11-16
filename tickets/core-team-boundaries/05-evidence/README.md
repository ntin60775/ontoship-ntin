# Evidence тикета 05 «Перенос спеки team-profiles»

Юнит core-team-boundaries, спека «Готово» 5 (решение 8, триаж G6/S2/G22).
База ядра `9fc1c21`, team-коммит `03969fa`.

- [01-move-diff.md](01-move-diff.md) — карта переноса: файлы team,
  носители ядра, маркеры, пробелы.
- [02-red-base.md](02-red-base.md) — красная проба: базовые факты
  (критерии 1/3/4) и промежуточные прогоны (lint I4 ×7, traceability
  1 failed) после снятия файлов до правки носителей.
- [03-checks.md](03-checks.md) — проверки критериев 1–4: дерево, sha256,
  grep висящих ссылок и маркеров, виды, полный набор, install --check.
- [spec-link-form.diff](spec-link-form.diff) — diff спеки: только форма
  ссылок, содержание не менялось.
- [lint.log](lint.log) — `lint --strict` ядра, чисто.
- [core-suite.log](core-suite.log) — `pytest -q` ядра, 784 passed.
- [04-panel.md](04-panel.md) — отчёт ревью-панели: вердикты, 17 групп
  находок, правки одним проходом.