# 08-evidence — артефакты дымовой пробы sa08

Проба: ручной /ship, корневая сессия
`session-4cb90e5b-6156-4b93-ab05-e0589b703df7`, 2026-11-17.
Temp-проект: `/tmp/sa08-smoke/proj` (git bundle — `toy-project.bundle`,
после уборки /tmp восстанавливается `git clone toy-project.bundle`).
Отчёт пробы — в тикете [08-live-proof.md](../08-live-proof.md),
секция «Отчёт пробы».

| файл | что |
|---|---|
| 01-install-core.log | установка ядра --copy, 10 бандлов, exit 0 |
| 02-install-pack.log | установка эталонного пака --copy --pack, exit 0 |
| 03-check.log | install.sh --check: 10 бандлов ok, пак ok, check: ok |
| 04-init-verify.log | init: валидатор пака, маркеры, git status, sha256 проход 1 |
| 05-init-idempotence.log | init проход 2: block == template, sha256 совпали |
| 06-init-newline-fix.log | расхождение newline AGENTS.md и исправление (BLOCK_FENCE) |
| 07-init-report.md | отчёт init: четыре файла, бутстрап, роль пака ask-ом |
| 08-manifest-mutated.json | мутированный манифест (expect_exit 1) |
| 09-red-probe.log | красная проба: baseline зелёный → мутация → гейт красный, exit 1 |
| 10-red-stop-restore.log | остановка прохода, восстановление манифеста (sha256), зелёный повтор |
| 10a-red-stop-git-state.log | git-состояние остановки: main = ae26ce9, merge нет |
| 11-toy-red-base.log | финальные доказательства toy: провенанс, краснота базы, дифф, grep, сверка строк |
| 12-toy-fix.log | первичный срез 38b8e0e (заменён правками панели c1e04cb) |
| 13-toy-ship-gates.log | гейты внутреннего ship: 1 пройдено, exit 0 |
| *-attempt1.log | логи первой попытки, потерянной внешним клинером /tmp (инцидент 1) |
| toy-project.bundle | git bundle toy-репо (main 653c062, вся история пробы) |

Коммиты toy-репо: `82a964c` README с опечаткой → `0ea80b1` init →
`ae26ce9` toy-тикет → `38b8e0e` первичный срез → `c1e04cb` правки
панели → `653c062` автоприёмка (merge ff в main).