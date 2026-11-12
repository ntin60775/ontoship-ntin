    return {
      inject: ['slots', 'locale', 'sidebarRightTabs', 'sidebarRight', 'remote', 'remote.workspaceFiles'],
      apply(ctx) {
        const t = ctx.locale.bind(NS);
        ctx.effect(() => ctx.locale.register(NS, { en: LOCALE_EN, ru: LOCALE_RU }), 'ontoship-board: dictionaries');
        ctx.effect(() => ctx.sidebarRightTabs.register({
          id: PKG,
          kind: KIND,
          title: () => t('tab.title'),
          guide: [{
            id: 'open',
            order: 65,
            title: () => t('tab.title'),
            description: () => t('tab.description'),
            icon: BoardIcon,
          }],
        }), 'ontoship-board: tab type');

        const sources = new Map();
        const getSource = sessionId => {
          let source = sources.get(sessionId);
          if (source === undefined) {
            source = createBoardSource(ctx.remote, sessionId);
            sources.set(sessionId, source);
          }
          return source;
        };

        ctx.effect(() => ctx.slots.inject('sidebar.right.pane.tab', () => ctx.slots.register({
          name: 'sidebar.right.pane.tab', key: PKG, locale: NS,
          inject: sessionId => ({ source: getSource(sessionId) }),
        }, BoardBody)), 'ontoship-board: tab body');
        ctx.effect(() => ctx.slots.inject('sidebar.right.pane.tab.title', () => ctx.slots.register({
          name: 'sidebar.right.pane.tab.title', key: PKG, locale: NS,
        }, BoardTitle)), 'ontoship-board: tab title');

        // A reconnect may have missed file changes: re-read every live board.
        ctx.effect(() => ctx.on('connection/reset', () => {
          for (const source of sources.values()) void source.reload();
        }), 'ontoship-board: connection reset');

        // Follow the on-screen Session: open the board once per Session when
        // the working folder carries continue.md; never multiply tabs.
        ctx.effect(() => {
          const opened = new Set();
          let disposed = false;
          const hasTab = sessionId => ctx.sidebarRight.openTabs.getSnapshot()
            .some(tab => tab.kind === KIND && tab.sessionId === sessionId);
          const tryOpen = sessionId => {
            if (disposed || sessionId === undefined || opened.has(sessionId)) return;
            opened.add(sessionId);
            if (hasTab(sessionId)) return;
            void (async () => {
              try {
                const res = await ctx.remote.workspaceFiles.stat(sessionId, 'docs/ops/continue.md');
                if (disposed || !res.ok) return;
                if (ctx.sidebarRight.mounted.getSnapshot() !== sessionId) return;
                if (hasTab(sessionId)) return;
                ctx.sidebarRight.openTab(KIND);
              } catch { /* the guide entry stays available */ }
            })();
          };
          const unsubscribe = ctx.sidebarRight.mounted.subscribe(() => {
            tryOpen(ctx.sidebarRight.mounted.getSnapshot());
          });
          tryOpen(ctx.sidebarRight.mounted.getSnapshot());
          return () => {
            // Stop auto-open first, then close only this plugin's own tabs.
            disposed = true;
            unsubscribe();
            for (const tab of ctx.sidebarRight.openTabs.getSnapshot()) {
              if (tab.kind === KIND) ctx.sidebarRight.closeIn(tab.sessionId, tab.tabId);
            }
          };
        }, 'ontoship-board: auto-open and teardown');
      },
    };
  },
});