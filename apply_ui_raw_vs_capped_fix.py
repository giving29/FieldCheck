#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
UI FIX #2 · COMPOSITE RAW-vs-CAPPED DISPLAY BUG
═══════════════════════════════════════════════════════════════════════════
Root cause (May 26 nt diagnosis):
  API /verdict/player returns Tim Duncan correctly:
    - composite: 9.3 (top-level, V022.32-YX cap applied) ✓
    - composite_v022_31.raw: 9.9
    - composite_v022_31.cap: 9.3
  But fieldcheck-verdict.html line 3589 reads composite from chain:
    og.composite (nested overall_grade.composite — RAW 9.9 pre-cap)
       || data.composite (top-level — capped 9.3 ✓)
       || eg.composite

  og.composite wins because it's first AND non-null.
  Result: UI shows 9.9 ICON instead of 9.3 ELITE+ (tc(9.9)=ICON, tc(9.3)=ELITE+)

  This composite variable propagates to:
    - Line 3615: tier classification (tc(composite))
    - Line 3727: big-number display (.snum)
    - Line 3818: Composite snap card
    - Line 3948: radar overlay label
    - Line 3973-3977: interpretation text

  Fixing line 3589 cascades to all downstream displays.

Fix: reorder the chain so data.composite (top-level CAPPED value) is read
FIRST, falling back to og.composite/eg.composite only if data.composite null.
Single str_replace. Surgical. No other changes.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, hashlib
from pathlib import Path

VERDICT = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-raw-vs-capped-fix.bak')

print("═══ UI FIX #2 · COMPOSITE RAW vs CAPPED ═══\n")

if not VERDICT.exists():
    print("✗ fieldcheck-verdict.html not found · ABORT"); sys.exit(1)

content = VERDICT.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ fieldcheck-verdict.html: {size_before:,} bytes · sha={sha_before}")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("\n▸ Anchor detection...")

# Line 3589 composite read chain
old = "var composite=og.composite!=null?Number(og.composite):(data.composite!=null?Number(data.composite):(eg.composite!=null?Number(eg.composite):null));"

if content.count(old) != 1:
    print(f"✗ anchor count = {content.count(old)} (expected 1) · ABORT")
    sys.exit(1)
print("  ✓ A1 composite chain at line 3589")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(VERDICT, BACKUP)
print(f"\n▸ Backup: {BACKUP}")


# ─── P1: reorder chain so data.composite (top-level capped) is FIRST ───────
# Old: og || data || eg  (og.composite is RAW 9.9, wins)
# New: data || og || eg  (data.composite is CAPPED 9.3, wins)
new = "var composite=data.composite!=null?Number(data.composite):(og.composite!=null?Number(og.composite):(eg.composite!=null?Number(eg.composite):null));"

print("\n▸ P1: reorder composite chain · data.composite FIRST (capped)...")
content_new = content.replace(old, new, 1)
if content_new == content:
    print("✗ no-op · ABORT"); shutil.copy(BACKUP, VERDICT); sys.exit(1)
print(f"  ✓ delta {len(content_new)-len(content):+d}")


# ─── WRITE ─────────────────────────────────────────────────────────────────
VERDICT.write_text(content_new)
size_after = len(content_new)
sha_after = hashlib.sha256(content_new.encode()).hexdigest()[:12]
print(f"\n▸ fieldcheck-verdict.html · {size_after:,} bytes (delta {size_after-size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY ───────────────────────────────────────────────────────────
print("▸ Grep-verify (Tenet 47.1: EXACT substrings)...")
checks = [
    ("new chain present (data first)", new in content_new),
    ("old chain absent (og first)", old not in content_new),
    ("data.composite is FIRST", "var composite=data.composite!=null?Number(data.composite):(og.composite" in content_new),
    ("og.composite is SECOND now", "data.composite):(og.composite!=null?Number(og.composite):(eg.composite" in content_new),
    ("eg.composite still in chain", "eg.composite!=null?Number(eg.composite):null" in content_new),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring"); shutil.copy(BACKUP, VERDICT); sys.exit(1)


# ─── DONE ──────────────────────────────────────────────────────────────────
print()
print("═══════════════════════════════════════════════════════════════════════")
print(" UI FIX #2 APPLIED CLEAN · raw→capped composite display")
print("═══════════════════════════════════════════════════════════════════════")
print(f" fieldcheck-verdict.html · {size_after:,} bytes (delta {size_after-size_before:+d})")
print(f"")
print(f" Chain reordered at line 3589:")
print(f"   OLD: og.composite (raw 9.9) → data.composite → eg.composite")
print(f"   NEW: data.composite (capped 9.3) → og.composite → eg.composite")
print(f"")
print(f" Cascades to:")
print(f"   ✓ Big-number display (.snum) — was 9.9, now 9.3")
print(f"   ✓ Tier classification (tc()) — was ICON, now ELITE+")
print(f"   ✓ Composite snap card — was 9.9/10, now 9.3/10")
print(f"   ✓ Radar overlay label — was 9.9, now 9.3")
print(f"   ✓ Interpretation text — was 'Generational profile at 9.9', now 'Composite at 9.3'")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: ./fc-deploy-dev.sh, verify Duncan = 9.3 ELITE+, then ./fc-promote-prod.sh")
