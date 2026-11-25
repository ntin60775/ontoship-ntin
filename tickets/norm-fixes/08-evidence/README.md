# Доказательства nf08 — критерий → артефакт

| критерий тикета | артефакт | ожидание / факт |
|---|---|---|
| 1. install-режимы сносят legacy-симлинки | demo.txt, final-suite.txt (test_install_removes_legacy_symlinks_to_the_producer, test_copy_install_removes_legacy_symlinks) | `removed legacy ...` в link и copy, обе формы (корень целиком, per-bundle); факт |
| 2. реальные каталоги не трогаются | final-suite.txt (инвариант-тест: реальный `.qoder/skills/ship/` с локальным файлом, foreign-target, name-mismatch, producer-root) | файл и симлинки-не-цели на месте; факт |
| 3. --check read-only | check-read-only.txt (дерево до/после), final-suite.txt (test_check_warns_about_legacy_entries_without_deleting_them) | warning'и названы, дерево байт-в-байт; факт |
| 4. --dry-run не пишет | dry-run-tree.txt (дерево до/после), final-suite.txt (test_dry_run_plans_legacy_removal_without_writing) | `would remove legacy ...`, дерево не изменилось; факт |
| 5. красная проба на базе | red-probe-base.txt | 3 failed на 447b9b5; факт |
| 6. носители нормы в паритете | panel-report.md (группы 1, 3, 7, 10, 14–19), дифф коммита | тексты install.sh/usage, harness-agnostic, harnesses, deliver SKILL/спека, install-dry-run, core-team-boundaries, пины deliver-теста; факт |
| 7. набор зелёный | final-suite.txt, lint-strict.txt | 838 passed (до P3-правок warning-хвоста), lint чисто; факт |
| P2-дефект панели (внешняя граница) | target-red-before-fix.txt, p2-after-fix.txt, final-suite.txt (target-тест) | красен до фикса, внешние каталоги целы после; факт |
| prod | prod-checks.txt | selfhost check ok + чистая copy check ok; факт |
| панель | panel-report.md | 4 роли, 27→20 групп, 1 P1 / 9 P2 / 10 P3, все P1/P2 закрыты |

Дополнительный проход P3 (после первого merge): warning `--check`
согласован с guard'ами `legacy_cleanup` (симлинк-корень/симлинк-base —
«install does not follow symlinked roots; remove it manually»), шаг 3
deliver и пин переведены на «legacy-симлинки», текст ревизии deliver
уточнён; тест честности warning'а добавлен в target-тест.