#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
APPLY V5 v2 PHASE A · WORKER PATCH
═══════════════════════════════════════════════════════════════════════════
V022.32-YX → V022.34-V5

4 patch groups:
  P1 · cap clamp removal at composite output (line ~11476)
       composite reads _v22_31_raw, capped_legacy retained in metadata
  P2 · synthesis prompt surgical rewrites (9 replaces + 1 insert)
       REFERENCE BANDS → REFERENCE DISTRIBUTION
       HARD CAP / CEILING / MAX language → evidence-range / evidence to
       INSERT before WITHIN-TIER: CROSS-SPORT anchors + PHENOM CRITERIA
                                   + ANTI-INFLATION (8 items) + DEFAULT-LOW
  P4 · banner V022.32-YX → V022.34-V5
       cache v022.32yx → v022.34v5

PRESERVED untouched: WITHIN-TIER DIFFERENTIATION (the moat — decimal facet diff)
DEFERRED to Phase B: per-facet evidence audit output schema

Run from ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, subprocess, hashlib
from pathlib import Path

print("═══ V5 v2 PHASE A · V022.32-YX → V022.34-V5 ═══\n")

WORKER = Path('worker.js')
if not WORKER.exists():
    print(f"FAIL: {WORKER} not found")
    sys.exit(1)

orig_bytes = WORKER.stat().st_size
c = WORKER.read_text()
orig_sha = hashlib.sha256(c.encode()).hexdigest()[:12]
print(f"▸ worker.js · {orig_bytes:,} bytes · sha={orig_sha}\n")


# ══════════════════════════════════════════════════════════════════════════
# PRE-FLIGHT: all 15 anchor strings must exist before any change
# ══════════════════════════════════════════════════════════════════════════
print("▸ Pre-flight · anchor verification (15 anchors)\n")

ANCHORS = [
    # P1 cap removal
    ('A01_cap_app_line', '''        const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);
      result.composite = Math.round(_v22_31_capped * 10) / 10;
      result.composite_v022_31 = {
        raw: Math.round(_v22_31_raw * 100) / 100,
        cap: _v22_31_cap,'''),
    # P2.1 REFERENCE BANDS header
    ('A02_ref_bands', 'REFERENCE BANDS — these are HARD CAPS, not suggestions:'),
    # P2.2 active cap line
    ('A03_active_cap', '  9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — capped while active'),
    # P2.3 rookie CEILING line
    ('A04_rookie_ceiling', '  7.5-7.9     NBA rookie / very-early-pro CEILING (Cooper Flagg, Caitlin Clark yr 2)'),
    # P2.4 D1 HARD CAP line
    ('A05_d1_hardcap', '  7.0-7.4     D1 All-American HARD CAP — Cameron Boozer / AJ Dybantsa freshman ceiling'),
    # P2.5 HS HARD CAP line
    ('A06_hs_hardcap', '  5.0-5.4     HS #1 NATIONAL HARD CAP — Tyran Stokes, Saniyah Hall (no HS player exceeds 5.4)'),
    # P2.6 PER-TIER FACET CEILINGS header + intro
    ('A07_facet_ceilings', '''PER-TIER FACET CEILINGS (CRITICAL):

For "pro-context" facets at HS — character under PRO pressure, mental_strength in PRO clutch moments, coachability under PRO coaching, competitiveness vs PROS — score CANNOT exceed 6 regardless of how impressive the HS reputation. The evidence simply does not exist yet. You have not seen them tested at that level.'''),
    # P2.7 HS facet caps block (full block, contiguous)
    ('A08_hs_facet_caps', '''HS athlete facet caps:
  • talent (raw skill in HS context):        up to 7 (HS#1 might be 5-7)
  • physical (measurables/athleticism):      up to 8 (some HS players are physically pro-ready)
  • mental_iq (game IQ in PRO context):      MAX 6 — never seen pro defenses
  • character (off-field, general):          up to 7
  • mindset (growth orientation):            up to 7
  • mental_strength (in PRO context):        MAX 6 — no pro-level adversity yet
  • coachability (in PRO context):           MAX 6 — never coached at pro level
  • competitiveness (vs PROS):               MAX 6 — never competed against pros'''),
    # P2.8 D1 facet caps
    ('A09_d1_facet_caps', '''D1 facet caps:
  • all facets capped at 7.4 unless legitimate pro-level evidence exists'''),
    # P2.9 Steph anchor
    ('A10_steph_active_cap', '  • Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active cap)'),
    # P2.10 INSERT anchor (Jordan line + blank + WITHIN-TIER)
    ('A11_insert_anchor', '''  •   • Michael Jordan 1996 peak                    → composite 9.9 (the only one)

WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):'''),
    # P4 banner
    ('A12_banner', '// FIELDCHECK_WORKER_VERSION = V022.32-YX · TENET 47 ATOMIC · 8 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, Y (stage=unknown fallback), X (decimal facet diff · THE MOAT)'),
    # P4 cache key
    ('A13_cache', "const cacheVersion = 'v022.32yx';"),
    # Verify WITHIN-TIER moat exists and is left alone
    ('A14_moat_preserve', 'WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):'),
    # Verify cap variable structure is intact (P1 surgical target)
    ('A15_cap_var', 'let _v22_31_cap = 10.0;'),
]

missing = []
for name, anchor in ANCHORS:
    if anchor in c:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name}  ← NOT FOUND")
        missing.append(name)

if missing:
    print(f"\n✗ PRE-FLIGHT FAILED · {len(missing)} anchor(s) missing")
    print(f"  Missing: {', '.join(missing)}")
    print(f"  No changes made. Worker.js untouched.")
    sys.exit(1)

print(f"\n✓ All 15 anchors verified. Proceeding with patches.\n")


# ══════════════════════════════════════════════════════════════════════════
# BACKUP
# ══════════════════════════════════════════════════════════════════════════
backup = WORKER.with_suffix('.js.pre-V022.34-V5.bak')
shutil.copy(WORKER, backup)
print(f"▸ Backup: {backup}\n")


# ══════════════════════════════════════════════════════════════════════════
# P1 · CAP REMOVAL AT COMPOSITE OUTPUT
# ══════════════════════════════════════════════════════════════════════════
print("▸ P1 · cap clamp removal · composite reads _v22_31_raw")

p1_old = '''        const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);
      result.composite = Math.round(_v22_31_capped * 10) / 10;
      result.composite_v022_31 = {
        raw: Math.round(_v22_31_raw * 100) / 100,
        cap: _v22_31_cap,'''

p1_new = '''        const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);
      // V5 v2: composite reads RAW directly. cap retained in metadata only for transparency.
      result.composite = Math.round(_v22_31_raw * 10) / 10;
      result.composite_v022_31 = {
        raw: Math.round(_v22_31_raw * 100) / 100,
        capped_legacy: Math.round(_v22_31_capped * 10) / 10,
        cap: _v22_31_cap,'''

c = c.replace(p1_old, p1_new, 1)
print(f"  ✓ composite now reads _v22_31_raw · capped_legacy retained in metadata\n")


# ══════════════════════════════════════════════════════════════════════════
# P2 · SYNTHESIS PROMPT REWRITES
# ══════════════════════════════════════════════════════════════════════════
print("▸ P2 · synthesis prompt surgical rewrites")

# P2.1 REFERENCE BANDS header
c = c.replace(
    'REFERENCE BANDS — these are HARD CAPS, not suggestions:',
    'REFERENCE DISTRIBUTION — natural distribution evidence produces (NOT enforcement boundaries; PHENOMS with pro-tier evidence at sub-pro age may exceed — see PHENOM CRITERIA below):',
    1
)
print("  ✓ P2.1 REFERENCE BANDS → REFERENCE DISTRIBUTION")

# P2.2 active cap line
c = c.replace(
    '  9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — capped while active',
    '  9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — active career still open',
    1
)
print("  ✓ P2.2 9.0-9.3 · 'capped while active' → 'active career still open'")

# P2.3 rookie CEILING
c = c.replace(
    '  7.5-7.9     NBA rookie / very-early-pro CEILING (Cooper Flagg, Caitlin Clark yr 2)',
    '  7.5-7.9     NBA rookie / very-early-pro evidence range (Cooper Flagg, Caitlin Clark yr 2) — limited sample; draft slot/recruiting rank does NOT elevate',
    1
)
print("  ✓ P2.3 7.5-7.9 · CEILING → evidence range + anti-inflation note")

# P2.4 D1 HARD CAP
c = c.replace(
    '  7.0-7.4     D1 All-American HARD CAP — Cameron Boozer / AJ Dybantsa freshman ceiling',
    '  7.0-7.4     D1 All-American evidence range — Cameron Boozer / AJ Dybantsa fresh (single year college sample; lineage/rank does NOT elevate)',
    1
)
print("  ✓ P2.4 7.0-7.4 · HARD CAP → evidence range + anti-inflation note")

# P2.5 HS HARD CAP
c = c.replace(
    '  5.0-5.4     HS #1 NATIONAL HARD CAP — Tyran Stokes, Saniyah Hall (no HS player exceeds 5.4)',
    '  5.0-5.4     HS #1 NATIONAL evidence range — Tyran Stokes, Saniyah Hall (HS-only evidence; rank does NOT elevate; phenom may exceed — see PHENOM CRITERIA)',
    1
)
print("  ✓ P2.5 5.0-5.4 · HARD CAP → evidence range + phenom pointer")

# P2.6 PER-TIER FACET CEILINGS section
p26_old = '''PER-TIER FACET CEILINGS (CRITICAL):

For "pro-context" facets at HS — character under PRO pressure, mental_strength in PRO clutch moments, coachability under PRO coaching, competitiveness vs PROS — score CANNOT exceed 6 regardless of how impressive the HS reputation. The evidence simply does not exist yet. You have not seen them tested at that level.'''

p26_new = '''PER-TIER FACET EVIDENCE BOUNDS (CRITICAL):

For "pro-context" facets at HS — character under PRO pressure, mental_strength in PRO clutch moments, coachability under PRO coaching, competitiveness vs PROS — the athlete has NOT been tested at that level, so evidence does not exist to justify above 6. PHENOMS (must pass ALL 4 phenom criteria below) may exceed. Default-low when evidence absent.'''

c = c.replace(p26_old, p26_new, 1)
print("  ✓ P2.6 PER-TIER FACET CEILINGS → EVIDENCE BOUNDS + reframing")

# P2.7 HS facet caps block
p27_old = '''HS athlete facet caps:
  • talent (raw skill in HS context):        up to 7 (HS#1 might be 5-7)
  • physical (measurables/athleticism):      up to 8 (some HS players are physically pro-ready)
  • mental_iq (game IQ in PRO context):      MAX 6 — never seen pro defenses
  • character (off-field, general):          up to 7
  • mindset (growth orientation):            up to 7
  • mental_strength (in PRO context):        MAX 6 — no pro-level adversity yet
  • coachability (in PRO context):           MAX 6 — never coached at pro level
  • competitiveness (vs PROS):               MAX 6 — never competed against pros'''

p27_new = '''HS athlete facet evidence bounds (PHENOMS may exceed):
  • talent (raw skill in HS context):        evidence to 7 (HS#1 may show 5-7)
  • physical (measurables/athleticism):      evidence to 8 (some HS players are physically pro-ready)
  • mental_iq (game IQ in PRO context):      evidence to 6 — has not faced pro defenses
  • character (off-field, general):          evidence to 7
  • mindset (growth orientation):            evidence to 7
  • mental_strength (in PRO context):        evidence to 6 — no pro-level adversity yet (PHENOM exception applies)
  • coachability (in PRO context):           evidence to 6 — never coached at pro level
  • competitiveness (vs PROS):               evidence to 6 — never competed against pros'''

c = c.replace(p27_old, p27_new, 1)
print("  ✓ P2.7 HS facet caps → evidence bounds (8 lines reframed)")

# P2.8 D1 facet caps
p28_old = '''D1 facet caps:
  • all facets capped at 7.4 unless legitimate pro-level evidence exists'''

p28_new = '''D1 facet evidence bounds (PHENOMS may exceed):
  • all facets evidence ranges to 7.4 unless legitimate pro-level evidence exists'''

c = c.replace(p28_old, p28_new, 1)
print("  ✓ P2.8 D1 facet caps → evidence bounds")

# P2.9 Steph anchor
c = c.replace(
    '  • Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active cap)',
    '  • Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active career still open)',
    1
)
print("  ✓ P2.9 Steph · '(active cap)' → '(active career still open)'")


# P2.10 INSERT new V5 sections before WITHIN-TIER DIFFERENTIATION
v5_insert = '''CROSS-SPORT THEORETICAL 10 ANCHORS (universal — all sports):
  Character (apex):     Duncan / Jeter / Federer / Nicklaus tier
  Mindset:              Kobe / Brady / Tiger peak / Nadal tier
  Mental Strength:      Jordan G6 / Brady 28-3 / Djokovic 5-set / Tiger 15th green
  Talent:               LeBron peak / Mahomes peak / Trout / Messi peak / Tiger peak
  Physical:             LeBron 2012 / Bo Jackson / Ronaldo prime / Trout / Bolt
  Mental/IQ:            Bird-Magic-Jokic / Manning-Brady / Xavi-Iniesta-Pirlo / Gretzky
  Coachability:         Duncan/Popovich / Brady/Belichick / Nadal/T.Nadal / Messi/Guardiola
  Competitiveness:      Jordan / Brady / Djokovic-Serena / Tiger peak / Cristiano

PHENOM CRITERIA (must pass ALL 4 to exceed standard evidence range — earned by evidence, NOT awarded by hype):
  REQ 1: Pro-tier evidence at sub-pro age (not projection — actual measurable pro-tier evidence demonstrated NOW)
  REQ 2: Multi-source corroboration (3+ INDEPENDENT sources agreeing on the pro-tier evidence)
  REQ 3: Older-competition validation (dominance vs significantly OLDER competitors, not same-age cohort)
  REQ 4: Sustained across multiple events (pattern across multiple high-level events, not single-tournament)

  Canonical phenoms (passed all 4): Kobe-17 (Adidas ABCD vs older All-Americans + pro pickup), LeBron-17 (college scrimmages vs 19yo + Nike pro evals), KD-18 (Naismith POY freshman vs Big 12), Tiger-17 (3x US Junior + adult amateur wins), Mahomes-21 (pro-tier college Big 12), Gauff-15 (Wimbledon QF beating WTA top-10), Gretzky-17 (110pt WHA rookie vs adults), Bo Jackson-22 (pro-tier dual-sport).
  "Top recruit" or "5-star" status alone does NOT qualify. Most amateurs do NOT meet phenom criteria.

ANTI-INFLATION (these signals DO NOT justify higher facet scores — universal across all facets, all sports):
  1. Recruiting rankings (247/On3/Rivals/ESPN composite) — projection consensus, not evidence
  2. Draft slot / mock draft consensus — rookies do NOT inherit pro scores by draft position
  3. NIL deal size or brand deals — market price for marketing, not athletic
  4. Media narrative or hype — opinion aggregates (these shape consensus polygon, NOT FieldCheck polygon)
  5. Family lineage ("son of NBA player") — the parent is NOT the athlete
  6. Coach quotes during recruitment — sales pitches; only post-arrival quotes count
  7. Single-event heroics — sample-of-one, must show pattern across multiple events
  8. Combine measurables without game translation — 40 time/vertical/wingspan alone are inputs, require game-level translation

DEFAULT-LOW PRINCIPLE:
When evidence is missing for a facet, the facet defaults to 2-3, NOT to average 5. The algorithm EARNS higher scores from evidence; it does not ASSUME them. Missing evidence = low score, not neutral score. This is the core fix from V4: V4 assumed 5 baseline and adjusted up on hype signals; V5 assumes low until evidence justifies higher.

'''

p210_old = '''  •   • Michael Jordan 1996 peak                    → composite 9.9 (the only one)

WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):'''

p210_new = '''  •   • Michael Jordan 1996 peak                    → composite 9.9 (the only one)

''' + v5_insert + '''WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):'''

c = c.replace(p210_old, p210_new, 1)
print(f"  ✓ P2.10 INSERT before WITHIN-TIER · CROSS-SPORT + PHENOM + ANTI-INFLATION + DEFAULT-LOW ({len(v5_insert):,} chars)")


# ══════════════════════════════════════════════════════════════════════════
# P4 · BANNER + CACHE BUMP
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ P4 · banner + cache bump")

p4_banner_old = '// FIELDCHECK_WORKER_VERSION = V022.32-YX · TENET 47 ATOMIC · 8 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, Y (stage=unknown fallback), X (decimal facet diff · THE MOAT)'
p4_banner_new = '// FIELDCHECK_WORKER_VERSION = V022.34-V5 · V5 ALGORITHM · 10 is only ceiling · evidence rigor only limiter · phenom criteria locked (4 reqs) · anti-inflation explicit (8 signals) · default-low principle · cross-sport anchors · cap kept in metadata only · capped_legacy retained for transparency'

c = c.replace(p4_banner_old, p4_banner_new, 1)
print("  ✓ banner V022.32-YX → V022.34-V5")

p4_cache_old = "const cacheVersion = 'v022.32yx';"
p4_cache_new = "const cacheVersion = 'v022.34v5';"

cache_count_before = c.count(p4_cache_old)
c = c.replace(p4_cache_old, p4_cache_new)
cache_count_after = c.count(p4_cache_new)
print(f"  ✓ cache v022.32yx → v022.34v5 ({cache_count_before} → {cache_count_after} occurrences)")


# ══════════════════════════════════════════════════════════════════════════
# WRITE + VERIFY
# ══════════════════════════════════════════════════════════════════════════
WORKER.write_text(c)
new_bytes = WORKER.stat().st_size
new_sha = hashlib.sha256(c.encode()).hexdigest()[:12]
delta = new_bytes - orig_bytes
print(f"\n▸ worker.js · {new_bytes:,} bytes (delta +{delta:,}) · sha={new_sha}\n")


# ══════════════════════════════════════════════════════════════════════════
# GREP-VERIFY (Tenet 47.1)
# ══════════════════════════════════════════════════════════════════════════
print("▸ Grep-verify · post-patch state\n")

checks = [
    # P1
    ('P1 composite reads raw', 'result.composite = Math.round(_v22_31_raw * 10) / 10' in c),
    ('P1 capped_legacy in metadata', 'capped_legacy:' in c),
    ('P1 OLD capped output removed', 'result.composite = Math.round(_v22_31_capped * 10) / 10' not in c),
    # P2
    ('P2.1 REFERENCE DISTRIBUTION header', 'REFERENCE DISTRIBUTION — natural distribution' in c),
    ('P2.1 OLD HARD CAPS header removed', 'REFERENCE BANDS — these are HARD CAPS' not in c),
    ('P2.2 active career still open', 'active career still open' in c),
    ('P2.2 OLD "capped while active" removed', 'capped while active' not in c),
    ('P2.3 rookie evidence range', '7.5-7.9     NBA rookie / very-early-pro evidence range' in c),
    ('P2.3 OLD rookie CEILING removed', 'very-early-pro CEILING' not in c),
    ('P2.4 D1 evidence range', '7.0-7.4     D1 All-American evidence range' in c),
    ('P2.4 OLD D1 HARD CAP removed', 'D1 All-American HARD CAP' not in c),
    ('P2.5 HS evidence range', '5.0-5.4     HS #1 NATIONAL evidence range' in c),
    ('P2.5 OLD HS HARD CAP removed', 'HS #1 NATIONAL HARD CAP' not in c),
    ('P2.6 EVIDENCE BOUNDS header', 'PER-TIER FACET EVIDENCE BOUNDS (CRITICAL):' in c),
    ('P2.6 OLD CEILINGS header removed', 'PER-TIER FACET CEILINGS (CRITICAL):' not in c),
    ('P2.7 HS facet evidence bounds', 'HS athlete facet evidence bounds (PHENOMS may exceed):' in c),
    ('P2.7 OLD MAX language removed', 'MAX 6 — never seen pro defenses' not in c),
    ('P2.8 D1 facet evidence bounds', 'D1 facet evidence bounds (PHENOMS may exceed):' in c),
    ('P2.8 OLD D1 caps removed', 'D1 facet caps:' not in c),
    ('P2.9 Steph active career', '(active career still open)' in c),
    # P2.10 INSERT
    ('P2.10 CROSS-SPORT anchors', 'CROSS-SPORT THEORETICAL 10 ANCHORS' in c),
    ('P2.10 PHENOM CRITERIA', 'PHENOM CRITERIA (must pass ALL 4' in c),
    ('P2.10 REQ 1', 'REQ 1: Pro-tier evidence at sub-pro age' in c),
    ('P2.10 Kobe-17 phenom', 'Kobe-17 (Adidas ABCD' in c),
    ('P2.10 Tiger-17 phenom', 'Tiger-17 (3x US Junior' in c),
    ('P2.10 ANTI-INFLATION', 'ANTI-INFLATION (these signals DO NOT' in c),
    ('P2.10 recruiting rankings excluded', '1. Recruiting rankings (247/On3/Rivals/ESPN' in c),
    ('P2.10 family lineage excluded', '5. Family lineage' in c),
    ('P2.10 DEFAULT-LOW PRINCIPLE', 'DEFAULT-LOW PRINCIPLE:' in c),
    ('P2.10 defaults to 2-3', 'defaults to 2-3, NOT to average 5' in c),
    # MOAT preserve
    ('MOAT preserved', 'WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):' in c),
    ('MOAT decimal spread preserved', 'HS DECIMAL spread' in c),
    # P4
    ('P4 banner V022.34-V5', 'FIELDCHECK_WORKER_VERSION = V022.34-V5' in c),
    ('P4 OLD V022.32-YX banner removed', 'FIELDCHECK_WORKER_VERSION = V022.32-YX' not in c),
    ('P4 cache v022.34v5', "cacheVersion = 'v022.34v5'" in c),
    ('P4 OLD cache v022.32yx removed', "cacheVersion = 'v022.32yx'" not in c),
    # 8 facets list unchanged
    ('8 facets list preserved', '1. character — integrity' in c and '8. competitiveness — drive' in c),
    # Cap variable still defined (P1 only changes composite output, not cap math)
    ('cap variable structure preserved', 'let _v22_31_cap = 10.0;' in c),
    ('cap_applied metadata preserved', 'cap_applied: _v22_31_raw > _v22_31_cap' in c),
]

all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok:
        all_ok = False

if not all_ok:
    print("\n✗ POST-PATCH VERIFICATION FAILED")
    print(f"  Restore from {backup} if needed: cp {backup} worker.js")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# NODE SYNTAX CHECK (Tenet 47 · catches const/let issues)
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ Node syntax check")
r = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"  ✗ SYNTAX FAIL: {r.stderr}")
    print(f"  Restore: cp {backup} worker.js")
    sys.exit(1)
print("  ✓ syntax OK")


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" V5 v2 PHASE A APPLIED · V022.34-V5")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" worker.js · V022.32-YX → V022.34-V5 · {new_bytes:,} bytes (delta +{delta:,})")
print(f" sha · {orig_sha} → {new_sha}")
print(f"")
print(f" V5 v2 changes:")
print(f"   ✓ P1 · composite reads RAW · cap kept in metadata (capped_legacy retained)")
print(f"   ✓ P2 · synthesis prompt 9 surgical rewrites + 4-section insert")
print(f"          REFERENCE BANDS → REFERENCE DISTRIBUTION")
print(f"          HARD CAP / CEILING / MAX → evidence-range / evidence to")
print(f"          NEW: CROSS-SPORT anchors (all 8 facets)")
print(f"          NEW: PHENOM CRITERIA (4 reqs, 8 canonical cases)")
print(f"          NEW: ANTI-INFLATION (8 explicit signals)")
print(f"          NEW: DEFAULT-LOW PRINCIPLE")
print(f"          PRESERVED: WITHIN-TIER DIFFERENTIATION (the moat)")
print(f"   ✓ P4 · banner V022.34-V5 · cache v022.34v5 (cold cache)")
print(f"")
print(f" DEFERRED Phase B: per-facet evidence audit output schema")
print(f"")
print(f" Backup: {backup}")
print(f"")
print(f" NEXT:")
print(f"   1. ./fc-deploy-dev.sh    # ships V022.34-V5 to dev")
print(f"   2. python3 v022_32_q_battery_v2.py    # cold cache, ~22min")
print(f"   3. Eyeball battery results against 16 test cases:")
print(f"        Stokes 4.5-5.4 · Flagg 6.5-7.5 · Caitlin 7.0-7.8 ·")
print(f"        Duncan 9.3-9.6 · Steph 9.0-9.3 · Jordan 9.9 ·")
print(f"        Mahomes 8.8-9.2 · Brady 9.4-9.7 · Tiger 9.5-9.8 ·")
print(f"        Trout 9.0-9.4 · Boozer 6.0-7.0 · Goodin 6.0-6.7 ·")
print(f"        Gauff 7.5-8.2 · Kobe-17 6.0-7.0 · Ivanyo 3.5-5.5 · HS median 3.0-4.0")
print(f"   4. If pass → ./fc-promote-prod.sh")
print(f"      If fail → iterate prompt rigor (NOT add caps); update living docs")
print(f"               (canonical Tab 19 + methodology section + standalone) together")
