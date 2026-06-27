// netlify/functions/coverage.js
// The Coverage agent — live ingestion. Reads the PUBLIC record (Claude + web
// search) and returns a PROVISIONAL read in the exact shape coverage.html
// renders. The honesty firewall is enforced in the system prompt: provisional
// never grade, public athletic signal only, no fabrication, confidence capped.

const MODEL = 'claude-sonnet-4-6';

const { checkAndCount, clientIp } = require('./_ratelimit');

const SYS = `You are the FieldCheck Coverage agent. Given an athlete's name, sport, position, school, and state, read the PUBLIC athletic record using web search and produce a PROVISIONAL read.

THE HONESTY FIREWALL — non-negotiable:
- PROVISIONAL, never a grade. Built from public signal only.
- Use ONLY public athletic-performance information (stats, results, rosters, write-ups, honor lists). Do NOT include or infer contact details, home address, or other sensitive personal data. Athletes may be minors — stay strictly on the public athletic record.
- Report ONLY what sources actually show. If you cannot confidently identify the athlete or find little signal, SAY SO and return LOW confidence with a careful, conservative read. NEVER fabricate achievements, stats, or identity.
- Confidence reflects public evidence richness and is CAPPED: public-only evidence can never exceed 70. Thin or none → 28–45.
- The provisional number is 0–10, centered conservatively (public signal rarely justifies above ~6.5). Typical range 3.2–6.8.
- ALWAYS surface what is MISSING: graded film and the four invisible facets (competitiveness, mental strength, mindset, character) cannot be read from the public record.

Return ONLY a JSON object — no prose, no markdown fences:
{"num":"5.4","conf":42,"band":"a real college track","found":[["ROSTER","short sentence"],["RESULT","short sentence"]],"missing":[["FILM","No graded film yet — the only place the invisible four show."],["INVIS","Competitiveness, mental strength, mindset, character — unread without you."]]}
"found" = 1–4 concrete public signals you ACTUALLY found (tag + short sentence). If none, found = [["NONE","Limited public signal under this name — a provisional baseline only."]].
"band" is one short phrase: "a strong college track" / "a real college track" / "a developing college path" / "an early, building profile" / "building the base".`;

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
  if (!process.env.ANTHROPIC_API_KEY) return resp(200, { read: null, reason: 'no_key' });

  let q;
  try { q = JSON.parse(event.body || '{}'); } catch (e) { return resp(400, { error: 'bad json' }); }
  if (!q.name) return resp(200, { read: null, reason: 'no_name' });

  // cost guard: per-IP throttle + global daily cap (UI falls back to local read on 429)
  const gate = await checkAndCount(clientIp(event));
  if (!gate.ok) return resp(200, { read: null, reason: gate.reason });

  const ask = `Athlete: ${q.name}\nSport: ${q.sport || '(unspecified)'}\nPosition: ${q.pos || '(unspecified)'}\nSchool/club: ${q.school || '(unspecified)'}\nState: ${q.state || '(unspecified)'}\n\nRead the public record and return the provisional read JSON.`;

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1200,
        system: SYS,
        tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 4 }],
        messages: [{ role: 'user', content: ask }]
      })
    });
    if (!r.ok) { const t = await r.text(); return resp(200, { read: null, reason: 'api_' + r.status, detail: t.slice(0, 300) }); }
    const data = await r.json();
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n');
    const read = parseRead(text);
    return resp(200, { read: read, model: MODEL });
  } catch (e) {
    return resp(200, { read: null, reason: 'fetch_error', detail: String(e).slice(0, 200) });
  }
};

function parseRead(text) {
  let s = (text || '').trim().replace(/^```(json)?/i, '').replace(/```$/, '').trim();
  const a = s.indexOf('{'), b = s.lastIndexOf('}');
  if (a >= 0 && b > a) s = s.slice(a, b + 1);
  let o;
  try { o = JSON.parse(s); } catch (e) { return null; }
  // enforce the firewall numerically, regardless of model output
  let num = parseFloat(o.num); if (!(num >= 0 && num <= 10)) num = 4.5;
  num = Math.max(3.2, Math.min(6.8, num));
  let conf = parseInt(o.conf, 10); if (!(conf >= 0 && conf <= 100)) conf = 38;
  conf = Math.max(25, Math.min(70, conf)); // public-only is capped at 70
  const found = Array.isArray(o.found) && o.found.length
    ? o.found.slice(0, 4).map(f => [String(f[0] || 'SIGNAL').slice(0, 12), String(f[1] || '').slice(0, 160)])
    : [['NONE', 'Limited public signal under this name — a provisional baseline only.']];
  const missing = [
    ['FILM', 'No graded film yet — the only place the invisible four show.'],
    ['INVIS', 'Competitiveness, mental strength, mindset, character — unread without you.']
  ];
  return { num: num.toFixed(1), conf: conf, band: String(o.band || 'an early, building profile').slice(0, 60), found: found, missing: missing, ev: conf / 100 };
}

function resp(code, obj) {
  return { statusCode: code, headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' }, body: JSON.stringify(obj) };
}
