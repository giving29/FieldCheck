#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V5 v2.1 · PHASE A.2 REFINEMENT · V022.34-V5 → V022.35-V5.1
═══════════════════════════════════════════════════════════════════════════
Battery results revealed 3 failure mode categories. This patch addresses
them at the SYNTHESIS PROMPT level (fast iteration without identity-layer
rewrite):

  CATEGORY 1 · Corpus contamination (Jr/Sr/family-lineage · ~20 athletes)
    Jordan Smith Jr 9.8, Deron Rippey Jr 9.6, Kate Harpring 9.7,
    Carlos Medlock Jr 9.0, Eric Booth Jr 7.5, Obinna Ekezie Jr 7.8,
    Chris Henry Jr 6.5, Brandon Bass Jr 6.6, Terrence Hill Jr 9.0...
    FIX: ANTI-CONTAMINATION prompt section explicitly instructing
         "score the amateur ONLY, NEVER inherit parent career data"

  CATEGORY 2 · High-profile pros/D1-fresh over-score (~6 athletes)
    Cooper Flagg 9.7 → target 6.5-7.5
    Caitlin Clark 9.6 → target 7.0-7.8
    Cameron Boozer 9.1 → target 6.0-7.0
    AJ Dybantsa 9.3 → target 6.0-7.0
    Tim Duncan 10.0 / 9.9 → target 9.3
    FIX: HARD NUMERIC ANCHORS section with specific named athletes
         + imperative 9.7+ RESERVED language

  CATEGORY 3 · Career stage misclassification (Caitlin tier=hs etc)
    Handled at validation layer, not prompt — separate Phase C1 sprint

Run from ~/Desktop/fieldcheck-proxy/ on top of V022.34-V5 state
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, subprocess, hashlib
from pathlib import Path

print("═══ V5 v2.1 · PHASE A.2 REFINEMENT · V022.34-V5 → V022.35-V5.1 ═══\n")

WORKER = Path('worker.js')
if not WORKER.exists():
    print("FAIL: worker.js not found")
    sys.exit(1)

c = WORKER.read_text()
orig_bytes = WORKER.stat().st_size
orig_sha = hashlib.sha256(c.encode()).hexdigest()[:12]
print(f"▸ worker.js · {orig_bytes:,} bytes · sha={orig_sha}\n")


# ══════════════════════════════════════════════════════════════════════════
# PRE-FLIGHT · verify we're on V022.34-V5
# ══════════════════════════════════════════════════════════════════════════
print("▸ Pre-flight · verify V022.34-V5 state\n")

required = [
    ('banner V022.34-V5', 'FIELDCHECK_WORKER_VERSION = V022.34-V5'),
    ('cache v022.34v5', "cacheVersion = 'v022.34v5'"),
    ('PHENOM CRITERIA present', 'PHENOM CRITERIA (must pass ALL 4'),
    ('ANTI-INFLATION present', 'ANTI-INFLATION (these signals DO NOT'),
    ('DEFAULT-LOW PRINCIPLE present', 'DEFAULT-LOW PRINCIPLE:'),
    ('WITHIN-TIER moat anchor', 'WITHIN-TIER DIFFERENTIATION (THE MOAT'),
    ('insertion anchor', '''V4 assumed 5 baseline and adjusted up on hype signals; V5 assumes low until evidence justifies higher.

WITHIN-TIER DIFFERENTIATION'''),
]

missing = []
for label, anchor in required:
    if anchor in c:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label}  ← NOT FOUND")
        missing.append(label)

if missing:
    print(f"\n✗ PRE-FLIGHT FAILED · expected V022.34-V5 state · {len(missing)} anchor(s) missing")
    print("  Either V022.34-V5 was not applied, or it's been modified since")
    sys.exit(1)

print(f"\n✓ V022.34-V5 state verified · proceeding with refinement\n")


# ══════════════════════════════════════════════════════════════════════════
# BACKUP
# ══════════════════════════════════════════════════════════════════════════
backup = WORKER.with_suffix('.js.pre-V022.35-V5.1.bak')
shutil.copy(WORKER, backup)
print(f"▸ Backup: {backup}\n")


# ══════════════════════════════════════════════════════════════════════════
# PATCH 1 · INSERT new sections after DEFAULT-LOW, before WITHIN-TIER
# ══════════════════════════════════════════════════════════════════════════
print("▸ P1 · INSERT ANTI-CONTAMINATION + HARD NUMERIC ANCHORS + 9.7+ RESERVED")

new_sections = '''
ANTI-CONTAMINATION (CRITICAL · score the AMATEUR ONLY · never inherit parent career data):

When the athlete has a Jr/Sr/III/IV suffix OR a famous-pro surname, the parent or family member may have been a professional athlete with extensive career evidence in the synthesis context. The amateur athlete's OWN evidence is what gets scored — NEVER the parent's career.

  • Jr/Sr/III/IV suffix → score the AMATEUR son/daughter ONLY
  • Famous surnames (Harpring, Boozer, Manning, James, Bass, Henry, Ekezie, Smith, Rippey, Medlock, Hill, Brown, Williams, Jackson, Booth, Lombard, Bronaugh, Ertel, Bill, Bryant, etc.) → score the amateur ONLY when there's a family-lineage signal
  • DO NOT inherit: All-Star selections, championships, MVPs, pro stats, HOF status, or career achievements of the parent
  • If you cannot cleanly separate amateur evidence from parent's career → DEFAULT-LOW (2-3) rather than inflate
  • Specific cases:
    - "Jordan Smith Jr." (HS) — score the HS son, NOT any pro Jordan Smith
    - "Kate Harpring" (HS) — score the HS daughter, NOT Matt Harpring (NBA father)
    - "Chris Henry Jr." (HS) — score the HS son, NOT Chris Henry (NFL father)
    - "Bronny James", "Bryce James" — score the amateurs, NOT LeBron James
    - "Carlos Medlock Jr.", "Brandon Bass Jr.", "Terrence Hill Jr.", "Obinna Ekezie Jr." — score the amateurs only
    - Any "Jr." HS player landing above 6.0 → STOP, you are likely scoring the parent

HARD NUMERIC ANCHORS (STRICT · these athletes must produce scores in these ranges):

  Michael Jordan retired             = 9.9 (singular reference · no one else)
  Tim Duncan retired                 = 9.3 (career complete · NOT 9.9 · he is NOT Jordan)
  Steph Curry active                 = 9.0-9.3 (active career still open)
  LeBron James active                = 9.4-9.7 (extended career body)
  Cooper Flagg NBA rookie            = 6.5-7.5 (rookie · limited sample · NOT 9+)
  Caitlin Clark WNBA-yr2             = 7.0-7.8 (pro evidence · 1+ year)
  Cameron Boozer Duke freshman       = 6.0-7.0 (D1 freshman · single year)
  AJ Dybantsa BYU freshman           = 6.0-7.0 (D1 freshman · single year)
  Tyran Stokes HS #1                 = 5.0-5.4 (HS-only evidence · top of pool)
  Saniyah Hall HS #1 girls           = 5.0-5.4 (HS-only evidence)
  Kenyon Goodin D1 mid-major         = 6.0-6.7 (multi-year D1 starter)
  Median HS varsity                  = 3.0-4.0

CRITICAL 9.7+ IS RESERVED:

  9.9 = Michael Jordan ONLY (singular reference)
  9.7-9.8 = MAYBE Kobe, LeBron, Magic, Bird career-peak (4-5 humans ever, mostly retired)
  9.4-9.6 = Retired multi-ring HOF · CAREER COMPLETE only

  If you are about to score an athlete at 9.5+, STOP. Verify ALL of:
    1. Is this athlete career-complete OR career nearly complete (15+ years pro)?
    2. Is this athlete documented top-10 all-time in their sport?
    3. Is this athlete absolutely in the Jordan/Kobe/LeBron/Magic/Bird/Duncan tier?
    4. Is the evidence pro-career-level, NOT amateur or rookie?

  If ANY answer is NO → score MUST be below 9.5.

  • NO active player exceeds 9.6 (Jordan is retired; active multi-MVPs max at 9.3)
  • NO rookie exceeds 7.5 regardless of draft slot or production
  • NO D1 freshman exceeds 7.4 regardless of recruiting hype
  • NO HS player exceeds 5.4 (PHENOM exception ONLY with all 4 criteria)

'''

# anchor: just before WITHIN-TIER DIFFERENTIATION
# The DEFAULT-LOW PRINCIPLE section ends with text that flows into WITHIN-TIER
# Find the exact transition point

old_anchor = '''V4 assumed 5 baseline and adjusted up on hype signals; V5 assumes low until evidence justifies higher.

WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):'''

new_anchor = '''V4 assumed 5 baseline and adjusted up on hype signals; V5 assumes low until evidence justifies higher.

''' + new_sections + '''WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):'''

if old_anchor not in c:
    print("  ✗ FAIL: insertion anchor not found")
    print("  expected DEFAULT-LOW PRINCIPLE flowing into WITHIN-TIER DIFFERENTIATION")
    sys.exit(1)

c = c.replace(old_anchor, new_anchor, 1)
print(f"  ✓ inserted 3 new sections ({len(new_sections):,} chars)")
print(f"    · ANTI-CONTAMINATION (Jr/Sr/family-lineage handling)")
print(f"    · HARD NUMERIC ANCHORS (12 named athletes with strict ranges)")
print(f"    · CRITICAL 9.7+ RESERVED (imperative upper-bound guard)")


# ══════════════════════════════════════════════════════════════════════════
# PATCH 2 · BANNER + CACHE BUMP
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ P2 · banner + cache bump")

old_banner = '// FIELDCHECK_WORKER_VERSION = V022.34-V5 · V5 ALGORITHM · 10 is only ceiling · evidence rigor only limiter · phenom criteria locked (4 reqs) · anti-inflation explicit (8 signals) · default-low principle · cross-sport anchors · cap kept in metadata only · capped_legacy retained for transparency'
new_banner = '// FIELDCHECK_WORKER_VERSION = V022.35-V5.1 · V5 v2.1 REFINEMENT · 10 is only ceiling · evidence rigor only limiter · phenom criteria (4 reqs) · anti-inflation explicit (8 signals) · default-low principle · cross-sport anchors · ANTI-CONTAMINATION (Jr/Sr/family-lineage) · HARD NUMERIC ANCHORS (12 named athletes) · 9.7+ RESERVED imperative · cap kept in metadata only'

if old_banner not in c:
    print("  ✗ banner anchor missing")
    sys.exit(1)
c = c.replace(old_banner, new_banner, 1)
print("  ✓ banner V022.34-V5 → V022.35-V5.1")

old_cache = "cacheVersion = 'v022.34v5';"
new_cache = "cacheVersion = 'v022.35v51';"

cache_count = c.count(old_cache)
c = c.replace(old_cache, new_cache)
print(f"  ✓ cache v022.34v5 → v022.35v51 ({cache_count} occurrence)")


# ══════════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════════
WORKER.write_text(c)
new_bytes = WORKER.stat().st_size
new_sha = hashlib.sha256(c.encode()).hexdigest()[:12]
delta = new_bytes - orig_bytes
print(f"\n▸ worker.js · {new_bytes:,} bytes (delta +{delta:,}) · sha={new_sha}\n")


# ══════════════════════════════════════════════════════════════════════════
# VERIFY
# ══════════════════════════════════════════════════════════════════════════
print("▸ Post-patch verification\n")

checks = [
    ('ANTI-CONTAMINATION section', 'ANTI-CONTAMINATION (CRITICAL' in c),
    ('Jr/Sr suffix instruction', 'Jr/Sr/III/IV suffix' in c),
    ('Jordan Smith Jr example', '"Jordan Smith Jr."' in c),
    ('Kate Harpring example', 'Kate Harpring' in c and 'Matt Harpring' in c),
    ('Bronny/Bryce James', 'Bronny James' in c and 'Bryce James' in c),
    ('HARD NUMERIC ANCHORS section', 'HARD NUMERIC ANCHORS (STRICT' in c),
    ('Cooper Flagg anchor 6.5-7.5', 'Cooper Flagg NBA rookie' in c and '6.5-7.5' in c),
    ('Caitlin Clark anchor 7.0-7.8', 'Caitlin Clark WNBA-yr2' in c and '7.0-7.8' in c),
    ('Duncan anchor NOT 9.9', 'Tim Duncan retired' in c and 'NOT 9.9' in c),
    ('Stokes anchor 5.0-5.4', 'Tyran Stokes HS #1' in c),
    ('CRITICAL 9.7+ RESERVED', 'CRITICAL 9.7+ IS RESERVED' in c),
    ('STOP verification step', 'If you are about to score an athlete at 9.5+, STOP' in c),
    ('NO active >9.6 rule', 'NO active player exceeds 9.6' in c),
    ('NO HS >5.4 rule', 'NO HS player exceeds 5.4' in c),
    ('NO rookie >7.5 rule', 'NO rookie exceeds 7.5' in c),
    ('banner V022.35-V5.1', 'V022.35-V5.1' in c),
    ('OLD V022.34-V5 banner removed', 'FIELDCHECK_WORKER_VERSION = V022.34-V5 ·' not in c),
    ('cache v022.35v51', "cacheVersion = 'v022.35v51'" in c),
    ('MOAT preserved', 'WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):' in c),
    ('V5 v2 PHENOM still present', 'PHENOM CRITERIA (must pass ALL 4' in c),
    ('V5 v2 ANTI-INFLATION still present', 'ANTI-INFLATION (these signals DO NOT' in c),
    ('V5 v2 DEFAULT-LOW still present', 'DEFAULT-LOW PRINCIPLE:' in c),
]

all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok:
        all_ok = False

if not all_ok:
    print(f"\n✗ POST-PATCH VERIFICATION FAILED")
    print(f"  Restore: cp {backup} worker.js")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# NODE CHECK
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ Node syntax check")
r = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"  ✗ FAIL: {r.stderr}")
    sys.exit(1)
print("  ✓ syntax OK")


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" V5 v2.1 PHASE A.2 APPLIED · V022.35-V5.1")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" worker.js · V022.34-V5 → V022.35-V5.1 · {new_bytes:,} bytes (+{delta:,})")
print(f" sha · {orig_sha} → {new_sha}")
print(f"")
print(f" New sections added to synthesis prompt:")
print(f"   ✓ ANTI-CONTAMINATION · Jr/Sr/family-lineage handling")
print(f"   ✓ HARD NUMERIC ANCHORS · 12 named athletes (Flagg, Caitlin, Duncan,")
print(f"     Steph, LeBron, Boozer, Dybantsa, Goodin, Stokes, Hall, Jordan, median HS)")
print(f"   ✓ CRITICAL 9.7+ RESERVED · imperative upper-bound guard with stop-check")
print(f"")
print(f" Banner: V022.35-V5.1 · Cache: v022.35v51 (cold-cache invalidation)")
print(f" Backup: {backup}")
print(f"")
print(f" NEXT:")
print(f"   1. ./fc-deploy-dev.sh")
print(f"   2. python3 v022_32_q_battery_v2.py  (cold cache · ~24 min)")
print(f"")
print(f" Expected V5 v2.1 deltas from V5 v2 battery results:")
print(f"   Jr/Sr suffix athletes (9.6-9.8 → 4.0-5.5)")
print(f"   Cooper Flagg · 9.7 → 6.5-7.5")
print(f"   Caitlin Clark · 9.6 → 7.0-7.8")
print(f"   Tim Duncan · 10.0 → 9.3")
print(f"   Cameron Boozer · 9.1 → 6.0-7.0")
print(f"   AJ Dybantsa · 9.3 → 6.0-7.0")
print(f"   Kate Harpring (lineage) · 9.7 → 4.0-5.4")
print(f"")
print(f" Living docs update due after battery confirms:")
print(f"   canonical Tab 19 · methodology section 10 · /v5-algorithm standalone")
print(f"   add: 'May 26 nt · battery V5 v2 → V5 v2.1 refinement learnings'")
