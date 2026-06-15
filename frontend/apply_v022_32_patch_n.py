#!/usr/bin/env python3
"""
V022.32 · PATCH N · fixes 2 stage-detection bugs surfaced by post-V022.32 smoke:

  N1 · Steph Curry showed stage=early_pro (cap 8.0) instead of prime_pro (cap 9.3)
       Reason: isProSig && isCollegeSig → 'early_pro' default. No discriminator for
       active multi-MVP / multi-champion players.
       Fix: Add hasPrimeProSig text-pattern check (multi-MVP, multi-champion, multi-AS).
            Insert prime_pro cascade entry BEFORE the early_pro fallthrough.

  N2 · Tyran Stokes / Saniyah Hall showed stage=unknown despite Rainier Beach HS / Montverde
       Reason: HS school override is `_v22_31_isHSSchool && !isLegendValidated`.
       Patch M's hasTextHOF text regex appears to false-positive on scout reports that
       mention HOFers by comparison ("Tyran Stokes is in conversations about future HOFers").
       Fix: Drop the `!isLegendValidated` guard from HS + college overrides. A
            school-confirmed HS player is ALWAYS prep_amateur, regardless of stray text.
            The "HOFer coaching at HS" edge case was overthought — a HS player IS the
            HS player; HOFer mentions in their scout report don't change that.
"""
import sys, shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.32-N.bak")
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
        print(f"  Searched for: {old[:160]}...", file=sys.stderr)
        sys.exit(2)
    if c > 1:
        print(f"✗ {label} · {c} matches (AMBIGUOUS)", file=sys.stderr); sys.exit(2)
    src = src.replace(old, new)
    applied += 1
    delta = len(new) - len(old)
    print(f"✓ {label} (Δ {'+' if delta>=0 else ''}{delta})")


# ═══════════════════════════════════════════════════════════════════════════
# PATCH N1 · Drop the `!isLegendValidated` guard from HS school override
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
      // Dropped the `!isLegendValidated` guard — original rationale (HOFer coaching at HS)
      // was overthought. A school-confirmed HS player is ALWAYS prep_amateur regardless of
      // stray HOFer mentions in their scout reports. Patch M's hasTextHOF was false-positively
      // tripping on scout-report HOFer-comparisons ("future HOFer conversations"), defeating
      // the HS override for Tyran Stokes / Saniyah Hall.
      if (_v22_31_isHSSchool) {
        stage = 'prep_amateur';
        stageSignals.push('v022.31_hs_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.31 · PATCH L2 + V022.32 · PATCH N1 · COLLEGE school override is ABSOLUTE (same reasoning).
      else if (_v22_31_isCollegeSchool) {
        stage = 'college_amateur';
        stageSignals.push('v022.31_college_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }"""

apply("PATCH_N1_drop_legend_guard_from_school_overrides", PATCH_N1_OLD, PATCH_N1_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH N2 · Add hasPrimeProSig + prime_pro cascade entry
# ═══════════════════════════════════════════════════════════════════════════
# Insert BEFORE the "isProSig && isCollegeSig" fallthrough to early_pro.
# Active multi-MVP/champion players (Steph, LeBron, Jokic, Giannis, Embiid) should
# route to prime_pro (cap 9.3), not early_pro (cap 8.0).

PATCH_N2_OLD = """      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

PATCH_N2_NEW = """      // V022.32 · PATCH N2 · prime_pro detection — active multi-MVP / multi-champion players
      // who would otherwise fall into the isProSig && isCollegeSig "early_pro" bucket because
      // they have college mentions in their bio. Steph Curry (2x MVP, 4x champ), LeBron (4x MVP),
      // Jokic (3x MVP), Giannis (2x MVP), Embiid (MVP), Tatum (multi-AS), etc. all need prime_pro.
      const hasPrimeProSig = /\\b(2[ -]?time mvp|2x mvp|two[ -]?time mvp|three[ -]?time mvp|3[ -]?time mvp|3x mvp|four[ -]?time mvp|4x mvp|five[ -]?time mvp|5x mvp|2[ -]?time (?:nba |wnba |nfl )?champion|2x (?:nba |wnba |nfl )?champion|three[ -]?time (?:nba |wnba |nfl )?champion|3[ -]?time (?:nba |wnba |nfl )?champion|3x (?:nba |wnba |nfl )?champion|four[ -]?time (?:nba |wnba |nfl )?champion|4x (?:nba |wnba |nfl )?champion|five[ -]?time (?:nba |wnba |nfl )?champion|5[ -]?time (?:nba |wnba |nfl )?champion|6[ -]?time (?:nba |wnba |nfl )?champion|seven[ -]?time (?:nba |wnba |nfl )?champion|[2-9][ -]?time all[- ]star|multi[- ]time all[- ]star|all-nba first team|first[- ]team all-nba|defensive player of the year|finals mvp|kia mvp|nba mvp|wnba mvp|nfl mvp|league mvp|world series mvp|cy young|silver slugger)\\b/i.test(allText);

      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

apply("PATCH_N2_add_hasPrimeProSig_signal", PATCH_N2_OLD, PATCH_N2_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH N3 · Insert prime_pro cascade entry BEFORE early_pro fallthrough
# ═══════════════════════════════════════════════════════════════════════════
# The cascade currently has:
#   ...
#   else if (isProSig && !isCollegeSig) { stage = 'prime_pro'; ... }
#   else if (isProSig && isCollegeSig) { stage = 'early_pro'; ... }
# We need to add a check: even with college keywords, if hasPrimeProSig is true → prime_pro.
# We hook into the early_pro entry and add a guard.

PATCH_N3_OLD = """      else if (isProSig && isCollegeSig) {
        stage = 'early_pro';
        stageSignals.push('pro+college_keyword');
      }"""

PATCH_N3_NEW = """      // V022.32 · PATCH N3 · disambiguate: if active multi-MVP/champion signals present,
      // route to prime_pro (cap 9.3) instead of early_pro (cap 8.0). Steph Curry / LeBron /
      // Jokic / Giannis / Embiid get the right stage now.
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
WORKER.write_text(src)
print(f"\n✓ V022.32 Patch N applied · {applied} patches · {orig_len:,} → {len(src):,} chars (Δ +{len(src)-orig_len:,})")
print("""
Next:
  node --check worker.js && ./fc-deploy-dev.sh

Then re-smoke. Expected:
  Tyran Stokes      tier=hs   stage=prep_amateur   composite ≤ 6.5
  Saniyah Hall      tier=hs   stage=prep_amateur   composite ≤ 6.5
  Cameron Boozer    tier=d1   stage=college_amateur composite ≤ 7.5
  Cooper Flagg      tier=pro  stage=early_pro       composite ≤ 8.0
  Tim Duncan        tier=pro  stage=legend_pro      composite = 9.7
  Stephen Curry     tier=pro  stage=prime_pro       composite ≤ 9.3
""")
