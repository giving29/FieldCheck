// netlify/functions/ledger.js
// P2 — THE RECORD's durable store. Append-only prediction ledger backed by
// Upstash Redis REST (PURE FETCH, ZERO dependencies — deliberately no SDK, to
// avoid the bundler static-scan trap that broke @netlify/blobs three times).
//
//   GET  ?action=list   -> public read  -> { entries:[...], live:true }
//   POST ?action=log     -> TOKEN-GATED  -> appends one entry (server-side only)
//
// INTEGRITY: writes require the secret FC_LEDGER_TOKEN header, so the browser
// can never inject a fake prediction. The public can read; only the engine writes.
//
// SAFE BY DEFAULT: if Upstash env vars are absent, list returns live:false and
// log is a no-op — The Record page falls back to its static seed. Nothing breaks
// before the datastore is configured.

const RURL = process.env.UPSTASH_REDIS_REST_URL;
const RTOK = process.env.UPSTASH_REDIS_REST_TOKEN;
const WRITE_TOKEN = process.env.FC_LEDGER_TOKEN;
const KEY = 'fc:ledger:v1';
const CAP = 500;

async function redis(cmd) {
  const r = await fetch(RURL, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + RTOK, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd)
  });
  if (!r.ok) throw new Error('upstash_' + r.status);
  const j = await r.json();
  return j.result;
}

exports.handler = async (event) => {
  const action = ((event.queryStringParameters || {}).action) || 'list';

  // Not configured -> safe no-op. Page falls back to its seed.
  if (!RURL || !RTOK) {
    if (action === 'list') return resp(200, { entries: [], live: false, reason: 'not_configured' });
    return resp(200, { ok: false, live: false, reason: 'not_configured' });
  }

  try {
    if (action === 'list') {
      const raw = (await redis(['LRANGE', KEY, '0', String(CAP - 1)])) || [];
      const entries = raw.map(function (x) { try { return JSON.parse(x); } catch (e) { return null; } }).filter(Boolean);
      return resp(200, { entries: entries, live: true, count: entries.length });
    }

    if (action === 'log') {
      if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
      // TOKEN GATE — only server-side callers with the secret may write.
      const h = event.headers || {};
      const tok = h['x-fc-token'] || h['X-Fc-Token'] || h['x-fc-token'.toUpperCase()];
      if (!WRITE_TOKEN || tok !== WRITE_TOKEN) return resp(403, { error: 'forbidden' });

      let e;
      try { e = JSON.parse(event.body || '{}'); } catch (err) { return resp(400, { error: 'bad_json' }); }
      if (!e.name || !e.read) return resp(400, { error: 'missing_fields' });

      const today = new Date().toISOString().slice(0, 10);
      // same-day dedup: don't double-log the same athlete on the same day (refresh spam guard)
      const recent = (await redis(['LRANGE', KEY, '0', '49'])) || [];
      const dupe = recent.some(function (x) {
        try { const o = JSON.parse(x); return o.slug === e.slug && o.date === today; } catch (_) { return false; }
      });
      if (dupe) return resp(200, { ok: true, deduped: true });

      // normalize the stored entry (append-only — never edited after this)
      const entry = {
        name: String(e.name).slice(0, 60),
        slug: String(e.slug || e.name).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 60),
        pos: String(e.pos || '').slice(0, 10),
        cls: String(e.cls || '').slice(0, 8),
        read: String(e.read).slice(0, 5),
        prov: e.prov !== false,
        status: ['tracking', 'reference', 'confirmed'].indexOf(e.status) >= 0 ? e.status : 'tracking',
        date: today,
        note: String(e.note || '').slice(0, 200),
        evidence: e.evidence && typeof e.evidence === 'object' ? e.evidence : null,
        outcome: null,
        source: String(e.source || 'engine').slice(0, 24)
      };

      await redis(['LPUSH', KEY, JSON.stringify(entry)]);
      await redis(['LTRIM', KEY, '0', String(CAP - 1)]);
      return resp(200, { ok: true, logged: true });
    }

    return resp(400, { error: 'unknown_action' });
  } catch (err) {
    // never hard-fail — page falls back to seed
    if (action === 'list') return resp(200, { entries: [], live: false, error: String(err).slice(0, 120) });
    return resp(200, { ok: false, error: String(err).slice(0, 120) });
  }
};

function resp(code, obj) {
  return {
    statusCode: code,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store', 'access-control-allow-origin': '*' },
    body: JSON.stringify(obj)
  };
}
