# 02: init и конфиг DSH

**Спека:** [docs/plans/dsh-adaptation.md](../../docs/plans/dsh-adaptation.md)

**Что построить:** DSH-ветку скилла `init` одним срезом — харнесс
определяется доступным инструментом (`list_subagent_models`/`subagent`
— DSH, `ListModels` — ZCode), DSH-ветка пишет управляемый блок с
командой `/ship`, конфиг ролей из `list_subagent_models` и четыре
строки `.gitignore` (`.gitmark/`, `*-map.html`, `.scratch/`,
`.agents/skills/`), не запускает `gen_agents.py` и не создаёт
`.zcode/agents/`/`.zcode/workflows/`. ZCode-ветка сохраняет шесть строк
и генератор. Управляемый блок этого репозитория приводится к DSH-виду с
`/ship`; ZCode-ветка проверяется контрактом и генератором на временном
ZCode-конфиге, без живого ZCode-прогона (харнесс — legacy).

**Блокируется:** 01 (панель нужна для ship этого тикета).

**Демо-путь:** временный git-проект с установленным ядром: первый
`init` пишет DSH-блок, конфиг и четыре строки, `.zcode` не появляется;
второй `init` не меняет ни байта; `git diff` пуст; `install.sh --check`
возвращает 0; контракт ZCode-ветки на временном конфиге даёт шесть строк
и определения ролей; живой ZCode-прогон не требуется — харнесс legacy.

**Критерии приёмки**:

- [ ] DSH-ветка — артефакт: `skills/init/SKILL.md`, `AGENTS.md`;
      ожидание: харнесс выбирается по инструменту, DSH-ветка пишет блок
      с `/ship`, конфиг из `list_subagent_models`, четыре строки
      `.gitignore`, не зовёт `gen_agents.py`; блок этого репозитория
      приведён к DSH-виду с `/ship`; ZCode-ветка сохраняет шесть строк
      и генератор (спека, «Готово» 2)
- [ ] живой init DSH — артефакт: временный git-проект, вывод `init` и
      `git status`; ожидание: блок/конфиг/четыре строки на месте,
      `.zcode/agents/` и `.zcode/workflows/` отсутствуют, второй прогон
      без изменений, `install.sh --check` — 0 (спека, «Готово» 2)
- [ ] idempotency — артефакт: повторный `init` и `git diff`; ожидание:
      ни одного изменённого байта, включая конфиг и скелет
      `docs/ops/continue.md` (спека, «Готово» 2)
- [ ] ZCode legacy — артефакт: временный ZCode-конфиг,
      `tests/test_skill_init.py`, `tests/test_gen_agents.py`; ожидание:
      контракт держит шесть строк ZCode-ветки, генератор пишет
      определения ролей на ZCode-маршрутах, тесты зелёные; живой
      ZCode-прогон не требуется — ZCode legacy (спека, «Готово» 6,
      «Ограничения»)
- [ ] контракт — артефакт: `tests/test_skill_init.py`; ожидание: новые
      DSH-проверки (ветка, блок с `/ship`, четыре строки) краснеют на
      базовом коммите и зелены на срезе; равенство блока репозитория
      DSH-шаблону и ZCode-шаблон сохранены; существующие ZCode-проверки
      не рваны (спека, «Готово» 2, 6)
- [ ] охранник — артефакт: `python3 -m pytest tests/ -q`,
      `python3 skills/kb-search/gitmark.py lint --strict`; ожидание:
      зелёные после среза (спека, «Готово» 9)

## Доказательства

Срез: worktree `ontoship-ntin-wt-dsh02`, ветка `dsh02-init` от базового
коммита `37057f4`. Тесты первыми: `24c8a9d` — красная проба, `372f53a` —
реализация. `create_worktree` снова упал («node» нет в PATH), worktree
создан `git worktree` (спека, следствие 6).

**Красная проба на базовом коммите** (полный набор, финальный тест-сет;
`git worktree add --detach /tmp/dsh02-base-probe 37057f4` и копия
`tests/test_skill_init.py`): **17 failed / 445 passed**. Все падения — в
`test_skill_init.py`: контракт скилла (два блока, выбор харнесса,
DSH-бутстрап), два набора `.gitignore`, равенство блока репозитория,
ZCode legacy и can-fail предусловия. Остальные 445 зелены.

**Разбор расхождений ожидание/факт:**

- ожидание — `create_worktree` создаёт worktree; факт — инструмент падает
  на `node` в PATH, использован `git worktree` (разрешено спекой);
- ожидание — init спрашивает модель каждой роли ask-инструментом; факт —
  в живом демо ответ оператора (решение 5) передан заранее, ask не
  задавался; контракт сторожит текст ask, живая ветка ask не проживалась —
  названный пробел демо, не дефект среза;
- остальных расхождений не было.

**Реализация.**

- `skills/init/SKILL.md`: шаг 0 — харнесс по инструменту хоста
  (`list_subagent_models`/`subagent` — DSH, `ListModels` — ZCode; ни
  одного или оба — вопрос и остановка); два управляемых блока (DSH с
  `/ship`, ZCode сохранён); `.gitignore` — четыре строки в DSH и шесть
  в ZCode; бутстрап разведён: DSH берёт маршруты из
  `list_subagent_models`, пишет `<provider>/<model>` и максимум уровня,
  модель сессии — из runtime-контекста, генератор не запускает; ZCode
  сохраняет `ListModels`, `[current]`, генератор и перезапуск.
- `AGENTS.md`: блок репозитория равен DSH-шаблону после подстановки
  `.agents/skills`.
- `tests/test_skill_init.py`: два блока, выбор харнесса, два набора
  `.gitignore`, DSH/ZCode-бутстрап и can-fail пробы.

**Живой init DSH.** Временный git-проект `/tmp/dsh02-live-init-final` (`git
init`, коммитов нет), ядро установлено из среза:
`scripts/install.sh --copy /tmp/dsh02-live-init-final` — девять бандлов
(`copied …`); `scripts/install.sh --check /tmp/dsh02-live-init-final` —
`check: ok` (0). Исполнение — отдельный DSH-агент `init-demo-02` с cwd temp по
скиллу; харнесс определён инструментами `list_subagent_models` и
`subagent`; корень — `.agents/skills`. Первый проход — `created`:
`AGENTS.md` (ровно блок DSH, `<навыковый корень>` → `.agents/skills`),
`.gitignore` (четыре строки), `.agents/config.toml` (шесть секций, все
`deepseek-account/deepseek-flash`, `level = "max"`),
`docs/ops/continue.md` (скелет, `updated: 2026-11-09`). Каталога
`.zcode` нет. `git status --short` — четыре untracked записи; `git diff`
пуст (коммитов нет); маркеры 1/1.

Второй проход — `unchanged` по всем четырём файлам; sha256 до/после
идентичны, `git status` посимвольно тот же. Сверка с шаблонами
самостоятельная: `AGENTS.md` == блок DSH с подстановкой, `.gitignore` ==
набор DSH, `continue.md` == скелет с датой. sha256:

```text
ac01b2fbeec9f1a0e50f44a1995e5e29186fd1fa21971fce2bcaf48a32cbadda  AGENTS.md
4c7b0a8d6cd6370f6b6c53402763b3bcdbd771aa613aa26d85f447d8a09bedc5  .gitignore
4750e5d0122794036f9ee798c4de1427d3e9b77bac8d446a189bd88533eda629  .agents/config.toml
8cd542a0a06f68b1eaab935b18455f0ffa146ffad71cc42ec1a530b0b9f7bd15  docs/ops/continue.md
```

Расхождение демо: ask моделей не задавался, ответ оператора передан
заранее — названный пробел.

**ZCode legacy.** Временный ZCode-конфиг `/tmp/dsh02-zcode-legacy`:
четыре ревьюера — `qwen-alibaba-model-studio-intl/deepseek-v4.1-flash-1017`,
`critic` — `qwen-token-plan/qwen3.8-flash` с `xhigh`, `curator` —
`account:zai-individual-coding-plan/GLM-5.3-Flash`.
`python3 skills/init/gen_agents.py /tmp/dsh02-zcode-legacy` — `6 role(s)
in sync`, шесть определений `.zcode/agents/*.md` с `model:` и
`thoughtLevel:`. ZCode-ветка скилла держит `ListModels`, `[current]`,
шесть строк и генератор (контракт); живой ZCode-прогон не заявлен —
харнесс legacy.

**Зелёный счёт.** `python3 -m pytest tests/ -q` — **462 passed = 458 + 4**
(контракт выбора харнесса, контракты DSH- и ZCode-веток, одна can-fail
проба `test_dsh_branch_contract_can_fail`; часть старых проверок
переписана без смены счёта). `python3 skills/kb-search/gitmark.py
lint --strict` — «чисто (102 файлов)».

**Панель (живой прогон, 2026-11-09).** Четыре роли одним сообщением через
`subagent` с `provider`, `model` и `reasoning_effort` из конфига
(`deepseek-account`, `deepseek-flash`, `max`); фолбэков нет. Все четыре
вердикта — «принять с находками»: reviewer-spec — 1 P2 / 3 P3,
reviewer-tests — 1 P2 / 2 P3, reviewer-code — 2 P2 / 4 P3,
reviewer-kb — 2 P2 / 5 P3; сырых 20 (6 P2 / 14 P3), после дедупликации
16 (5 P2 / 11 P3). Правки `e670778` закрыли 13 (5 P2 и 8 P3); девятая
P3 — состояние runbook — обновляется отдельным docs-коммитом после merge.
Оставлены две P3, обе — носители тикета 05: описание `init` в
`skills/README.md` не называет двух харнессов; «Факты окружения» runbook
хранят старые записи о DSH (`MISSING_CREDENTIAL`, «каталог не проверен»)
и получат «снято» тикетом 05. Повторного прогона нет.

**Приёмка:** тикет принят оператором 2026-11-09 (ask, вариант «принять»).
