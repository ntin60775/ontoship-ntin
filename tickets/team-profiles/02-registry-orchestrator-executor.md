# 02: Реестр исполнителей и пресеты orchestrator/executor

**Спека:** [team-profiles](../../docs/plans/team-profiles.md), «Готово» 1, 2.

**Блокируется:** 01

**Что построить:** хост-плагин `ontoship-executors` в team-бандле, строка
ДО деклараций пресетов; путь через `ctx.get('profileContext').dir`;
читает `<profile>/ontoship/executors.json` один раз при apply; схема —
массив `{id, provider, model, level}`, запись `executor` обязательна;
отдаёт синхронный `executors()` (массив id) для `!!js`-allowlist;
валидирует и дедуплицирует, при ошибке/пустом/без `executor` — громкий
лог и дефолт `["executor"]`. Пресеты `orchestrator` (read-only fs,
subagent, send_message, ask) и `executor` (рабочие инструменты, без ask);
spawn-инструмент оркестратора с `agentPreset: executor` и
`allowedAgentPresets` через `!!js`, `modelSelection: true`.

**Демо-путь:** `executors.json` с двумя id → новая сессия оркестратора,
enum `agent_preset` показывает оба; битый файл → дефолт `["executor"]`;
спавн исполнителя.

**Критерии приёмки:**

- [ ] Плагин реестра — артефакт: вывод контрактных тестов
      (profileContext.dir, чтение один раз, схема, валидация/дедуп,
      дефолт при ошибке/пустом/без executor); ожидание: «Готово» 2;
      на базе плагина нет.
- [ ] Allowlist — артефакт: тесты `[]`, дубли, без `executor`,
      неизвестный id; ожидание: enum из реестра, неизвестный id — отказ
      при вызове, `agentPreset: executor`; на базе нет.
- [ ] Композиция orchestrator/executor — артефакт: вывод контрактного
      теста (orchestrator: read-only fs + subagent + send_message + ask;
      executor: рабочие инструменты, без ask); ожидание: «Готово» 1, 8;
      на базе пресетов нет.
- [ ] Live — артефакт: id сессии оркестратора, enum с двумя id,
      спавн ребёнка-исполнителя; ожидание: спавн работает; на базе нет.