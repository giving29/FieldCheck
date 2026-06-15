#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-Q · ATOMIC RECOVERY · Tenet 47 grep-verified
═══════════════════════════════════════════════════════════════════════════

This script does what I should have done from the start:

  1. REVERT canonical to V5.24/V022.32 (truth-aligned with current worker)
  2. PRE-FLIGHT verify every anchor exists exactly once in worker.js
  3. APPLY patches O, N1, N3+Q1+Q3 using EXACT text from your diagnostic
  4. GREP-VERIFY each patch landed (Tenet 47 · no success without proof)
  5. BUMP worker banner to V022.32-Q + cacheVersion to v022.32q
  6. RE-VERIFY worker has expected text
  7. ATOMICALLY bump canonical to V5.25/V022.32-Q ONLY after worker confirms

What ships:
  PATCH O  · V4-tight caps (HS 5.4, D1 7.4, D2/D3/JUCO/NAIA 6.8, early_pro 7.9)
  PATCH N1 · HS + college school overrides become ABSOLUTE (drop !isLegendValidated guard)
  PATCH N3 + Q1 + Q3 · prime_pro cascade entry BEFORE legend_pro
                       · pro-prefix REQUIRED in regex (Caitlin's college MVP won't match)
                       · active multi-MVP overrides projected-HOF text (Steph fix)

What is NOT in this patch (deliberate · separate concerns):
  • hasTextHOF tightening (Patch Q2) — only matters if hasTextHOF exists in current worker;
    diagnostic showed it doesn't. Skipped to avoid touching unrelated code.
  • Curated-profile bypass patch — Caitlin's 9.05 frontend display comes from
    PLAYER_PROFILES merged via getPlayerProfile (line 26523+). Different code path.
  • Tim Duncan / Michael Jordan legend_pro detection — needs wikidata/bbref enrichment;
    text-only signals can't reliably identify them as retired HOFers.
  • Moat extensions (ext 1-8) — stay in /mnt/user-data/outputs awaiting V022.32-Q stable.

Apply:
  cd ~/Desktop/fieldcheck-proxy
  cp ~/Downloads/v022_32_q_recovery.py .
  python3 v022_32_q_recovery.py
  node --check worker.js && ./fc-deploy-dev.sh
  ./deploy_v022_32_full.sh smoke
═══════════════════════════════════════════════════════════════════════════
"""
import sys
import shutil
from pathlib import Path

WORKER = Path("worker.js")
CANONICAL = Path("FC_CANONICAL_STATE_V1.html")

if not WORKER.exists() or not CANONICAL.exists():
    print("✗ ERROR: worker.js or FC_CANONICAL_STATE_V1.html not found in CWD")
    print(f"  CWD: {Path.cwd()}")
    sys.exit(1)

# ─── BACKUPS ────────────────────────────────────────────────────────────────
shutil.copy2(WORKER, "worker.js.pre-V022.32-Q-RECOVERY.bak")
shutil.copy2(CANONICAL, "FC_CANONICAL_STATE_V1.html.pre-V022.32-Q-RECOVERY.bak")
print("✓ Backups created")
print(f"  • worker.js.pre-V022.32-Q-RECOVERY.bak")
print(f"  • FC_CANONICAL_STATE_V1.html.pre-V022.32-Q-RECOVERY.bak")
print()

src = WORKER.read_text()
canonical = CANONICAL.read_text()
orig_src_len = len(src)
orig_canonical_len = len(canonical)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1 · REVERT CANONICAL LIE (V5.25/V022.32-Q references → V5.24/V022.32)
# ═══════════════════════════════════════════════════════════════════════════
print("▸ Phase 1 · Revert canonical to truth (V5.24/V022.32)")

before_v525 = canonical.count("V5.25")
before_qref = canonical.count("V022.32-Q")
canonical = canonical.replace("V5.25", "V5.24")
canonical = canonical.replace("V022.32-Q", "V022.32")
CANONICAL.write_text(canonical)
print(f"  ✓ Reverted {before_v525} occurrences of V5.25 → V5.24")
print(f"  ✓ Reverted {before_qref} occurrences of V022.32-Q → V022.32")
print(f"  canonical is now truth-aligned with deployed worker (V022.32 plain)")
print()


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2 · PRE-FLIGHT · verify every anchor exists exactly once
# ═══════════════════════════════════════════════════════════════════════════
print("▸ Phase 2 · Pre-flight anchor verification (Tenet 47)")

def verify_unique(label, anchor):
    c = src.count(anchor)
    if c == 0:
        print(f"✗ PRE-FLIGHT FAIL: {label} · anchor NOT FOUND in worker.js")
        print(f"   tried: {anchor[:200]}{'...' if len(anchor)>200 else ''}")
        sys.exit(2)
    if c > 1:
        print(f"✗ PRE-FLIGHT FAIL: {label} · anchor matches {c} times (ambiguous)")
        sys.exit(2)
    print(f"  ✓ {label}")

CAP_OLD = """      if (_v22_31_tier === 'hs') _v22_31_cap = 6.5;
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
verify_unique("PATCH O · cap block", CAP_OLD)

HS_OLD = "if (_v22_31_isHSSchool && !isLegendValidated) {"
verify_unique("PATCH N1a · HS override line", HS_OLD)

COL_OLD = "else if (_v22_31_isCollegeSchool && !isLegendValidated) {"
verify_unique("PATCH N1b · college override line", COL_OLD)

LEGEND_OLD = """      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""
verify_unique("PATCH N3+Q1+Q3 · legend_pro insertion anchor", LEGEND_OLD)

VBANNER_OLD = "// FIELDCHECK_WORKER_VERSION = V022.32 · CALIBRATION · TENET 46 V4 universe-blind scale · 3-patch bundle: REF table (HS 3.5/D1 6.2/Pro 7.7, sigma 0.7) + synthesis Haiku V4 anchor + brutal_honest V4 anchor · cacheVersion v022.32 · base V022.31"
verify_unique("Version banner", VBANNER_OLD)

CV_OLD = "const cacheVersion = 'v022.32';  // V022.32 CALIBRATION · invalidates v022.31 synthesis cache (V4 anchor changes synthesis output)"
verify_unique("cacheVersion", CV_OLD)

print()


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3 · APPLY PATCHES with grep-verify after each
# ═══════════════════════════════════════════════════════════════════════════
print("▸ Phase 3 · Apply patches with Tenet 47 grep-verify")

def apply_and_verify(label, old, new, marker):
    global src
    src = src.replace(old, new)
    if marker not in src:
        print(f"✗ TENET 47 VIOLATION: {label} grep-verify failed (marker missing: {marker[:80]})")
        sys.exit(3)
    print(f"  ✓ {label} (Δ {len(new)-len(old):+d}) · marker verified in file")

# ─── PATCH O · V4-tight caps ────────────────────────────────────────────────
CAP_NEW = """      // V022.32-Q · PATCH O · TIGHTENED TO V4 SPEC · every decimal sacred
      if (_v22_31_tier === 'hs') _v22_31_cap = 5.4;                                    // V4: HS#1 (Stokes/Hall)
      else if (_v22_31_tier === 'd3') _v22_31_cap = 6.8;                               // V4: D3 ceiling
      else if (_v22_31_tier === 'd2') _v22_31_cap = 6.8;                               // V4: D2 ceiling
      else if (_v22_31_tier === 'd1') _v22_31_cap = 7.4;                               // V4: D1 AA cap (Boozer)
      else if (_v22_31_tier === 'juco' || _v22_31_tier === 'naia') _v22_31_cap = 6.8;  // V4
      else if (_v22_31_tier === 'pro') {
        if (_v22_31_stage === 'legend_pro') _v22_31_cap = 9.7;
        else if (_v22_31_stage === 'prime_pro') _v22_31_cap = 9.3;
        else if (_v22_31_stage === 'retired_pro') _v22_31_cap = 9.6;
        else _v22_31_cap = 7.9;                                                        // V4: NBA rookie ceiling
      }"""
apply_and_verify("PATCH O · V4-tight caps", CAP_OLD, CAP_NEW, "V022.32-Q · PATCH O")

# ─── PATCH N1a · HS override absolute ──────────────────────────────────────
HS_NEW = "if (_v22_31_isHSSchool) {  // V022.32-Q · PATCH N1 · HS school override is ABSOLUTE"
apply_and_verify("PATCH N1a · HS override absolute", HS_OLD, HS_NEW, "V022.32-Q · PATCH N1 · HS school override is ABSOLUTE")

# ─── PATCH N1b · College override absolute ─────────────────────────────────
COL_NEW = "else if (_v22_31_isCollegeSchool) {  // V022.32-Q · PATCH N1 · college school override is ABSOLUTE"
apply_and_verify("PATCH N1b · College override absolute", COL_OLD, COL_NEW, "college school override is ABSOLUTE")

# ─── PATCH N3 + Q1 + Q3 · prime_pro cascade with pro-prefix-required regex ─
LEGEND_NEW = """      // V022.32-Q · PATCH N3 + Q1 + Q3 · prime_pro cascade · BEFORE legend_pro check.
      // Pro-prefix REQUIRED in regex · Caitlin Clark's Wooden Award (college MVP) will NOT match.
      // Active multi-MVP/champion overrides projected-HOF text · Steph Curry routes to prime_pro
      // (cap 9.3) instead of legend_pro (cap 9.7) because he's ACTIVE.
      else if (
        /\\b(?:[2-9][- ]?time (?:nba|wnba|nfl|mlb) (?:mvp|champion|all[- ]star)|multi[- ]time (?:nba|wnba|nfl) all[- ]star|(?:nba|wnba|nfl) mvp|all-(?:nba|wnba) first team|first[- ]team all-(?:nba|wnba)|nba finals mvp|wnba finals mvp|world series mvp|nba defensive player of the year|wnba defensive player of the year)\\b/i.test(allText)
        && isProSig
        && !(isRetiredSig && /(?:retired|former)\\s+(?:nba|wnba|nfl|mlb)\\s+(?:player|star|champion|mvp)/i.test(allText))
      ) {
        stage = 'prime_pro';
        stageSignals.push('q1_prime_pro_overrides_hof_projection');
      }
      // V022.30 + V022.32-Q · legend_pro requires validation AND explicit retirement signal
      else if (
        isLegendSig && isProSig && isLegendValidated
        && (isRetiredSig && /(?:retired|former)\\s+(?:nba|wnba|nfl|mlb)/i.test(allText))
      ) {"""
apply_and_verify("PATCH N3+Q1+Q3 · prime_pro cascade", LEGEND_OLD, LEGEND_NEW, "V022.32-Q · PATCH N3 + Q1 + Q3")

# ─── Version banner bump ───────────────────────────────────────────────────
VBANNER_NEW = "// FIELDCHECK_WORKER_VERSION = V022.32-Q · TENET 47 ATOMIC · 4 patches: O (V4-tight caps HS 5.4/D1 7.4/D2-D3-JUCO-NAIA 6.8/early_pro 7.9) + N1 (school overrides ABSOLUTE) + N3+Q1+Q3 (prime_pro cascade · pro-prefix-required regex · active multi-MVP overrides projected-HOF) · base V022.32 calibration"
apply_and_verify("Version banner V022.32 → V022.32-Q", VBANNER_OLD, VBANNER_NEW, "V022.32-Q · TENET 47 ATOMIC")

# ─── cacheVersion bump ─────────────────────────────────────────────────────
CV_NEW = "const cacheVersion = 'v022.32q'; // V022.32-Q · invalidates v022.32 synthesis cache (cap + cascade changes)"
apply_and_verify("cacheVersion v022.32 → v022.32q", CV_OLD, CV_NEW, "'v022.32q'")

WORKER.write_text(src)
print()
print(f"  Worker written: {orig_src_len:,} → {len(src):,} chars (Δ +{len(src)-orig_src_len:,})")
print()


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4 · FINAL VERIFICATION · Tenet 47 enforcement
# ═══════════════════════════════════════════════════════════════════════════
print("▸ Phase 4 · Final worker grep-verification (Tenet 47)")

worker_after = WORKER.read_text()
checks = [
    ("V022.32-Q · TENET 47 ATOMIC", "Version banner"),
    ("V022.32-Q · PATCH O", "V4 caps marker"),
    ("V022.32-Q · PATCH N1 · HS school override is ABSOLUTE", "HS override absolute"),
    ("V022.32-Q · PATCH N1 · college school override is ABSOLUTE", "College override absolute"),
    ("V022.32-Q · PATCH N3 + Q1 + Q3", "Prime_pro cascade marker"),
    ("'v022.32q'", "cacheVersion v022.32q"),
    ("_v22_31_cap = 5.4", "HS cap = 5.4 (V4)"),
    ("_v22_31_cap = 7.4", "D1 cap = 7.4 (V4)"),
    ("_v22_31_cap = 6.8", "D2/D3 cap = 6.8 (V4)"),
    ("_v22_31_cap = 7.9", "early_pro cap = 7.9 (V4)"),
    ("q1_prime_pro_overrides_hof_projection", "Prime_pro signal"),
    ("if (_v22_31_isHSSchool) {", "HS guard dropped (no &&)"),
    ("else if (_v22_31_isCollegeSchool) {", "College guard dropped (no &&)"),
]
all_ok = True
for marker, label in checks:
    if marker in worker_after:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ MISSING: {label}")
        all_ok = False

if not all_ok:
    print()
    print("✗ TENET 47 VIOLATION · worker missing expected patches. ABORTING canonical bump.")
    print("  RESTORE: cp worker.js.pre-V022.32-Q-RECOVERY.bak worker.js")
    sys.exit(4)

print()
print("✓ TENET 47 PASSED · all patches verified present in worker.js")
print()


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5 · ATOMIC CANONICAL BUMP (only after worker verified V022.32-Q)
# ═══════════════════════════════════════════════════════════════════════════
print("▸ Phase 5 · Atomically bump canonical to V5.25/V022.32-Q (worker confirmed)")

canonical = canonical.replace(
    'Canonical State · V5.24',
    'Canonical State · V5.25'
)
canonical = canonical.replace(
    'V5.24 May 26',
    'V5.25 May 26'
)
# Add a single V022.32-Q marker comment near the version stamp (don't bulk-replace)
canonical_marker = """<!-- V022.32-Q · ATOMIC RECOVERY APPLIED · Tenet 47 enforced
     Patches in worker.js (grep-verified):
       O · V4-tight caps (HS 5.4, D1 7.4, D2/D3/JUCO/NAIA 6.8, early_pro 7.9, pro stages 9.3-9.7)
       N1 · school overrides ABSOLUTE (Stokes/Hall route to prep_amateur)
       N3+Q1+Q3 · prime_pro cascade with pro-prefix-required regex (Steph→prime_pro, Caitlin's Wooden won't trip MVP)
     What's NOT in (separate work · documented in canonical):
       • hasTextHOF tightening (Patch Q2) — hasTextHOF doesn't exist in current worker
       • Curated profile bypass — frontend Caitlin 9.05 from PLAYER_PROFILES override path
       • Moat extensions — staged in /mnt/user-data/outputs · apply after V022.32-Q stable
     Author: V022.32-Q recovery script · Tenet 47 grep-verified atomicity
-->
"""
# Inject marker comment near </head> if present
if '</head>' in canonical:
    canonical = canonical.replace('</head>', canonical_marker + '</head>', 1)

CANONICAL.write_text(canonical)
print(f"  ✓ Canonical bumped: V5.24 → V5.25")
print(f"  ✓ V022.32-Q recovery marker injected")
print(f"  size: {orig_canonical_len:,} → {len(canonical):,} chars")
print()


# ═══════════════════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════════════════
print("═══════════════════════════════════════════════════════════════════════")
print("RECOVERY COMPLETE · V022.32-Q applied atomically with Tenet 47 verification")
print("═══════════════════════════════════════════════════════════════════════")
print()
print("WHAT HAPPENED:")
print("  Phase 1 ✓ Canonical reverted to truth (V5.24/V022.32) before patches")
print("  Phase 2 ✓ Pre-flight verified all 6 anchors unique in worker.js")
print("  Phase 3 ✓ Applied 5 patches (O, N1a, N1b, N3+Q1+Q3, version bumps)")
print("  Phase 4 ✓ Final grep-verify confirmed all 13 markers in worker.js")
print("  Phase 5 ✓ Atomically bumped canonical to V5.25/V022.32-Q (worker confirmed)")
print()
print("NEXT:")
print("  1. node --check worker.js                  # JS syntax sanity")
print("  2. ./fc-deploy-dev.sh                       # ships to dev")
print("  3. ./deploy_v022_32_full.sh smoke           # validate 8 anchors")
print()
print("EXPECTED SMOKE (post-V022.32-Q):")
print("  Tyran Stokes:    composite ≤5.4  tier=hs  stage=prep_amateur")
print("  Saniyah Hall:    composite ≤5.4  tier=hs  stage=prep_amateur")
print("  Cameron Boozer:  composite ≤7.4  tier=d1  stage=college_amateur")
print("  Cooper Flagg:    composite ≤7.9  tier=pro stage=early_pro or prime_pro")
print("  Stephen Curry:   composite ≤9.3  tier=pro stage=prime_pro      ← Q1 fix")
print("  Tim Duncan:      composite 9.7   tier=pro stage=legend_pro")
print("                   (requires retired+pro text · if not present, may show as prime_pro 9.3)")
print()
print("KNOWN-SEPARATE issues NOT touched by V022.32-Q:")
print("  • Caitlin Clark 9.05 frontend display · CURATED PROFILE override path")
print("    Fix requires touching PLAYER_PROFILES / getPlayerProfile (line 26523+ in worker.js)")
print("    Recommend separate Patch R after V022.32-Q smoke confirms")
print("  • Michael Jordan classified as d1/college_amateur · UNC mention dominates")
print("    Fix requires hasTextHOF text-signal layer (or wikidata HOF enrichment)")
print("    Recommend separate Patch S after V022.32-Q")
print()
print("ROLLBACK (if smoke goes wrong):")
print("  cp worker.js.pre-V022.32-Q-RECOVERY.bak worker.js")
print("  cp FC_CANONICAL_STATE_V1.html.pre-V022.32-Q-RECOVERY.bak FC_CANONICAL_STATE_V1.html")
print("  ./fc-deploy-dev.sh")
