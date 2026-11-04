# 02: релиз v0.5.0 и приёмка потребителя

**Спека:** [docs/plans/canon-section-in-bundles.md](../../docs/plans/canon-section-in-bundles.md)

**Что построить:** релиз v0.5.0 — bump версии плагина в
`.zcode-plugin/plugin.json`, тег на origin, перепин каталога маркета;
install по пину в чистый каталог — `method-phases.md` на месте; update
erp-demo раннером v0.4.0 → v0.5.0; проба путей по всем скиллам
установленного erp-demo — канон-упоминаний ноль, висящих ноль; запись
rollout в consumer-registry.

**Блокируется:** 01.

**Демо-путь:** update erp-demo раннером — `.zcode/deployed.json` с
пином v0.5.0, проба путей чистая, rollout в реестре с датой.

**Критерии приёмки**:

- [ ] bump и тег — артефакт: `.zcode-plugin/plugin.json` и `ls-remote`;
      ожидание: версия 0.5.0, тег `v0.5.0` на origin (спека, «Готово» 4)
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

## Доказательства

(дописываются при исполнении)
