#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
UI FIX · FC17 POLYGON GATE FOR NON-FC17 PLAYERS
═══════════════════════════════════════════════════════════════════════════
Root cause (May 26 nt diagnosis): fieldcheck-verdict.html has tryMount() in
the IIFE tail that unconditionally:
  1. Clears polygon container (ovl.innerHTML = '')
  2. Calls window.FC17_POLYGON.mount() which silently fails for non-FC17 data
  3. Hides ALL legacy (.scpanel, .ibox, .radleg, .radhow, "// At a glance",
     eg-timeline/drift/overlay subtabs, legacy tier badges)

For Tim Duncan / Tyran Stokes / 99% of athletes WITHOUT hardcoded FC17 data
(only Flagg/Caleb/Caitlin/Skinner have it), this leaves a BLANK polygon
area with no fallback.

Fix: insert FC17 availability gate after the idempotent check. If
FC17_POLYGON.isAvailable(p.name) returns false, early-return BEFORE the
unconditional clear + hide. Legacy renders normally for non-FC17 players.

Surgical: ONE str_replace, ONE gate inserted. ~7 lines.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, hashlib
from pathlib import Path

VERDICT = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-fc17-gate.bak')

print("═══ UI FIX · FC17 POLYGON GATE ═══\n")

if not VERDICT.exists():
    print("✗ fieldcheck-verdict.html not found · ABORT"); sys.exit(1)

content = VERDICT.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ fieldcheck-verdict.html: {size_before:,} bytes · sha={sha_before}")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("\n▸ Anchor detection...")

# A1: the idempotent check line in tryMount() — must be unique to find the right tryMount
anchor = "if (ovl.querySelector('.fc17-polygon-root')) return; // already mounted - idempotent"
if content.count(anchor) != 1:
    print(f"✗ anchor count = {content.count(anchor)} · ABORT")
    sys.exit(1)
print("  ✓ A1 idempotent check line (insertion point)")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(VERDICT, BACKUP)
print(f"\n▸ Backup: {BACKUP}")


# ─── P1: insert FC17 availability gate AFTER idempotent check ──────────────
new_block = """if (ovl.querySelector('.fc17-polygon-root')) return; // already mounted - idempotent

    // ─── FC17 AVAILABILITY GATE (UI FIX May 26 nt · prevents blank polygon for non-FC17 players)
    // Without this gate: tryMount() unconditionally clears + hides legacy for ALL players, but
    // FC17_POLYGON.mount() only succeeds for the 4 hardcoded data files (Flagg/Caleb/Caitlin/
    // Skinner). For every other player (Tim Duncan, Stokes, 99% of athletes) the result is a
    // BLANK polygon area with hidden legacy. With this gate: non-FC17 players early-return
    // and legacy polygon + score panel + "// At a glance" + interpretation render normally.
    if (!window.FC17_POLYGON || !window.FC17_POLYGON.isAvailable(p.name)) {
      return;
    }"""

print("\n▸ P1: insert FC17 availability gate...")
content_new = content.replace(anchor, new_block, 1)
if content_new == content:
    print("✗ P1 no-op · ABORT"); shutil.copy(BACKUP, VERDICT); sys.exit(1)
print(f"  ✓ delta {len(content_new)-len(content):+d}")


# ─── WRITE ─────────────────────────────────────────────────────────────────
VERDICT.write_text(content_new)
size_after = len(content_new)
sha_after = hashlib.sha256(content_new.encode()).hexdigest()[:12]
print(f"\n▸ fieldcheck-verdict.html · {size_after:,} bytes (delta +{size_after-size_before}) · sha={sha_after}\n")


# ─── GREP-VERIFY (Tenet 47.6: EXACT substrings) ────────────────────────────
print("▸ Grep-verify (Tenet 47.6)...")
checks = [
    ("FC17 AVAILABILITY GATE header", "FC17 AVAILABILITY GATE (UI FIX May 26 nt" in content_new),
    ("gate condition inserted", "!window.FC17_POLYGON || !window.FC17_POLYGON.isAvailable(p.name)" in content_new),
    ("comment explains effect", "non-FC17 players early-return" in content_new),
    ("idempotent check preserved", "if (ovl.querySelector('.fc17-polygon-root')) return; // already mounted - idempotent" in content_new),
    ("mount call still present", "window.FC17_POLYGON.mount(ovl, { playerId: p.name });" in content_new),
    ("hide code still present (only fires for FC17 players now)", "scp.style.display = 'none'" in content_new),
    ("FC17_INTERPRETATION mount still present", "window.FC17_INTERPRETATION.mount" in content_new),
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
print(" UI FIX APPLIED CLEAN · FC17 polygon gate")
print("═══════════════════════════════════════════════════════════════════════")
print(f" fieldcheck-verdict.html · {size_after:,} bytes (delta +{size_after-size_before})")
print(f"")
print(f" Effect:")
print(f"   Flagg / Caleb / Caitlin / Skinner: FC17 polygon + interpretation mount (unchanged)")
print(f"   ALL other players:                  legacy polygon + score panel + interpretation (RESTORED)")
print(f"")
print(f" Tim Duncan verdict page will now show:")
print(f"   ✓ legacy polygon visual (8-facet radar via buildMiniRadar)")
print(f"   ✓ score panel (.scpanel) with facet bars")
print(f"   ✓ \"// At a glance\" 3-pillar section")
print(f"   ✓ FieldCheck Interpretation text (legacy or new — both available)")
print(f"   ✓ tier badges (legacy)")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: ./fc-deploy-dev.sh (deploys netlify draft) then verify on dev, then promote prod")
