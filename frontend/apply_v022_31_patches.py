#!/usr/bin/env python3
"""
V022.31 STABILIZATION patches applied to worker.js
─────────────────────────────────────────────────────────────────────────────
Fixes the 4 bugs surfaced by V022.30 110-battery:

  Bug 1 (composite=null for all 110) → PATCH G + I
    • G: response-time composite resolution looks in the right path
    • I: tier-based hard cap (HS<=6.5, D1<=7.5, pro_rookie<=8.0, etc.)
         until V022.32 calibration recalibrates Haiku source

  Bug 2 (career_stage HS→retired_pro/prime_pro) → PATCH H
    • HS school override: if current_school matches HS pattern, force
      prep_amateur regardless of stray text mentions
    • Tightened retired_sig regex: requires explicit pro-context

  Bug 3 (percentile near-constant 97/57/85) → addressed by PATCH I
    Once composite is capped per tier, percentile downstream will follow

  Bug 4 (bbref_pro 92% 429-rate-limited) → PATCH J
    • KV cache wrapper, 24h on success, 1h on 429 (no retry storm)

Plus: VERSION_BUMP (V022.30 → V022.31) and CACHE_VERSION_BUMP for synthesis
"""
import sys
import shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.31.bak")

if not WORKER.exists():
    print(f"ERROR: {WORKER} not found in current directory", file=sys.stderr)
    print(f"Run this from ~/Desktop/fieldcheck-proxy/", file=sys.stderr)
    sys.exit(1)

shutil.copy2(WORKER, BACKUP)
print(f"✓ Backed up to {BACKUP} ({BACKUP.stat().st_size:,} bytes)")

src = WORKER.read_text()
orig_len = len(src)
patches_applied = 0

def apply(label, old, new):
    global src, patches_applied
    count = src.count(old)
    if count == 0:
        print(f"✗ {label} · OLD STRING NOT FOUND in worker.js", file=sys.stderr)
        print(f"   First 200 chars of OLD:\n   {old[:200]}", file=sys.stderr)
        sys.exit(2)
    if count > 1:
        print(f"✗ {label} · OLD STRING MATCHES {count} TIMES (ambiguous)", file=sys.stderr)
        sys.exit(2)
    src = src.replace(old, new)
    patches_applied += 1
    delta = len(new) - len(old)
    print(f"✓ {label} (Δ {'+' if delta >= 0 else ''}{delta} chars)")

# ═══════════════════════════════════════════════════════════════════
# VERSION BUMP · V022.30 → V022.31
# ═══════════════════════════════════════════════════════════════════
apply("VERSION_BUMP",
    "// FIELDCHECK_WORKER_VERSION = V022.30 · ARCHITECTURAL FIX",
    "// FIELDCHECK_WORKER_VERSION = V022.31 · STABILIZATION · 4-PATCH BUNDLE · composite exposure + career_stage HS override + tier-cap + bbref KV cache · base V022.30 sha=b643099b · ships BEFORE V022.32 calibration (Tenet 46 V4)\n// FIELDCHECK_WORKER_VERSION_HISTORICAL = V022.30 · ARCHITECTURAL FIX")

# ═══════════════════════════════════════════════════════════════════
# PATCH G + I · composite top-level exposure + tier-based hard cap
# Bug: response composite reads verdictResult.eval_grid.composite which
# doesn't exist (real path is verdictResult.encyclopedia.eval_grid.composite)
# Also: synthesis.overall_score IS computed but never surfaced at top level
# Cap: until V022.32 recalibrates Haiku source, clamp by tier+stage
# ═══════════════════════════════════════════════════════════════════
PATCH_G_OLD = "    composite: verdictResult.composite || (verdictResult.eval_grid && verdictResult.eval_grid.composite) || null,"

PATCH_G_NEW = """    // V022.31 · PATCH G + I · composite exposure with tier-based hard cap (stabilization)
    composite: (function() {
      const _raw = verdictResult.composite
        || (verdictResult.encyclopedia && verdictResult.encyclopedia.eval_grid && verdictResult.encyclopedia.eval_grid.composite)
        || (verdictResult.encyclopedia && verdictResult.encyclopedia.synthesis && verdictResult.encyclopedia.synthesis.overall_score)
        || null;
      if (_raw === null) return null;
      const _tier = String(((verdictResult.encyclopedia || {}).position_pool_benchmark || {}).tier || 'unknown').toLowerCase();
      const _stage = String(((((verdictResult.encyclopedia || {}).facts || {}).identity || {}).career_stage) || 'unknown').toLowerCase();
      let _cap = 10.0;
      if (_tier === 'hs') _cap = 6.5;
      else if (_tier === 'd3') _cap = 7.0;
      else if (_tier === 'd2') _cap = 7.0;
      else if (_tier === 'd1') _cap = 7.5;
      else if (_tier === 'juco' || _tier === 'naia') _cap = 7.0;
      else if (_tier === 'pro') {
        if (_stage === 'legend_pro') _cap = 9.7;
        else if (_stage === 'prime_pro') _cap = 9.3;
        else if (_stage === 'retired_pro') _cap = 9.6;
        else _cap = 8.0;
      }
      const _capped = Math.min(_raw, _cap);
      return Math.round(_capped * 10) / 10;
    })(),
    composite_v022_31_stabilization_cap: true,"""

apply("PATCH_G_I_composite_expose_and_cap", PATCH_G_OLD, PATCH_G_NEW)

# ═══════════════════════════════════════════════════════════════════
# PATCH H · career_stage HS school override + tighter retired regex
# ═══════════════════════════════════════════════════════════════════
PATCH_H_OLD = """      // ── STAGE DETECTION ──
      let stage = 'unknown';
      let stageSignals = [];
      const isRetiredSig = /\\b(retired|retirement|formerly played|former professional|completed.*career|career.*concluded)\\b/i.test(allText);"""

PATCH_H_NEW = """      // ── STAGE DETECTION ──
      let stage = 'unknown';
      let stageSignals = [];

      // V022.31 · PATCH H · HS-school override · prevents stray text mentions ("his father played
      // in the NBA", "retired jersey number", "the school produced NBA players") from misclassifying
      // HS athletes. If current_school matches HS patterns AND does NOT match college, force prep_amateur.
      const _v22_31_currentSchool = String((id && id.current_school) || '').toLowerCase();
      const _v22_31_isHSSchool = /\\b(high school|hs\\b|prep school|preparatory|academy|christian school|jesuit|catholic high|charter school|sierra canyon|montverde|prolific prep|spire academy|link academy|notre dame|imm?aculate|montverd|hebron christian|hill[- ]school)\\b/i.test(_v22_31_currentSchool)
        && !/\\b(college|university|institute|state college|community college|tech college|junior college)\\b/i.test(_v22_31_currentSchool);

      // V022.31 · PATCH H · TIGHTENED retired signal — require explicit pro-context co-occurrence.
      // Old regex matched bare "retired"/"retirement" — hit on retired jersey numbers, retired coaches,
      // unrelated "completed.*career" / "career.*concluded" fragments.
      const isRetiredSig = /\\b(?:retired (?:nba|wnba|nfl|mlb|mls|professional|pro\\b)|(?:nba|wnba|nfl|mlb|mls)[^.]{0,50}(?:retirement|retired in)|formerly played (?:in|with)\\s+(?:the\\s+)?(?:nba|wnba|nfl|mlb)|(?:nba|wnba|nfl|mlb) hall of fame inductee|former (?:nba|wnba|nfl|mlb) (?:player|forward|guard|center|pitcher|quarterback)|career[- ]concluded (?:in|with))\\b/i.test(allText);"""

apply("PATCH_H_career_stage_HS_override_and_tighter_retired", PATCH_H_OLD, PATCH_H_NEW)

# ═══════════════════════════════════════════════════════════════════
# PATCH H continued · HS override IN the stage cascade
# ═══════════════════════════════════════════════════════════════════
PATCH_H2_OLD = """      // V022.30 · legend_pro requires validation now
      if (isLegendSig && isProSig && isLegendValidated) {"""

PATCH_H2_NEW = """      // V022.31 · PATCH H · HS school override takes precedence over text signals
      // (unless legend_pro is validated with HOF + structured accolades - then the player is
      // actually a returning HOF coach speaking at HS, which is fine to flag as legend)
      if (_v22_31_isHSSchool && !isLegendValidated) {
        stage = 'prep_amateur';
        stageSignals.push('v022.31_hs_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

apply("PATCH_H_HS_cascade_override", PATCH_H2_OLD, PATCH_H2_NEW)

# ═══════════════════════════════════════════════════════════════════
# PATCH J · bbref_pro KV cache wrapper · defangs Cloudflare-IP 429
# ═══════════════════════════════════════════════════════════════════
PATCH_J_OLD = """async function fetchBasketballRefPro(name, env) {
  const t0 = Date.now();
  const query = encodeURIComponent(name);
  const searchUrl = `https://www.basketball-reference.com/search/search.fcgi?search=${query}`;"""

PATCH_J_NEW = """// V022.31 · PATCH J · KV cache wrapper to defang Cloudflare-IP 429 rate-limiting from basketball-reference.com.
// Successful fetches cached 24h. 429-results cached 1h (prevents retry storm). Other errors 10min.
async function fetchBasketballRefPro(name, env) {
  const _v22_31_t0 = Date.now();
  const _v22_31_cacheKey = `bbref:v022.31:${String(name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 80)}`;
  if (env && env.FIELDCHECK_KV) {
    try {
      const _v22_31_cached = await env.FIELDCHECK_KV.get(_v22_31_cacheKey, 'json');
      if (_v22_31_cached && _v22_31_cached.cached_at) {
        return { ..._v22_31_cached, _v22_31_cache_hit: true, ms: Date.now() - _v22_31_t0 };
      }
    } catch (_v22_31_e) { /* swallow cache errors */ }
  }
  const _v22_31_result = await _fetchBasketballRefPro_uncached(name, env);
  if (env && env.FIELDCHECK_KV && _v22_31_result) {
    let _v22_31_ttl = 600;
    if (_v22_31_result.ok) _v22_31_ttl = 86400;
    else if (_v22_31_result.error && /429|rate.?limit|search_failed_4/i.test(String(_v22_31_result.error))) _v22_31_ttl = 3600;
    try {
      await env.FIELDCHECK_KV.put(_v22_31_cacheKey, JSON.stringify({ ..._v22_31_result, cached_at: new Date().toISOString() }), { expirationTtl: _v22_31_ttl });
    } catch (_v22_31_e) { /* swallow cache errors */ }
  }
  return _v22_31_result;
}

async function _fetchBasketballRefPro_uncached(name, env) {
  const t0 = Date.now();
  const query = encodeURIComponent(name);
  const searchUrl = `https://www.basketball-reference.com/search/search.fcgi?search=${query}`;"""

apply("PATCH_J_bbref_KV_cache_wrapper", PATCH_J_OLD, PATCH_J_NEW)

# ═══════════════════════════════════════════════════════════════════
# CACHE VERSION BUMP · invalidates V022.30 synthesis cache
# ═══════════════════════════════════════════════════════════════════
apply("CACHE_VERSION_BUMP_synthesis",
    "const cacheVersion = 'v022.30';",
    "const cacheVersion = 'v022.31';  // V022.31 stabilization · invalidates v022.30 synthesis cache")

# ═══════════════════════════════════════════════════════════════════
# WRITE
# ═══════════════════════════════════════════════════════════════════
WORKER.write_text(src)
delta = len(src) - orig_len
print()
print(f"✓ V022.31 STABILIZATION applied to worker.js")
print(f"  · {patches_applied} patches applied")
print(f"  · Δ {'+' if delta >= 0 else ''}{delta} chars ({orig_len:,} → {len(src):,})")
print(f"  · Backup at {BACKUP}")
print()
print("Next steps:")
print("  node --check worker.js               # validate JS syntax")
print("  ls -la worker.js                     # confirm file size grew")
print("  head -2 worker.js                    # confirm V022.31 banner")
print("  grep -c 'V022.31' worker.js          # should show 8+ hits")
print()
print("Then deploy to dev:")
print("  ./fc-deploy-dev.sh")
print()
print("After deploy, wipe v022.30 KV cache + re-run battery:")
print("  for k in synth projection prostack trajpath coachvoices audience; do")
print("    wrangler kv key delete --binding=FIELDCHECK_KV --remote \\")
print("      \"${k}:v022.30:mens-basketball:unknown\" 2>&1 | tail -1")
print("  done")
print("  ./fc-batch-test-v2.sh")
