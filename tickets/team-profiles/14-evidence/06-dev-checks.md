# 14 — dev-проверки (полный контур)

База: `d4194cb`; worktree `ontoship-ntin-wt-tp14`. Время: 2026-11-16.

| проверка | команда | результат | лог |
|---|---|---|---|
| красная проба на базе | три тест-файла среза на `/tmp/tp14-base3` (detached `d4194cb`) | **13 новых проверок красные**: 5 новых тестов + 8 новых якорных случаев `method-phases`; 23 старых якоря зелены | `01-red-on-base.log` |
| целевые контракты | `pytest tests/test_canon_sync.py tests/test_skill_grilling.py tests/test_skill_chain.py` | **136 passed** | `02-target-tests.log` |
| полный набор | `pytest -q` | **789 passed** (база 776 + 13) | `03-full-pytest.log` |
| KB lint | `python3 skills/kb-search/gitmark.py lint --strict` | чисто, код 0 (60 файлов) | `04-lint.log` |
| install | `scripts/install.sh --copy /tmp/tp14-install` + `--check` | `ok`/`check: ok`, код 0 | `05-install-check.log` |
| носители | grep/walk фактов | канон/зеркало/grilling/chain; harnesses принципа не несёт; methodContract 2 без bump | `05-carriers-check.md` |

Красная проба: 5 новых тестов (`test_triviality_override_in_canon_and_mirror`
×2, `test_triviality_override_can_fail`, `test_triviality_filter_contract`,
`test_brief_predecides_trivialities`) и 8 новых якорных случаев
`test_anchor_in_every_carrier[method-phases:…]` на базе падают; старые 23
якоря method-набора на базе зелены (они не про фильтр). Отбор:
`-k "triviality or brief_predecides"` и
`-k "test_anchor_in_every_carrier and method-phases"`.

## Разбор расхождений ожидание/факт

- **Красная проба, ожидание/факт.** Первый прогон дал 5 failed при
  ожидании «все новые проверки красные». Расхождение разобрано: восемь
  новых якорных случаев входят в параметризованный
  `test_anchor_in_every_carrier` и не попадали под `-k` первого прогона;
  прогон расширен, факт — 13 новых проверок красные (5 + 8), старые
  зелены. Логи — `01-red-on-base.log`. Иных расхождений ожидание/факт в
  dev-контуре не было.
- **Независимый прогон панели.** `reviewer-code` прогнал три тест-файла
  среза на базе целиком и получил 35 failed: кроме 13 новых проверок,
  общий `_contract_errors` краснит и старые тесты, которым нужны новые
  фразы. Оба факта верны при своих отборах: красная проба среза
  ограничена новыми проверками, полный прогон на базе не заявлялся
  зелёным.
