# 03: живой полигон consumer-registry

**Спека:** [docs/plans/entry-and-continuity.md](../../docs/plans/entry-and-continuity.md)

**Что построить:** живой холодный старт в чужом проекте: клон
`consumer-registry` → `install` локальной сборки ntin через кэш раннера →
`init` → свежая сессия. Сценарий 1: «сделай план по ишью #7» — агент
загружает `grilling` и создаёт `docs/plans/<slug>.md`; `EnterPlanMode` не
вызван ни разу. Сценарий 2: «поправь строку в README полигона» (правка,
заведомо не тянущая спеку) — первым шагом ship-ран, правки внутри тикета,
не свободные `Edit`. Раунд итерации — правка шаблона блока одним срезом
вместе с вербатим-контрактом `BLOCK` в `tests/test_skill_init.py` и блоком
`AGENTS.md` репо → переустановка в полигон → свежая сессия → проба; не
больше трёх раундов. Логи сессий складываются в каталог полигона;
доказательство — выписка вызовов инструментов.

**Блокируется:** 01, 02.

**Демо-путь:** базовая проба — инцидент `sess_74567fb5` в
`sot-zcode-marketplace` на версии без секции: план-мод вызван (red-before
зафиксирован логом хоста). После тикетов 01–02: лог свежей сессии в
полигоне — `grilling` вызван, спека создана, `EnterPlanMode` отсутствует;
вторая сессия — ship-ран.

**Критерии приёмки**:

- [x] полигон поднят — артефакт: клон `consumer-registry`, журнал деплоя
      раннера; ожидание: `install` по локальной сборке и `init` прошли
      (спека, «Готово» 4)
- [ ] сценарий «план» — артефакт: лог сессии с вызовами инструментов;
      ожидание: `grilling` вызван, спека создана, `EnterPlanMode`
      отсутствует (спека, «Готово» 4)
- [ ] сценарий «правка» — артефакт: лог второй сессии и состояние дерева;
      ожидание: ship-ран первым шагом, правки в рамках тикета
      (спека, «Готово» 4)
- [ ] итерации — артефакт: лог раундов (не больше трёх) в тикете;
      ожидание: зелёный раунд или фиксация красного третьего с
      активацией тикета 04 (спека, «Готово» 4, 5)

## Доказательства

Полигон — `/home/prog7/home/dev/personal/consumer-registry`
(репо-заглушка `consumer-registry` v0.1.0, один коммит `30d612a`).
Durable-источники этого раздела: git-история и файлы полигона, журнал
раннера, артефакты хоста `~/.zcode/cli/artifacts/sess_<id>/`, БД сообщений
`~/.zcode/cli/db/db.sqlite`, апп-лог `~/.zcode/cli/log/zcode-2026-11-02.jsonl`.
Rollout-файлы сессий ротируются (начало срезается) — выписки сняты из них
своевременно и приведены в конце раздела дословно.

**Красный на базе.** Инцидент `sess_74567fb5` 2026-11-02 в проекте
`sot-zcode-marketplace` на ntin v0.1.0 без секции «Вход в работу»:
запрос «план по #10» в 10:26:14Z, вызов `EnterPlanMode` в 10:26:55Z,
одобренный план в 10:46:23Z, дальше прямые правки в `main` — источник:
апп-лог `~/.zcode/cli/log/zcode-2026-11-02.jsonl`. Это поведение до
тикетов 01–02; полигон доказывает смену.

**Установка — локальная сборка через кэш раннера.** Worktree среза
`eac-03-polygon` от `e9aa9f5`; локальная сборка (main на 9 коммитов
впереди тега `v0.2.1`, с секцией «Вход в работу») подставлена в кэш
раннера `~/.cache/sot-zcode-marketplace/ontoship-ntin-v0.2.1/`; гейт
пин↔version пройден (0.2.1 = 0.2.1). Штатный `install` раннера
(`deploy/deploy-plugin.py` маркета, каталог `14816cf`):

```text
деплой ontoship-ntin (v0.2.1, манифест: plugin) в …/consumer-registry
  skills/{kb-search,kb-curate,init,grilling,to-tickets,ship,testing,critic,onto-doc}
    → .agents/skills/…
  .zcode/workflows/onto-doc.dwf.ts → .zcode/workflows/
пост-шаг: run пропущен (нет docs), say — запусти скилл init
```

`deployed.json`: ref `v0.2.1`, 10 маппингов, `deployed_at`
`2026-11-02T16:37:36+0200`. Секция «Вход в работу» подтверждена grep-ом
в установленной копии `.agents/skills/init/SKILL.md` полигона (на момент
проб — 1 вхождение; после прохода кэш раннера восстановлен до подлинного
тега `v0.2.1`, где секции нет по определению релиза).

**Init — четыре файла, шесть ролей (снимок на момент init).** Выполняла
деплой-сессия `sess_c9fcce2c` (ntin-workspace, 16:41–16:55) против
полигона. Durable-след — артефакты хоста этой сессии
(`~/.zcode/cli/artifacts/sess_c9fcce2c-…/`): запись `AGENTS.md`
(call_3102…, управляемый блок с секцией «Вход в работу», плейсхолдер
подставлен `.agents/skills`), `.gitignore` — 7 строк (call_fc193…),
скелет `docs/ops/continue.md` (call_5cc145…), `.agents/config.toml` —
шесть ролей (call_2088…: ревью на `deepseek-v4.1-flash-1017`, `critic`
на `GLM-5.3`, `curator` на `GLM-5.3-Flash`). Оговорка: это состояние на
момент init и обеих проб; позже слайс Т1 полигона принёс проектные
`AGENTS.md` и `.gitignore`, init-версии вытеснены (блок сохранён сессией
пробы 2 в `/tmp/cr-t1/backup/AGENTS.md.ontoship` перед ff-merge —
эфемерно). Восстановление блока перед перезапуском проб — повторный
прогон init (идемпотентен, теперь по tracked-файлу).

**Прогон 1 «план» — механика зелёная, ввод отличался от спеки.** Свежая
сессия `sess_505b31d5` (16:57–17:36 по апп-логу, 53 вызова инструментов
по `tool.call.started`: 44 до ротации rollout + 9 после). Ввод
оператора — «изучи ишью 7» (seq 0), затем «стартуй юнит» (seq 15,
15:00:41Z) — команда словаря метода, не дословный запрос спеки «сделай
план по ишью #7». Что доказано: `grilling` вызван (15:01:03Z, уже после
команды), draft-спека `docs/plans/consumer-registry-v0.2.0.md` создана
и прошла план-гейт ask-ом, `EnterPlanMode`/`ExitPlanMode` отсутствуют во
всей сессии; дальше метод без понуждения — `to-tickets`, три тикета со
сверкой понимания, критик-гейт workflow `dwfrun-89ddee1e` на модели из
конфига полигона, состояние в `continue.md`. Чего не доказано: вызов
`grilling` на естественный план-запрос без команды словаря — маршрутизация
из правила входа не гонялась (критерий остаётся открытым до перезапуска).

**Прогон 2 «правка» — ship-ран полный, ввод отличался от спеки.** Вторая
свежая сессия `sess_66c06d97` (17:40–18:10) — ввод «шип тикет 1» (seq 0),
команда словаря, не дословный запрос спеки «поправь строку в README
полигона». Что доказано: полный проход ship — worktree
`consumer-registry.t1` от базы `30d612a`, ветка `t1/repo`, тикет Т1
полигона, срез `1d82dc7` (правка README вошла в слайс тикета),
ревью-панель `dwfrun-9aefc1d2` — четыре актёра на
`deepseek-v4.1-flash-1017$max`, находки закрыты срезом `f7c479e`, merge
`--ff-only t1/repo` и снос worktree (шаг 6 дословно; ветка после слияния
удалена — durable-след: reflog `merge t1/repo: Fast-forward` и
родительство `1d82dc7 → f7c479e` в main), приёмка Т1 отдельным
ask-вопросом, `EnterPlanMode` отсутствует. Правки проекта — только в
worktree; после merge сессия делала учётные правки в главном дереве
(статус тикета, `continue.md` — 16:10Z), свободных правок проекта нет.
Чего не доказано: уход правки без команды словаря в ship-ран —
маршрутизация из правила входа не гонялась (критерий остаётся открытым
до перезапуска).

**Итерации.** Раундов правки шаблона — ноль: шаблон блока не редактировался,
переустановка в полигон не потребовалась (механика обеих проб зелёная с
первой попытки). Тикет 04 (условный хук) не активируется — условие
(«третий раунд красный») не наступило; зацепка в runbook — финальной
записью после merge.

**Регрессия ntin.** Полный набор в worktree среза — **386 passed**
(без изменений кода: тикет правит только этот файл доказательств).

**Расхождения ожидание/факт:**

- ввод обеих проб отличался от спеки: «изучи ишью 7» + «стартуй юнит»
  вместо «сделай план по ишью #7», «шип тикет 1» вместо «поправь строку
  в README полигона» (источник — БД сообщений, seq 0/15); механика метода
  обеими пробами доказана целиком, маршрутизация естественных запросов —
  нет; два критерия приёмки открыты до перезапуска проб дословными
  запросами спеки;
- init выполняла сессия в ntin-workspace (`sess_c9fcce2c`), а не
  отдельная свежая сессия полигона — init — это шаг установки, не проба;
  результат init (четыре файла, подстановка плейсхолдера) доказан
  артефактами хоста и состоянием диска на момент init;
- ротация rollout срезала начало обеих сессий: выписка прогона 1 снята
  до ротации (44 из 53 вызовов, остальные 9 — хвост с обработкой находок
  критика), выписка прогона 2 — хвост после ротации (21 вызов); начало
  прогона 2 (создание worktree, слайс) доказывается durable-состоянием:
  коммиты `1d82dc7` и `f7c479e`, reflog ff-merge;
- прогон 1 прошёл дальше план-гейта (полные фазы 1–2 с критиком) —
  спека этого не запрещает; все наблюдаемые критерии зелёные;
- запрос прогона 2 ушёл в ship-ран тикета Т1 целиком — правка README
  легла в полный слайс тикета; ожидание «правки в рамках тикета»
  выполнено, «ship-ран первым шагом» — под командой словаря;
- блок «Вход в работу» вытеснен из `AGENTS.md` полигона слайсом Т1
  после проб (см. «Init»); на поведение проб это не влияло — обе прошли
  при живом блоке;
- ранняя запись этого тикета утверждала «деплой-сессия дважды
  опустошала continue.md ntin» — снято: артефакты `sess_c9fcce2c`
  показывают обычные правки, коммит `e048e7a` — +17/−3 по runbook;
  опустошений не было;
- proof-выписки приведены в тикете дословно (ниже) — эфемерный
  `.scratch/probes/` полигона ссылкой-доказательством не служит.

**Критик-гейт юнита:** прогон `dwfrun-57b899ce` до первого ship юнита
(запись в runbook, находки закрыты `5c3b7b8`) — гейт пройден ссылкой.

**Панель** — `dwfrun-31ad61c4-4bbc-4695-8570-29ec41c6c65a` (четыре роли
параллельно, модель `qwen-alibaba-model-studio-intl/deepseek-v4.1-flash-1017$max`
из `.agents/config.toml`, запасной путь `subagent_model`; вход роли —
дифф `e048e7a..c73aa4b`, тикет, спека, канон; сверка определений с
конфигом до запуска пройдена — 6 ролей in sync). Вердикты: reviewer-spec
«принять с находками», reviewer-tests **«вернуть»**, reviewer-code
«принять», reviewer-kb «принять с находками»; сырых находок 1 P1 /
7 P2 / 11 P3, после дедупликации — P1 и шесть P2 смысловых. Фолбэков и
пропусков ролей не было. Границы проверки (со слов ролей): install/init
и живые сессии панели не перезапускала; сверялись deployed.json,
конфиг ролей, git-история полигона, выписки; pytest 386 passed и lint
--strict перепроверены.

Судьба находок: P1 (ввод проб отличался от спеки — маршрутизация не
доказана) — подтверждено исполнителем по БД сообщений; два критерия
сняты с [x], перезапуск проб дословными запросами — у оператора.
Закрыто правками этого же среза: счёт вызовов и время прогона 1 (53 и
17:36), уточнение Edit-путей (учётные правки после merge отделены от
правок проекта), init-артефакты переписаны как снимок с durable-ссылками
на артефакты хоста и оговоркой о вытеснении блока, red-before получил
адрес (апп-лог, три метки времени), «дважды опустошала» снято как
ошибка чтения артефактов, ветка `t1/repo` переформулирована через
reflog и родительство, ссылка на кэш заменена на установленную копию и
`deployed.json`, выписки перенесены в тикет дословно, грамматика
(«init — это», «наблюдаемые критерии», падежи). Зацепка оператору и
финальной записи runbook: абзац «остались свежая сессия и два сценария»
(`e048e7a`) переписывается записью о прогоне 03.

**Выписка прогона 1** (44 вызова до ротации rollout
`model-io-sess_505b31d5-…jsonl`; полные 53 — апп-лог, 14:57:46–15:36:10Z;
план-режим отсутствует):

```text
  1. Bash  gh issue view 7 --repo ntin60775/sot-zcode-marketplace --json …
  2. Bash  git -C …/consumer-registry ls-files && untracked
  3. Bash  ls -la полигона, рекурсивный ls
  4. Read  docs/ops/continue.md                    # правило входа: сессия отсюда
  5. Read  deploy.json
  6. Read  skills/consumer-registry/SKILL.md
  7. Bash  ls .agents/redpolitika.md и пр.
  8. Skill  skill=post                             # глобальный ru-text роутинг
  9. Bash  git tag -l полигона
 10. Skill  skill=grilling                         # ← запрос плана → grilling
 11. Bash  cat .gitignore, .agents, .zcode
 12. Bash  ls кандидатов контура
 13. Bash  find контурных репо
 14. TodoWrite  собрать факты
 15. Bash  git log маркета
 16. Bash  git log 1c-zcode
 17. Bash  python3 -c json каталога маркета
 18. Bash  git log тегов 1c-zcode
 19. Bash  python3 -I heredoc по .zcode/work
 20. Bash  grep AGENTS.md маркета
 21. Bash  ls .zcode 1c-zcode
 22. Bash  git tag -V хвост 1c-zcode + heredoc
 23. AskUserQuestion  header=Версия                # интервью grilling
 24. Bash  date +%z, сверка зон
 25. Write  docs/plans/consumer-registry-v0.2.0.md # ← draft-спека создана
 26. AskUserQuestion  header=План-гейт              # план-гейт ask-ом
 27. Skill  skill=to-tickets                       # фаза 2 по методу
 28. TodoWrite
 29. AskUserQuestion  header=Тикет 1               # нарезка ask-ом
 30. AskUserQuestion  header=Понимание 1           # сверка понимания
 31. Write  tickets/consumer-registry-v0.2.0/01-repo.md
 32. Write  tickets/consumer-registry-v0.2.0/02-release.md
 33. Write  tickets/consumer-registry-v0.2.0/03-pilot.md
 34. Bash  head -20 .agents/skills/critic/SKILL.md
 35. Read  .agents/skills/critic/SKILL.md
 36. Read  .agents/config.toml
 37. Read  .zcode/agents/critic.md
 38. Agent  subagent_type=critic                   # критик-гейт после нарезки
 39. ListModels
 40. AskUserQuestion  header=Запуск критика
 41. TodoWrite
 42. Skill  skill=dynamic-workflows
 43. CreateWorkflow  name=Критик плана consumer-registry
 44. Write  docs/ops/continue.md                   # состояние в runbook
+ 9 после ротации (хвост): Bash, Ask «Находки критика», 6 Edit
  (спека, тикеты 01/03, continue.md), TodoWrite
```

**Выписка прогона 2** (хвост после ротации rollout
`model-io-sess_66c06d97-…jsonl`; план-режим отсутствует; начало —
создание worktree `.t1` и слайс — доказано коммитами `1d82dc7`, `f7c479e`
и reflog ff-merge):

```text
  1. Edit  …/consumer-registry.t1/scripts/registry_check.py
  2. Edit  …/consumer-registry.t1/scripts/registry_check.py
  3. Edit  …/consumer-registry.t1/scripts/registry_check.py
  4. Edit  …/consumer-registry.t1/scripts/registry_check.py
  5. Write …/consumer-registry.t1/tests/test_registry.py
  6. Write …/consumer-registry.t1/templates/gitignore.snippet
  7. Edit  …/consumer-registry.t1/skills/consumer-registry/SKILL.md
  8. Edit  …/consumer-registry.t1/README.md          # правка README в слайсе
  9. Bash  cd …/t1 && python3 tests/test_registry.py
 10. Bash  WT=…/t1 … reviewer-code mutants: must all reject
 11. Bash  python3 heredoc: schema/data пробы валидатора
 12. Bash  python3 heredoc: schema/data пробы валидатора
 13. Bash  cd …/t1 && git add -A && git commit -m "fix: находки ревью-панели…"
 14. Bash  git merge --ff-only t1/repo && git worktree remove …  # шаг 6 ship
 15. Read  …/consumer-registry/.gitignore            # проверки после merge
 16. Read  …/consumer-registry/AGENTS.md
 17. Bash  mkdir -p /tmp/cr-t1/backup && cp AGENTS.md …   # бэкап блока вне репо
 18. Bash  mv AGENTS.md …/backup/AGENTS.md.ontoship && …  # перед ff-merge
 19. Bash  python3 tests/test_registry.py; validator…     # прогон на слитом дереве
 20. TodoWrite  Worktree от базового коммита 30d612a…
 21. AskUserQuestion  header=Приёмка Т1              # приёмка отдельным вопросом
+ учётные правки после merge: Edit tickets/…/01-repo.md,
  docs/ops/continue.md (16:10Z)
```
