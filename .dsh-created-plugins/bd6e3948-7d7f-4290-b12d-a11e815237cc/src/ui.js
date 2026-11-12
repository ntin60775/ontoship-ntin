/*
 * OntoShip chain board — Client UI and data source.
 *
 * Plain declarations concatenated inside the client factory closure after
 * the model. React and the createElement alias come from the closure. The
 * board reads the session workspace through the existing workspaceFiles
 * Remote namespace and stores nothing: every snapshot is derived from the
 * markdown it just read.
 */

const { Fragment, useEffect, useMemo, useState, useSyncExternalStore } = React;

/** Board status -> Temporal badge color scheme (see docs/DETAIL.md). */
const STATUS_SCHEME = {
  blocked: 'neutral',
  ready: 'accent',
  active: 'info',
  review: 'warning',
  accepted: 'success',
};
const COLUMN_ORDER = ['blocked', 'ready', 'active', 'review', 'accepted'];

/**
 * Temporal UI badge palette (temporalio/ui, light and dark themes): colored
 * text, tinted surface, alpha border. Containers and plain text use host
 * theme tokens; only status accents carry these literals.
 */
const BOARD_CSS = `
.osb-root {
  --osb-info-text: #0d74ce; --osb-info-border: rgba(0, 144, 255, 0.6); --osb-info-surface: #d5efff;
  --osb-success-text: #218358; --osb-success-border: rgba(48, 164, 108, 0.6); --osb-success-surface: #d6f1df;
  --osb-warning-text: #ab6400; --osb-warning-border: rgba(255, 197, 61, 0.6); --osb-warning-surface: #ffee9c;
  --osb-neutral-text: #544e4c; --osb-neutral-border: rgba(195, 194, 187, 0.6); --osb-neutral-surface: #f0efec;
  --osb-accent-text: #402060; --osb-accent-border: rgba(142, 78, 198, 0.8); --osb-accent-surface: #ead5f9;
  display: flex; flex-direction: column; height: 100%; min-height: 0;
  color: var(--dsw-alias-label-primary); font-size: 13px;
}
body[data-ds-dark-theme] .osb-root {
  --osb-info-text: #8ec8f6; --osb-info-border: rgba(0, 144, 255, 0.7); --osb-info-surface: #113264;
  --osb-success-text: #8eceaa; --osb-success-border: rgba(48, 164, 108, 0.7); --osb-success-surface: #193b2d;
  --osb-warning-text: #e9c162; --osb-warning-border: rgba(255, 197, 61, 0.7); --osb-warning-surface: #4f3422;
  --osb-neutral-text: #c3c2bb; --osb-neutral-border: rgba(195, 194, 187, 0.7); --osb-neutral-surface: #2a2a2a;
  --osb-accent-text: #be93e4; --osb-accent-border: rgba(142, 78, 198, 0.8); --osb-accent-surface: #402060;
}
.osb-header { padding: 10px 12px 8px; border-bottom: 1px solid var(--dsw-alias-border-l1); flex: none; }
.osb-unitrow { display: flex; align-items: baseline; gap: 8px; min-width: 0; }
.osb-unitlabel { color: var(--dsw-alias-label-tertiary); font-size: 11px; flex: none; }
.osb-unit { font-weight: 600; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.osb-summary { color: var(--dsw-alias-label-secondary); font-size: 11px; margin-top: 2px; }
.osb-derived { color: var(--dsw-alias-label-tertiary); font-size: 10px; margin-top: 2px; }
.osb-toggle { display: flex; gap: 4px; margin-top: 8px; }
.osb-toggle button {
  border: 1px solid var(--dsw-alias-border-l2); background: transparent; color: var(--dsw-alias-label-secondary);
  border-radius: 6px; padding: 3px 10px; font-size: 12px; cursor: pointer;
}
.osb-toggle button:hover { background: var(--dsw-alias-interactive-bg-hover); }
.osb-toggle button[aria-pressed="true"] {
  background: var(--dsw-alias-interactive-bg-active); color: var(--dsw-alias-label-primary);
  border-color: var(--dsw-alias-border-selected);
}
.osb-content { flex: 1; min-height: 0; overflow: auto; padding: 10px 12px; }
.osb-message { color: var(--dsw-alias-label-secondary); padding: 16px 4px; line-height: 1.5; }
.osb-retry {
  margin-top: 10px; border: 1px solid var(--dsw-alias-border-l2); background: transparent;
  color: var(--dsw-alias-label-primary); border-radius: 6px; padding: 4px 12px; font-size: 12px; cursor: pointer;
}
.osb-retry:hover { background: var(--dsw-alias-interactive-bg-hover); }
.osb-graphwrap { overflow: auto; max-width: 100%; }
.osb-node { cursor: pointer; }
.osb-node:focus { outline: none; }
.osb-node:focus rect, .osb-node:hover rect { stroke-width: 2; }
.osb-node-num { font-weight: 700; font-size: 12px; }
.osb-node-title { font-size: 10px; }
.osb-edge { fill: none; stroke: var(--dsw-alias-border-l3); stroke-width: 1.5; }
.osb-note { color: var(--dsw-alias-label-tertiary); font-size: 11px; margin-top: 8px; line-height: 1.4; }
.osb-columns { display: flex; flex-direction: column; gap: 12px; }
.osb-column { border: 1px solid var(--dsw-alias-border-l1); border-radius: 8px; background: var(--dsw-alias-bg-layer-1); }
.osb-colhead { display: flex; align-items: center; gap: 6px; padding: 6px 10px; border-bottom: 1px solid var(--dsw-alias-border-l1); }
.osb-colname { font-size: 12px; font-weight: 600; }
.osb-colcount { color: var(--dsw-alias-label-tertiary); font-size: 11px; margin-left: auto; }
.osb-cards { display: flex; flex-direction: column; gap: 6px; padding: 8px; }
.osb-empty-col { color: var(--dsw-alias-label-tertiary); font-size: 11px; padding: 2px 4px; }
.osb-card {
  display: block; width: 100%; text-align: left; border: 1px solid var(--dsw-alias-border-l1);
  border-left-width: 3px; border-radius: 6px; background: var(--dsw-alias-card-fill);
  padding: 6px 8px; cursor: pointer; color: var(--dsw-alias-label-primary); font-size: 12px;
}
.osb-card:hover { background: var(--dsw-alias-card-fill-hover); }
.osb-card-top { display: flex; align-items: baseline; gap: 6px; min-width: 0; }
.osb-card-num { font-weight: 700; flex: none; }
.osb-card-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.osb-card-meta { color: var(--dsw-alias-label-tertiary); font-size: 10px; margin-top: 3px; }
.osb-dot { width: 8px; height: 8px; border-radius: 50%; flex: none; display: inline-block; }
.osb-badge {
  display: inline-flex; align-items: center; border: 1px solid; border-radius: 4px;
  padding: 1px 6px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em;
}
.osb-legend { flex: none; border-top: 1px solid var(--dsw-alias-border-l1); padding: 8px 12px; }
.osb-legend-title { color: var(--dsw-alias-label-tertiary); font-size: 10px; margin-bottom: 5px; }
.osb-legend-row { display: flex; flex-wrap: wrap; gap: 4px 10px; }
.osb-legend-item { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: var(--dsw-alias-label-secondary); }
.osb-scheme-info { color: var(--osb-info-text); }
.osb-scheme-success { color: var(--osb-success-text); }
.osb-scheme-warning { color: var(--osb-warning-text); }
.osb-scheme-neutral { color: var(--osb-neutral-text); }
.osb-scheme-accent { color: var(--osb-accent-text); }
.osb-badge.osb-scheme-info { background: var(--osb-info-surface); border-color: var(--osb-info-border); }
.osb-badge.osb-scheme-success { background: var(--osb-success-surface); border-color: var(--osb-success-border); }
.osb-badge.osb-scheme-warning { background: var(--osb-warning-surface); border-color: var(--osb-warning-border); }
.osb-badge.osb-scheme-neutral { background: var(--osb-neutral-surface); border-color: var(--osb-neutral-border); }
.osb-badge.osb-scheme-accent { background: var(--osb-accent-surface); border-color: var(--osb-accent-border); }
.osb-dot.osb-scheme-info { background: var(--osb-info-text); }
.osb-dot.osb-scheme-success { background: var(--osb-success-text); }
.osb-dot.osb-scheme-warning { background: var(--osb-warning-text); }
.osb-dot.osb-scheme-neutral { background: var(--osb-neutral-text); }
.osb-dot.osb-scheme-accent { background: var(--osb-accent-text); }
.osb-card.osb-scheme-info { border-left-color: var(--osb-info-text); }
.osb-card.osb-scheme-success { border-left-color: var(--osb-success-text); }
.osb-card.osb-scheme-warning { border-left-color: var(--osb-warning-text); }
.osb-card.osb-scheme-neutral { border-left-color: var(--osb-neutral-text); }
.osb-card.osb-scheme-accent { border-left-color: var(--osb-accent-text); }
.osb-titleicon { flex: none; }
`;

/** Small DAG glyph for the tab chip and the guide entry. */
function BoardIcon(props) {
  const size = (props && props.size) || 16;
  return h('svg', {
    viewBox: '0 0 16 16', width: size, height: size, className: 'osb-titleicon',
    'aria-hidden': true, style: { display: 'inline-block', verticalAlign: '-2px' },
  },
    h('path', { d: 'M4 5 L11 3 M4 5 L11 8 M4 11 L11 8 M4 11 L11 13', stroke: 'currentColor', strokeWidth: 1.2, fill: 'none', opacity: 0.6 }),
    h('circle', { cx: 4, cy: 5, r: 2, fill: 'currentColor' }),
    h('circle', { cx: 4, cy: 11, r: 2, fill: 'currentColor', opacity: 0.7 }),
    h('circle', { cx: 11, cy: 3, r: 2, fill: 'currentColor', opacity: 0.5 }),
    h('circle', { cx: 11, cy: 8, r: 2, fill: 'currentColor', opacity: 0.5 }),
    h('circle', { cx: 11, cy: 13, r: 2, fill: 'currentColor', opacity: 0.5 }),
  );
}

/** One Temporal-colored status badge. */
function StatusBadge({ status, t }) {
  const scheme = STATUS_SCHEME[status];
  return h('span', { className: `osb-badge osb-scheme-${scheme}` }, t(`status.${status}`));
}

/** Legend row: every board status with its Temporal color. */
function Legend({ t }) {
  return h('div', { className: 'osb-legend' },
    h('div', { className: 'osb-legend-title' }, t('board.legend')),
    h('div', { className: 'osb-legend-row' },
      COLUMN_ORDER.map(status => h('span', { key: status, className: 'osb-legend-item' },
        h('span', { className: `osb-dot osb-scheme-${STATUS_SCHEME[status]}` }),
        t(`status.${status}`),
      )),
    ),
  );
}

const DAG_NODE_W = 150;
const DAG_NODE_H = 46;
const DAG_GAP_X = 54;
const DAG_GAP_Y = 14;
const DAG_PAD = 14;

/** Dependency graph: layers left to right, blocker -> dependent arrows. */
function DagView({ board, t, onOpen }) {
  const positions = useMemo(() => {
    const map = new Map();
    board.layerGroups.forEach((nums, layer) => {
      nums.forEach((num, row) => {
        map.set(num, {
          x: DAG_PAD + layer * (DAG_NODE_W + DAG_GAP_X),
          y: DAG_PAD + row * (DAG_NODE_H + DAG_GAP_Y),
        });
      });
    });
    return map;
  }, [board]);
  const width = DAG_PAD * 2 + board.layerGroups.length * (DAG_NODE_W + DAG_GAP_X) - DAG_GAP_X;
  const maxRows = board.layerGroups.reduce((m, g) => Math.max(m, g.length), 1);
  const height = DAG_PAD * 2 + maxRows * (DAG_NODE_H + DAG_GAP_Y) - DAG_GAP_Y;
  const schemeOf = num => STATUS_SCHEME[board.byNum.get(num).column];
  return h('div', null,
    h('div', { className: 'osb-graphwrap' },
      h('svg', {
        width, height, viewBox: `0 0 ${width} ${height}`, role: 'img',
        'aria-label': t('board.graphAria', { slug: board.unit }),
        style: { display: 'block' },
      },
        h('defs', null,
          h('marker', {
            id: 'osb-arrow', viewBox: '0 0 8 8', refX: 7, refY: 4,
            markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse',
          }, h('path', { d: 'M0,0 L8,4 L0,8 z', fill: 'var(--dsw-alias-border-l3)' })),
        ),
        board.edges.map(e => {
          const a = positions.get(e.from);
          const b = positions.get(e.to);
          const x1 = a.x + DAG_NODE_W;
          const y1 = a.y + DAG_NODE_H / 2;
          const x2 = b.x;
          const y2 = b.y + DAG_NODE_H / 2;
          const mx = (x1 + x2) / 2;
          return h('path', {
            key: `${e.from}-${e.to}`, className: 'osb-edge',
            d: `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`,
            markerEnd: 'url(#osb-arrow)',
          });
        }),
        board.tickets.map(ticket => {
          const p = positions.get(ticket.num);
          const scheme = schemeOf(ticket.num);
          const label = String(ticket.num).padStart(2, '0');
          const short = ticket.title.length > 22 ? `${ticket.title.slice(0, 21)}…` : ticket.title;
          const tip = `${label} ${ticket.title}\n${t(`status.${ticket.column}`)}`
            + (ticket.blockers.length > 0 ? `\n${t('board.blockedBy', { list: ticket.blockers.map(b => String(b).padStart(2, '0')).join(', ') })}` : '');
          return h('g', {
            key: ticket.num, className: 'osb-node', tabIndex: 0, role: 'button',
            'aria-label': `${label} ${ticket.title}`,
            onClick: () => onOpen(ticket),
            onKeyDown: ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); onOpen(ticket); } },
          },
            h('title', null, tip),
            h('rect', {
              x: p.x, y: p.y, width: DAG_NODE_W, height: DAG_NODE_H, rx: 8,
              fill: `var(--osb-${scheme}-surface)`, stroke: `var(--osb-${scheme}-border)`, strokeWidth: 1.5,
            }),
            h('text', {
              x: p.x + 10, y: p.y + 18, className: `osb-node-num osb-scheme-${scheme}`,
              fill: `var(--osb-${scheme}-text)`,
            }, label),
            h('text', {
              x: p.x + 10, y: p.y + 34, className: `osb-node-title osb-scheme-${scheme}`,
              fill: `var(--osb-${scheme}-text)`,
            }, short),
          );
        }),
      ),
    ),
    board.cycle ? h('div', { className: 'osb-note' }, 'cycle in edges') : null,
    board.dangling.length > 0
      ? h('div', { className: 'osb-note' }, board.dangling.map(d => t('board.dangling', { num: String(d.from).padStart(2, '0') })).join('; '))
      : null,
  );
}

/** One Kanban card: number, title, criteria progress, blockers. */
function TicketCard({ ticket, t, onOpen }) {
  const scheme = STATUS_SCHEME[ticket.column];
  const meta = [];
  if (ticket.criteriaTotal > 0) meta.push(t('board.criteria', { done: ticket.criteriaDone, total: ticket.criteriaTotal }));
  if (ticket.blockers.length > 0) meta.push(t('board.blockedBy', { list: ticket.blockers.map(b => String(b).padStart(2, '0')).join(', ') }));
  else meta.push(t('board.noBlockers'));
  return h('button', {
    type: 'button', className: `osb-card osb-scheme-${scheme}`,
    onClick: () => onOpen(ticket), title: t('action.openTicket'),
  },
    h('span', { className: 'osb-card-top' },
      h('span', { className: 'osb-card-num' }, String(ticket.num).padStart(2, '0')),
      h('span', { className: 'osb-card-title' }, ticket.title),
    ),
    h('span', { className: 'osb-card-meta' }, meta.join(' · ')),
  );
}

/** Kanban: the five columns stacked for the narrow sidebar. */
function KanbanView({ board, t, onOpen }) {
  return h('div', { className: 'osb-columns', role: 'list', 'aria-label': t('board.kanbanAria', { slug: board.unit }) },
    COLUMN_ORDER.map(status => {
      const tickets = board.columns[status];
      return h('section', { key: status, className: 'osb-column', role: 'listitem' },
        h('div', { className: 'osb-colhead' },
          h('span', { className: `osb-dot osb-scheme-${STATUS_SCHEME[status]}` }),
          h('span', { className: 'osb-colname' }, t(`status.${status}`)),
          h('span', { className: 'osb-colcount' }, tickets.length),
        ),
        h('div', { className: 'osb-cards' },
          tickets.length === 0
            ? h('div', { className: 'osb-empty-col' }, '—')
            : tickets.map(ticket => h(TicketCard, { key: ticket.num, ticket, t, onOpen })),
        ),
      );
    }),
  );
}

/**
 * Per-session board source: reads continue.md and the unit's ticket folder
 * through the workspaceFiles Remote, watches both, and publishes derived
 * snapshots. Attach starts the work; detach stops every stream and timer.
 */
function createBoardSource(remote, sessionId) {
  let snapshot = { kind: 'loading' };
  const listeners = new Set();
  let attached = 0;
  let controller = null;
  let detachFn = null;
  let reloadTimer = null;
  let loadSeq = 0;
  let unit = null;
  let dirWatch = null;

  const publish = next => {
    snapshot = next;
    for (const listener of [...listeners]) listener();
  };
  const subscribe = listener => {
    listeners.add(listener);
    return () => { listeners.delete(listener); };
  };
  const getSnapshot = () => snapshot;

  const sleep = (ms, signal) => new Promise(resolve => {
    const timer = setTimeout(done, ms);
    function done() {
      signal.removeEventListener('abort', done);
      clearTimeout(timer);
      resolve();
    }
    signal.addEventListener('abort', done, { once: true });
    if (signal.aborted) done();
  });

  /** Read a whole text file page by page; failures travel as RemoteResult. */
  async function readAll(path, signal) {
    let offset = 1;
    let text = '';
    for (;;) {
      const res = await remote.workspaceFiles.read(sessionId, path, { offset, limit: 1000 }, signal);
      if (!res.ok) return res;
      if (res.value.lines === 0) return { ok: true, value: text };
      text += (offset > 1 ? '\n' : '') + res.value.text;
      if (res.value.eof) return { ok: true, value: text };
      offset += res.value.lines;
    }
  }

  /** One watch generation; resolves on the first change frame or a normal end. */
  async function watchUntilChange(path, signal) {
    const handle = remote.workspaceFiles.changes(sessionId, path, signal);
    try {
      for await (const frame of handle) {
        if (signal.aborted) return;
        if (frame.kind === 'change') return;
      }
    } finally {
      try { handle.dispose(); } catch { /* already closed */ }
    }
  }

  const isMissing = err => {
    const code = err && err.code;
    return code === 'workspace-file/not-found'
      || code === 'workspace-file/not-directory'
      || code === 'workspace-file/watch-unsupported';
  };

  /**
   * Watch one target; while it is missing, watch the nearest ancestor so its
   * creation is observed, then retry the exact target. Carrier faults retry
   * with a pause; the loop ends only with the signal.
   */
  async function watchLoop(path, signal, onChange) {
    while (!signal.aborted) {
      try {
        await watchUntilChange(path, signal);
        if (signal.aborted) return;
        onChange();
      } catch (err) {
        if (signal.aborted) return;
        if (isMissing(err)) {
          // Walk up to the nearest existing ancestor and wait for any change
          // there (a creation), then retry the exact target.
          let parent = path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '.';
          for (;;) {
            try {
              await watchUntilChange(parent, signal);
              break;
            } catch (ancestorErr) {
              if (signal.aborted) return;
              if (isMissing(ancestorErr) && parent !== '.') {
                parent = parent.includes('/') ? parent.slice(0, parent.lastIndexOf('/')) : '.';
                continue;
              }
              await sleep(2000, signal);
              break;
            }
          }
          continue;
        }
        await sleep(1500, signal);
      }
    }
  }

  function stopDirWatch() {
    if (dirWatch !== null) {
      dirWatch.stop();
      dirWatch = null;
    }
  }

  function startDirWatch(signal) {
    stopDirWatch();
    if (unit === null) return;
    const child = new AbortController();
    const onParentAbort = () => { child.abort(); };
    signal.addEventListener('abort', onParentAbort, { once: true });
    void watchLoop(`tickets/${unit}`, child.signal, scheduleReload);
    dirWatch = {
      stop() {
        signal.removeEventListener('abort', onParentAbort);
        child.abort();
      },
    };
  }

  async function load(signal) {
    const seq = ++loadSeq;
    const stale = () => signal.aborted || seq !== loadSeq;
    const cont = await readAll('docs/ops/continue.md', signal);
    if (stale()) return;
    if (!cont.ok) {
      if (cont.error.code === 'workspace-file/not-found') {
        unit = null;
        stopDirWatch();
        publish({ kind: 'noContinue' });
        return;
      }
      publish({ kind: 'error', message: cont.error.message });
      return;
    }
    const slug = parseCurrentUnit(cont.value);
    if (slug === null) {
      unit = null;
      stopDirWatch();
      publish({ kind: 'noUnit' });
      return;
    }
    const unitChanged = slug !== unit;
    unit = slug;
    if (unitChanged && controller !== null) startDirWatch(controller.signal);
    const dir = `tickets/${slug}`;
    const listing = await remote.workspaceFiles.list(sessionId, dir, signal);
    if (stale()) return;
    if (!listing.ok) {
      if (listing.error.code === 'workspace-file/not-found') {
        publish({ kind: 'noDir', unit: slug });
        return;
      }
      publish({ kind: 'error', message: listing.error.message });
      return;
    }
    const entries = listing.value.entries.filter(e => e.type === 'file' && e.name.endsWith('.md') && e.name !== 'README.md');
    const files = [];
    for (const entry of entries) {
      const res = await readAll(`${dir}/${entry.name}`, signal);
      if (stale()) return;
      if (res.ok) files.push({ name: entry.name, text: res.value });
    }
    const derived = deriveBoard(cont.value, files);
    if (stale()) return;
    publish(derived.kind === 'board' ? { kind: 'board', board: derived.board } : derived);
  }

  function scheduleReload() {
    if (controller === null) return;
    if (reloadTimer !== null) clearTimeout(reloadTimer);
    reloadTimer = setTimeout(() => {
      reloadTimer = null;
      void reload();
    }, 250);
  }

  async function reload() {
    if (controller === null) return;
    try {
      await load(controller.signal);
    } catch (err) {
      if (controller !== null && !controller.signal.aborted) {
        publish({ kind: 'error', message: String((err && err.message) || err) });
      }
    }
  }

  /** Start reads and watches for one mounted body; returns the detach. */
  function attach(signal) {
    attached += 1;
    if (attached === 1) {
      if (signal.aborted) {
        attached = 0;
        return () => {};
      }
      controller = new AbortController();
      const inner = controller.signal;
      const onAbort = () => { controller.abort(); };
      signal.addEventListener('abort', onAbort, { once: true });
      void reload();
      void watchLoop('docs/ops/continue.md', inner, scheduleReload);
      detachFn = () => {
        signal.removeEventListener('abort', onAbort);
        stopDirWatch();
        controller.abort();
        controller = null;
        if (reloadTimer !== null) {
          clearTimeout(reloadTimer);
          reloadTimer = null;
        }
      };
    }
    return () => {
      attached -= 1;
      if (attached === 0 && detachFn !== null) {
        const stop = detachFn;
        detachFn = null;
        stop();
      }
    };
  }

  return { subscribe, getSnapshot, attach, reload };
}

/** The tab body: header, view toggle, derived content, legend. */
function BoardBody(props) {
  const { sessionId, useTabInfo, t, source } = props;
  const tab = useTabInfo();
  const snap = useSyncExternalStore(source.subscribe, source.getSnapshot);
  const [view, setView] = useState('graph');

  useEffect(() => {
    const detach = source.attach(tab.signal);
    const unbind = tab.actions.bindCommands({ refresh: () => { void source.reload(); } });
    return () => { unbind(); detach(); };
  }, [source, tab.signal, tab.actions]);

  const board = snap.kind === 'board' ? snap.board : null;
  const onOpen = ticket => {
    if (board === null) return;
    try {
      tab.actions.openResource(`dsh-resource://file/session/${sessionId}/tickets/${board.unit}/${ticket.file}`);
    } catch { /* no file viewer in this profile: the board itself stays usable */ }
  };

  let content;
  if (snap.kind === 'loading') {
    content = h('div', { className: 'osb-message', role: 'status' }, t('board.loading'));
  } else if (snap.kind === 'error') {
    content = h('div', { className: 'osb-message', role: 'alert' },
      t('error.read', { message: snap.message }),
      h('div', null, h('button', { type: 'button', className: 'osb-retry', onClick: () => { void source.reload(); } }, t('action.retry'))),
    );
  } else if (snap.kind === 'noContinue') {
    content = h('div', { className: 'osb-message' }, t('empty.noContinue'));
  } else if (snap.kind === 'noUnit') {
    content = h('div', { className: 'osb-message' }, t('empty.noUnit'));
  } else if (snap.kind === 'noDir') {
    content = h('div', { className: 'osb-message' }, t('empty.noDir', { slug: snap.unit }));
  } else if (snap.kind === 'noTickets') {
    content = h('div', { className: 'osb-message' }, t('empty.noTickets', { slug: snap.unit }));
  } else if (view === 'graph') {
    content = h(DagView, { board, t, onOpen });
  } else {
    content = h(KanbanView, { board, t, onOpen });
  }

  return h('div', { className: 'osb-root' },
    h('style', null, BOARD_CSS),
    h('div', { className: 'osb-header' },
      board !== null ? h(Fragment, null,
        h('div', { className: 'osb-unitrow' },
          h('span', { className: 'osb-unitlabel' }, t('board.unit')),
          h('span', { className: 'osb-unit', title: board.unit }, board.unit),
        ),
        h('div', { className: 'osb-summary' }, t('board.summary', { count: board.tickets.length, frontier: board.frontier })),
      ) : null,
      h('div', { className: 'osb-derived' }, t('board.derived')),
      board !== null ? h('div', { className: 'osb-toggle', role: 'group' },
        h('button', { type: 'button', 'aria-pressed': view === 'graph', onClick: () => setView('graph') }, t('view.graph')),
        h('button', { type: 'button', 'aria-pressed': view === 'kanban', onClick: () => setView('kanban') }, t('view.kanban')),
      ) : null,
    ),
    h('div', { className: 'osb-content' }, content),
    board !== null ? h(Legend, { t }) : null,
  );
}

/** The tab chip title: glyph plus the localized name. */
function BoardTitle(props) {
  const { t } = props;
  return h(Fragment, null, h(BoardIcon, { size: 16 }), ' ', t('tab.title'));
}