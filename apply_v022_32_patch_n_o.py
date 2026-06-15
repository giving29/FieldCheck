#!/usr/bin/env python3
"""
V022.32 · COMBINED PATCH N + O
═══════════════════════════════════════════════════════════════════════════

PATCH N · Stage-detection fixes from post-V022.32 smoke surfacing:
  N1 · HS / college school overrides become ABSOLUTE — drop !isLegendValidated guard
       (Patch M's hasTextHOF false-positive defeated HS override for Stokes/Hall)
  N2 · Add hasPrimeProSig text detection (multi-MVP, multi-champion, multi-AS, DPOY, etc.)
  N3 · Insert prime_pro cascade entry BEFORE early_pro fallthrough
       (Steph Curry / LeBron / Jokic now route to prime_pro cap 9.3, not early_pro cap 8.0)

PATCH O · V022.31 hard caps tightened to V4 Tenet 46 spec — every decimal counts:
       HS         6.5 → 5.4   (V4 HS#1 hard cap, Stokes/Hall = 5.3)
       D3         7.0 → 6.8   (V4 D3 Jostens ceiling)
       D2         7.0 → 6.8
       D1         7.5 → 7.4   (V4 D1 AA hard cap, Boozer/Dybantsa freshman)
       JUCO/NAIA  7.0 → 6.8
       early_pro  8.0 → 7.9   (V4 NBA rookie ceiling, Cooper Flagg / Caitlin Clark yr 2)
       prime_pro  9.3 → 9.3   (V4 active multi-MVP — Steph/Jokic/Giannis NOW)
       retired_pro 9.6 → 9.6  (V4 retired HOF — Wade/Drexler)
       legend_pro  9.7 → 9.7  (V4 Kobe/LeBron peak — Tim Duncan)
       (9.8 reserved for Magic/Bird peak. 9.9 Michael Jordan 1996. 10.0 unreachable.)
"""
import sys, shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.32-N-O.bak")
if not WORKER.exists():
    print("ERROR: worker.js not found", file=sys.stderr); sys.exit(1)
shutil.copy2(WORKER, BACKUP)
print(f"✓ Backed up to {BACKUP}")

src = WORKER.read_text()
orig_len = len(src)
applied = 0

def apply(label, old, new):
    global src, applied
    c = src.count(old)
    if c == 0:
        print(f"✗ {label} · OLD NOT FOUND", file=sys.stderr)
        print(f"  Searched for: {old[:200]}...", file=sys.stderr)
        sys.exit(2)
    if c > 1:
        print(f"✗ {label} · {c} matches (AMBIGUOUS)", file=sys.stderr); sys.exit(2)
    src = src.replace(old, new)
    applied += 1
    delta = len(new) - len(old)
    print(f"✓ {label} (Δ {'+' if delta>=0 else ''}{delta})")


# ═══════════════════════════════════════════════════════════════════════════
# PATCH N1 · Drop !isLegendValidated guards from school overrides
# ═══════════════════════════════════════════════════════════════════════════
PATCH_N1_OLD = """      // V022.31 · PATCH H · HS school override takes precedence over text signals
      // (unless legend_pro is validated with HOF + structured accolades - then the player is
      // actually a returning HOF coach speaking at HS, which is fine to flag as legend)
      if (_v22_31_isHSSchool && !isLegendValidated) {
        stage = 'prep_amateur';
        stageSignals.push('v022.31_hs_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.31 · PATCH L2 · COLLEGE school override · prevents Cameron-Boozer-style cascade where
      // college freshman gets pro tier because text mentions NBA projections
      else if (_v22_31_isCollegeSchool && !isLegendValidated) {
        stage = 'college_amateur';
        stageSignals.push('v022.31_college_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }"""

PATCH_N1_NEW = """      // V022.31 · PATCH H + V022.32 · PATCH N1 · HS school override is ABSOLUTE.
      // Dropped !isLegendValidated guard — Patch M's hasTextHOF false-positively trips on
      // scout-report HOFer-comparisons ("future HOFer conversations"), defeating the HS override
      // for Tyran Stokes / Saniyah Hall. A school-confirmed HS player IS prep_amateur regardless
      // of what HOFer mentions appear in their scout text.
      if (_v22_31_isHSSchool) {
        stage = 'prep_amateur';
        stageSignals.push('v022.31_hs_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.31 · PATCH L2 + V022.32 · PATCH N1 · COLLEGE school override is ABSOLUTE.
      else if (_v22_31_isCollegeSchool) {
        stage = 'college_amateur';
        stageSignals.push('v022.31_college_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }"""

apply("PATCH_N1_drop_legend_guard_from_school_overrides", PATCH_N1_OLD, PATCH_N1_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH N2 · Add hasPrimeProSig text-pattern detection
# ═══════════════════════════════════════════════════════════════════════════
PATCH_N2_OLD = """      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

PATCH_N2_NEW = """      // V022.32 · PATCH N2 · prime_pro detection — active multi-MVP / multi-champion players
      // who would otherwise fall into isProSig && isCollegeSig "early_pro" bucket because
      // they have college mentions in their bio. Steph Curry (2x MVP, 4x champ), LeBron (4x MVP),
      // Jokic (3x MVP), Giannis (2x MVP), Embiid (MVP), etc. all need prime_pro routing.
      const hasPrimeProSig = /\\b(2[ -]?time mvp|2x mvp|two[ -]?time mvp|three[ -]?time mvp|3[ -]?time mvp|3x mvp|four[ -]?time mvp|4x mvp|five[ -]?time mvp|5x mvp|2[ -]?time (?:nba |wnba |nfl )?champion|2x (?:nba |wnba |nfl )?champion|three[ -]?time (?:nba |wnba |nfl )?champion|3[ -]?time (?:nba |wnba |nfl )?champion|3x (?:nba |wnba |nfl )?champion|four[ -]?time (?:nba |wnba |nfl )?champion|4x (?:nba |wnba |nfl )?champion|five[ -]?time (?:nba |wnba |nfl )?champion|5[ -]?time (?:nba |wnba |nfl )?champion|6[ -]?time (?:nba |wnba |nfl )?champion|seven[ -]?time (?:nba |wnba |nfl )?champion|[2-9][ -]?time all[- ]star|multi[- ]time all[- ]star|all-nba first team|first[- ]team all-nba|defensive player of the year|finals mvp|kia mvp|nba mvp|wnba mvp|nfl mvp|league mvp|world series mvp|cy young|silver slugger)\\b/i.test(allText);

      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

apply("PATCH_N2_add_hasPrimeProSig_signal", PATCH_N2_OLD, PATCH_N2_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH N3 · Insert prime_pro cascade entry BEFORE early_pro fallthrough
# ═══════════════════════════════════════════════════════════════════════════
PATCH_N3_OLD = """      else if (isProSig && isCollegeSig) {
        stage = 'early_pro';
        stageSignals.push('pro+college_keyword');
      }"""

PATCH_N3_NEW = """      // V022.32 · PATCH N3 · disambiguate: if active multi-MVP/champion signals present,
      // route to prime_pro (cap 9.3) instead of early_pro (cap 7.9). Steph/LeBron/Jokic/Giannis
      // get the right stage; rookies still go to early_pro.
      else if (isProSig && isCollegeSig && hasPrimeProSig) {
        stage = 'prime_pro';
        stageSignals.push('prime_pro+college_keyword+multi_mvp_or_champ');
      }
      else if (isProSig && isCollegeSig) {
        stage = 'early_pro';
        stageSignals.push('pro+college_keyword');
      }"""

apply("PATCH_N3_prime_pro_cascade_entry", PATCH_N3_OLD, PATCH_N3_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH O · Tighten V022.31 hard caps to V4 Tenet 46 spec
# ═══════════════════════════════════════════════════════════════════════════
PATCH_O_OLD = """      const _v22_31_tier = String(((_v22_31_enc || {}).position_pool_benchmark || {}).tier || 'unknown').toLowerCase();
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
      }"""

PATCH_O_NEW = """      const _v22_31_tier = String(((_v22_31_enc || {}).position_pool_benchmark || {}).tier || 'unknown').toLowerCase();
      const _v22_31_stage = String(((((_v22_31_enc || {}).facts || {}).identity || {}).career_stage) || 'unknown').toLowerCase();
      // V022.32 · PATCH O · TIGHTENED TO V4 TENET 46 SPEC · every decimal sacred.
      //   9.9 = Michael Jordan 1996 only · 9.8 = Magic/Bird peak · 9.7 = Kobe/LeBron peak
      //   9.6 = retired HOF (Wade/Drexler) · 9.3 = active multi-MVP cap (Steph/Jokic NOW)
      //   7.9 = NBA rookie ceiling (Flagg/Caitlin yr 2) · 7.4 = D1 AA hard cap (Boozer)
      //   6.8 = D2/D3/JUCO/NAIA ceiling · 5.4 = HS#1 hard cap (Stokes/Hall)
      let _v22_31_cap = 10.0;
      if (_v22_31_tier === 'hs') _v22_31_cap = 5.4;
      else if (_v22_31_tier === 'd3') _v22_31_cap = 6.8;
      else if (_v22_31_tier === 'd2') _v22_31_cap = 6.8;
      else if (_v22_31_tier === 'd1') _v22_31_cap = 7.4;
      else if (_v22_31_tier === 'juco' || _v22_31_tier === 'naia') _v22_31_cap = 6.8;
      else if (_v22_31_tier === 'pro') {
        if (_v22_31_stage === 'legend_pro') _v22_31_cap = 9.7;
        else if (_v22_31_stage === 'prime_pro') _v22_31_cap = 9.3;
        else if (_v22_31_stage === 'retired_pro') _v22_31_cap = 9.6;
        else _v22_31_cap = 7.9;
      }"""

apply("PATCH_O_tighten_caps_to_V4_spec", PATCH_O_OLD, PATCH_O_NEW)


# ═══════════════════════════════════════════════════════════════════════════
WORKER.write_text(src)
print(f"\n✓ Patch N+O applied · {applied} patches · {orig_len:,} → {len(src):,} chars (Δ +{len(src)-orig_len:,})")
print("""
Next:
  node --check worker.js && ./fc-deploy-dev.sh

Then re-smoke (cache already nuked from V022.32 ship). Expected post-N+O:

  Tyran Stokes      tier=hs   stage=prep_amateur    composite ≤ 5.4   ★ V4 HS#1 cap
  Saniyah Hall      tier=hs   stage=prep_amateur    composite ≤ 5.4   ★ V4 HS#1 cap
  Cameron Boozer    tier=d1   stage=college_amateur composite ≤ 7.4   ★ V4 D1 AA cap
  Cooper Flagg      tier=pro  stage=early_pro       composite ≤ 7.9   ★ V4 rookie ceiling
  Tim Duncan        tier=pro  stage=legend_pro      composite = 9.7   ★ Kobe/LeBron tier
  Stephen Curry     tier=pro  stage=prime_pro       composite ≤ 9.3   ★ active multi-MVP cap

Every decimal counts. V4 enforced.
""")
