# Формат файлов сессии (живой сэмпл)

Сэмпл снят 2026-11-15 в 02:43 до удаления пробной сессии
`session-60f6f2cc-1bd9-405e-b31b-cfd8975158aa` (cwd `/tmp/tp11-probe`).
Каталог после удаления сессии пуст, сам project-каталог удалён вручную.

```text
$ ls -la ~/.dsh/sessions/--tmp-tp11-probe--/session-60f6f2cc-1bd9-405e-b31b-cfd8975158aa/
итого 40
-rw-rw-r-- 1 prog7 prog7     0 ноя 15 02:42 session.lock
-rw------- 1 prog7 prog7 26949 ноя 15 02:43 session.v4.jsonl.zstd

$ zstd -dc …/session.v4.jsonl.zstd | head -3
{"type":"session","version":4,"id":"session-60f6f2cc-1bd9-405e-b31b-cfd8975158aa","createdAt":1794703331343,"cwd":"/tmp/tp11-probe","isSeeded":false,"delegationDepth":0,"agentPreset":"executor"}
{"type":"permission/preset","seq":0,"time":1794703331372,"data":{"preset":"danger-full-access"}}
{"type":"sandbox/mode","seq":1,"time":1794703331373,"data":{"mode":"danger-full-access"}}

$ zstd -dc …/session.v4.jsonl.zstd | tail -2
{"type":"step/end","seq":68,"time":1794703384855,"data":{"turn":4,"step":4}}
{"type":"turn/end","seq":69,"time":1794703384857,"data":{"turn":4,"reason":{"kind":"completed"}}}
```

Факты:

- файл — zstd-сжатый JSONL; первая строка — заголовок сессии с
  `delegationDepth` и `agentPreset`, дальше по событию на строку
  (`seq` монотонен; тот же `seq` отдаёт `session/events`);
- заголовок подтверждает глубину API-сессии: `delegationDepth: 0`
  (отсюда доступность `schedule_create`, см. `source-facts.md`);
- файл дописывается по ходу сессии (на момент снятия — 26 949 байт,
  последний `seq` 69);
- `session.lock` — файл блокировки writer-а;
- путь и имя — `projectKey`/`sessionDir` из
  `packages/session/session-persistence-jsonl/src/format.ts:215–290`;
  сырой формат пригоден для forensic-чтения через `zstd -dc`, но для
  ведения сессии оркестратору нужен API (`session/wait`/`session/events`),
  потому что файл — сжатый и не даёт событийной подписки.
- после `session/delete` каталог сессии исчезает (проверено
  `05-cleanup-storage.txt`); пустой project-каталог остаётся и снимается
  вручную.
