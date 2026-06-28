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

THE DOSSIER — assemble evidence across INDEPENDENT source types and judge agreement:
- Source types: ROSTER (official team/school roster), RESULT (box scores, match results, stat lines), PRESS (news write-ups, articles), HONOR (all-conference, all-state, award lists), PROFILE (club/recruiting profile pages).
- For each signal you actually found, tag which source TYPE it came from.
- "agreement": when the SAME underlying fact appears in 2+ INDEPENDENT source types, that is corroboration — it raises trust. Count how many distinct source types corroborate the athlete's identity/level. More independent types agreeing = higher confidence (still capped at 70 for public-only).
- Be honest: if everything traces to a single source type, agreement is LOW even if the signal is loud.

Return ONLY a JSON object — no prose, no markdown fences:
{"num":"5.4","conf":42,"band":"a real college track","found":[["ROSTER","short sentence","ROSTER"],["RESULT","short sentence","RESULT"]],"missing":[["FILM","No graded film yet — the only place the invisible four show."],["INVIS","Competitiveness, mental strength, mindset, character — unread without you."]],"dossier":{"sourceTypes":["ROSTER","RESULT","HONOR"],"agreement":"strong","corroborated":"Identity and level confirmed across roster, results, and an honors list."}}
"found" = 1–4 concrete public signals you ACTUALLY found: [display-tag, short sentence, SOURCE_TYPE]. If none, found = [["NONE","Limited public signal under this name — a provisional baseline only.","NONE"]] and dossier.sourceTypes = [].
"dossier.sourceTypes" = the DISTINCT independent source types you actually drew from (subset of ROSTER/RESULT/PRESS/HONOR/PROFILE). "agreement" = "strong" (3+ types), "moderate" (2 types), "thin" (1 type), or "none".
"dossier.corroborated" = one honest sentence on what the independent sources agree on (or that they don't).
"band" is one short phrase: "a strong college track" / "a real college track" / "a developing college path" / "an early, building profile" / "building the base".`;


// --- P2: server-side auto-log a QUALIFYING read to The Record (integrity-safe) ---
// Only logs reads that clear a real corroboration bar, so the ledger fills with signal,
// not every random search. Fire-and-forget; wrapped so it can never break the user's read.
async function autoLogRead(read, q, origin) {
  try {
    if (!process.env.FC_LEDGER_TOKEN) return;            // store not configured -> skip
    if (!read || !read.num) return;                       // no number -> nothing to log
    const num = parseFloat(read.num);
    if (!isFinite(num)) return;
    const dos = read.dossier || {};
    const agree = dos.agreement || 'none';
    // QUALITY BAR: need 2+ independent source types (strong/moderate). Thin/none never auto-logs.
    if (agree !== 'strong' && agree !== 'moderate') return;
    const types = Array.isArray(dos.sourceTypes) ? dos.sourceTypes : [];
    if (types.length < 2) return;

    const entry = {
      name: q.name,
      slug: String(q.name).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 60),
      pos: q.pos || '',
      cls: q.state || '',
      read: read.num,
      prov: true,
      status: 'tracking',
      note: 'Coverage read \u00b7 ' + (q.school || 'public record') + (q.state ? ', ' + q.state : '') + '. Auto-logged on a corroborated read.',
      evidence: {
        sources: { count: types.length, types: types },
        signals: (read.found || []).map(function (x) { return Array.isArray(x) ? x[1] : String(x); }).filter(Boolean).slice(0, 5)
      },
      source: 'coverage'
    };

    await fetch(origin + '/.netlify/functions/ledger?action=log', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-fc-token': process.env.FC_LEDGER_TOKEN },
      body: JSON.stringify(entry)
    });
  } catch (e) { /* logging must never break the read */ }
}

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
    // auto-log a qualifying read to The Record (server-side, integrity-safe, non-blocking on failure)
    const proto = (event.headers && (event.headers['x-forwarded-proto'] || 'https'));
    const host = (event.headers && (event.headers['host'] || event.headers['Host'])) || '';
    if (host) { await autoLogRead(read, q, proto + '://' + host); }
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
  const VALID_TYPES = ['ROSTER','RESULT','PRESS','HONOR','PROFILE'];
  const found = Array.isArray(o.found) && o.found.length
    ? o.found.slice(0, 4).map(f => [String(f[0] || 'SIGNAL').slice(0, 12), String(f[1] || '').slice(0, 160), String(f[2] || '').toUpperCase().slice(0, 10)])
    : [['NONE', 'Limited public signal under this name — a provisional baseline only.', 'NONE']];
  // build the dossier from declared source types, intersected with what's actually defensible
  const dossierIn = (o.dossier && typeof o.dossier === 'object') ? o.dossier : {};
  let types = Array.isArray(dossierIn.sourceTypes) ? dossierIn.sourceTypes.map(t => String(t).toUpperCase()).filter(t => VALID_TYPES.indexOf(t) >= 0) : [];
  // also fold in any source types the found-signals actually carried
  found.forEach(f => { if (VALID_TYPES.indexOf(f[2]) >= 0 && types.indexOf(f[2]) < 0) types.push(f[2]); });
  types = types.slice(0, 5);
  const sc = types.length;
  const agreement = sc >= 3 ? 'strong' : sc === 2 ? 'moderate' : sc === 1 ? 'thin' : 'none';
  const dossier = {
    sourceTypes: types,
    sourceCount: sc,
    agreement: agreement,
    corroborated: String(dossierIn.corroborated || (sc >= 2 ? 'Confirmed across independent public sources.' : sc === 1 ? 'Single-source signal — corroboration still thin.' : 'No corroborating public sources found.')).slice(0, 180)
  };
  const missing = [
    ['FILM', 'No graded film yet — the only place the invisible four show.'],
    ['INVIS', 'Competitiveness, mental strength, mindset, character — unread without you.']
  ];
  return { num: num.toFixed(1), conf: conf, band: String(o.band || 'an early, building profile').slice(0, 60), found: found, missing: missing, dossier: dossier, ev: conf / 100 };
}

function resp(code, obj) {
  return { statusCode: code, headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' }, body: JSON.stringify(obj) };
}
