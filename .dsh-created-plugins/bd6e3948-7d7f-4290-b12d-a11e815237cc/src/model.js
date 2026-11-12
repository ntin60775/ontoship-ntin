/*
 * OntoShip chain board — pure model.
 *
 * Plain declarations: the build concatenates this file inside the client
 * factory closure, and the test harness imports it as a module. No imports,
 * no exports, no side effects. Everything here is a pure function of the
 * markdown text it is given; nothing is stored.
 */

/** Escape a string for literal use inside a RegExp. */
function escapeRe(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * The current unit of a continue.md runbook: the earliest open mention that
 * was never closed afterwards. The runbook convention puts the current state
 * at the top of «Где мы», so the earliest still-open mention is the current
 * unit; older chronicle entries follow below.
 * @param {string} text - full continue.md text.
 * @returns {string|null} unit slug, or null when no unit is open.
 */
function parseCurrentUnit(text) {
  const events = [];
  const collect = (re, kind) => {
    for (const m of text.matchAll(re)) {
      events.push({ slug: m[1].toLowerCase(), pos: m.index, kind });
    }
  };
  collect(/открыт[аы]?\s+(?:мини-)?юнит\s+`([a-z0-9][a-z0-9-]*)`/gi, 'open');
  collect(/(?:мини-)?юнит\s+`([a-z0-9][a-z0-9-]*)`\s+открыт/gi, 'open');
  collect(/юнит\s+`([a-z0-9][a-z0-9-]*)`\s+закрыт/gi, 'close');
  collect(/последний\s+закрытый\s*[—–-]\s*`([a-z0-9][a-z0-9-]*)`/gi, 'close');
  const lastOpen = new Map();
  const lastClose = new Map();
  for (const e of events) {
    const table = e.kind === 'open' ? lastOpen : lastClose;
    const prev = table.get(e.slug);
    if (prev === undefined || e.pos > prev) table.set(e.slug, e.pos);
  }
  let best = null;
  for (const [slug, openPos] of lastOpen) {
    const closePos = lastClose.get(slug);
    if (closePos !== undefined && closePos > openPos) continue;
    if (best === null || openPos < best.pos) best = { slug, pos: openPos };
  }
  return best === null ? null : best.slug;
}

/**
 * The unit's paragraph inside the «Порядок тикетов» section: from the line
 * that starts with `slug`: to the next unit paragraph or section heading.
 * @param {string} text - full continue.md text.
 * @param {string} slug - unit slug.
 * @returns {string} the paragraph, or '' when the section or unit is absent.
 */
function extractUnitParagraph(text, slug) {
  const section = text.search(/^##\s+Порядок тикетов\s*$/m);
  if (section < 0) return '';
  const rest = text.slice(section);
  const startRe = new RegExp('^`' + escapeRe(slug) + '`\\s*:', 'm');
  const start = startRe.exec(rest);
  if (start === null) return '';
  const bodyStart = start.index + start[0].length;
  const after = rest.slice(bodyStart);
  const end = /^`[a-z0-9][a-z0-9-]*`\s*:|^##\s/m.exec(after);
  return rest.slice(start.index, bodyStart + (end === null ? after.length : end.index));
}

/**
 * Ticket execution states recorded by the unit paragraph. Mentions are read
 * in chronicle order; a later mention overrides an earlier one. Acceptance
 * during slicing («принят со сверкой понимания», «принят в нарезке») is not
 * an execution state.
 * @param {string} paragraph - the unit paragraph from continue.md.
 * @returns {Map<number, 'accepted'|'done'|'active'>} states by ticket number.
 */
function parseTicketStates(paragraph) {
  const states = new Map();
  const mentionRe = /тикет[а-яё]{0,3}\s*(\d{1,3})(?:\s*[–—-]\s*(\d{1,3}))?/gi;
  const mentions = [...paragraph.matchAll(mentionRe)];
  for (let i = 0; i < mentions.length; i += 1) {
    const m = mentions[i];
    const from = parseInt(m[1], 10);
    const to = m[2] === undefined ? from : parseInt(m[2], 10);
    const windowStart = m.index + m[0].length;
    const windowEnd = i + 1 < mentions.length
      ? Math.min(mentions[i + 1].index, windowStart + 600)
      : Math.min(paragraph.length, windowStart + 600);
    const rawWindow = paragraph.slice(windowStart, windowEnd);
    // A state keyword belongs to this ticket only until another ticket
    // number appears: «блокер тикета 06 снят (04 принят ранее)» must not
    // give ticket 06 the acceptance of ticket 04. Standalone 1-2 digit
    // numbers are ticket references; parts of dates and versions are not
    // cut before the keyword in the canonical «сделан 2026-11-11» order.
    let cut = rawWindow.length;
    for (const numRef of rawWindow.matchAll(/\d{1,2}/g)) {
      const before = rawWindow[numRef.index - 1] || '';
      const after = rawWindow[numRef.index + numRef[0].length] || '';
      if (/[\d.]/.test(before) || /[\d.]/.test(after)) continue;
      cut = numRef.index;
      break;
    }
    const window = rawWindow.slice(0, cut);
    const slicing = /со\s+сверкой\s+понимания|в\s+нарезке/i.test(window);
    let state;
    if (!slicing && /принят(?:а|ы|о)?(?![а-яё])|принял(?![а-яё])/i.test(window)) state = 'accepted';
    else if (/сделан(?:а|ы|о)?(?![а-яё])|жд[её]т\s+при[её]мки/i.test(window)) state = 'done';
    else if (/в\s+работе(?![а-яё])|исполняется|исполняют/i.test(window)) state = 'active';
    if (state === undefined) continue;
    const lo = Math.min(from, to);
    const hi = Math.max(from, to);
    for (let num = lo; num <= hi; num += 1) states.set(num, state);
  }
  return states;
}

/**
 * Parse one ticket file. A ticket carries the «Блокируется» marker; report
 * artifacts in the same folder do not and are not tickets.
 * @param {string} text - file content.
 * @param {string} fileName - base name, e.g. 06-chain-orchestrator.md.
 * @returns {object|null} parsed ticket, or null when the file is not a ticket.
 */
function parseTicketFile(text, fileName) {
  const marker = /^\*\*Блокируется:\*\*/m.exec(text);
  if (marker === null) return null;
  const head = /^#\s+(\d{1,3})\s*[:.]\s*(.*)$/m.exec(text);
  const fileNum = /^(\d{1,3})-/.exec(fileName);
  const num = head !== null ? parseInt(head[1], 10) : fileNum !== null ? parseInt(fileNum[1], 10) : null;
  if (num === null) return null;
  const title = head !== null && head[2].trim() !== '' ? head[2].trim() : fileName;
  const rest = text.slice(marker.index + marker[0].length);
  const paragraph = rest.split(/\n[ \t]*\n/)[0];
  const blockers = new Set();
  if (!/ничем/i.test(paragraph)) {
    let matches = [...paragraph.matchAll(/тикет[а-яё]{0,3}\s*(\d{1,3})(?:\s*[–—-]\s*(\d{1,3}))?/gi)];
    if (matches.length === 0 && /\d/.test(paragraph)) {
      matches = [...paragraph.matchAll(/(\d{1,3})(?:\s*[–—-]\s*(\d{1,3}))?/g)];
    }
    for (const m of matches) {
      const from = parseInt(m[1], 10);
      const to = m[2] === undefined ? from : parseInt(m[2], 10);
      for (let n = Math.min(from, to); n <= Math.max(from, to); n += 1) {
        if (n !== num) blockers.add(n);
      }
    }
  }
  const criteriaDone = (text.match(/^-\s*\[x\]/gim) || []).length;
  const criteriaOpen = (text.match(/^-\s*\[\s\]/gim) || []).length;
  const criteriaTotal = criteriaDone + criteriaOpen;
  const fileDone = criteriaTotal > 0 && criteriaOpen === 0 && /^##\s+Доказательства/m.test(text);
  return {
    num,
    file: fileName,
    title,
    blockers: [...blockers].sort((a, b) => a - b),
    criteriaDone,
    criteriaTotal,
    fileDone,
  };
}

/**
 * Layer of every ticket: longest blocker chain above it (roots at 0).
 * Cycles cannot happen in a sliced unit; if one appears, the back edge
 * contributes 0 and the board is flagged instead of hanging.
 * @param {Array} tickets - parsed tickets with resolved columns.
 * @returns {{layers: Map<number, number>, cycle: boolean}}
 */
function computeLayers(tickets) {
  const byNum = new Map(tickets.map(t => [t.num, t]));
  const layers = new Map();
  const visiting = new Set();
  let cycle = false;
  const depth = (num) => {
    if (layers.has(num)) return layers.get(num);
    if (visiting.has(num)) { cycle = true; return 0; }
    visiting.add(num);
    const ticket = byNum.get(num);
    let d = 0;
    if (ticket !== undefined) {
      for (const b of ticket.blockers) {
        if (byNum.has(b)) d = Math.max(d, depth(b) + 1);
      }
    }
    visiting.delete(num);
    layers.set(num, d);
    return d;
  };
  for (const t of tickets) depth(t.num);
  return { layers, cycle };
}

/**
 * Build the whole board from parsed inputs. Columns: accepted and review
 * come from the resolved state, active from the runbook, blocked and ready
 * are computed from the edges (ready is the frontier).
 * @param {string} unit - unit slug.
 * @param {Array} parsed - parseTicketFile results.
 * @param {Map<number, string>} proseStates - states from continue.md.
 * @returns {object} board model.
 */
function buildBoard(unit, parsed, proseStates) {
  const tickets = parsed
    .filter(t => t !== null)
    .sort((a, b) => a.num - b.num)
    .map(t => {
      const prose = proseStates.get(t.num);
      const state = prose !== undefined ? prose : t.fileDone ? 'done' : null;
      return { ...t, state, stateSource: prose !== undefined ? 'continue' : t.fileDone ? 'file' : null };
    });
  const byNum = new Map(tickets.map(t => [t.num, t]));
  const resolved = t => t.state === 'accepted' || t.state === 'done';
  const columns = { blocked: [], ready: [], active: [], review: [], accepted: [] };
  const edges = [];
  const dangling = [];
  for (const t of tickets) {
    const unresolved = t.blockers.filter(b => {
      const blocker = byNum.get(b);
      return blocker === undefined || !resolved(blocker);
    });
    t.unresolvedBlockers = unresolved;
    for (const b of t.blockers) {
      if (byNum.has(b)) edges.push({ from: b, to: t.num });
      else dangling.push({ from: b, to: t.num });
    }
    if (t.state === 'accepted') t.column = 'accepted';
    else if (t.state === 'done') t.column = 'review';
    else if (t.state === 'active') t.column = 'active';
    else if (unresolved.length > 0) t.column = 'blocked';
    else t.column = 'ready';
    columns[t.column].push(t);
  }
  const { layers, cycle } = computeLayers(tickets);
  for (const t of tickets) t.layer = layers.get(t.num) || 0;
  const maxLayer = tickets.reduce((m, t) => Math.max(m, t.layer), 0);
  const layerGroups = [];
  for (let l = 0; l <= maxLayer; l += 1) {
    layerGroups.push(tickets.filter(t => t.layer === l).map(t => t.num));
  }
  return {
    unit,
    tickets,
    byNum,
    columns,
    edges,
    dangling,
    layerGroups,
    cycle,
    frontier: columns.ready.length,
  };
}

/**
 * Convenience pipeline: raw markdown inputs to a board, or a named absence.
 * @param {string|null} continueText - continue.md content, null when missing.
 * @param {Array<{name: string, text: string}>} files - unit folder files.
 * @returns {{kind: 'board', board: object}|{kind: 'noContinue'|'noUnit'|'noTickets', unit?: string}}
 */
function deriveBoard(continueText, files) {
  if (continueText === null || continueText === undefined) return { kind: 'noContinue' };
  const unit = parseCurrentUnit(continueText);
  if (unit === null) return { kind: 'noUnit' };
  const paragraph = extractUnitParagraph(continueText, unit);
  const proseStates = parseTicketStates(paragraph);
  const parsed = files.map(f => parseTicketFile(f.text, f.name));
  const board = buildBoard(unit, parsed, proseStates);
  if (board.tickets.length === 0) return { kind: 'noTickets', unit };
  return { kind: 'board', board };
}