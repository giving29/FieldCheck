// netlify/functions/messenger.js
// THE MESSENGER — the outreach layer. One agent, two directions:
//   player2coach : a player turns their verdict into a grounded intro to a program
//   coach2player : a coach turns a discovered read into a professional first contact
//
//   POST ?action=draft -> generates the message (real Claude call, grounded in the verdict)
//   POST ?action=log    -> TOKEN-GATED -> persists a PRIVACY-MINIMAL record of the draft
//   GET  ?action=list    -> public read of recent outreach metadata (counts/mode/date)
//
// HARD LINES (by design):
//   - It DRAFTS. It never sends. No real contact info is fetched, invented, or stored.
//   - coach2player drafts stay professional and route through proper channels — never an
//     auto-DM, never anything that assumes or addresses a minor inappropriately.
//   - The persisted record is metadata (mode, target descriptor, the read it carried, date) —
//     NOT message bodies with personal data, NOT emails/handles.
//   - Writes are gated by FC_LEDGER_TOKEN (browser can't spam the store).
//   - Safe no-op if env unconfigured.

const MODEL = 'claude-sonnet-4-6';
const RURL = process.env.UPSTASH_REDIS_REST_URL;
const RTOK = process.env.UPSTASH_REDIS_REST_TOKEN;
const WRITE_TOKEN = process.env.FC_LEDGER_TOKEN;
const KEY = 'fc:messenger:v1';
const CAP = 500;

const SYS = `You are FieldCheck's Messenger. You draft ONE grounded, specific outreach message from a verdict (an honest athletic read across 8 facets vs the sport's greatest). You never hype, never inflate, never invent facts. The power of the message is that it carries a verifiable read, not adjectives.

RULES:
- Ground every claim in the verdict provided. If a facet or number isn't given, don't assert it.
- The message references that the read is on FieldCheck's public record — a falsifiable, timestamped number, not a self-promotion. That's the credibility.
- Keep it short, human, and specific. No clichés ("hard worker", "great motor"), no exclamation spam.
- player2coach: a player (or family) introducing themselves to a college/club program. Confident, humble, specific about fit. Mentions the film/evidence backs the number.
- coach2player: a program reaching a player they found through the public record. Professional, respectful, routes through proper channels. NEVER assumes the athlete's age or uses familiar/inappropriate tone; this may be a minor — keep it strictly professional and parent/guardian-aware.
- Output ONLY the message body (subject line first if it's an email, then a blank line, then the body). No preamble, no meta-commentary.`;

exports.handler = async (event) => {
  const action = ((event.queryStringParameters || {}).action) || 'draft';

  if (action === 'list') {
    if (!RURL || !RTOK) return resp(200, { entries: [], live: false });
    try {
      const raw = (await redis(['LRANGE', KEY, '0', '99'])) || [];
      const entries = raw.map(function (x) { try { return JSON.parse(x); } catch (e) { return null; } }).filter(Boolean);
      return resp(200, { entries: entries, live: true, count: entries.length });
    } catch (e) { return resp(200, { entries: [], live: false, error: String(e).slice(0, 120) }); }
  }

  if (action === 'log') {
    if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
    if (!RURL || !RTOK) return resp(200, { ok: false, reason: 'not_configured' });
    const h = event.headers || {};
    const tok = h['x-fc-token'] || h['X-Fc-Token'];
    if (!WRITE_TOKEN || tok !== WRITE_TOKEN) return resp(403, { error: 'forbidden' });
    let e;
    try { e = JSON.parse(event.body || '{}'); } catch (err) { return resp(400, { error: 'bad_json' }); }
    // PRIVACY-MINIMAL record: mode, who it was about (the athlete already public on The Record),
    // target descriptor (program name or generic), the read it carried, date. NO contact info, NO body.
    const rec = {
      mode: e.mode === 'coach2player' ? 'coach2player' : 'player2coach',
      athlete: String(e.athlete || '').slice(0, 60),
      target: String(e.target || '').slice(0, 80),   // descriptor only (e.g. "Stanford WVB"), never an email/handle
      read: String(e.read || '').slice(0, 5),
      date: new Date().toISOString().slice(0, 10)
    };
    try {
      await redis(['LPUSH', KEY, JSON.stringify(rec)]);
      await redis(['LTRIM', KEY, '0', String(CAP - 1)]);
      return resp(200, { ok: true, logged: true });
    } catch (err) { return resp(200, { ok: false, error: String(err).slice(0, 120) }); }
  }

  // action === 'draft'
  if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
  if (!process.env.ANTHROPIC_API_KEY) return resp(200, { draft: null, reason: 'no_key' });
  let q;
  try { q = JSON.parse(event.body || '{}'); } catch (e) { return resp(400, { error: 'bad_json' }); }
  if (!q.athlete || !q.read) return resp(200, { draft: null, reason: 'missing_verdict' });

  const mode = q.mode === 'coach2player' ? 'coach2player' : 'player2coach';
  const facets = Array.isArray(q.facets) ? q.facets.slice(0, 8).join(', ') : '(facets not provided)';
  const evidence = Array.isArray(q.evidence) ? q.evidence.slice(0, 5).join('; ') : (q.evidence || '(evidence not provided)');

  const ask = `Mode: ${mode}
Athlete: ${q.athlete}${q.pos ? ' (' + q.pos + ')' : ''}
FieldCheck read: ${q.read} (provisional, on the public record)
Standout facets: ${facets}
Evidence on record: ${evidence}
Target: ${q.target || (mode === 'player2coach' ? 'a college program that fits' : 'the athlete, through proper channels')}
${q.channel ? 'Channel: ' + q.channel : 'Channel: email'}

Draft the outreach message now.`;

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-api-key': process.env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model: MODEL, max_tokens: 700, system: SYS, messages: [{ role: 'user', content: ask }] })
    });
    if (!r.ok) { const t = await r.text(); return resp(200, { draft: null, reason: 'api_' + r.status, detail: t.slice(0, 200) }); }
    const data = await r.json();
    const draft = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
    return resp(200, { draft: draft, mode: mode, model: MODEL });
  } catch (e) {
    return resp(200, { draft: null, reason: 'fetch_error', detail: String(e).slice(0, 200) });
  }
};

async function redis(cmd) {
  const r = await fetch(RURL, { method: 'POST', headers: { 'Authorization': 'Bearer ' + RTOK, 'Content-Type': 'application/json' }, body: JSON.stringify(cmd) });
  if (!r.ok) throw new Error('upstash_' + r.status);
  const j = await r.json();
  return j.result;
}
function resp(code, obj) {
  return { statusCode: code, headers: { 'content-type': 'application/json', 'cache-control': 'no-store', 'access-control-allow-origin': '*' }, body: JSON.stringify(obj) };
}
