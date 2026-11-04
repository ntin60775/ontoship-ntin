# 01: секция канона и перепись ссылок

**Спека:** [docs/plans/canon-section-in-bundles.md](../../docs/plans/canon-section-in-bundles.md)

**Что построить:** методную секцию «Три фазы» канона (строки 60–100)
как `skills/ship/references/method-phases.md` — стоять самостоятельно,
без фактов ntin-репо, держащую дословно якоря из перечня ниже;
переписать шесть носителей-упоминаний канона на файлы бандлов: шапки
`critic`, `grilling`, `ship`, `to-tickets` → кросс-ссылка
`../ship/references/method-phases.md`; шапка `testing` → свой
`references/quality-rule.md` (канон-часть предложения); тело
`to-tickets` в блоке «Порядок» («Нарезка не закончена без критика
(канон, „Три фазы“…)») → кросс-ссылка; guard-фраза на имя
`method-phases.md` в каждом ссылающемся скилле (перечень — критерий
guard); правки контрактных тестов `tests/test_skill_critic.py`,
`tests/test_skill_ship.py`, `tests/test_skill_testing.py` —
REQUIRED_PHRASES и `test_skill_anchors_to_the_canon` требуют бандл-ссылки
вместо канон-пути (находка P1 критика); якорные тесты: паритет
«канон ↔ секция» — набор method-phases в SETS `tests/test_canon_sync.py`,
проверка переписи и guard-набор — в `tests/test_bundle_references.py`.

**Якоря секции** (секция держит дословно, остальной текст вольна
переписывать; при несовместимости — точка остановки, решение
оператора):

1. «Факты — работа агента; решения — работа оператора.»
2. «Никаких якорей `file:line` — они гниют.»
3. «Переходы ручные, кроме grill → spec.»
4. «один прогон ревью (панель специалистов параллельно, один отчёт)»

**Блокируется:** нет.

**Демо-путь:** `scripts/install.sh` link и copy во временный проект —
`method-phases.md` на месте, проба ссылок по всем скиллам чистая
(канон-путей нет, бандл-файлы резолвятся).

**Критерии приёмки**:

- [ ] секция — артефакт: `skills/ship/references/method-phases.md`;
      ожидание: текст раздела «Три фазы» канона (60–100), переписанный
      стоять самостоятельно, без проектных фактов, с дословными якорями
      из перечня выше (спека, «Готово» 1)
- [ ] якорный паритет — артефакт: набор method-phases в SETS
      `tests/test_canon_sync.py` и его мутационные пробы; ожидание:
      формулировки-якоря в каноне и секции, удаление якоря в любом
      носителе краснит (спека, «Готово» 1)
- [ ] перепись — артефакт: `SKILL.md` пяти скиллов; ожидание: все
      шесть носителей ссылаются на файлы бандлов, включая блок
      «Порядок» to-tickets (спека, «Готово» 2)
- [ ] отсутствие канон-пути — артефакт: расширение OLD_CARRIERS в
      `tests/test_bundle_references.py` (греп `docs/decisions/…` по
      телам поставляемых скиллов) и проверка кросс-ссылки в блоке
      «Порядок» to-tickets; ожидание: обе проверки краснят на базовом
      коммите и зелёные после переписи, мутации названы (спека,
      «Готово» 2; находка P2-3 критика)
- [ ] контрактные тесты — артефакт: `tests/test_skill_critic.py`,
      `tests/test_skill_ship.py`, `tests/test_skill_testing.py`;
      ожидание: REQUIRED_PHRASES и `test_skill_anchors_to_the_canon`
      требуют бандл-ссылки (`../ship/references/method-phases.md`,
      `references/quality-rule.md`); на базовом коммите краснят
      (скиллы ещё несут канон-путь), после переписи — зелёные
      (находка P1 критика)
- [ ] guard — артефакт: guard-фразы в `critic`, `grilling`, `ship`,
      `to-tickets` (testing несёт guard на `quality-rule.md`) и
      guard-набор теста; ожидание: запрещённые формулировки и потеря
      фразы ловятся мутациями у всех четырёх (спека, «Готово» 3)
- [ ] тест ссылок — артефакт: тест установки обоими каналами;
      ожидание: link и copy ставят `method-phases.md`, ссылки скиллов
      резолвятся на диске (спека, «Готово» 2)
- [ ] полный набор — артефакт: `python3 -m pytest tests/ -q`; ожидание:
      набор зелёный, арифметика прироста названа в доказательствах;
      класс — инвариант-охранник зелени набора, не доказательство
      пункта «Готово» (находка P3 критика)

## Доказательства

Срез: worktree `ontoship-ntin-wt-csib01`, ветка `csib-01-method-phases` от
базового коммита `d2fa71d`. Тесты написаны первыми, носители переписаны
после красной пробы (test-first в одном worktree).

**Красная проба на базовом коммите** (тестовые правки внесены, носители ещё
на базе): прогон шести затронутых файлов — **21 failed / 112 passed**.
Состав: canon_sync — носитель method-phases отсутствует и 4 якорных случая
method-phases; bundle_references — новые точки без ссылок на диске, без
guard, канон-путь жив в пяти телах, кросс-ссылки в «Порядке» нет, предусловие
can-fail; контракты critic/ship — REQUIRED на бандл-ссылку и их can-fail
предусловия; testing и ship — якорные тесты; install — резолв ссылок
установки.

**Реализация.**

- `skills/ship/references/method-phases.md` — секция «Три фазы» канона
  (строки 60–100), переписана стоять самостоятельно (переносы строк выровнены
  под ширину 80, смысл и якоря без правок); четыре якоря дословно; путей
  репо (`docs/plans/`, `skills/`) нет; канон-пути нет (обратная ссылка —
  явный отказ спеки).
- Перепись шести упоминаний: шапки `critic`, `grilling`, `to-tickets` →
  `../ship/references/method-phases.md`; шапка `ship` → свой
  `references/method-phases.md` (секция «Три фазы» названа словами); шапка
  `testing` → канон-часть предложения снята, бандл-носитель
  `references/quality-rule.md` остался; тело `to-tickets` («Порядок», шаг 6)
  → кросс-ссылка `../ship/references/method-phases.md`.
- Guard-фраза («файл бандла — первоисточник, проект переопределяет его
  документом `docs/reference/method-phases.md` — написал свой, бери его»)
  внесена в шапки `critic`, `grilling`, `ship`, `to-tickets`; testing несёт
  прежний guard на `quality-rule.md`.

**Тесты.**

- `tests/test_canon_sync.py` — набор `method-phases` в SETS (канон ↔ секция),
  4 якоря; probe пары method-phases в `test_parity_mutations_can_fail`
  (нормализация стрелки компаратором).
- `tests/test_bundle_references.py` — POINTS расширены четырьмя шапками
  (critic, grilling, ship, to-tickets); `_skill_texts` читает все девять
  поставляемых тел; проверки `_canon_path_errors` (канон-путь вне тел) и
  `_crosslink_errors` (кросс-ссылка в блоке «Порядок») с тестами; мутации:
  потеря кросс-ссылки (все вхождения), утечка канон-пута в kb-search
  (fabricated tree), потеря guard-головы у каждого из четырёх скиллов
  (параметризованная проба).
- Контрактные тесты (P1 критика): `test_skill_critic.py` — REQUIRED
  `../ship/references/method-phases.md` вместо канон-пути, якорный тест с
  пробой перелинковки на канон; `test_skill_ship.py` — REQUIRED
  `references/method-phases.md`, `test_skill_anchors_to_the_canon` →
  `test_skill_anchors_to_the_bundle_section` (бандл-ссылка, «три фазы»,
  канон-пути нет); `test_skill_testing.py` — канон-путь снят с REQUIRED,
  якорный тест переименован аналогично (носитель quality-rule.md, канон-пути
  нет).
- `tests/test_skill_ship.py`, `tests/test_skill_to_tickets.py` —
  `_body_mutated` получил `count=-1` для no-guard пробы: guard-фраза теперь
  в двух блоках носителя, потеря обязана краснить при утрате любого.
- `tests/test_install.py` — `SECTION_REF` + резолв ссылок на
  method-phases.md/quality-rule.md в дереве установки (link и copy) с
  мутацией висящей ссылки в copy; `test_install_carries_bundle_references`
  подхватил method-phases.md автоматически (REFERENCES с диска).

**Разбор расхождений по ходу исполнения** (правило testing-бандла): первый
зелёный прогон дал 3 отказа — (1) regex `SECTION_REF`: класс `[a-z0-9-]+`
не съедает `/` после имени бандла, левый старт «../ship/»+«references/»
невозможен, матч садился на бесхвостый «references/…» — слэш перенесён внутрь
опциональной группы; (2–3) no-guard пробы ship и to-tickets заменяли только
первое вхождение guard-фразы (их стало два на носитель) — проба переведена
на все вхождения. Оба отказа — дефекты прибора, не носителей; финальный
счёт ниже.

**Зелёный счёт.** Полный набор в worktree: **446 passed = 433 + 13**
(+5 canon_sync: носитель в carrier-exists и 4 якорных случая;
+6 bundle_references: 2 проверки + 4 guard-пробы по скиллам; +1 якорный тест
critic; +1 тест резолва ссылок установки; переименования тестов счёт не
меняют). `gitmark.py index` — 92 файла, 229 ссылок; `lint --strict` — чисто.

**Демо-путь (вживую, temp-проект):** `scripts/install.sh` link и copy —
`method-phases.md` на месте в обоих деревьях; пробы ссылок: critic, grilling,
to-tickets → `../ship/references/method-phases.md` и testing →
`references/quality-rule.md` резолвятся; канон-путей в телах установленных
скиллов нет (grep `docs/decisions/` по обоим деревьям даёт 4 файла —
`ontology.md` × 2 и `gitmark.py` × 2: таксономия каталогов KB потребителя и
код движка, не ссылки на канон); кросс-ссылка в «Порядке» to-tickets на
месте.

**Панель:** id прогона дописывается после запуска.
