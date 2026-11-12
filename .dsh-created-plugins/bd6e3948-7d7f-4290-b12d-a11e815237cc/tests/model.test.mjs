/**
 * Model tests: pure parsing and board derivation.
 * Runs the real ontoship-ntin data when present, plus synthetic edge cases.
 * Usage: node tests/model.test.mjs
 */
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const pkgRoot = resolve(here, '..');
const modelSource = await readFile(join(pkgRoot, 'src/model.js'), 'utf8');
const model = await import(`data:text/javascript,${encodeURIComponent(
  `${modelSource}\nexport { parseCurrentUnit, extractUnitParagraph, parseTicketStates, parseTicketFile, computeLayers, buildBoard, deriveBoard };\n`,
)}`);
const { parseCurrentUnit, extractUnitParagraph, parseTicketStates, parseTicketFile, buildBoard, deriveBoard } = model;

let passed = 0;
const test = (name, fn) => {
  fn();
  passed += 1;
  console.log(`ok - ${name}`);
};

// --- parseCurrentUnit -------------------------------------------------------

test('current unit: earliest still-open mention wins (runbook convention)', () => {
  const text = [
    '# Продолжение',
    '**Открыт юнит `new-unit` (2026-11-11)**: работа.',
    'Открыт юнит `old-unit` (2026-11-01): история.',
    'Юнит `old-unit` закрыт: всё принято.',
  ].join('\n');
  assert.equal(parseCurrentUnit(text), 'new-unit');
});

test('current unit: open-after wording and mini-units', () => {
  const text = '**Юнит `alpha` открыт командой оператора 2026-11-04**.\n**Мини-юнит `beta` открыт решением оператора 2026-11-01**.';
  assert.equal(parseCurrentUnit(text), 'alpha');
});

test('current unit: closed unit is not current', () => {
  const text = 'Открыт юнит `alpha` (2026-11-01).\n**юнит `alpha` закрыт: оба тикета приняты.**';
  assert.equal(parseCurrentUnit(text), null);
});

test('current unit: reopened after close counts', () => {
  const text = 'Открыт юнит `alpha`.\nюнит `alpha` закрыт.\nОткрыт юнит `alpha` снова.';
  assert.equal(parseCurrentUnit(text), 'alpha');
});

test('current unit: no mentions -> null', () => {
  assert.equal(parseCurrentUnit('На открытых юнитов нет; завершённые — в индексе.'), null);
});

test('current unit: last-closed summary line closes a unit', () => {
  const text = 'Открыт юнит `alpha`.\nПоследний закрытый — `alpha` (2026-11-11, ниже).';
  assert.equal(parseCurrentUnit(text), null);
});

// --- extractUnitParagraph ---------------------------------------------------

test('unit paragraph: bounded by next unit and section heading', () => {
  const text = [
    '## Порядок тикетов',
    '',
    '`alpha`: **01 старт → 02 финиш.** Тикет 01 сделан.',
    '`beta`: **01 иное.** Тикет 01 принят.',
    '',
    '## Факты окружения',
    'что-то',
  ].join('\n');
  const para = extractUnitParagraph(text, 'alpha');
  assert.ok(para.startsWith('`alpha`:'));
  assert.ok(para.includes('Тикет 01 сделан.'));
  assert.ok(!para.includes('`beta`'));
  assert.ok(!para.includes('Факты окружения'));
});

test('unit paragraph: absent section -> empty', () => {
  assert.equal(extractUnitParagraph('## Где мы\nОткрыт юнит `alpha`.', 'alpha'), '');
});

// --- parseTicketStates ------------------------------------------------------

test('states: сделан -> done, принят -> accepted, later overrides', () => {
  const para = '`u`: **Тикет 01 «а» сделан 2026-11-11** (срез). **Тикет 01 принят оператором 2026-11-12**.';
  const states = parseTicketStates(para);
  assert.equal(states.get(1), 'accepted');
});

test('states: ждёт приёмки -> done', () => {
  const states = parseTicketStates('`u`: **Тикет 02 сделан, влит и ждёт приёмки**.');
  assert.equal(states.get(2), 'done');
});

test('states: в работе -> active', () => {
  const states = parseTicketStates('`u`: тикет 03 в работе у сессии.');
  assert.equal(states.get(3), 'active');
});

test('states: slicing acceptance is not execution', () => {
  const states = parseTicketStates('`u`: тикет 01 принят со сверкой понимания; тикет 02 принят в нарезке того же прогона.');
  assert.equal(states.size, 0);
});

test('states: range mention applies to every number', () => {
  const states = parseTicketStates('`u`: Тикеты 01–04 сделаны, влиты и приняты 2026-11-11.');
  for (const n of [1, 2, 3, 4]) assert.equal(states.get(n), 'accepted');
});

test('states: blocker mention without keywords changes nothing', () => {
  const states = parseTicketStates('`u`: блокер тикетов 05 и 06 снят, очередь дальше.');
  assert.equal(states.size, 0);
});

test('states: foreign ticket state inside an aside does not leak', () => {
  const states = parseTicketStates('`u`: Блокер тикета 06 снят (04 принят ранее); свободен тикет 06 — по команде оператора.');
  assert.equal(states.size, 0);
});

// --- parseTicketFile --------------------------------------------------------

const TICKET = [
  '# 06: Цепочка-оркестратор',
  '',
  '**Спека:** [u](../../docs/plans/u.md).',
  '',
  '**Блокируется:** тикет 04 (гейт), тикет 05 (исполнитель).',
  '',
  '**Что построить:** что-то.',
  '',
  '**Критерии приёмки**:',
  '',
  '- [x] Первый критерий.',
  '- [ ] Второй критерий.',
].join('\n');

test('ticket file: number, title, blockers', () => {
  const t = parseTicketFile(TICKET, '06-chain.md');
  assert.equal(t.num, 6);
  assert.equal(t.title, 'Цепочка-оркестратор');
  assert.deepEqual(t.blockers, [4, 5]);
  assert.equal(t.criteriaDone, 1);
  assert.equal(t.criteriaTotal, 2);
  assert.equal(t.fileDone, false);
});

test('ticket file: report artifact without marker is not a ticket', () => {
  assert.equal(parseTicketFile('# Отчёт триажа\n\nтекст', '04-projection-report.md'), null);
});

test('ticket file: ничем -> no blockers', () => {
  const t = parseTicketFile('# 01: Старт\n\n**Блокируется:** ничем.\n', '01-start.md');
  assert.deepEqual(t.blockers, []);
});

test('ticket file: range blockers and multiline paragraph', () => {
  const t = parseTicketFile('# 08: Финал\n\n**Блокируется:** тикеты 01–07.\n\nдалее', '08-live.md');
  assert.deepEqual(t.blockers, [1, 2, 3, 4, 5, 6, 7]);
  const multi = parseTicketFile('# 05: Исполнитель\n\n**Блокируется:** тикет 02 (роли паков в реестре), тикет 04 (пул\nвалидации и гейт проекций).\n\nдалее', '05-x.md');
  assert.deepEqual(multi.blockers, [2, 4]);
});

test('ticket file: fileDone needs all criteria and evidence', () => {
  const done = parseTicketFile(`${TICKET.replace('- [ ] Второй', '- [x] Второй')}\n\n## Доказательства\n\nфакты\n`, '06-chain.md');
  assert.equal(done.fileDone, true);
  const noEvidence = parseTicketFile(TICKET.replace('- [ ] Второй', '- [x] Второй'), '06-chain.md');
  assert.equal(noEvidence.fileDone, false);
});

// --- buildBoard / deriveBoard -----------------------------------------------

const files = [
  { name: '01-a.md', text: '# 01: А\n\n**Блокируется:** ничем.\n' },
  { name: '02-b.md', text: '# 02: Б\n\n**Блокируется:** тикет 01.\n' },
  { name: '03-c.md', text: '# 03: В\n\n**Блокируется:** тикет 01.\n' },
  { name: '04-d.md', text: '# 04: Г\n\n**Блокируется:** тикеты 02, 03.\n' },
];

test('board: blocked and ready computed from edges', () => {
  const board = buildBoard('u', files.map(f => parseTicketFile(f.text, f.name)), new Map());
  assert.deepEqual(board.columns.ready.map(t => t.num), [1]);
  assert.deepEqual(board.columns.blocked.map(t => t.num), [2, 3, 4]);
  assert.equal(board.frontier, 1);
});

test('board: done blocker unblocks dependents', () => {
  const board = buildBoard('u', files.map(f => parseTicketFile(f.text, f.name)), new Map([[1, 'done']]));
  assert.deepEqual(board.columns.review.map(t => t.num), [1]);
  assert.deepEqual(board.columns.ready.map(t => t.num), [2, 3]);
  assert.deepEqual(board.columns.blocked.map(t => t.num), [4]);
});

test('board: accepted and active columns from prose', () => {
  const states = new Map([[1, 'accepted'], [2, 'active']]);
  const board = buildBoard('u', files.map(f => parseTicketFile(f.text, f.name)), states);
  assert.deepEqual(board.columns.accepted.map(t => t.num), [1]);
  assert.deepEqual(board.columns.active.map(t => t.num), [2]);
  assert.deepEqual(board.columns.ready.map(t => t.num), [3]);
});

test('board: fileDone fallback when prose is silent', () => {
  const doneFile = { name: '01-a.md', text: '# 01: А\n\n**Блокируется:** ничем.\n\n- [x] критерий\n\n## Доказательства\n\nфакт\n' };
  const board = buildBoard('u', [parseTicketFile(doneFile.text, doneFile.name), parseTicketFile(files[1].text, files[1].name)], new Map());
  assert.equal(board.byNum.get(1).state, 'done');
  assert.equal(board.byNum.get(1).stateSource, 'file');
  assert.deepEqual(board.columns.ready.map(t => t.num), [2]);
});

test('board: layers follow longest blocker chain', () => {
  const board = buildBoard('u', files.map(f => parseTicketFile(f.text, f.name)), new Map());
  assert.equal(board.byNum.get(1).layer, 0);
  assert.equal(board.byNum.get(2).layer, 1);
  assert.equal(board.byNum.get(4).layer, 2);
  assert.deepEqual(board.layerGroups, [[1], [2, 3], [4]]);
});

test('board: dangling blocker keeps ticket blocked and is reported', () => {
  const orphan = { name: '02-b.md', text: '# 02: Б\n\n**Блокируется:** тикет 09.\n' };
  const board = buildBoard('u', [parseTicketFile(files[0].text, files[0].name), parseTicketFile(orphan.text, orphan.name)], new Map());
  assert.deepEqual(board.columns.blocked.map(t => t.num), [2]);
  assert.deepEqual(board.dangling, [{ from: 9, to: 2 }]);
});

test('board: cycle does not hang and is flagged', () => {
  const a = parseTicketFile('# 01: А\n\n**Блокируется:** тикет 02.\n', '01-a.md');
  const b = parseTicketFile('# 02: Б\n\n**Блокируется:** тикет 01.\n', '02-b.md');
  const board = buildBoard('u', [a, b], new Map());
  assert.equal(board.cycle, true);
  assert.equal(board.tickets.length, 2);
});

test('deriveBoard: named absences', () => {
  assert.equal(deriveBoard(null, []).kind, 'noContinue');
  assert.equal(deriveBoard('нет юнитов', []).kind, 'noUnit');
  assert.equal(deriveBoard('Открыт юнит `u`.', []).kind, 'noTickets');
});

test('deriveBoard: prose states scoped to the unit paragraph', () => {
  const text = [
    'Открыт юнит `u`.',
    '## Порядок тикетов',
    '`other`: Тикет 01 принят оператором.',
    '`u`: **01 старт.** Тикет 01 сделан.',
  ].join('\n');
  const derived = deriveBoard(text, [files[0]]);
  assert.equal(derived.kind, 'board');
  assert.equal(derived.board.byNum.get(1).state, 'done');
});

// --- real repository data ----------------------------------------------------

const repoRoot = resolve(pkgRoot, '../..');
let realContinue = null;
let realFiles = null;
try {
  realContinue = await readFile(join(repoRoot, 'docs/ops/continue.md'), 'utf8');
  const dir = join(repoRoot, 'tickets/standards-autoship');
  const names = (await readdir(dir)).filter(n => n.endsWith('.md'));
  realFiles = [];
  for (const name of names) {
    realFiles.push({ name, text: await readFile(join(dir, name), 'utf8') });
  }
} catch {
  console.log('skip - real ontoship-ntin data not present');
}

if (realContinue !== null && realFiles !== null) {
  test('real data: current unit is standards-autoship', () => {
    assert.equal(parseCurrentUnit(realContinue), 'standards-autoship');
  });

  test('real data: eight tickets, report artifacts excluded', () => {
    const derived = deriveBoard(realContinue, realFiles);
    assert.equal(derived.kind, 'board');
    const board = derived.board;
    assert.deepEqual(board.tickets.map(t => t.num), [1, 2, 3, 4, 5, 6, 7, 8]);
    assert.ok(!board.tickets.some(t => t.file.includes('report')));
  });

  test('real data: 01-05 accepted, 06 ready frontier, 07-08 blocked', () => {
    const { board } = deriveBoard(realContinue, realFiles);
    assert.deepEqual(board.columns.accepted.map(t => t.num), [1, 2, 3, 4, 5]);
    assert.deepEqual(board.columns.ready.map(t => t.num), [6]);
    assert.deepEqual(board.columns.blocked.map(t => t.num), [7, 8]);
    assert.equal(board.frontier, 1);
  });

  test('real data: edges match the sliced blockers', () => {
    const { board } = deriveBoard(realContinue, realFiles);
    const key = e => `${e.from}->${e.to}`;
    const edges = new Set(board.edges.map(key));
    for (const expected of ['1->2', '1->3', '2->5', '4->5', '4->6', '5->6', '4->7', '5->7', '6->7', '1->8', '2->8', '3->8', '4->8', '5->8', '6->8', '7->8']) {
      assert.ok(edges.has(expected), `missing edge ${expected}`);
    }
    assert.equal(board.edges.length, 16);
    assert.equal(board.dangling.length, 0);
  });

  test('real data: layers and criteria progress', () => {
    const { board } = deriveBoard(realContinue, realFiles);
    assert.deepEqual(board.layerGroups, [[1, 4], [2, 3], [5], [6], [7], [8]]);
    const t1 = board.byNum.get(1);
    assert.equal(t1.criteriaDone, t1.criteriaTotal);
    assert.ok(t1.criteriaTotal > 0);
    const t6 = board.byNum.get(6);
    assert.equal(t6.criteriaDone, 0);
    assert.ok(t6.criteriaTotal > 0);
  });
}

console.log(`\n${passed} tests passed`);