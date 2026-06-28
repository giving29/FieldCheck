// netlify/functions/discovery.js
// The Discovery agent — live. Claude parses a coach's natural-language ask AND
// reads the public record (web search) to surface real candidates, each with a
// PROVISIONAL read. Same shape discovery.html renders. Honesty + safety firewall
// enforced in the system prompt AND numerically. Rate-limited (shared budget).

const MODEL = 'claude-sonnet-4-6';

const { checkAndCount, clientIp } = require('./_ratelimit');

const SYS = `You are the FieldCheck Discovery agent, used by college coaches. Given a natural-language recruiting ask, you (1) parse the intent and (2) use web search to surface REAL athletes from the PUBLIC record who fit, each with a PROVISIONAL read.

THE HONESTY + SAFETY FIREWALL — non-negotiable:
- PROVISIONAL reads only, never grades. Built from public signal.
- Use ONLY public athletic-performance information (rosters, results, write-ups, honor lists, club/HS pages). NEVER include or infer contact details, home address, social handles, or any way to reach an athlete directly. Many are minors — this is a hard rule.
- Surface REAL athletes only when the public record actually supports them. If the ask is too broad or the public record is thin, return FEWER (or zero) candidates rather than inventing names. NEVER fabricate athletes, stats, schools, or achievements.
- Each provisional number is 0–10, centered conservatively (public signal rarely justifies above ~6.5). Range 3.2–6.8.
- "Rank the overlooked": prefer athletes a recruiting service might miss, consistent with the ask.
- Do NOT rank by fame. A well-known name is not automatically a high read.

Work FAST and efficiently: use at most 2 web searches total, then answer. Prefer returning 2–4 well-grounded candidates quickly over an exhaustive list.

First, parse the ask into: position (e.g. OH/S/MB/L/OPP), region/state, class year, minimum read, and trait priorities (e.g. "invisible-four" if they mention character/competitiveness/mental/mindset/undervalued/overlooked; "D1-projection" if they mention D1/power/high-major).

Then return ONLY a JSON object — no prose, no markdown fences:
{"ask":{"pos":"OH","region":"Texas","cls":"2026","minGrade":6.0,"traits":["invisible-four"]},"candidates":[{"name":"First Last","pos":"OH","cls":"2026","school":"School, ST","num":"6.1","facet":"competitiveness","facetVal":"7.2","srcCount":3,"srcTypes":["ROSTER","RESULT","HONOR"]}]}
- ask fields: use null for anything not specified. traits is an array (may be empty).
- candidates: 0–4 real athletes, each with pos, cls, school (City/School + state), num (provisional, string), facet (their standout, lowercase), facetVal (string 0–10). Order by honest read, strongest first.
- If you cannot confirm a real FULL NAME for a candidate, OMIT that candidate entirely. Never put a description, position, school, or placeholder in the name field — a name is a real person's first and last name or nothing.
- For EACH candidate, from the sources you already saw while finding them, report srcCount = how many DISTINCT independent source types corroborate that athlete's identity/level (ROSTER, RESULT, PRESS, HONOR, PROFILE), and srcTypes = that list. Do NOT run extra searches for this — only count what you already encountered. If a candidate rests on a single source, srcCount = 1 (be honest).
- If the public record cannot support real candidates, return "candidates": [].`;


// --- P2: server-side auto-log QUALIFYING Discovery candidates to The Record ---
// Loops candidates, logs each that clears the corroboration bar (2+ source types).
// Same integrity model as Coverage: token-gated, deduped, non-blocking on failure.
async function autoLogCandidates(result, origin) {
  try {
    if (!process.env.FC_LEDGER_TOKEN) return;
    if (!result || !Array.isArray(result.candidates)) return;
    for (var i = 0; i < result.candidates.length; i++) {
      var c = result.candidates[i];
      try {
        if (!c || !c.name || !c.num) continue;
        var num = parseFloat(c.num);
        if (!isFinite(num)) continue;
        var src = c.sources || {};
        var agree = src.agreement || 'none';
        if (agree !== 'strong' && agree !== 'moderate') continue;   // QUALITY BAR
        var types = Array.isArray(src.types) ? src.types : [];
        if (types.length < 2) continue;

        var entry = {
          name: c.name,
          slug: String(c.name).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 60),
          pos: c.pos || '',
          cls: c.cls || '',
          read: c.num,
          prov: true,
          status: 'tracking',
          note: 'Discovery read \u00b7 ' + (c.school || 'public record') + '. Surfaced by fit, corroborated across sources.',
          evidence: {
            sources: { count: types.length, types: types },
            signals: [c.facet ? ('Standout: ' + c.facet + (c.facetVal ? ' (' + c.facetVal + ')' : '')) : null,
                      'Surfaced by coach search on fit'].filter(Boolean)
          },
          source: 'discovery'
        };

        await fetch(origin + '/.netlify/functions/ledger?action=log', {
          method: 'POST',
          headers: { 'content-type': 'application/json', 'x-fc-token': process.env.FC_LEDGER_TOKEN },
          body: JSON.stringify(entry)
        });
      } catch (inner) { /* one bad candidate never blocks the rest or the response */ }
    }
  } catch (e) { /* logging must never break the search */ }
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
  if (!process.env.ANTHROPIC_API_KEY) return resp(200, { result: null, reason: 'no_key' });

  let body;
  try { body = JSON.parse(event.body || '{}'); } catch (e) { return resp(400, { error: 'bad json' }); }
  const query = (body.query || '').toString().slice(0, 400);
  if (!query.trim()) return resp(200, { result: null, reason: 'no_query' });

  // cost guard: per-IP throttle + global daily cap (UI falls back to local mock on 429)
  const gate = await checkAndCount(clientIp(event));
  if (!gate.ok) return resp(200, { result: null, reason: gate.reason });

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
        max_tokens: 900,
        system: SYS,
        tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 1 }],
        messages: [{ role: 'user', content: 'Recruiting ask: ' + query }]
      })
    });
    if (!r.ok) { const t = await r.text(); return resp(200, { result: null, reason: 'api_' + r.status, detail: t.slice(0, 300) }); }
    const data = await r.json();
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n');
    const result = parseResult(text);
    // auto-log qualifying candidates to The Record (server-side, integrity-safe, non-blocking)
    const proto = (event.headers && (event.headers['x-forwarded-proto'] || 'https'));
    const host = (event.headers && (event.headers['host'] || event.headers['Host'])) || '';
    if (host) { await autoLogCandidates(result, proto + '://' + host); }
    return resp(200, { result: result, model: MODEL });
  } catch (e) {
    return resp(200, { result: null, reason: 'fetch_error', detail: String(e).slice(0, 200) });
  }
};

function buildSources(c) {
  var VALID = ['ROSTER','RESULT','PRESS','HONOR','PROFILE'];
  var types = Array.isArray(c.srcTypes) ? c.srcTypes.map(function(t){return String(t).toUpperCase();}).filter(function(t){return VALID.indexOf(t)>=0;}) : [];
  var n = types.length || Math.max(0, Math.min(5, parseInt(c.srcCount, 10) || 0));
  if (types.length) n = types.length;
  var agreement = n >= 3 ? 'strong' : n === 2 ? 'moderate' : n === 1 ? 'thin' : 'none';
  return { count: n, agreement: agreement, types: types.slice(0, 5) };
}
function clampNum(v, lo, hi, dflt) {
  let n = parseFloat(v);
  if (!(n >= 0 && n <= 10)) n = dflt;
  return Math.max(lo, Math.min(hi, n));
}

function parseResult(text) {
  let s = (text || '').trim().replace(/^```(json)?/i, '').replace(/```$/, '').trim();
  const a = s.indexOf('{'), b = s.lastIndexOf('}');
  if (a >= 0 && b > a) s = s.slice(a, b + 1);
  let o;
  try { o = JSON.parse(s); } catch (e) { return null; }

  const ask = o.ask && typeof o.ask === 'object' ? o.ask : {};
  const cleanAsk = {
    pos: ask.pos || null,
    region: ask.region || null,
    cls: ask.cls ? String(ask.cls) : null,
    minGrade: (ask.minGrade >= 0 && ask.minGrade <= 10) ? ask.minGrade : null,
    traits: Array.isArray(ask.traits) ? ask.traits.slice(0, 4) : []
  };

  const cands = (Array.isArray(o.candidates) ? o.candidates : []).slice(0, 6).map(c => ({
    name: String(c.name || '').slice(0, 60),
    pos: String(c.pos || cleanAsk.pos || '').slice(0, 8),
    cls: c.cls ? String(c.cls).slice(0, 6) : (cleanAsk.cls || ''),
    school: String(c.school || '').slice(0, 80),
    num: clampNum(c.num, 3.2, 6.8, 4.8).toFixed(1),   // provisional, capped conservative
    facet: String(c.facet || 'competitiveness').toLowerCase().slice(0, 32),
    facetVal: clampNum(c.facetVal, 3.0, 8.0, 6.5).toFixed(1),
    sources: buildSources(c),
    provisional: true
  })).filter(c => {
    var n = c.name || '';
    if (!n) return false;
    // must look like a real person's name: two+ capitalized words, no placeholder tells
    if (/\b(at|HS|high school|\/|unknown|unconfirmed|various|TBD|outside hitter|setter|libero|middle|opposite)\b/i.test(n)) return false;
    var words = n.trim().split(/\s+/);
    if (words.length < 2) return false;
    if (!/^[A-Z]/.test(words[0]) || !/^[A-Z]/.test(words[words.length-1])) return false;
    return true;
  });

  return { ask: cleanAsk, candidates: cands };
}

function resp(code, obj) {
  return { statusCode: code, headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' }, body: JSON.stringify(obj) };
}
