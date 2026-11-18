// WS-мост пробы deliver/03: отвечает на ask сессий как GUI-клиент.
// Legacy-ask профиля блокирующий: ответ идёт через forwarded waterfall
// 'user-questions/request' → POST /api/$events/result. Политики —
// ask-policy.json {sid: {policy, name}}; мост перечитывает файл на каждое событие.
// Зависимость: node + ws (пакет DSH-чекаута, apps/cli/node_modules/ws).
// Правки панели: снята не использовавшаяся approval-ветка (событий
// approval/request в пробе не было — bridge.log), снят custom-fallback
// (ответы матрицы совпали с label опций дословно), ошибки parse — громкие.
import WebSocket from '/home/prog7/home/dev/contrib/forks/deepseek-harness/apps/cli/node_modules/ws/index.js'
import fs from 'node:fs'

const WORK = '/tmp/dlv03/work'
const BASE = 'http://127.0.0.1:3096'
const log = m => {
  const line = `[${new Date().toTimeString().slice(0, 8)}] bridge: ${m}`
  console.log(line)
  fs.appendFileSync(`${WORK}/bridge.log`, line + '\n')
}

const tokenMatch = fs.readFileSync(`${WORK}/host.log`, 'utf8')
  .match(/dsh web: http:\/\/[^ ]*token=([A-Za-z0-9_-]+)/)
if (!tokenMatch) { console.error('launch-токен не найден в host.log'); process.exit(1) }
const token = tokenMatch[1]

async function answerCookie() {
  const res = await fetch(`${BASE}/connect?token=${token}&interactions=answer`, { redirect: 'manual' })
  const sc = res.headers.get('set-cookie') || ''
  const c = sc.split(';')[0]
  if (!c) throw new Error('no set-cookie on /connect interactions=answer')
  fs.writeFileSync(`${WORK}/cookie-answer.txt`, c, { mode: 0o600 })
  return c
}

function policyOf(sid) {
  let p
  try {
    p = JSON.parse(fs.readFileSync(`${WORK}/ask-policy.json`, 'utf8'))
  } catch (e) {
    log(`ОШИБКА чтения ask-policy.json: ${e.message} — сессия ${sid} без политики, ответ не даётся`)
    return { policy: 'no-policy', name: '?' }
  }
  if (!p[sid]) log(`политика для ${sid} не зарегистрирована — ответ не даётся`)
  return p[sid] || { policy: 'no-policy', name: '?' }
}

function pickAnswer(request, policy) {
  const qs = request.questions || []
  if (policy.startsWith('channel:')) {
    const want = policy.split(':')[1]
    return {
      answers: qs.map(q => {
        const opts = (q.options || []).map(o => o.label)
        const hit = opts.find(l => l === want || l.startsWith(want + ' ') || l.startsWith(want + '('))
        if (!hit) throw new Error(`label канала "${want}" не найден в опциях ask: ${opts.join(', ')}`)
        return { id: q.id, selected: [hit] }
      }),
    }
  }
  return null
}

const cookie = await answerCookie()
const ws = new WebSocket(`ws://127.0.0.1:3096/api/remote.mux`, { headers: { cookie } })
let clientId = null
const seen = new Set()

ws.on('open', () => {
  log('WS open, opening $events stream')
  ws.send(JSON.stringify({ type: 'open', streamId: 'ev1', endpoint: '$events', payload: { args: {} } }))
})

ws.on('message', async raw => {
  let msg
  try { msg = JSON.parse(raw.toString()) } catch { return }
  if (msg.type !== 'item' || msg.streamId !== 'ev1') return
  const f = msg.value
  if (f.type === 'ready') { clientId = f.clientId; log(`ready clientId=${clientId}`); return }
  if (f.type === 'cancel') { log(`cancel eventId=${f.eventId}`); return }
  if (f.type === 'emit') { log(`emit ${f.event}`); return }
  if (f.type !== 'waterfall') return
  const sid = String(f.agentId)
  const { policy, name } = policyOf(sid)
  log(`waterfall ${f.event} session=${name}(${sid.slice(8, 16)}) eventId=${f.eventId} policy=${policy}`)
  fs.writeFileSync(`${WORK}/ask-${name}-${f.eventId.slice(0, 8)}.json`,
    JSON.stringify({ session: sid, event: f.event, eventId: f.eventId, request: f.request }, null, 1) + '\n')
  if (seen.has(f.eventId)) return
  if (f.event === 'user-questions/request') {
    const value = pickAnswer(f.request, policy)
    if (value === null) { log(`не отвечаю (policy=${policy}) — ask зафиксирован`); return }
    seen.add(f.eventId)
    const body = {
      type: 'client-request', rpcId: 'dlv03-bridge-' + f.eventId.slice(0, 8),
      method: '$events/result',
      payload: { args: { clientId, eventId: f.eventId, outcome: { kind: 'result', value } } },
    }
    const res = await fetch(`${BASE}/api/$events/result`, {
      method: 'POST', headers: { 'content-type': 'application/json', cookie }, body: JSON.stringify(body),
    })
    const j = await res.json()
    log(`answer ${name} ok=${j.result?.ok} value=${JSON.stringify(value).slice(0, 200)}`)
    fs.writeFileSync(`${WORK}/answer-${name}-${f.eventId.slice(0, 8)}.json`, JSON.stringify(j, null, 1) + '\n')
  }
})

ws.on('close', (code, reason) => { log(`WS close ${code} ${reason}`); process.exit(1) })
ws.on('error', e => { log(`WS error ${e.message}`); process.exit(1) })
setInterval(() => { if (ws.readyState === WebSocket.OPEN) ws.ping() }, 30000)
