#!/usr/bin/env python3
"""Драйвер пробы deliver/03: HTTP API изолированного хоста 3096.

Credential (launch-токен, cookie) живут только в /tmp/dlv03/work и не
печатаются. Вызовы: python3 drv.py <method> '<json-args>' [outfile]
"""
import json
import pathlib
import re
import sys
import urllib.request
import uuid

WORK = pathlib.Path('/tmp/dlv03/work')
BASE = 'http://127.0.0.1:3096'
COOKIE_FILE = WORK / 'cookie.txt'


def token() -> str:
    log = (WORK / 'host.log').read_text(encoding='utf-8', errors='replace')
    m = re.search(r'dsh web: http://[^ ]*token=([A-Za-z0-9_-]+)', log)
    if not m:
        raise SystemExit('launch-токен не найден в host.log')
    return m.group(1)


def cookie() -> str:
    if COOKIE_FILE.exists():
        return COOKIE_FILE.read_text().strip()
    req = urllib.request.Request(BASE + '/connect?token=' + token() + '&interactions=none')

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    op = urllib.request.build_opener(NoRedirect)
    try:
        op.open(req)
    except urllib.error.HTTPError as e:
        headers = e.headers
    else:
        raise SystemExit('ожидался redirect с Set-Cookie')
    sc = headers.get('Set-Cookie', '')
    c = sc.split(';')[0]
    if not c:
        raise SystemExit('Set-Cookie пуст')
    import os
    fd = os.open(str(COOKIE_FILE), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(c)
    return c


def call(method: str, args: dict) -> dict:
    body = json.dumps({
        'type': 'client-request',
        'rpcId': 'dlv03-' + uuid.uuid4().hex[:12],
        'method': method,
        'payload': {'args': args},
    }).encode()
    req = urllib.request.Request(
        BASE + '/api/' + method,
        data=body,
        headers={'content-type': 'application/json', 'cookie': cookie()},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    method = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    out = sys.argv[3] if len(sys.argv) > 3 else None
    result = call(method, args)
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if out:
        (WORK / out).write_text(text + '\n', encoding='utf-8')
        ok = result.get('result', {}).get('ok')
        print(f'{method} ok={ok} -> {out} ({len(text)} bytes)')
        if not ok:
            print(text[:1500])
    else:
        print(text[:4000])


if __name__ == '__main__':
    main()
