/**
 * Client artifact smoke tests: load client.js through a fake module loader,
 * mount apply() against stub services, and drive one board source through a
 * scripted workspaceFiles Remote. Usage: node tests/client.test.mjs
 */
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const pkgRoot = resolve(here, '..');
const artifact = await readFile(join(pkgRoot, 'client.js'), 'utf8');
const manifest = JSON.parse(await readFile(join(pkgRoot, 'package.json'), 'utf8'));
const PKG = manifest.name;
const KIND = `${PKG}:chain`;

let passed = 0;
const test = async (name, fn) => {
  await fn();
  passed += 1;
  console.log(`ok - ${name}`);
};

/** Load the artifact the way the browser module system does. */
function loadArtifact() {
  let registration;
  const sandbox = { window: { __ModuleLoader__: { load: reg => { registration = reg; } } } };
  const fn = new Function('window', artifact);
  fn(sandbox.window);
  assert.ok(registration, 'artifact registered a module');
  assert.equal(registration.id, PKG);
  const reactStub = {
    createElement: (...args) => ({ type: args[0], props: args[1], children: args.slice(2) }),
    Fragment: 'Fragment',
    useEffect: () => {},
    useMemo: fn => fn(),
    useState: initial => [initial, () => {}],
    useSyncExternalStore: (sub, get) => get(),
  };
  const plugin = registration.factory(name => {
    if (name === 'react') return reactStub;
    throw new Error(`unexpected require: ${name}`);
  });
  return plugin;
}

/** Scripted workspaceFiles Remote over an in-memory file map. */
function fakeRemote(files) {
  const notFound = path => ({ ok: false, error: { code: 'workspace-file/not-found', message: `no entry at "${path}"` } });
  return {
    workspaceFiles: {
      read: async (sid, path, range) => {
        const text = files.get(path);
        if (text === undefined) return notFound(path);
        const lines = text.split('\n');
        const offset = (range && range.offset) || 1;
        const limit = (range && range.limit) || 1000;
        const page = lines.slice(offset - 1, offset - 1 + limit);
        return {
          ok: true,
          value: {
            absolutePath: `/w/${path}`, version: 'v1', offset,
            text: page.join('\n'), lines: page.length,
            eof: offset - 1 + limit >= lines.length,
          },
        };
      },
      list: async (sid, path) => {
        const prefix = `${path}/`;
        const names = [...files.keys()]
          .filter(k => k.startsWith(prefix))
          .map(k => k.slice(prefix.length))
          .filter(n => n.length > 0 && !n.includes('/'));
        if (names.length === 0) return notFound(path);
        return { ok: true, value: { path, entries: names.map(name => ({ name, type: 'file' })), truncated: false } };
      },
      stat: async (sid, path) => (files.has(path)
        ? { ok: true, value: { absolutePath: `/w/${path}`, version: 'v1' } }
        : notFound(path)),
      changes: (sid, path, signal) => ({
        [Symbol.asyncIterator]() {
          return {
            next: () => new Promise(resolve => {
              if (signal.aborted) resolve({ done: true });
              else signal.addEventListener('abort', () => resolve({ done: true }), { once: true });
            }),
            return: () => Promise.resolve({ done: true }),
          };
        },
        dispose() {},
      }),
    },
  };
}

/** Stub Client context collecting effects and registrations. */
function fakeCtx(remote) {
  const disposers = [];
  const registrations = [];
  const tabDefs = [];
  const closed = [];
  let openTabs = [];
  const ctx = {
    locale: {
      bind: () => key => key,
      register: (ns, dicts) => { ctx.registeredLocales = dicts; return () => {}; },
    },
    effect(fn) { const d = fn(); disposers.push(d); return d; },
    on: () => () => {},
    slots: {
      inject: (name, fn) => fn(),
      register: (decl, component) => { registrations.push({ decl, component }); return () => {}; },
    },
    sidebarRightTabs: { register: def => { tabDefs.push(def); return () => {}; } },
    sidebarRight: {
      mounted: { getSnapshot: () => undefined, subscribe: () => () => {} },
      openTabs: { getSnapshot: () => openTabs },
      openTab: () => {},
      closeIn: (sessionId, tabId) => { closed.push({ sessionId, tabId }); },
    },
    remote,
  };
  return { ctx, disposers, registrations, tabDefs, closed, setOpenTabs: tabs => { openTabs = tabs; } };
}

const CONTINUE = [
  '# Продолжение',
  '**Открыт юнит `demo` (2026-11-12)**: работа.',
  '## Порядок тикетов',
  '`demo`: **01 старт → 02 финиш.** Тикет 01 принят оператором 2026-11-12.',
].join('\n');
const T1 = '# 01: Старт\n\n**Блокируется:** ничем.\n\n- [x] критерий\n\n## Доказательства\n\nфакт\n';
const T2 = '# 02: Финиш\n\n**Блокируется:** тикет 01.\n\n- [ ] критерий\n';

await test('artifact: registers the package id and exposes inject/apply', () => {
  const plugin = loadArtifact();
  assert.ok(Array.isArray(plugin.inject));
  for (const service of ['slots', 'locale', 'sidebarRightTabs', 'sidebarRight', 'remote', 'remote.workspaceFiles']) {
    assert.ok(plugin.inject.includes(service), `inject missing ${service}`);
  }
  assert.equal(typeof plugin.apply, 'function');
});

await test('apply: one package-prefixed tab type and both keyed seats', () => {
  const plugin = loadArtifact();
  const { ctx, registrations, tabDefs } = fakeCtx(fakeRemote(new Map()));
  plugin.apply(ctx);
  // Runtime dictionaries are flat dot-key string maps in every locale.
  for (const locale of ['en', 'ru']) {
    const dict = ctx.registeredLocales[locale];
    assert.ok(dict, `locale ${locale} registered`);
    for (const [key, value] of Object.entries(dict)) {
      assert.equal(typeof value, 'string', `${locale}.${key} must be a string`);
      assert.ok(!key.includes('meta'), 'meta is plugin-manager only');
    }
    assert.equal(typeof dict['tab.title'], 'string');
    assert.equal(typeof dict['status.blocked'], 'string');
    assert.equal(typeof dict['board.summary'], 'string');
  }
  assert.equal(tabDefs.length, 1);
  assert.equal(tabDefs[0].id, PKG);
  assert.equal(tabDefs[0].kind, KIND);
  assert.ok(tabDefs[0].guide.length === 1);
  const body = registrations.find(r => r.decl.name === 'sidebar.right.pane.tab');
  const title = registrations.find(r => r.decl.name === 'sidebar.right.pane.tab.title');
  assert.ok(body && body.decl.key === PKG);
  assert.ok(title && title.decl.key === PKG);
  assert.equal(typeof body.component, 'function');
  assert.equal(typeof title.component, 'function');
  const face = body.decl.inject('sess-1');
  assert.equal(typeof face.source.subscribe, 'function');
  assert.equal(typeof face.source.getSnapshot, 'function');
  assert.equal(typeof face.source.attach, 'function');
  assert.equal(typeof face.source.reload, 'function');
});

await test('teardown: closes only this plugin kind, preserves unrelated tabs', () => {
  const plugin = loadArtifact();
  const harness = fakeCtx(fakeRemote(new Map()));
  plugin.apply(harness.ctx);
  harness.setOpenTabs([
    { sessionId: 's1', tabId: 'mine', kind: KIND, contentId: 'x' },
    { sessionId: 's1', tabId: 'other', kind: 'files', contentId: 'y' },
    { sessionId: 's2', tabId: 'mine2', kind: KIND, contentId: 'z' },
  ]);
  // The auto-open effect is the last registered effect.
  const teardown = harness.disposers[harness.disposers.length - 1];
  teardown();
  assert.deepEqual(harness.closed, [
    { sessionId: 's1', tabId: 'mine' },
    { sessionId: 's2', tabId: 'mine2' },
  ]);
});

await test('source: derives the board from the scripted workspace', async () => {
  const plugin = loadArtifact();
  const files = new Map([
    ['docs/ops/continue.md', CONTINUE],
    ['tickets/demo/01-start.md', T1],
    ['tickets/demo/02-finish.md', T2],
  ]);
  const { ctx, registrations } = fakeCtx(fakeRemote(files));
  plugin.apply(ctx);
  const body = registrations.find(r => r.decl.name === 'sidebar.right.pane.tab');
  const source = body.decl.inject('sess-1').source;
  const controller = new AbortController();
  const detach = source.attach(controller.signal);
  await new Promise(resolve => setTimeout(resolve, 50));
  const snap = source.getSnapshot();
  assert.equal(snap.kind, 'board');
  assert.equal(snap.board.unit, 'demo');
  assert.deepEqual(snap.board.columns.accepted.map(t => t.num), [1]);
  assert.deepEqual(snap.board.columns.ready.map(t => t.num), [2]);
  detach();
  controller.abort();
});

await test('source: missing continue.md is a named absence, not an error', async () => {
  const plugin = loadArtifact();
  const { ctx, registrations } = fakeCtx(fakeRemote(new Map()));
  plugin.apply(ctx);
  const body = registrations.find(r => r.decl.name === 'sidebar.right.pane.tab');
  const source = body.decl.inject('sess-1').source;
  const controller = new AbortController();
  const detach = source.attach(controller.signal);
  await new Promise(resolve => setTimeout(resolve, 50));
  assert.equal(source.getSnapshot().kind, 'noContinue');
  detach();
  controller.abort();
});

await test('source: missing unit folder is a named absence', async () => {
  const plugin = loadArtifact();
  const files = new Map([['docs/ops/continue.md', CONTINUE]]);
  const { ctx, registrations } = fakeCtx(fakeRemote(files));
  plugin.apply(ctx);
  const body = registrations.find(r => r.decl.name === 'sidebar.right.pane.tab');
  const source = body.decl.inject('sess-1').source;
  const controller = new AbortController();
  const detach = source.attach(controller.signal);
  await new Promise(resolve => setTimeout(resolve, 50));
  const snap = source.getSnapshot();
  assert.equal(snap.kind, 'noDir');
  assert.equal(snap.unit, 'demo');
  detach();
  controller.abort();
});

await test('source: reload picks up markdown edits (derived, nothing stored)', async () => {
  const plugin = loadArtifact();
  const files = new Map([
    ['docs/ops/continue.md', CONTINUE],
    ['tickets/demo/01-start.md', T1],
    ['tickets/demo/02-finish.md', T2],
  ]);
  const { ctx, registrations } = fakeCtx(fakeRemote(files));
  plugin.apply(ctx);
  const body = registrations.find(r => r.decl.name === 'sidebar.right.pane.tab');
  const source = body.decl.inject('sess-1').source;
  const controller = new AbortController();
  const detach = source.attach(controller.signal);
  await new Promise(resolve => setTimeout(resolve, 50));
  assert.deepEqual(source.getSnapshot().board.columns.ready.map(t => t.num), [2]);
  // The operator accepts ticket 02 in the runbook.
  files.set('docs/ops/continue.md', `${CONTINUE} Тикет 02 принят оператором 2026-11-12.`);
  await source.reload();
  const snap = source.getSnapshot();
  assert.deepEqual(snap.board.columns.accepted.map(t => t.num), [1, 2]);
  assert.deepEqual(snap.board.columns.ready.map(t => t.num), []);
  detach();
  controller.abort();
});

console.log(`\n${passed} tests passed`);