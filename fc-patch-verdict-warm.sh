#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"

[ -f worker.js ] || { echo "ABORT :: worker.js not found"; exit 1; }
[ -f wrangler.toml ] || { echo "ABORT :: wrangler.toml not found"; exit 1; }

if grep -q "async function warmVerdictCache" worker.js; then
  echo "Already patched — warmVerdictCache present. Nothing to do."
  exit 0
fi

cp worker.js "worker.js.bak.$(date +%Y%m%d_%H%M)"
cp wrangler.toml "wrangler.toml.bak.$(date +%Y%m%d_%H%M)"
echo "backed up worker.js + wrangler.toml"

python3 - <<'PY'
w = open("worker.js").read()

# 1) warmVerdictCache function (inserted before the global json() helper)
fn = r'''// --- VERDICT CACHE WARM - keeps marquee verdicts hot off the user path -------
// Walks PLAYER_PROFILES in cursor-batched slices. Regenerates verdicts that are
// missing or older than the refresh threshold and stores them under the SAME key
// the /verdict/player read path uses. Pure background; cost-guarded; idempotent.
async function warmVerdictCache(env, opts) {
  opts = opts || {};
  const sliceSize = opts.sliceSize || 8;
  const ttl = opts.ttlSeconds || 432000;                        // 120h
  const refreshAfterMs = (opts.refreshAfterHours || 72) * 3600000;
  if (!env.FIELDCHECK_KV) return { error: 'no_kv' };
  if (typeof PLAYER_PROFILES !== 'object' || !PLAYER_PROFILES) return { error: 'no_profiles' };
  const slugs = Object.keys(PLAYER_PROFILES);
  let offset = 0;
  try { const c = await env.FIELDCHECK_KV.get('verdict_warm:cursor', 'json'); if (c && typeof c.next === 'number') offset = c.next; } catch (_) {}
  if (offset >= slugs.length) offset = 0;
  const slice = slugs.slice(offset, offset + sliceSize);
  let warmed = 0, skipped_fresh = 0, skipped_bad = 0, errors = 0;
  for (const slug of slice) {
    try {
      const p = PLAYER_PROFILES[slug] || {};
      const name = p.name || '';
      const sport = p.sport || '';
      if (!name || !sport) { skipped_bad++; continue; }
      // SAME key the read path builds, with empty schoolHint (how the home path calls it)
      const cacheKey = 'verdict:player:v10:' + (sport || 'unknown') + ':' +
        name.toLowerCase().replace(/[^\w]/g, '') + ':';
      let cached = null;
      try { cached = await env.FIELDCHECK_KV.get(cacheKey, 'json'); } catch (_) {}
      if (cached && cached.generated_at && (Date.now() - cached.generated_at) < refreshAfterMs) { skipped_fresh++; continue; }
      const result = await handlePlayerVerdict(env, { name: name, sport: sport });
      if (result && !result.error) {
        result.generated_at = Date.now();
        result._warmed = true;
        await env.FIELDCHECK_KV.put(cacheKey, JSON.stringify(result), { expirationTtl: ttl });
        warmed++;
      } else { errors++; }
    } catch (_) { errors++; }
  }
  const next = (offset + sliceSize) >= slugs.length ? 0 : offset + sliceSize;
  try { await env.FIELDCHECK_KV.put('verdict_warm:cursor', JSON.stringify({ next: next, updated_at: Date.now() }), { expirationTtl: 86400 * 60 }); } catch (_) {}
  return { total: slugs.length, offset: offset, slice: slice.length, warmed: warmed, skipped_fresh: skipped_fresh, skipped_bad: skipped_bad, errors: errors, next: next };
}

function json(obj, status = 200) {'''
anchor1 = "function json(obj, status = 200) {"
assert w.count(anchor1) == 1, "json anchor not unique"
w = w.replace(anchor1, fn, 1)

# 2) cron branch in scheduled()
anchor2 = "  async scheduled(event, env, ctx) {\n    const tasks = [];"
cron = anchor2 + r'''
    if (event.cron === '0 */2 * * *') {
      // VERDICT CACHE WARM - every 2h - keeps marquee verdicts hot off the user path
      tasks.push((async () => {
        try { const r = await warmVerdictCache(env); console.log('verdict_warm:', JSON.stringify(r)); }
        catch (e) { console.log('verdict_warm error', String(e)); }
      })());
    }'''
assert w.count(anchor2) == 1, "scheduled anchor not unique"
w = w.replace(anchor2, cron, 1)

# 3) manual trigger route (for dev testing) before /clips/recompute-all
anchor3 = "      // -- WEEKLY-CRON-v1"
# fallback to the route line if the comment differs
route_anchor = "      if (path === '/clips/recompute-all'"
new_route = r'''      // -- verdict cache warm - manual trigger (dev testing / on-demand) --
      if (path === '/admin/warm-verdicts' && (request.method === 'POST' || request.method === 'GET')) {
        try {
          const n = parseInt(url.searchParams.get('slice') || '0', 10);
          const res = await warmVerdictCache(env, n > 0 ? { sliceSize: n } : {});
          return json({ ok: true, ...res });
        } catch (e) { return json({ error: 'warm_failed', detail: String(e).slice(0, 200) }, 500); }
      }
''' + route_anchor
assert w.count(route_anchor) == 1, "recompute-all route anchor not unique"
w = w.replace(route_anchor, new_route, 1)

# 4) bump verdict TTL 24h -> 120h and stamp generated_at
anchor4 = """            // Store in cache with 24h TTL
            try {
              await env.FIELDCHECK_KV.put(cacheKey, JSON.stringify(result), { expirationTtl: 86400 });"""
new4 = """            // Store in cache with 120h TTL (warm-friendly) + generated_at stamp
            try {
              result.generated_at = result.generated_at || Date.now();
              await env.FIELDCHECK_KV.put(cacheKey, JSON.stringify(result), { expirationTtl: 432000 });"""
assert w.count(anchor4) == 1, "ttl anchor not unique"
w = w.replace(anchor4, new4, 1)

open("worker.js","w").write(w)
print("worker.js patched: warmVerdictCache + cron + /admin/warm-verdicts + 120h TTL")

# 5) wrangler.toml - add warm cron to PROD triggers only
t = open("wrangler.toml").read()
ta = 'crons = ["*/30 * * * *", "0 9 * * 1"]'
tn = 'crons = ["*/30 * * * *", "0 9 * * 1", "0 */2 * * *"]'
assert t.count(ta) == 1, "wrangler prod crons anchor not unique"
t = t.replace(ta, tn, 1)
open("wrangler.toml","w").write(t)
print("wrangler.toml patched: prod warm cron 0 */2 * * * added")
PY

echo ""
echo "DONE."
