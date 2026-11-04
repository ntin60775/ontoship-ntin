# 02: релиз v0.5.0 и приёмка потребителя

**Спека:** [docs/plans/canon-section-in-bundles.md](../../docs/plans/canon-section-in-bundles.md)

**Что построить:** после merge тикетов юнита в main — релиз v0.5.0:
bump версии плагина в `.zcode-plugin/plugin.json`, тег на
merge-коммите main, перепин каталога маркета; install по пину в
чистый каталог — `method-phases.md` на месте; update erp-demo раннером
v0.4.0 → v0.5.0; проба путей по всем скиллам установленного erp-demo —
канон-упоминаний ноль, висящих ноль; запись rollout в
consumer-registry; закрытие юнита — правки continue.md (п. 7 «Что
осталось») и строки юнита в docs/plans/README.md (прецедент — тикет
03 bundle-references).

**Блокируется:** 01.

**Демо-путь:** update erp-demo раннером — `.zcode/deployed.json` с
пином v0.5.0, проба путей чистая, rollout в реестре с датой.

**Критерии приёмки**:

- [ ] bump и тег — артефакт: `.zcode-plugin/plugin.json` и `ls-remote`;
      ожидание: версия 0.5.0, тег `v0.5.0` на origin указывает на
      merge-коммит main (спека, «Готово» 4; находка P3 критика)
- [ ] пин каталога — артефакт: `marketplace.json` маркета и `validate`;
      ожидание: пин ↔ version v0.5.0 согласована (спека, «Готово» 4)
- [ ] install по пину — артефакт: чистый temp-каталог;
      ожидание: гейт пин↔version пройден, `method-phases.md` в бандле
      ship установлен (спека, «Готово» 4)
- [ ] update erp-demo — артефакт: `.zcode/deployed.json` erp-demo;
      ожидание: пин v0.5.0, `method-phases.md` в
      `.agents/skills/ship/references/` (спека, «Готово» 5)
- [ ] проба путей — артефакт: вывод пробы по erp-demo; ожидание:
      канон-упоминаний ноль, висящих императивных ссылок ноль
      (спека, «Готово» 5)
- [ ] реестр потребителей — артефакт: запись consumer-registry;
      ожидание: rollout `v0.4.0 → v0.5.0` в erp-demo назван с датой
      (спека, «Готово» 5)
- [ ] закрытие юнита — артефакт: `docs/ops/continue.md` (п. 7 «Что
      осталось») и `docs/plans/README.md`; ожидание: п. 7 закрыт
      записью о юните `canon-section-in-bundles`, строка юнита в
      индексе планов — завершённый статус (спека, «Цель»; находка
      P2-2 критика)

## Доказательства

- **Срез** — worktree `ontoship-ntin-wt-csib02` от `e99fe76`:
  bump версии `.zcode-plugin/plugin.json` 0.4.0 → 0.5.0; закрытие
  п. 7 «Что осталось» в `docs/ops/continue.md`; строка юнита в
  `docs/plans/README.md`. Значение версии плагина тесты не пинят —
  красная проба на срез не заводится (прецедент тикета 03
  bundle-references); гейт пин↔version докажет живая установка по
  пину — артефакт дописывается после merge.
- **Релизные артефакты** (merge, тег `v0.5.0`, пин каталога, чистая
  установка, update erp-demo, проба путей, rollout в реестре) —
  дописываются после merge.
