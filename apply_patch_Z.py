#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-Z · PATCH Z · HS DECIMAL FORCING (BREAK THE CLUSTER)
═══════════════════════════════════════════════════════════════════════════
V022.32-YX battery (May 26 late) showed HS still clusters at 5.4 because
cap floors all raws ≥5.4. Haiku is scoring HS facets at 5-6 range (above
cap). To get UTR-style within-tier spread, Haiku must default HS facets
to 3.5-4.5 range (most of the HS pool) and reserve 5+ for HS top-25.

Patch Z inserts a HS CALIBRATION INSTINCT section at the TOP of the
synthesis prompt — before the existing REFERENCE BANDS — so it primes
Haiku's mental model before scoring decisions.

Surgical ops:
  1. Insert HS CALIBRATION INSTINCT section before REFERENCE BANDS
  2. Bump cache v022.32yx → v022.32z (invalidate stale syntheses)
  3. Bump banner V022.32-YX → V022.32-Z

Tenet 47.6: grep-verify with EXACT substring from inserted text.
Tenet 47.4: prompt-only, no _v22_31_* mutations · const-safe.

Atomicity: backup → patch → grep-verify → node-check → restore on failure
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-Z.bak')

print("═══ V022.32-Z · PATCH Z · HS DECIMAL FORCING ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

if "V022.32-YX · TENET 47 ATOMIC · 8 patches" not in content:
    print("✗ Not on V022.32-YX baseline · ABORT"); sys.exit(1)
print("  ✓ baseline = V022.32-YX (8 patches)\n")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("▸ Anchor detection...")

# A1: REFERENCE BANDS heading (insertion point — Z goes BEFORE this)
a1_marker = "REFERENCE BANDS — these are HARD CAPS, not suggestions:"
if content.count(a1_marker) != 1:
    print(f"✗ A1 REFERENCE BANDS count = {content.count(a1_marker)} · ABORT"); sys.exit(1)
print("  ✓ A1 REFERENCE BANDS heading")

# A2: cache version (currently v022.32yx)
a2_old = "const cacheVersion = 'v022.32yx'"
if content.count(a2_old) != 1:
    print(f"✗ A2 cache version count = {content.count(a2_old)} · ABORT"); sys.exit(1)
print("  ✓ A2 cache version")

# A3: banner
a3_rx = re.compile(r"// FIELDCHECK_WORKER_VERSION = V022\.32-YX · TENET 47 ATOMIC · 8 patches[^\n]*")
a3_m = a3_rx.search(content)
if not a3_m:
    print("✗ A3 banner not found · ABORT"); sys.exit(1)
a3_old = a3_m.group(0)
print("  ✓ A3 banner\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP}\n")


# ─── P1: insert HS CALIBRATION INSTINCT block BEFORE REFERENCE BANDS ───────
hs_forcing_block = """HS CALIBRATION INSTINCT (READ THIS FIRST — most common miscalibration):

Your default instinct for HS athletes should be facets in the 3.5-4.5 range. Most HS athletes (90%+) score facets in 3.0-4.8 range. The 5.0+ band is RESERVED for HS top-25 nationally. The 5.4 composite cap is ONLY for HS #1 nationally (Stokes/Hall tier).

DEFAULT HS FACET RANGES (memorize these):
  • HS varsity / 3-star recruit (median HS):    facets 3.0-4.0  → composite 3.0-3.5
  • HS top 500 / 4-star recruit:                 facets 3.5-4.5  → composite 3.5-4.0
  • HS top 100 / strong 4-star or 5-star fringe: facets 4.0-4.8  → composite 4.0-4.4
  • HS top 25 / consensus 5-star:                facets 4.3-5.2  → composite 4.4-4.7
  • HS top 10:                                    facets 4.7-5.5  → composite 4.7-5.0
  • HS top 5:                                     facets 4.8-5.8  → composite 5.0-5.2
  • HS #1 nationally (Stokes/Hall):              facets 5.0-6.0  → composite 5.2-5.4 (HARD CAP)

COMMON MISCALIBRATION (the bug to avoid):
You see an "elite HS prospect" with NIL deals and recruit hype, and your instinct is to score facets at 6-7. WRONG. Even Tyran Stokes (HS #1) facets at 5.0-6.0 — composite cap 5.4. NIL deals and recruit hype do NOT lift HS facets above 5.0 unless top-25 national evidence is explicit.

HARD RULE: If you score a HS athlete's facet above 5.0, you MUST cite explicit top-25 national evidence (5-star consensus, ESPN top-25, MaxPreps POY, multiple D1 high-major offers). Otherwise, the facet must be ≤5.0. If you can't cite top-100 national evidence, the facet must be ≤4.5.

DEFAULT INSTINCT (memorize):
  • HS facets default = 3.5-4.5
  • D1 facets default = 5.5-6.5 (AA hard cap 7.4)
  • D2/D3/JUCO facets default = 4.5-5.5 (cap 6.8)
  • Pro facets scale per V4 bands below

══════════════════════════════════════════════════════════════════════════

REFERENCE BANDS — these are HARD CAPS, not suggestions:"""

print("▸ P1: insert HS CALIBRATION INSTINCT block before REFERENCE BANDS...")
content_v1 = content.replace(a1_marker, hs_forcing_block, 1)
if content_v1 == content:
    print("✗ P1 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v1)-len(content):+d}\n")


# ─── P2: cache version bump ────────────────────────────────────────────────
a2_new = "const cacheVersion = 'v022.32z'"
print("▸ P2: cache v022.32yx → v022.32z...")
content_v2 = content_v1.replace(a2_old, a2_new, 1)
if content_v2 == content_v1:
    print("✗ P2 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v2)-len(content_v1):+d}\n")


# ─── P3: banner bump ───────────────────────────────────────────────────────
a3_new = "// FIELDCHECK_WORKER_VERSION = V022.32-Z · TENET 47 ATOMIC · 9 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, Y, X, Z (HS decimal forcing · break the cluster · default HS facets 3.5-4.5)"
print("▸ P3: banner V022.32-YX → V022.32-Z...")
content_final = content_v2.replace(a3_old, a3_new, 1)
if content_final == content_v2:
    print("✗ P3 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓\n")


# ─── WRITE ─────────────────────────────────────────────────────────────────
WORKER.write_text(content_final)
size_after = len(content_final)
sha_after = hashlib.sha256(content_final.encode()).hexdigest()[:12]
print(f"▸ worker.js · {size_after:,} bytes (delta {size_after-size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY (Tenet 47.6: EXACT substrings) ────────────────────────────
print("▸ Grep-verify (Tenet 47.1 + 47.6)...")
checks = [
    ("HS CALIBRATION INSTINCT header", "HS CALIBRATION INSTINCT (READ THIS FIRST" in content_final),
    ("default range statement", "default instinct for HS athletes should be facets in the 3.5-4.5 range" in content_final),
    ("90% range claim", "Most HS athletes (90%+) score facets in 3.0-4.8 range" in content_final),
    ("DEFAULT HS FACET RANGES table", "DEFAULT HS FACET RANGES (memorize these)" in content_final),
    ("HS varsity anchor", "HS varsity / 3-star recruit (median HS)" in content_final),
    ("HS #1 anchor", "HS #1 nationally (Stokes/Hall)" in content_final),
    ("MISCALIBRATION warning", "COMMON MISCALIBRATION (the bug to avoid)" in content_final),
    ("NIL/recruit warning", "NIL deals and recruit hype do NOT lift HS facets above 5.0" in content_final),
    ("HARD RULE", "If you score a HS athlete's facet above 5.0, you MUST cite" in content_final),
    ("DEFAULT INSTINCT memorize", "HS facets default = 3.5-4.5" in content_final),
    ("D1 default", "D1 facets default = 5.5-6.5" in content_final),
    ("REFERENCE BANDS preserved", "REFERENCE BANDS — these are HARD CAPS, not suggestions" in content_final),
    ("banner V022.32-Z", "V022.32-Z · TENET 47 ATOMIC · 9 patches" in content_final),
    ("cache v022.32z", "'v022.32z'" in content_final),
    ("Patch Y still present", "V022.32-Y · PATCH Y · stage=unknown fallback" in content_final),
    ("Patch X decimal still present", "score: number 0.0-10.0 with ONE DECIMAL PRECISION" in content_final),
    ("WITHIN-TIER section still present", "WITHIN-TIER DIFFERENTIATION (THE MOAT" in content_final),
    ("old V022.32-YX banner removed", "V022.32-YX · TENET 47 ATOMIC · 8 patches" not in content_final),
    ("old cache v022.32yx removed", "const cacheVersion = 'v022.32yx'" not in content_final),
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
print(" V022.32-Z APPLIED CLEAN · HS DECIMAL FORCING")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-YX → V022.32-Z · cache: v022.32yx → v022.32z")
print(f"")
print(f" New HS CALIBRATION INSTINCT section forces Haiku to:")
print(f"   • Default HS facets to 3.5-4.5 (not 5-6 as before)")
print(f"   • Require explicit top-25 evidence for facet >5.0")
print(f"   • Reserve 5+ band for HS top-25 nationally only")
print(f"   • Recognize NIL/hype DOES NOT lift HS scores above 5.0")
print(f"")
print(f" Expected V022.32-Z battery vs V022.32-YX:")
print(f"   HS median composite: 5.4 → 4.2 (real spread emerges below cap)")
print(f"   HS distribution range: 2.5-5.4 (vs current cluster at 5.4)")
print(f"   Stokes ≠ Branch III ≠ varsity (UTR-style at last)")
print(f"   D1 unchanged (Patch Z is HS-specific)")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: deploy, battery, then UI fix (polygon + new articulation)")
