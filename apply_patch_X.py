#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-X · PATCH X · WITHIN-LEVEL DECIMAL DIFFERENTIATION (THE MOAT)
═══════════════════════════════════════════════════════════════════════════
Root cause of the clustering at 5.4: the synthesis prompt asks Haiku for
INTEGER facet scores (line 3617). Integers kill decimal granularity.
Elite HS athletes all snap to facet=5 → composite=5.0 → cap floors to 5.4 →
zero within-tier spread (Stokes = Branch III = 5.4).

Patch X fixes this at the prompt layer (doesn't touch the cascade):
  1. Facet score: integer 0-10 → decimal 0.0-10.0 with one-decimal precision
  2. Add WITHIN-TIER DIFFERENTIATION section with explicit mid-tier decimal
     anchors (top-25 / top-100 / top-500 / varsity for HS · equivalents D1)
  3. Update JSON example "score": 7 → "score": 4.7 to anchor decimal usage
  4. Strengthen DISCIPLINE statement with within-tier spread requirement
  5. Bump cache v022.32u → v022.32x (invalidate ALL stale syntheses)

Expected battery impact:
  · HS composite distribution: median 5.4 → median ~4.3, max 5.4, min ~2.5
  · D1 composite: median 6.3 → median ~5.8, broader spread
  · Tyran Stokes ≠ Bruce Branch III ≠ HS varsity contributor (UTR-style)
  · Cap compliance NATURALLY improves (raws come in below cap by design)

Atomicity: backup → patch → grep-verify → node-check → restore on failure
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-X.bak')

print("═══ V022.32-X · PATCH X · WITHIN-LEVEL DECIMAL DIFFERENTIATION ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

if "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content:
    print("✗ Not on V022.32-U baseline · ABORT"); sys.exit(1)
print("  ✓ baseline = V022.32-U (6 patches)\n")


# ─── ANCHOR DETECTION (each anchor must be exactly 1) ──────────────────────
print("▸ Anchor detection...")

# A1: integer score instruction (line 3617)
a1_old = "- score: integer 0-10 (null only if absolutely no signal)"
if content.count(a1_old) != 1:
    print(f"✗ A1 integer-score instruction count = {content.count(a1_old)} · ABORT")
    sys.exit(1)
print("  ✓ A1 integer-score instruction")

# A2: JSON example "score": 7
a2_old = '"character": { "score": 7, "evidence": "...[source]...", "sources": ["maxpreps","reddit"], "confidence": "medium" }'
if content.count(a2_old) != 1:
    print(f"✗ A2 JSON example count = {content.count(a2_old)} · ABORT")
    sys.exit(1)
print("  ✓ A2 JSON example")

# A3: insertion point — after "Michael Jordan 1996 peak" line (end of calibration anchors)
a3_marker = "Michael Jordan 1996 peak                    → composite 9.9 (the only one)"
if content.count(a3_marker) != 1:
    print(f"✗ A3 Jordan anchor count = {content.count(a3_marker)} · ABORT")
    sys.exit(1)
print("  ✓ A3 Jordan anchor (insertion point)")

# A4: DISCIPLINE statement (need to find full line; pattern match)
a4_rx = re.compile(r"DISCIPLINE: If your facet scores would AVERAGE above the band ceiling for the athlete's tier[^\n]*", re.MULTILINE)
a4_m = a4_rx.search(content)
if not a4_m:
    print("✗ A4 DISCIPLINE statement not found · ABORT"); sys.exit(1)
a4_old = a4_m.group(0)
print(f"  ✓ A4 DISCIPLINE statement")

# A5: cache version
a5_old = "const cacheVersion = 'v022.32u'"
if content.count(a5_old) != 1:
    print(f"✗ A5 cache version count = {content.count(a5_old)} · ABORT"); sys.exit(1)
print("  ✓ A5 cache version")

# A6: banner
a6_rx = re.compile(r"// FIELDCHECK_WORKER_VERSION = V022\.32-U · TENET 47 ATOMIC · 6 patches[^\n]*")
a6_m = a6_rx.search(content)
if not a6_m:
    print("✗ A6 banner not found · ABORT"); sys.exit(1)
a6_old = a6_m.group(0)
print(f"  ✓ A6 banner\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP}\n")


# ─── P1: integer → decimal facet scoring ───────────────────────────────────
a1_new = "- score: number 0.0-10.0 with ONE DECIMAL PRECISION (e.g., 4.3 not 4, 5.2 not 5) — null only if absolutely no signal"
print("▸ P1: integer → decimal facet scoring...")
content_v1 = content.replace(a1_old, a1_new, 1)
if content_v1 == content:
    print("✗ P1 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v1)-len(content):+d}\n")


# ─── P2: JSON example uses decimal ─────────────────────────────────────────
a2_new = '"character": { "score": 4.7, "evidence": "...[source]...", "sources": ["maxpreps","reddit"], "confidence": "medium" }'
print("▸ P2: JSON example with decimal...")
content_v2 = content_v1.replace(a2_old, a2_new, 1)
if content_v2 == content_v1:
    print("✗ P2 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v2)-len(content_v1):+d}\n")


# ─── P3: insert WITHIN-TIER DIFFERENTIATION section after Jordan anchor ────
within_tier_section = """  • Michael Jordan 1996 peak                    → composite 9.9 (the only one)

WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):

Decimals matter. Athletes within a tier MUST differentiate via decimals. Two HS athletes are NEVER both 5.4 unless they're both consensus-#1 nationally. Use the FULL decimal range — don't cluster at the ceiling.

HS DECIMAL spread (use full range 2.0-5.4):
  • HS #1 nationally (Stokes/Hall tier)         → composite 5.2-5.4 · top facets 5.0-6.0
  • HS top 10 (5-star top-10)                    → composite 4.8-5.2 · facets 4.7-5.5
  • HS top 25 (5-star top-25)                    → composite 4.4-4.8 · facets 4.3-5.2
  • HS top 100 (5-star or strong 4-star)        → composite 4.0-4.4 · facets 3.8-4.8
  • HS top 500 (4-star)                          → composite 3.5-4.0 · facets 3.4-4.4
  • HS strong varsity / 3-star                   → composite 3.0-3.5 · facets 3.0-4.0
  • HS varsity contributor                       → composite 2.5-3.0 · facets 2.5-3.5
  • HS rotation / developing                     → composite <2.5

D1 DECIMAL spread (use full range 4.5-7.4):
  • D1 All-American hard cap (Boozer/Dybantsa)  → composite 7.0-7.4 · facets 7.0-7.4
  • D1 conference Player of the Year             → composite 6.6-7.0 · facets 6.4-7.2
  • D1 conference starter standout                → composite 6.2-6.6 · facets 6.0-6.8
  • D1 starter                                   → composite 5.8-6.2 · facets 5.5-6.5
  • D1 rotation player                           → composite 5.2-5.8 · facets 4.8-6.0
  • D1 bench / depth                             → composite 4.5-5.2 · facets 4.2-5.5

D2/D3/JUCO/NAIA DECIMAL spread (use full range 4.0-6.8):
  • Top D2 AA / D3 Jostens / JUCO standout       → composite 6.4-6.8 · facets 6.0-6.8
  • D2/D3 conference starter                     → composite 5.6-6.2 · facets 5.2-6.4
  • D2/D3 rotation                               → composite 4.8-5.4 · facets 4.4-5.6
  • D2/D3 bench                                  → composite 4.0-4.8 · facets 3.8-5.0

THE TEST: After scoring, if your 8 facets all end up with the SAME or VERY CLOSE numbers, you're under-using the decimal range. Real athletes have asymmetric profiles — high physical + lower mental_iq, or high coachability + lower competitiveness. SPREAD the facets. Use decimals like 4.3, 5.1, 6.7 — not just round 4, 5, 6, 7.
"""

a3_old_block = "  • Michael Jordan 1996 peak                    → composite 9.9 (the only one)"
print("▸ P3: insert WITHIN-TIER DIFFERENTIATION section...")
content_v3 = content_v2.replace(a3_old_block, within_tier_section, 1)
if content_v3 == content_v2:
    print("✗ P3 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v3)-len(content_v2):+d}\n")


# ─── P4: strengthen DISCIPLINE statement ───────────────────────────────────
a4_new = a4_old + " ADDITIONALLY: facet scores within the same tier MUST differentiate via decimals. If two HS athletes both end up with facet=5.0, you're not using the full range. The 5th best HS player is NOT the same as the 50th. Use 4.7 vs 5.1 vs 5.3 to capture real ranking differences."
print("▸ P4: strengthen DISCIPLINE statement...")
content_v4 = content_v3.replace(a4_old, a4_new, 1)
if content_v4 == content_v3:
    print("✗ P4 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v4)-len(content_v3):+d}\n")


# ─── P5: cache version bump ────────────────────────────────────────────────
a5_new = "const cacheVersion = 'v022.32x'"
print("▸ P5: cache v022.32u → v022.32x...")
content_v5 = content_v4.replace(a5_old, a5_new, 1)
if content_v5 == content_v4:
    print("✗ P5 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v5)-len(content_v4):+d}\n")


# ─── P6: banner bump ───────────────────────────────────────────────────────
a6_new = "// FIELDCHECK_WORKER_VERSION = V022.32-X · TENET 47 ATOMIC · 7 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, X (decimal facet scoring + within-tier spread anchors · THE MOAT)"
print("▸ P6: banner V022.32-U → V022.32-X...")
content_final = content_v5.replace(a6_old, a6_new, 1)
if content_final == content_v5:
    print("✗ P6 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓\n")


# ─── WRITE ──────────────────────────────────────────────────────────────────
WORKER.write_text(content_final)
size_after = len(content_final)
sha_after = hashlib.sha256(content_final.encode()).hexdigest()[:12]
print(f"▸ worker.js · {size_after:,} bytes (delta {size_after-size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY ───────────────────────────────────────────────────────────
print("▸ Grep-verify (Tenet 47.1)...")
checks = [
    ("decimal score instruction", "score: number 0.0-10.0 with ONE DECIMAL PRECISION" in content_final),
    ("decimal JSON example", '"character": { "score": 4.7,' in content_final),
    ("WITHIN-TIER section title", "WITHIN-TIER DIFFERENTIATION (THE MOAT" in content_final),
    ("HS spread anchors", "HS top 100 (5-star or strong 4-star)" in content_final),
    ("D1 spread anchors", "D1 conference Player of the Year" in content_final),
    ("D2/D3 spread anchors", "Top D2 AA / D3 Jostens / JUCO standout" in content_final),
    ("THE TEST instruction", "Use decimals like 4.3, 5.1, 6.7" in content_final),
    ("DISCIPLINE strengthened", "facet scores within the same tier MUST differentiate via decimals" in content_final),
    ("banner V022.32-X", "V022.32-X · TENET 47 ATOMIC · 7 patches" in content_final),
    ("cache v022.32x", "'v022.32x'" in content_final),
    ("old integer-score removed", "- score: integer 0-10 (null only if absolutely no signal)" not in content_final),
    ("old V022.32-U banner removed", "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content_final),
    ("old cache v022.32u removed", "const cacheVersion = 'v022.32u'" not in content_final),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print()


# ─── NODE SYNTAX CHECK ─────────────────────────────────────────────────────
print("▸ Node syntax check...")
result = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"✗ node --check FAILED · restoring")
    print(f"  stderr: {result.stderr[:800]}")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ passed\n")


# ─── DONE ──────────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" V022.32-X PATCH X APPLIED CLEAN · within-level decimal differentiation")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-U → V022.32-X · cache: v022.32u → v022.32x")
print(f" Synthesis prompt modifications (synthesizeEightFacets line 3357):")
print(f"   1. Facet scoring: integer 0-10 → decimal 0.0-10.0 (one decimal precision)")
print(f"   2. NEW within-tier differentiation section with HS/D1/D2/D3 spread anchors")
print(f"   3. JSON example uses decimal (\"score\": 4.7)")
print(f"   4. DISCIPLINE statement strengthened to require within-tier spread")
print(f"   5. Cache bumped to invalidate ALL stale cached syntheses")
print(f"")
print(f" Expected battery impact:")
print(f"   HS composite: median 5.4 → ~4.3 · range 2.5-5.4 (real spread)")
print(f"   D1 composite: median 6.3 → ~5.8 · range 4.5-7.4")
print(f"   Stokes ≠ Branch III ≠ varsity (UTR-style)")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: bump canonical V5.26 → V5.30, deploy, run battery, validate spread")
