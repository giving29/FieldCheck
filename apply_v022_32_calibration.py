#!/usr/bin/env python3
"""
V022.32 · CALIBRATION · Tenet 46 V4 universe-blind scale
═══════════════════════════════════════════════════════════════════════════

THREE coordinated patches recalibrate FieldCheck composite end-to-end:

  Patch G' · Position-pool REF table recalibration
    HS mean    3.5 (was ~5.8 — uninflated)
    D1 mean    6.2 (was ~7.2)
    D2 mean    5.7 (was ~6.5)
    D3 mean    5.5 (was ~5.9)
    JUCO mean  5.5 (was ~6.2)
    NAIA mean  5.4 (was ~5.9)
    Pro mean   7.7 (was ~8.4)
    SIGMA      0.7 globally (was 1.2 — tighter spread, V4 bands work out)

  Patch H' · Synthesis Haiku prompt embeds V4 calibration anchor BEFORE
    "SCORING PHILOSOPHY". Explicit per-facet per-tier ceilings. Anchored examples
    (Tyran Stokes 5.3, Boozer 7.2, Flagg 7.5, Steph 9.3, Duncan 9.7).

  Patch I' · Brutal_honest prompt embeds V4 calibration anchor at top so its
    output reads ANCHORED ("Stokes 5.3 means top of HS scale, ceiling because
    pro-context evidence cannot exist yet — climb to 7+ requires college proof").

  Version bumps:
    Worker banner    V022.31 → V022.32
    cacheVersion     v022.31 → v022.32 (invalidates all v022.31 synthesis caches)
"""
import sys, shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.32.bak")
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
# PATCH G' · Position-pool REF table — V4 calibrated distributions
# ═══════════════════════════════════════════════════════════════════════════

PATCH_G_OLD = """  const REF = {
    'mens-basketball__hs': { talent: 5.8, physical: 6.0, mental_iq: 5.5, character: 6.0, mindset: 6.0, mental_strength: 5.5, coachability: 6.0, competitiveness: 6.2 },
    'mens-basketball__d1': { talent: 7.2, physical: 7.4, mental_iq: 7.0, character: 7.0, mindset: 7.0, mental_strength: 6.8, coachability: 7.0, competitiveness: 7.5 },
    'mens-basketball__d2': { talent: 6.5, physical: 6.6, mental_iq: 6.4, character: 6.5, mindset: 6.5, mental_strength: 6.2, coachability: 6.5, competitiveness: 6.8 },
    'mens-basketball__d3': { talent: 5.8, physical: 5.8, mental_iq: 6.0, character: 6.5, mindset: 6.4, mental_strength: 5.8, coachability: 6.5, competitiveness: 6.3 },
    'mens-basketball__juco': { talent: 6.2, physical: 6.4, mental_iq: 6.0, character: 6.0, mindset: 6.2, mental_strength: 6.0, coachability: 6.0, competitiveness: 6.5 },
    'mens-basketball__naia': { talent: 5.8, physical: 5.8, mental_iq: 6.0, character: 6.3, mindset: 6.2, mental_strength: 5.8, coachability: 6.3, competitiveness: 6.4 },
    'mens-basketball__pro': { talent: 8.5, physical: 8.5, mental_iq: 8.2, character: 8.0, mindset: 8.2, mental_strength: 8.2, coachability: 8.0, competitiveness: 8.7 },
    'womens-basketball__hs': { talent: 5.8, physical: 5.8, mental_iq: 5.8, character: 6.2, mindset: 6.2, mental_strength: 5.8, coachability: 6.2, competitiveness: 6.3 },
    'womens-basketball__d1': { talent: 7.0, physical: 7.0, mental_iq: 7.2, character: 7.2, mindset: 7.0, mental_strength: 6.8, coachability: 7.0, competitiveness: 7.4 },
    'womens-basketball__d2': { talent: 6.3, physical: 6.3, mental_iq: 6.4, character: 6.5, mindset: 6.5, mental_strength: 6.2, coachability: 6.5, competitiveness: 6.7 },
    'womens-basketball__d3': { talent: 5.8, physical: 5.7, mental_iq: 6.0, character: 6.5, mindset: 6.4, mental_strength: 5.8, coachability: 6.5, competitiveness: 6.3 },
    'womens-basketball__pro': { talent: 8.3, physical: 8.3, mental_iq: 8.2, character: 8.0, mindset: 8.2, mental_strength: 8.2, coachability: 8.0, competitiveness: 8.5 },
    'football__hs': { talent: 5.8, physical: 6.2, mental_iq: 5.5, character: 6.0, mindset: 6.0, mental_strength: 5.8, coachability: 6.0, competitiveness: 6.5 },
    'football__d1': { talent: 7.2, physical: 7.6, mental_iq: 6.8, character: 7.0, mindset: 7.0, mental_strength: 7.0, coachability: 7.0, competitiveness: 7.6 },
    'football__d2': { talent: 6.4, physical: 6.8, mental_iq: 6.3, character: 6.5, mindset: 6.5, mental_strength: 6.3, coachability: 6.5, competitiveness: 6.8 },
    'football__d3': { talent: 5.8, physical: 6.0, mental_iq: 6.2, character: 6.8, mindset: 6.5, mental_strength: 6.0, coachability: 6.7, competitiveness: 6.4 },
    'football__juco': { talent: 6.4, physical: 6.8, mental_iq: 6.2, character: 6.2, mindset: 6.3, mental_strength: 6.3, coachability: 6.2, competitiveness: 6.6 },
    'football__pro': { talent: 8.4, physical: 8.6, mental_iq: 8.0, character: 8.0, mindset: 8.2, mental_strength: 8.3, coachability: 8.0, competitiveness: 8.6 },
    'baseball__hs': { talent: 5.8, physical: 5.8, mental_iq: 5.8, character: 6.2, mindset: 6.2, mental_strength: 5.8, coachability: 6.2, competitiveness: 6.2 },
    'baseball__d1': { talent: 7.0, physical: 7.0, mental_iq: 7.0, character: 7.0, mindset: 7.0, mental_strength: 6.8, coachability: 7.0, competitiveness: 7.4 },
    'baseball__pro': { talent: 8.3, physical: 8.0, mental_iq: 8.0, character: 7.8, mindset: 8.0, mental_strength: 8.0, coachability: 7.8, competitiveness: 8.4 },
    'soccer__hs': { talent: 5.8, physical: 5.8, mental_iq: 6.0, character: 6.2, mindset: 6.2, mental_strength: 5.8, coachability: 6.2, competitiveness: 6.2 },
    'mens-soccer__d1': { talent: 7.0, physical: 7.0, mental_iq: 7.0, character: 7.0, mindset: 7.0, mental_strength: 6.8, coachability: 7.0, competitiveness: 7.3 },
    'tennis__hs': { talent: 6.0, physical: 5.5, mental_iq: 6.5, character: 6.5, mindset: 6.5, mental_strength: 6.2, coachability: 6.5, competitiveness: 6.8 },
    'golf__hs': { talent: 6.0, physical: 5.0, mental_iq: 6.5, character: 6.5, mindset: 6.5, mental_strength: 6.5, coachability: 6.2, competitiveness: 6.5 }
  };
  // Standard deviation assumed 1.2 for all (typical for 0-10 athletic eval scales)
  const SIGMA = 1.2;"""

PATCH_G_NEW = """  // V022.32 · TENET 46 V4 · UNIVERSE-BLIND CALIBRATED DISTRIBUTIONS
  // Single 0-10 scale (gender/age/sport blind). UTR model.
  //   HS    mean 3.5  — median HS varsity. HS#1 (Stokes/Hall) = 5.3 at 99.5%ile
  //   D1    mean 6.2  — median D1 starter. AA hard cap 7.4 at ~99%ile (Boozer/Dybantsa)
  //   D2    mean 5.7  — D2 starter
  //   D3    mean 5.5  — D3 starter / Jostens range
  //   JUCO  mean 5.5  — JUCO standout
  //   NAIA  mean 5.4  — NAIA standout
  //   Pro   mean 7.7  — NBA rotation player. All-Star 8.5+ ~99%ile. HOF 9.4-9.7
  //   SIGMA 0.7 globally (tighter spread, V4 bands map cleanly to percentiles)
  const REF = {
    'mens-basketball__hs':       { talent: 3.7, physical: 3.8, mental_iq: 3.3, character: 3.5, mindset: 3.5, mental_strength: 3.3, coachability: 3.4, competitiveness: 3.7 },
    'mens-basketball__d1':       { talent: 6.4, physical: 6.5, mental_iq: 6.0, character: 6.2, mindset: 6.2, mental_strength: 5.9, coachability: 6.1, competitiveness: 6.5 },
    'mens-basketball__d2':       { talent: 5.7, physical: 5.8, mental_iq: 5.5, character: 5.7, mindset: 5.7, mental_strength: 5.5, coachability: 5.6, competitiveness: 5.9 },
    'mens-basketball__d3':       { talent: 5.4, physical: 5.5, mental_iq: 5.5, character: 5.7, mindset: 5.6, mental_strength: 5.3, coachability: 5.7, competitiveness: 5.6 },
    'mens-basketball__juco':     { talent: 5.5, physical: 5.6, mental_iq: 5.4, character: 5.4, mindset: 5.5, mental_strength: 5.3, coachability: 5.4, competitiveness: 5.7 },
    'mens-basketball__naia':     { talent: 5.3, physical: 5.3, mental_iq: 5.4, character: 5.5, mindset: 5.5, mental_strength: 5.2, coachability: 5.5, competitiveness: 5.6 },
    'mens-basketball__pro':      { talent: 7.9, physical: 7.9, mental_iq: 7.6, character: 7.5, mindset: 7.7, mental_strength: 7.6, coachability: 7.4, competitiveness: 8.1 },
    'womens-basketball__hs':     { talent: 3.7, physical: 3.6, mental_iq: 3.5, character: 3.7, mindset: 3.6, mental_strength: 3.4, coachability: 3.6, competitiveness: 3.7 },
    'womens-basketball__d1':     { talent: 6.2, physical: 6.2, mental_iq: 6.2, character: 6.3, mindset: 6.2, mental_strength: 5.9, coachability: 6.2, competitiveness: 6.4 },
    'womens-basketball__d2':     { talent: 5.5, physical: 5.5, mental_iq: 5.5, character: 5.6, mindset: 5.6, mental_strength: 5.3, coachability: 5.6, competitiveness: 5.7 },
    'womens-basketball__d3':     { talent: 5.3, physical: 5.3, mental_iq: 5.4, character: 5.6, mindset: 5.5, mental_strength: 5.2, coachability: 5.6, competitiveness: 5.5 },
    'womens-basketball__pro':    { talent: 7.7, physical: 7.7, mental_iq: 7.6, character: 7.5, mindset: 7.7, mental_strength: 7.6, coachability: 7.4, competitiveness: 7.9 },
    'football__hs':              { talent: 3.7, physical: 3.9, mental_iq: 3.3, character: 3.5, mindset: 3.5, mental_strength: 3.4, coachability: 3.5, competitiveness: 3.8 },
    'football__d1':              { talent: 6.4, physical: 6.7, mental_iq: 5.9, character: 6.2, mindset: 6.2, mental_strength: 6.1, coachability: 6.1, competitiveness: 6.6 },
    'football__d2':              { talent: 5.7, physical: 6.0, mental_iq: 5.5, character: 5.7, mindset: 5.7, mental_strength: 5.5, coachability: 5.6, competitiveness: 5.9 },
    'football__d3':              { talent: 5.3, physical: 5.4, mental_iq: 5.5, character: 5.9, mindset: 5.6, mental_strength: 5.3, coachability: 5.7, competitiveness: 5.5 },
    'football__juco':            { talent: 5.6, physical: 5.9, mental_iq: 5.4, character: 5.4, mindset: 5.5, mental_strength: 5.5, coachability: 5.4, competitiveness: 5.8 },
    'football__pro':             { talent: 7.9, physical: 8.1, mental_iq: 7.5, character: 7.5, mindset: 7.7, mental_strength: 7.7, coachability: 7.4, competitiveness: 8.0 },
    'baseball__hs':              { talent: 3.7, physical: 3.6, mental_iq: 3.5, character: 3.7, mindset: 3.6, mental_strength: 3.4, coachability: 3.6, competitiveness: 3.6 },
    'baseball__d1':              { talent: 6.2, physical: 6.2, mental_iq: 6.2, character: 6.2, mindset: 6.2, mental_strength: 5.9, coachability: 6.1, competitiveness: 6.4 },
    'baseball__pro':             { talent: 7.8, physical: 7.5, mental_iq: 7.5, character: 7.3, mindset: 7.5, mental_strength: 7.5, coachability: 7.3, competitiveness: 7.8 },
    'soccer__hs':                { talent: 3.7, physical: 3.6, mental_iq: 3.6, character: 3.7, mindset: 3.6, mental_strength: 3.4, coachability: 3.6, competitiveness: 3.6 },
    'mens-soccer__d1':           { talent: 6.2, physical: 6.2, mental_iq: 6.2, character: 6.2, mindset: 6.2, mental_strength: 5.9, coachability: 6.1, competitiveness: 6.4 },
    'tennis__hs':                { talent: 3.8, physical: 3.5, mental_iq: 4.0, character: 3.9, mindset: 3.9, mental_strength: 3.7, coachability: 3.9, competitiveness: 4.0 },
    'golf__hs':                  { talent: 3.8, physical: 3.2, mental_iq: 4.0, character: 3.9, mindset: 3.9, mental_strength: 3.9, coachability: 3.7, competitiveness: 3.8 }
  };
  // V022.32 · TENET 46 V4 · sigma tightened from 1.2 → 0.7 to map V4 bands to clean percentiles.
  //   With HS mean 3.5 and sigma 0.7:
  //     50%ile = 3.5 (median HS varsity)
  //     95%ile = 4.65 (4-star recruit)
  //     99%ile = 5.13 (HS top-10)
  //     99.5%ile = 5.3 (Tyran Stokes / Saniyah Hall — HS#1 hard cap)
  //   With D1 mean 6.2 and sigma 0.7:
  //     50%ile = 6.2  84%ile = 6.9  95%ile = 7.35 (D1 AA hard cap)
  //   With Pro mean 7.7 and sigma 0.7:
  //     50%ile = 7.7  84%ile = 8.4 (All-Star)  95%ile = 8.85  99%ile = 9.33 (active GOAT)
  //     V022.31 hard caps then clamp legend_pro=9.7, retired_pro=9.6, prime_pro=9.3
  const SIGMA = 0.7;"""

apply("PATCH_G_pos_pool_REF_recalibration", PATCH_G_OLD, PATCH_G_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH H' · Synthesis Haiku prompt embeds V4 calibration anchor
# ═══════════════════════════════════════════════════════════════════════════
# Inject BEFORE "SCORING PHILOSOPHY (critical):" line in synthesis prompt.
# This block teaches Haiku the V4 universe-blind scale so RAW scores come out
# correctly calibrated, not just clipped by V022.31 hard caps.

V4_ANCHOR = """SCORING CALIBRATION (V022.32 · TENET 46 V4 · UNIVERSE-BLIND · MANDATORY ANCHOR):

This is a SINGLE UNIVERSE 0.0–10.0 scale. Gender, age, sport, tier all share the same axis (UTR model). 10.0 is unreachable asymptote. 9.9 is reserved for Michael Jordan 1996 peak.

REFERENCE BANDS — these are HARD CAPS, not suggestions:

  9.9         Michael Jordan 1996 — 1-3 per sport in history
  9.7-9.8     Kobe/LeBron peak/Magic/Bird — top 5-10 ever
  9.4-9.6     Tim Duncan/Wade/Drexler — retired multi-ring HOF (top 15-30 ever)
  9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — capped while active
  8.5-8.9     Current multi-year All-Star (3+ ASG selections)
  8.0-8.4     Solid proven NBA starter (3+ yrs in league)
  7.5-7.9     NBA rookie / very-early-pro CEILING (Cooper Flagg, Caitlin Clark yr 2)
  7.0-7.4     D1 All-American HARD CAP — Cameron Boozer / AJ Dybantsa freshman ceiling
  6.4-6.9     D1 starter / D2 AA / D3 Jostens range (Ben Pearce)
  5.8-6.3     D1 rotation player / D2 starter
  5.0-5.4     HS #1 NATIONAL HARD CAP — Tyran Stokes, Saniyah Hall (no HS player exceeds 5.4)
  4.2-4.9     4-star recruit / top-500 HS
  3.4-4.1     HS varsity, solid contributor (median ≈ 3.5)
  <3.0        Developing / non-roster

PER-TIER FACET CEILINGS (CRITICAL):

For "pro-context" facets at HS — character under PRO pressure, mental_strength in PRO clutch moments, coachability under PRO coaching, competitiveness vs PROS — score CANNOT exceed 6 regardless of how impressive the HS reputation. The evidence simply does not exist yet. You have not seen them tested at that level.

HS athlete facet caps:
  • talent (raw skill in HS context):        up to 7 (HS#1 might be 5-7)
  • physical (measurables/athleticism):      up to 8 (some HS players are physically pro-ready)
  • mental_iq (game IQ in PRO context):      MAX 6 — never seen pro defenses
  • character (off-field, general):          up to 7
  • mindset (growth orientation):            up to 7
  • mental_strength (in PRO context):        MAX 6 — no pro-level adversity yet
  • coachability (in PRO context):           MAX 6 — never coached at pro level
  • competitiveness (vs PROS):               MAX 6 — never competed against pros

D1 facet caps:
  • all facets capped at 7.4 unless legitimate pro-level evidence exists

CALIBRATION ANCHORS — use these to NORMALIZE your scoring:

  • Tyran Stokes (HS #1 nationally)            → composite 5.3, top facets 5-6, pro-context 4-5
  • Saniyah Hall (HS #1 girls)                  → composite 5.3 (same as Stokes — HS#1 hard cap)
  • Cameron Boozer (Duke fresh, #1 NBA pick)   → composite 7.2, top facets 7-7.4
  • AJ Dybantsa (BYU fresh)                     → composite 7.0-7.2
  • Cooper Flagg (NBA rookie, top pick)        → composite 7.5-7.8
  • Caitlin Clark (NBA yr 2, rising All-Star)  → composite 7.7-7.9
  • Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active cap)
  • Tim Duncan (retired 5x champ, HOFer)       → composite 9.6-9.7
  • Michael Jordan 1996 peak                    → composite 9.9 (the only one)

DISCIPLINE: If your facet scores would AVERAGE above the band ceiling for the athlete's tier (given in CAREER STAGE above), you are MISCALIBRATED. Adjust DOWN. This is not "be harsh" — this is "be accurate at scale." Inflation breaks trust. Honest scoring is how FieldCheck becomes the bar.

"""

PATCH_H_OLD = """SCORING PHILOSOPHY (critical):
- DIRECT evidence (a coach quote about character, a clutch-moment news headline): score with MEDIUM or HIGH confidence"""

PATCH_H_NEW = V4_ANCHOR + """SCORING PHILOSOPHY (critical):
- DIRECT evidence (a coach quote about character, a clutch-moment news headline): score with MEDIUM or HIGH confidence"""

apply("PATCH_H_synthesis_V4_anchor", PATCH_H_OLD, PATCH_H_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# PATCH I' · Brutal_honest prompt embeds V4 calibration anchor at top
# ═══════════════════════════════════════════════════════════════════════════

PATCH_I_OLD = """  const prompt = `You are FieldCheck's brutally honest interpreter. Your job is the section athletes and parents share — the side-by-side read of what the public sources say vs what FieldCheck found, written for a real decision-maker, no hedging.

ATHLETE: ${ident.full_name}"""

PATCH_I_NEW = """  const prompt = `You are FieldCheck's brutally honest interpreter. Your job is the section athletes and parents share — the side-by-side read of what the public sources say vs what FieldCheck found, written for a real decision-maker, no hedging.

V022.32 CALIBRATION ANCHOR (TENET 46 V4) — read this BEFORE interpreting any composite score:

This is a SINGLE 0-10 universe scale (gender/age/sport blind, UTR model). Composite is NOT relative to peers — it places the athlete on a continuous range from "developing" to "Jordan-tier all-time."

Reference points to anchor your interpretation:
  - 5.3 = HS#1 NATIONAL hard cap (Tyran Stokes, Saniyah Hall — best HS players in country)
  - 7.2 = D1 All-American hard cap (Cameron Boozer, AJ Dybantsa freshman ceiling)
  - 7.5 = NBA rookie ceiling (Cooper Flagg / Caitlin Clark trajectory)
  - 8.5 = Multi-year NBA All-Star
  - 9.0-9.3 = Active multi-MVP (Steph/Jokic — capped while active)
  - 9.6-9.7 = Retired HOFer (Tim Duncan tier)
  - 9.9 = Michael Jordan 1996 peak (the only one in basketball history)

How to interpret composites for THIS athlete:
  - If composite is HS-tier (e.g., 5.3 for a HS player): say "this is top-of-HS — ceiling reached because pro-context evidence cannot exist yet. The climb to 7+ requires proving these facets at college and beyond."
  - If composite is D1-tier (e.g., 7.2): say "this is D1 All-American tier — the realistic ceiling at this stage. Pro projection requires demonstrating these traits against NBA-level competition."
  - If composite is pro-tier (e.g., 7.5-9): contextualize against active vs retired, MVP-tier, HOF trajectory.

NEVER say a composite of 5.3 is "limited" or "developing" for a HS player. 5.3 is the BEST. A HS player at 5.3 has reached the ceiling of his current evidence pool. The runway forward is real.

NEVER inflate a composite. If our number is 5.3 and 247sports says 5-star, we are right and they are inflating — that's the asymmetry.

ATHLETE: ${ident.full_name}"""

apply("PATCH_I_brutal_honest_V4_anchor", PATCH_I_OLD, PATCH_I_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# Worker banner version bump · V022.31 → V022.32
# ═══════════════════════════════════════════════════════════════════════════
PATCH_VER_OLD = """// FIELDCHECK_WORKER_VERSION = V022.31 · STABILIZATION · 4-PATCH BUNDLE · composite exposure + career_stage HS override + tier-cap + bbref KV cache · base V022.30 sha=b643099b · ships BEFORE V022"""

PATCH_VER_NEW = """// FIELDCHECK_WORKER_VERSION = V022.32 · CALIBRATION · TENET 46 V4 universe-blind scale · 3-patch bundle: REF table (HS 3.5/D1 6.2/Pro 7.7, sigma 0.7) + synthesis Haiku V4 anchor + brutal_honest V4 anchor · cacheVersion v022.32 · base V022.31"""

apply("VERSION_banner_bump_V022.31→V022.32", PATCH_VER_OLD, PATCH_VER_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# cacheVersion bump · invalidates v022.31 synthesis caches
# ═══════════════════════════════════════════════════════════════════════════
PATCH_CV_OLD = """          const cacheVersion = 'v022.31';  // V022.31 stabilization · invalidates v022.30 synthesis cache"""

PATCH_CV_NEW = """          const cacheVersion = 'v022.32';  // V022.32 CALIBRATION · invalidates v022.31 synthesis cache (V4 anchor changes synthesis output)"""

apply("CACHEVERSION_bump_v022.31→v022.32", PATCH_CV_OLD, PATCH_CV_NEW)


# ═══════════════════════════════════════════════════════════════════════════
# Write & report
# ═══════════════════════════════════════════════════════════════════════════
WORKER.write_text(src)
print(f"\n✓ V022.32 calibration applied · {applied} patches · {orig_len:,} → {len(src):,} chars (Δ +{len(src)-orig_len:,})")

print("""
═══════════════════════════════════════════════════════════════════════════
NEXT:
  node --check worker.js && ./fc-deploy-dev.sh

CACHE INVALIDATION (cacheVersion bumped automatically — but also nuke stale unknown-slug keys):

  for v in v022.30 v022.31; do
    for k in synth projection prostack trajpath coachvoices audience; do
      wrangler kv key delete --binding=FIELDCHECK_KV --remote \\
        "${k}:${v}:mens-basketball:unknown" 2>&1 | tail -1
    done
  done

SMOKE TEST EXPECTATIONS (post-V022.32):
  Tyran Stokes        composite ≈ 5.3  (raw from Haiku, no cap hit)
  Saniyah Hall        composite ≈ 5.3
  Cameron Boozer      composite ≈ 7.2  (Haiku produces this directly, no cap hit)
  Cooper Flagg        composite ≈ 7.5
  Caitlin Clark       composite ≈ 7.7-7.9
  Steph Curry         composite ≈ 9.0-9.3
  Tim Duncan          composite ≈ 9.6-9.7

The V022.31 hard caps stay as safety net. With V022.32 calibration, RAW scores
should match the bands directly so caps rarely fire.
═══════════════════════════════════════════════════════════════════════════
""")
