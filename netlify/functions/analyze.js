// netlify/functions/analyze.js
// FieldCheck Highlight Agent — live vision pipeline.
// Receives sampled frames per clip + athlete grade context, asks Claude to
// score the most compelling moments (biased to the invisible four), returns
// the exact moment shape the Studio UI renders. Key stays server-side.

const MODEL = 'claude-sonnet-4-6'; // swap to claude-opus-4-8 for max read quality, claude-haiku-4-5 for speed/cost

const SYS = `You are the FieldCheck Highlight Agent — an AI that watches an athlete's raw film and finds the moments that build the most honest, compelling case for them.

You are given sampled key-frames from several clips plus the athlete's FieldCheck grade (8 facets, each 0–10). The four INVISIBLE facets — Competitiveness, Mental Strength, Mindset, Character — are FieldCheck's edge: the traits no normal highlight reel captures. Deliberately surface moments that show those, not just the obvious kills/blocks/buckets.

For each compelling moment you can read in the frames, output one entry. Rules:
- Ground every read in what is actually visible (body language, effort, positioning, reaction, teammates, score situation). If frames are ambiguous, infer conservatively and lower confidence.
- Bias toward the invisible four — aim for at least half the moments to be invisible-facet reads.
- Captions are HONEST and specific, never hype. 6–12 words. Lowercase, like a scout's note. e.g. "resets fast after the error, swings clean".
- Tie each moment to exactly one facet from the athlete's label list.
- conf is 0–1 (your read confidence given still frames).

Return ONLY a JSON array, no prose, no markdown fences:
[{"clip":<int clip index>,"facet":"<one label>","fidx":<0-7 index>,"caption":"<honest note>","ts":"<m:ss>","conf":<0..1>}]
6–8 entries total. If you cannot read a clip, skip it.`;

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
  if (!process.env.ANTHROPIC_API_KEY) return resp(200, { moments: null, reason: 'no_key' });

  let body;
  try { body = JSON.parse(event.body || '{}'); } catch (e) { return resp(400, { error: 'bad json' }); }
  const athlete = body.athlete || {};
  const clips = Array.isArray(body.clips) ? body.clips.slice(0, 6) : [];
  if (!clips.length) return resp(200, { moments: null, reason: 'no_clips' });

  const labels = athlete.labels || [];
  const facets = athlete.facets || [];
  const invis = athlete.invis || [0, 4, 5, 7];

  // build the message: context text + frames grouped by clip
  const content = [];
  let ctx = `Athlete: ${athlete.name || 'unknown'} · ${athlete.sport || ''} ${athlete.pos || ''}\n`;
  ctx += `FieldCheck facets (index: label = grade):\n`;
  labels.forEach((l, i) => { ctx += `  ${i}: ${l} = ${(facets[i] != null ? facets[i] : '?')}${invis.indexOf(i) >= 0 ? '  [INVISIBLE]' : ''}\n`; });
  ctx += `\nClips and their sampled frames follow. Read them and return the moments JSON.`;
  content.push({ type: 'text', text: ctx });

  clips.forEach((c, ci) => {
    content.push({ type: 'text', text: `\n— Clip ${ci}: "${(c.name || 'clip').slice(0, 60)}" (~${Math.round(c.dur || 0)}s) —` });
    (c.frames || []).slice(0, 4).forEach((f) => {
      const data = String(f).replace(/^data:image\/\w+;base64,/, '');
      if (data) content.push({ type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data } });
    });
  });

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({ model: MODEL, max_tokens: 1500, system: SYS, messages: [{ role: 'user', content }] })
    });
    if (!r.ok) { const t = await r.text(); return resp(200, { moments: null, reason: 'api_' + r.status, detail: t.slice(0, 300) }); }
    const data = await r.json();
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n');
    const moments = parseMoments(text, labels);
    return resp(200, { moments: moments, model: MODEL });
  } catch (e) {
    return resp(200, { moments: null, reason: 'fetch_error', detail: String(e).slice(0, 200) });
  }
};

function parseMoments(text, labels) {
  let s = (text || '').trim().replace(/^```(json)?/i, '').replace(/```$/, '').trim();
  const a = s.indexOf('['), b = s.lastIndexOf(']');
  if (a >= 0 && b > a) s = s.slice(a, b + 1);
  let arr;
  try { arr = JSON.parse(s); } catch (e) { return null; }
  if (!Array.isArray(arr)) return null;
  return arr.map(m => {
    let fidx = Number(m.fidx);
    if (!(fidx >= 0 && fidx <= 7)) { const i = labels.indexOf(m.facet); fidx = i >= 0 ? i : 0; }
    return {
      clip: Number(m.clip) || 0,
      facet: m.facet || labels[fidx] || 'Read',
      fidx: fidx,
      caption: String(m.caption || '').slice(0, 120),
      ts: m.ts || '0:00',
      conf: Math.max(0.5, Math.min(0.99, Number(m.conf) || 0.8))
    };
  }).filter(m => m.caption);
}

function resp(code, obj) {
  return { statusCode: code, headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' }, body: JSON.stringify(obj) };
}
