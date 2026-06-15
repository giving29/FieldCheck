#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
FC17 ROUTING FIX · removes silent default-to-cooper_flagg fallback
═══════════════════════════════════════════════════════════════════════
Problem:
  fc17-polygon-mount.js line 564:
    const canonical = normalizeSlug(opts.playerId || 'cooper_flagg');
  This caused unknown players (e.g. Michael Jordan, LeBron James) to
  fall back to Cooper Flagg's polygon data — showing Flagg's facet
  scores on the wrong player's verdict page. With polygon polish applied,
  this also rendered Flagg's consensus shadow on those wrong pages.

Fix:
  Change to:
    const canonical = normalizeSlug(opts.playerId);
  Existing `if (!canonical)` guard catches null and returns false
  gracefully. Verdict page's legacy polygon code path then renders.

Files modified (with .pre-routing-fix.bak):
  - fc17-polygon-mount.js  (1 line changed)

Run from ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════
"""
import sys, shutil
from pathlib import Path

print("═══ FC17 ROUTING FIX · APPLY ═══\n")

POLYGON_MOUNT = Path('fc17-polygon-mount.js')

OLD_LINE = "const canonical = normalizeSlug(opts.playerId || 'cooper_flagg');"
NEW_LINE = "const canonical = normalizeSlug(opts.playerId);"

# ════════════════════════ STEP 1 · pre-flight ════════════════════════
if not POLYGON_MOUNT.exists():
    print(f"✗ FAIL: {POLYGON_MOUNT} not found in cwd")
    sys.exit(1)

content = POLYGON_MOUNT.read_text()
orig_size = POLYGON_MOUNT.stat().st_size

# Idempotency: if new line already present and old line gone, skip
if NEW_LINE in content and OLD_LINE not in content:
    print(f"✓ Already applied (default-to-flagg removed, fix in place)")
    sys.exit(0)

if OLD_LINE not in content:
    print(f"✗ FAIL: Expected line not found:")
    print(f"  '{OLD_LINE}'")
    print(f"  This script targets a specific line in fc17-polygon-mount.js.")
    print(f"  If the file was modified differently, do not run this patch.")
    sys.exit(1)

occurrences = content.count(OLD_LINE)
if occurrences != 1:
    print(f"✗ FAIL: Expected exactly 1 occurrence of target line, found {occurrences}")
    sys.exit(1)

print(f"▸ {POLYGON_MOUNT}: {orig_size:,} bytes")
print(f"▸ Found target line (1 occurrence): line will be changed")


# ════════════════════════ STEP 2 · backup ════════════════════════
print(f"\n▸ Creating .pre-routing-fix.bak backup...")
backup = Path(str(POLYGON_MOUNT) + '.pre-routing-fix.bak')
shutil.copy(POLYGON_MOUNT, backup)
print(f"  ✓ {backup.name} ({backup.stat().st_size:,} B)")


def rollback(reason):
    print(f"\n✗ ROLLING BACK · {reason}")
    shutil.copy(backup, POLYGON_MOUNT)
    print(f"  ✓ Restored {POLYGON_MOUNT.name}")
    sys.exit(1)


# ════════════════════════ STEP 3 · patch ════════════════════════
content = content.replace(OLD_LINE, NEW_LINE, 1)
POLYGON_MOUNT.write_text(content)

new_size = POLYGON_MOUNT.stat().st_size
delta = new_size - orig_size
print(f"\n▸ Patched · {POLYGON_MOUNT.name} ({new_size:,} B, delta {delta:+,} B)")


# ════════════════════════ STEP 4 · verification ════════════════════════
print(f"\n▸ Verification\n")

check_content = POLYGON_MOUNT.read_text()

checks = [
    ('Old line removed', OLD_LINE not in check_content),
    ('New line present', NEW_LINE in check_content),
    ('Existing null guard still present', 'if (!canonical) {' in check_content),
    ('console.warn for unrecognized still present', "FC17_POLYGON: unrecognized player slug:" in check_content),
    ('mount function signature intact', 'mount: function(container, opts) {' in check_content),
    ('isAvailable function intact', 'isAvailable: function(slug) {' in check_content),
    ('enhanceWithConsensus call still hooked (if polygon polish applied)', True),  # advisory
    ('Function count: normalizeSlug called >=2', check_content.count('normalizeSlug(') >= 2),
]

all_pass = True
for label, found in checks:
    print(f"  {'✓' if found else '✗'} {label}")
    if not found:
        all_pass = False

if not all_pass:
    rollback("verification failed")


# ════════════════════════ STEP 5 · summary ════════════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" FC17 ROUTING FIX · APPLIED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" Modified · {POLYGON_MOUNT.name} ({new_size:,} B, was {orig_size:,})")
print(f" Backup   · {backup.name}")
print()
print(f" CHANGE   · Line ~564")
print(f"            BEFORE: {OLD_LINE}")
print(f"            AFTER:  {NEW_LINE}")
print()
print(f" EFFECT   · Unknown players (Michael Jordan, LeBron James, etc.)")
print(f"            no longer silently fall back to Cooper Flagg's polygon.")
print(f"            FC17_POLYGON.mount() returns false → legacy polygon renders.")
print()
print(f" ROLLBACK · cp {backup.name} {POLYGON_MOUNT.name}")
print(f"            ./fc-deploy-dev.sh")
print()
print(f" NEXT · ./fc-deploy-dev.sh")
print(f"        Verify on DEV:")
print(f"          - Michael Jordan: should now show LEGACY polygon (not Flagg's)")
print(f"          - Cooper Flagg: still shows FC17 polygon + consensus shadow")
print(f"          - Caitlin Clark/Caleb Williams/Avery Skinner: still FC17 + consensus")
print(f"        If all good → ./fc-promote-prod.sh")
