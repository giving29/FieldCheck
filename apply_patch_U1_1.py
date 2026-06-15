#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-U1 · PATCH U1.1 · CASCADE REORDER
═══════════════════════════════════════════════════════════════════════════
Move U1 (HS-keyword amateur-first stage gate) to fire BEFORE Patch L2
college school override. Currently U1 sits AFTER college override, so HS
athletes with college commitment text (Alijah Arenas→USC, Lamar Brown,
Trevor Condon, Keisean Henderson, Jalen Brewster, Oliviyah Edwards,
Emily McDonald) get classified as college_amateur before U1 can fire.

Current cascade:  HS_school → College_school → U1 → prime_pro_cascade
New cascade:      HS_school → U1 → College_school → prime_pro_cascade

This is a BLOCK SWAP, not a content change. U1's logic is unchanged.
College school override's logic is unchanged. Only their relative order.

Atomicity:
  · Backup → worker.js.pre-V022.32-U1.bak
  · Bump V022.32-U → V022.32-U1, cache v022.32u → v022.32u1 (Tenet 47.2)
  · Grep-verify cascade ordering post-swap
  · node --check
  · Restore from backup on any failure
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-U1.bak')

print("═══ V022.32-U1 · PATCH U1.1 · CASCADE REORDER ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

# Confirm V022.32-U baseline
if "V022.32-U · TENET 47 ATOMIC" not in content:
    print("✗ Worker not on V022.32-U baseline · ABORT")
    sys.exit(1)
print("  ✓ baseline = V022.32-U\n")


# ─── DETECT CURRENT ORDERING ───────────────────────────────────────────────
print("▸ Current cascade ordering check...")
u1_marker = "u1_hs_keyword_amateur_first"
college_marker = "v022.31_college_school_override"

u1_pos = content.find(u1_marker)
college_pos = content.find(college_marker)

if u1_pos < 0:
    print("✗ U1 marker not found · ABORT"); sys.exit(1)
if college_pos < 0:
    print("✗ college override marker not found · ABORT"); sys.exit(1)

print(f"  U1 marker at offset: {u1_pos}")
print(f"  College marker at offset: {college_pos}")

if u1_pos < college_pos:
    print("\n✓ U1 already fires BEFORE college override · NO-OP, exiting cleanly")
    sys.exit(0)
print(f"  current order: college ({college_pos}) → U1 ({u1_pos}) · SWAP NEEDED\n")


# ─── MATCH THE FULL SEQUENCE [college block + whitespace + U1 block] ──────
print("▸ Matching cascade sequence...")

swap_rx = re.compile(
    # Group 1: college override block (5 lines)
    r'(^[ \t]*else if \(_v22_31_isCollegeSchool\)[^\n]*\n'
    r'[ \t]+stage = \'college_amateur\';[^\n]*\n'
    r'[ \t]+stageSignals\.push\(\'v022\.31_college_school_override\'\);[^\n]*\n'
    r'[ \t]+if \(_v22_31_currentSchool\) stageSignals\.push\(\'school=\'[^\n]*\n'
    r'[ \t]*\})'
    # Group 2: whitespace between blocks
    r'(\s*?\n)'
    # Group 3: U1 block (10 lines · 6 comment + 4 code)
    r'([ \t]*// V022\.32-U · PATCH U1 · AMATEUR-FIRST STAGE GATE[^\n]*\n'
    r'(?:[ \t]*//[^\n]*\n){5}'
    r'[ \t]*else if \(isHSSig && !isLegendValidated\)[^\n]*\n'
    r'[ \t]+stage = \'prep_amateur\';[^\n]*\n'
    r'[ \t]+stageSignals\.push\(\'u1_hs_keyword_amateur_first\'\);[^\n]*\n'
    r'[ \t]*\})',
    re.MULTILINE
)

matches = list(swap_rx.finditer(content))
print(f"  sequence matches: {len(matches)}")
if len(matches) != 1:
    print(f"✗ expected exactly 1 sequence · ABORT")
    if len(matches) > 1:
        for i, m in enumerate(matches[:3]):
            line_no = content[:m.start()].count('\n') + 1
            print(f"    match {i+1} at line {line_no}")
    sys.exit(1)

m = matches[0]
college_block = m.group(1)
between = m.group(2)
u1_block = m.group(3)
seq_start_line = content[:m.start()].count('\n') + 1
print(f"  sequence starts at line: {seq_start_line}")
print(f"  college block: {len(college_block)} chars · {college_block.count(chr(10)) + 1} lines")
print(f"  between: {repr(between)}")
print(f"  U1 block: {len(u1_block)} chars · {u1_block.count(chr(10)) + 1} lines\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP} ({BACKUP.stat().st_size:,} bytes)\n")


# ─── SWAP ───────────────────────────────────────────────────────────────────
print("▸ Swapping cascade order...")
new_block = u1_block + between + college_block
content_new = content[:m.start()] + new_block + content[m.end():]

if content_new == content:
    print("✗ no change · ABORT")
    sys.exit(1)
if len(content_new) != len(content):
    # swap should preserve length exactly
    print(f"✗ length mismatch · expected same, got delta {len(content_new) - len(content)} · ABORT")
    sys.exit(1)
print(f"  ✓ swap complete · length preserved {len(content_new):,}\n")


# ─── BUMP BANNER (V022.32-U → V022.32-U1) ──────────────────────────────────
print("▸ Bumping banner V022.32-U → V022.32-U1...")
old_banner_rx = re.compile(r'// FIELDCHECK_WORKER_VERSION = V022\.32-U · TENET 47 ATOMIC[^\n]*')
banner_match = old_banner_rx.search(content_new)
if not banner_match:
    print("✗ banner anchor not found · restoring")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
old_banner_text = banner_match.group(0)
new_banner_text = "// FIELDCHECK_WORKER_VERSION = V022.32-U1 · TENET 47 ATOMIC · 7 patches: O, N1a, N1b, N3+Q1+Q3, U1 (HS-amateur), U2 (stage-driven tier+cap), U1.1 (cascade reorder U1 BEFORE college override)"
content_new = content_new.replace(old_banner_text, new_banner_text, 1)
print(f"  ✓ banner bumped\n")


# ─── BUMP CACHE (v022.32u → v022.32u1) ─────────────────────────────────────
print("▸ Bumping cache v022.32u → v022.32u1...")
old_cache = "const cacheVersion = 'v022.32u'"
new_cache = "const cacheVersion = 'v022.32u1'"
if old_cache not in content_new:
    print(f"✗ cache anchor not found · restoring"); shutil.copy(BACKUP, WORKER); sys.exit(1)
content_new = content_new.replace(old_cache, new_cache, 1)
print(f"  ✓ cache bumped\n")


# ─── WRITE ──────────────────────────────────────────────────────────────────
WORKER.write_text(content_new)
size_after = len(content_new)
sha_after = hashlib.sha256(content_new.encode()).hexdigest()[:12]
print(f"▸ worker.js written · {size_after:,} bytes (delta {size_after - size_before:+d}) · sha={sha_after}\n")


# ─── POST-SWAP CASCADE ORDERING VERIFY (Tenet 47.1) ────────────────────────
print("▸ Post-swap cascade ordering verify...")
u1_pos_after = content_new.find(u1_marker)
college_pos_after = content_new.find(college_marker)
print(f"  U1 marker now at offset: {u1_pos_after}")
print(f"  College marker now at offset: {college_pos_after}")
if u1_pos_after >= college_pos_after:
    print("✗ U1 still does NOT fire before college override · restoring")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ U1 ({u1_pos_after}) NOW BEFORE college ({college_pos_after})\n")

# Marker presence verifications
print("▸ Marker grep-verify (Tenet 47.1)...")
checks = [
    ("U1 marker present", "u1_hs_keyword_amateur_first" in content_new),
    ("U1 comment present", "PATCH U1 · AMATEUR-FIRST STAGE GATE" in content_new),
    ("College override marker present", "v022.31_college_school_override" in content_new),
    ("U2 marker still present", "PATCH U2 · STAGE-DRIVEN TIER + CAP CONSISTENCY" in content_new),
    ("banner V022.32-U1", "V022.32-U1 · TENET 47 ATOMIC · 7 patches" in content_new),
    ("cache v022.32u1", "'v022.32u1'" in content_new),
    ("old V022.32-U banner removed", "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content_new),
    ("old cache v022.32u removed", "const cacheVersion = 'v022.32u'" not in content_new),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print()


# ─── NODE SYNTAX CHECK ─────────────────────────────────────────────────────
print("▸ Node syntax check...")
result = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"✗ node --check FAILED · restoring")
    print(f"  stderr: {result.stderr[:600]}")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ node --check passed\n")


# ─── DONE ──────────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" V022.32-U1 PATCH U1.1 APPLIED CLEAN · cascade reordered + verified")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-U → V022.32-U1")
print(f" Cache:  v022.32u → v022.32u1 (forces fresh synthesis)")
print(f" Cascade: HS_school → U1 → College_school → prime_pro_cascade")
print(f"")
print(f" Backup: {BACKUP}")
print(f"")
print(f" NEXT:")
print(f"   1) bump canonical V5.26 → V5.27 (atomic, Tenet 47.2)")
print(f"   2) ./fc-deploy-dev.sh")
print(f"   3) re-run 110-battery · expect HS compliance ≥85% (was 72%)")
