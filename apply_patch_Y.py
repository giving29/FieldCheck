#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-Y · PATCH Y · STAGE=UNKNOWN FALLBACK (THE GAP)
═══════════════════════════════════════════════════════════════════════════
Root cause from V022.32-X battery (May 26 nt): when cascade can't classify
stage cleanly, _v22_31_stage === 'unknown' → U2 doesn't fire → raw composite
escapes uncapped. Lamar Brown 9.5, Jett Washington 5.5, Jared Curtis 5.5
class — all stage=unknown leakers.

Patch Y inserts a fallback block BEFORE the composite cap is applied:
  • stage=unknown + tier=hs       → force prep_amateur, cap=5.4
  • stage=unknown + tier=d1       → force college_amateur, cap=7.4
  • stage=unknown + tier=d2/d3/juco/naia → college_amateur, cap=6.8
  • stage=unknown + tier=unknown  → HS default (most athletes are HS)

PROMPT-ORTHOGONAL: does NOT touch synthesis prompt. Existing cache (v022.32u)
stays valid → battery tests Patch Y's cap logic alone, no fresh-synthesis cost.

Atomicity: backup → patch → grep-verify → node-check → restore on failure
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-Y.bak')

print("═══ V022.32-Y · PATCH Y · STAGE=UNKNOWN FALLBACK ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

if "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content:
    print("✗ Not on V022.32-U baseline · ABORT")
    print("  Run: cp worker.js.pre-V022.32-X.bak worker.js first")
    sys.exit(1)
print("  ✓ baseline = V022.32-U (6 patches)\n")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("▸ Anchor detection...")

# A1: _v22_31_capped line (the insertion point — Patch Y goes BEFORE this)
anchor_rx = re.compile(r'const _v22_31_capped\s*=\s*Math\.min\([^)]+\);')
anchor_matches = anchor_rx.findall(content)
if len(anchor_matches) != 1:
    print(f"✗ _v22_31_capped anchor count = {len(anchor_matches)} · ABORT")
    print(f"  found: {anchor_matches[:3]}")
    sys.exit(1)
anchor_line = anchor_matches[0]
print(f"  ✓ A1 _v22_31_capped: {anchor_line[:70]}...")

# A2: banner
banner_rx = re.compile(r"// FIELDCHECK_WORKER_VERSION = V022\.32-U · TENET 47 ATOMIC · 6 patches[^\n]*")
banner_m = banner_rx.search(content)
if not banner_m:
    print("✗ A2 banner not found · ABORT"); sys.exit(1)
banner_old = banner_m.group(0)
print(f"  ✓ A2 banner\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP}\n")


# ─── P1: insert Patch Y block before _v22_31_capped ───────────────────────
patch_y_block = """// ─── V022.32-Y · PATCH Y · stage=unknown fallback (TENET 46 V4 amateur-first)
        // V022.32-X battery (May 26 nt) revealed stage=unknown athletes bypass U2's
        // cap enforcement. Lamar Brown 9.5 / Jett Washington 5.5 / Jared Curtis 5.5
        // class all escaped because cascade returned stage=unknown → U2 didn't fire.
        // Patch Y forces conservative defaults so cap always applies.
        if (_v22_31_stage === 'unknown') {
          if (_v22_31_tier === 'hs') {
            _v22_31_stage = 'prep_amateur';
            _v22_31_cap = 5.4;
          } else if (_v22_31_tier === 'd1') {
            _v22_31_stage = 'college_amateur';
            _v22_31_cap = 7.4;
          } else if (['d2','d3','juco','naia'].includes(_v22_31_tier)) {
            _v22_31_stage = 'college_amateur';
            _v22_31_cap = 6.8;
          } else {
            // tier ALSO unknown: conservative HS default (most athletes are HS-tier)
            _v22_31_stage = 'prep_amateur';
            _v22_31_tier = 'hs';
            _v22_31_cap = 5.4;
          }
        }
        """

print("▸ P1: insert Patch Y block before _v22_31_capped...")
content_v1 = content.replace(anchor_line, patch_y_block + anchor_line, 1)
if content_v1 == content:
    print("✗ P1 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v1)-len(content):+d}\n")


# ─── P2: banner bump ───────────────────────────────────────────────────────
banner_new = "// FIELDCHECK_WORKER_VERSION = V022.32-Y · TENET 47 ATOMIC · 7 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, Y (stage=unknown fallback · catches Lamar Brown class)"
print("▸ P2: banner V022.32-U → V022.32-Y...")
content_final = content_v1.replace(banner_old, banner_new, 1)
if content_final == content_v1:
    print("✗ P2 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓\n")


# ─── WRITE ─────────────────────────────────────────────────────────────────
WORKER.write_text(content_final)
size_after = len(content_final)
sha_after = hashlib.sha256(content_final.encode()).hexdigest()[:12]
print(f"▸ worker.js · {size_after:,} bytes (delta {size_after-size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY (Tenet 47.1 · exact substrings from inserted text) ────────
print("▸ Grep-verify (Tenet 47.1)...")
checks = [
    ("Patch Y comment header", "V022.32-Y · PATCH Y · stage=unknown fallback" in content_final),
    ("stage=unknown check", "if (_v22_31_stage === 'unknown')" in content_final),
    ("HS branch", "_v22_31_tier === 'hs'" in content_final),
    ("D1 branch", "_v22_31_tier === 'd1'" in content_final),
    ("D2/D3/JUCO array", "['d2','d3','juco','naia'].includes" in content_final),
    ("cap 5.4 set", "_v22_31_cap = 5.4" in content_final),
    ("cap 7.4 set", "_v22_31_cap = 7.4" in content_final),
    ("cap 6.8 set", "_v22_31_cap = 6.8" in content_final),
    ("Lamar Brown comment", "Lamar Brown 9.5" in content_final),
    ("banner V022.32-Y", "V022.32-Y · TENET 47 ATOMIC · 7 patches" in content_final),
    ("old V022.32-U banner removed", "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content_final),
    ("_v22_31_capped still present", "_v22_31_capped" in content_final),
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
print(" V022.32-Y PATCH Y APPLIED CLEAN · stage=unknown fallback")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-U → V022.32-Y (cache stays v022.32u — synthesis unchanged)")
print(f"")
print(f" When _v22_31_stage === 'unknown':")
print(f"   tier=hs            → stage=prep_amateur,   cap=5.4")
print(f"   tier=d1            → stage=college_amateur, cap=7.4")
print(f"   tier=d2/d3/juco/naia → stage=college_amateur, cap=6.8")
print(f"   tier=unknown       → stage=prep_amateur, tier=hs, cap=5.4 (HS default)")
print(f"")
print(f" Expected battery impact (vs V022.32-U baseline):")
print(f"   Lamar Brown 7.4 → 5.4 (caught)")
print(f"   Tate Ivanyo 9.3 → unchanged (stage=prime_pro, not unknown)")
print(f"   HS within cap: 72% → ~80%+ (gap closed)")
print(f"   GREEN count: 12 → 13+")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: bump canonical V5.30 → V5.31, deploy, battery, compare vs V022.32-U")
