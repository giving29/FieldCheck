#!/usr/bin/env python3
"""
V022.31 · PATCH K · expose composite at top-level of /verdict/player response

Bug: result.encyclopedia.eval_grid.composite = 9.7 (correctly computed)
     BUT result.composite is never set, so top-level response has no composite.

Fix: After all eval_grid + curated_profile + pathway_floor mutations, before the
     function returns, copy eval_grid.composite (or synthesis.canonical_facets_8 avg
     as fallback) to result.composite WITH the V022.31 tier-based stabilization cap.
"""
import sys
import shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.31-K.bak")

if not WORKER.exists():
    print(f"ERROR: {WORKER} not found", file=sys.stderr)
    sys.exit(1)

shutil.copy2(WORKER, BACKUP)
print(f"✓ Backed up to {BACKUP}")

src = WORKER.read_text()
orig_len = len(src)

# The unique anchor: the adapter_shadow catch block + the return result
# This is unique near line 11212 because of the specific error string
PATCH_K_OLD = """    result.adapter_shadow = { error: String(e && e.message ? e.message : e).slice(0, 200) };
  }
  return result;"""

PATCH_K_NEW = """    result.adapter_shadow = { error: String(e && e.message ? e.message : e).slice(0, 200) };
  }

  // ═══════════════════════════════════════════════════════════════════
  // V022.31 · PATCH K · expose composite at top-level + tier-based stabilization cap
  // ═══════════════════════════════════════════════════════════════════
  // Bug from V022.30: result.encyclopedia.eval_grid.composite was computed correctly
  // but result.composite (top-level) was never set. Brutal_honest had facet scores
  // but the response top-level had no composite for UI/clients to consume.
  // Fix: copy eval_grid.composite up, fall back to synthesis facet average, then apply
  // V022.31 tier-based hard cap (HS<=6.5, D1<=7.5, pro_rookie<=8.0, etc.) until V022.32
  // calibration properly recalibrates Haiku source-side.
  try {
    let _v22_31_raw = null;
    const _v22_31_enc = result.encyclopedia || {};
    if (_v22_31_enc.eval_grid && typeof _v22_31_enc.eval_grid.composite === 'number') {
      _v22_31_raw = _v22_31_enc.eval_grid.composite;
    } else if (_v22_31_enc.synthesis && typeof _v22_31_enc.synthesis.overall_score === 'number') {
      _v22_31_raw = _v22_31_enc.synthesis.overall_score;
    } else if (_v22_31_enc.synthesis && _v22_31_enc.synthesis.canonical_facets_8) {
      // Compute from 8 facets directly as ultimate fallback
      const _v22_31_facets = _v22_31_enc.synthesis.canonical_facets_8;
      const _v22_31_scores = Object.values(_v22_31_facets)
        .map(f => (f && typeof f.score === 'number') ? f.score : null)
        .filter(s => s !== null);
      if (_v22_31_scores.length >= 4) {
        _v22_31_raw = _v22_31_scores.reduce((a, b) => a + b, 0) / _v22_31_scores.length;
      }
    }

    if (_v22_31_raw !== null) {
      const _v22_31_tier = String(((_v22_31_enc || {}).position_pool_benchmark || {}).tier || 'unknown').toLowerCase();
      const _v22_31_stage = String(((((_v22_31_enc || {}).facts || {}).identity || {}).career_stage) || 'unknown').toLowerCase();
      let _v22_31_cap = 10.0;
      if (_v22_31_tier === 'hs') _v22_31_cap = 6.5;
      else if (_v22_31_tier === 'd3') _v22_31_cap = 7.0;
      else if (_v22_31_tier === 'd2') _v22_31_cap = 7.0;
      else if (_v22_31_tier === 'd1') _v22_31_cap = 7.5;
      else if (_v22_31_tier === 'juco' || _v22_31_tier === 'naia') _v22_31_cap = 7.0;
      else if (_v22_31_tier === 'pro') {
        if (_v22_31_stage === 'legend_pro') _v22_31_cap = 9.7;
        else if (_v22_31_stage === 'prime_pro') _v22_31_cap = 9.3;
        else if (_v22_31_stage === 'retired_pro') _v22_31_cap = 9.6;
        else _v22_31_cap = 8.0;
      }
      const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);
      result.composite = Math.round(_v22_31_capped * 10) / 10;
      result.composite_v022_31 = {
        raw: Math.round(_v22_31_raw * 100) / 100,
        cap: _v22_31_cap,
        tier: _v22_31_tier,
        stage: _v22_31_stage,
        cap_applied: _v22_31_raw > _v22_31_cap,
        source: (_v22_31_enc.eval_grid && typeof _v22_31_enc.eval_grid.composite === 'number') ? 'eval_grid.composite'
              : (_v22_31_enc.synthesis && typeof _v22_31_enc.synthesis.overall_score === 'number') ? 'synthesis.overall_score'
              : 'canonical_facets_8_average'
      };
    } else {
      result.composite = null;
      result.composite_v022_31 = { raw: null, reason: 'no_composite_source_available' };
    }
  } catch (_v22_31_e) {
    result.composite_v022_31 = { error: String(_v22_31_e && _v22_31_e.message || _v22_31_e).slice(0, 200) };
  }

  return result;"""

count = src.count(PATCH_K_OLD)
if count == 0:
    print("✗ PATCH K · OLD STRING NOT FOUND in worker.js", file=sys.stderr)
    print(f"   Tried to find:\n   {PATCH_K_OLD[:150]}...", file=sys.stderr)
    sys.exit(2)
if count > 1:
    print(f"✗ PATCH K · OLD STRING MATCHES {count} TIMES (ambiguous)", file=sys.stderr)
    sys.exit(2)

src = src.replace(PATCH_K_OLD, PATCH_K_NEW)
delta = len(PATCH_K_NEW) - len(PATCH_K_OLD)
print(f"✓ PATCH K applied · Δ +{delta} chars")

WORKER.write_text(src)
print(f"\n✓ worker.js · {orig_len:,} → {len(src):,} chars")
print(f"\nNext steps:")
print(f"  node --check worker.js")
print(f"  ./fc-deploy-dev.sh")
print(f"")
print(f"Then smoke test Tim Duncan again — composite should show 9.3 (prime_pro cap) or 9.7 (legend_pro cap)")
