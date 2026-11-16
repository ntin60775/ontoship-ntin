# DAG юнита team-profiles (ядро: закрытые тикеты)

Производный вид: граф зависимостей, вычисленный из блокирующих рёбер
тикетов `tickets/team-profiles/`. Источник истины — тикеты; файл
перегенерируется при смене статусов, отдельно не ведётся. Рёбра
показаны в транзитивной редукции (связи, задающие порядок исполнения);
полные блокеры каждого тикета — в его шапке и в Kanban. Цвета
статусов — лексика Temporal: Completed — зелёный, Running — синий,
Pending — серый, ожидание блокеров — янтарный.

Перенос 2026-11-17 (core-team-boundaries 05, триаж G22): открытые
тикеты 07/08 и спека переехали в ontoship-team; вид ядра
перегенерирован без 07/08 и несёт только закрытые тикеты. Полный граф
юнита и виды открытых тикетов — в team: носитель
`ontoship-team/tickets/team-profiles/` (dag.md, kanban.md).

```mermaid
flowchart TD
  T01["01 каркас team-бандла и architect"]
  T02["02 реестр и orchestrator/executor"]
  T03["03 выбор, маршруты и scout"]
  T04["04 OntoShip-носители и метод-контракт"]
  T05["05 стек 1C: ontoship-team-1c"]
  T06["06 релиз и поставка"]
  T09["09 личные имена агентов"]
  T10["10 таймер опроса — норма chain"]
  T11["11 разведка API-ведения сессий"]
  T12["12 гибридный READ-канал"]
  T13["13 tool-schedule у orchestrator"]
  T14["14 фильтр тривиальности"]

  T01 --> T02
  T02 --> T03
  T02 --> T05
  T02 --> T09
  T03 --> T04
  T04 --> T06
  T04 --> T10
  T05 --> T06
  T09 --> T06
  T10 --> T11
  T11 --> T12
  T12 --> T13

  classDef done fill:#d4edda,stroke:#28a745,color:#155724;
  classDef running fill:#cce5ff,stroke:#007bff,color:#004085;
  classDef pending fill:#e2e3e5,stroke:#6c757d,color:#383d41;
  classDef waiting fill:#fff3cd,stroke:#ffc107,color:#856404;

  class T01,T02,T03,T04,T05,T06,T09,T10,T11,T12,T13,T14 done;
```

Все тикеты вида закрыты автоприёмкой (2026-11-13/16). Ready-frontier
ядра пуст: открытая работа юнита (07, 08) — в team.

Обновлено: 2026-11-17, перенос 07/08 в team (core-team-boundaries 05).
