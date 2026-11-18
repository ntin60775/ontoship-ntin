#!/usr/bin/env python3
"""Раннер сессий пробы deliver/03: create → prompt → wait/answer → transcript.

Политики ask (отвечает WS-мост ask-bridge.mjs, не раннер):
  channel:<label> — мост отвечает на ask канала выбором label (нога
                    оператора; матрица тикета задаёт канал);
  stop-on-ask     — зафиксировать ask и остановить сессию (нога удаления
                    drifted-копии не исполняется — пробел пробы);
  no-ask          — ask не ожидается; появившийся ask — находка, остановка.
Раннер только наблюдает wait/events и фиксирует транскрипт.
"""
import json
import pathlib
import sys
import time

import drv

WORK = pathlib.Path('/tmp/dlv03/work')
DEADLINE_S = 30 * 60  # таймаут тикета: 30 мин/сессия


def log(msg: str) -> None:
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with (WORK / 'runner.log').open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def ok(res: dict) -> dict:
    r = res.get('result', {})
    if not r.get('ok'):
        raise RuntimeError(json.dumps(r, ensure_ascii=False)[:800])
    return r['value']


def create(cwd: str, name: str = 'session') -> str:
    res = drv.call('session/create', {'request': {'cwd': cwd, 'agentPreset': 'standard'}})
    (WORK / f'{name}-create.json').write_text(
        json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return ok(res)['sessionId']


def prompt(sid: str, text: str, rid: str) -> None:
    ok(drv.call('session/prompt', {'request': {
        'requestId': rid, 'sessionId': sid, 'mode': 'queue',
        'content': [{'type': 'text', 'text': text}]}}))


def wait(sid: str, after: int, timeout_ms: int = 180000) -> dict:
    return ok(drv.call('session/wait', {'request': {
        'sessionId': sid, 'timeoutMs': timeout_ms, 'afterSeq': after,
        'maxMessages': 400}}))


def events_page(sid: str, before: int | None = None) -> dict:
    req = {'address': {'kind': 'session', 'sessionId': sid}, 'maxMessages': 200}
    if before is not None:
        req['beforeSeq'] = before
    return ok(drv.call('session/events', {'request': req}))


def all_events(sid: str) -> list[dict]:
    recs: dict[int, dict] = {}
    before = None
    for _ in range(60):
        page = events_page(sid, before)
        batch = page.get('records', [])
        if not batch:
            break
        for r in batch:
            e = r.get('event', r)
            if 'seq' in e:
                recs[e['seq']] = e
        if not page.get('hasMore'):
            break
        before = min(e['seq'] for e in (r.get('event', r) for r in batch) if 'seq' in e)
    return [recs[k] for k in sorted(recs)]


def find_asks(events: list[dict]) -> list[dict]:
    """ask_user_question вызовы; answered — есть tool/result с тем же callId."""
    results = set()
    for e in events:
        if e.get('type') == 'tool/result':
            cid = e.get('data', {}).get('message', {}).get('toolCallId')
            if cid:
                results.add(cid)
    asks = []
    for e in events:
        if e.get('type') != 'assistant/message':
            continue
        for c in e['data']['message']['content']:
            if c.get('type') == 'tool-call' and c.get('name') == 'ask_user_question':
                try:
                    args = json.loads(c.get('arguments', '{}'))
                except json.JSONDecodeError as je:
                    raise RuntimeError(f'ask arguments not JSON at seq {e.get("seq")}: {je}') from je
                asks.append({'callId': c.get('id'), 'seq': e['seq'],
                             'questions': args.get('questions', []),
                             'answered': c.get('id') in results})
    return asks


def transcript(sid: str, events: list[dict]) -> str:
    lines = [f'# Транскрипт сессии {sid}', '']
    for e in events:
        t = e.get('type')
        ts = time.strftime('%H:%M:%S', time.localtime(e.get('time', 0) / 1000))
        seq = e.get('seq')
        if t == 'user/message':
            txt = ' '.join(c.get('text', '') for c in e['data'].get('content', []) if c.get('type') == 'text')
            src = e['data'].get('source', {})
            lines.append(f'## [{ts}] USER seq={seq} source={src.get("kind")}')
            lines.append(txt[:4000])
        elif t == 'assistant/message':
            m = e['data']['message']
            parts = []
            for c in m.get('content', []):
                ct = c.get('type')
                if ct == 'text' and c.get('text', '').strip():
                    parts.append('TEXT: ' + c['text'])
                elif ct == 'tool-call':
                    parts.append(f'TOOL {c.get("name")} id={c.get("id")} args={c.get("arguments", "")[:2500]}')
            if parts:
                lines.append(f'## [{ts}] ASSISTANT seq={seq} turn={e["data"].get("turn")} step={e["data"].get("step")}')
                lines.extend(parts)
        elif t == 'tool/result':
            d = e.get('data', {})
            m = d.get('message', {})
            content = m.get('content', '')
            if isinstance(content, list):
                content = ' '.join(str(c.get('text', c)) for c in content)
            err = d.get('error')
            lines.append(f'## [{ts}] TOOL-RESULT seq={seq} id={m.get("toolCallId")}' + (f' ERROR={err}' if err else ''))
            lines.append(str(content)[:1800])
        elif t in ('session/title', 'turn/end', 'step/end'):
            lines.append(f'## [{ts}] {t} seq={seq} {json.dumps(e.get("data", {}), ensure_ascii=False)[:300]}')
        else:
            lines.append(f'## [{ts}] {t} seq={seq}')
        lines.append('')
    return '\n'.join(lines)


def run(name: str, cwd: str, text: str, policy: str, sid: str | None = None) -> None:
    log(f'{name}: старт cwd={cwd} policy={policy} парафраз="{text}" resume={sid is not None}')
    if sid is None:
        sid = create(cwd, name)
        log(f'{name}: sessionId={sid}')
        (WORK / f'{name}-sid.txt').write_text(sid + '\n', encoding='utf-8')
        prompt(sid, text, f'dlv03-{name}-1')
    else:
        log(f'{name}: resume sessionId={sid}')
    pol = json.loads((WORK / 'ask-policy.json').read_text()) if (WORK / 'ask-policy.json').exists() else {}
    pol[sid] = {'policy': policy, 'name': name}
    (WORK / 'ask-policy.json').write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding='utf-8')
    start = time.time()
    after = -1
    answered: set[str] = set()
    stopped_on_ask = False
    while time.time() - start < DEADLINE_S:
        w = wait(sid, after)
        after = w['state']['cursor']
        reason = w['reason']
        evs = all_events(sid)
        asks = find_asks(evs)
        unanswered = [a for a in asks if not a['answered']]
        log(f'{name}: wait reason={reason} cursor={after} asks={len(asks)} unanswered={len(unanswered)}')
        if reason == 'idle' and not w['state'].get('running'):
            if unanswered:
                log(f'{name}: idle с неотвеченным ask callId={unanswered[-1]["callId"]} — фиксация, остановка')
                stopped_on_ask = True
            break
        if reason == 'input-required':
            if unanswered and policy in ('stop-on-ask', 'no-ask'):
                log(f'{name}: ask при policy={policy} — фиксация и остановка callId={unanswered[-1]["callId"]}')
                stopped_on_ask = True
                break
            log(f'{name}: input-required pendingInput={w["state"].get("pendingInput")} unanswered={len(unanswered)} — мост отвечает, sleep 20')
            time.sleep(20)
            continue
        # timeout или running — продолжаем ждать
    else:
        log(f'{name}: ДЕДЛАЙН 30 мин — остановка')
    evs = all_events(sid)
    (WORK / f'{name}-events.json').write_text(json.dumps(evs, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (WORK / f'{name}-transcript.md').write_text(transcript(sid, evs), encoding='utf-8')
    proj = drv.call('session/projections', {'request': {'sessionId': sid}})
    (WORK / f'{name}-projections.json').write_text(json.dumps(proj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    pv = proj.get('result', {}).get('value', {}).get('values', {})
    log(f'{name}: финиш stopped_on_ask={stopped_on_ask} tokenUsage={pv.get("tokenUsage")} title={pv.get("title")}')


if __name__ == '__main__':
    name = sys.argv[1]
    cfg = json.loads(sys.argv[2])
    run(name, cfg['cwd'], cfg['text'], cfg['policy'], cfg.get('sid'))
