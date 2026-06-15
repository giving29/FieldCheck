#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-U · CONST-TO-LET FIX · U2 needs let for reassignment
═══════════════════════════════════════════════════════════════════════════
Wrangler build failed because U2 patch reassigns _v22_31_tier / _v22_31_cap
which are declared `const`. Change both to `let` at their declaration sites.

JavaScript only enforces const at ASSIGNMENT, not at USE — so this change
is safe and breaks nothing downstream. The variables become mutable, which
is exactly what U2 requires.

Doctrine compliance:
  Tenet 47.1 grep-verify · 47.2 atomic (no version bump needed, same V022.32-U)
  Tenet 47.3 fix only the const-let issue, no other scope expansion
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-const-let-fix.bak')

print("═══ V022.32-U · CONST-TO-LET FIX ═══\n")

if not WORKER.exists():
    print(f"✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
print(f"▸ worker.js: {size_before:,} bytes")

# Confirm V022.32-U baseline
if "V022.32-U" not in content:
    print("✗ Worker is not on V022.32-U baseline · ABORT")
    sys.exit(1)
print("  ✓ baseline = V022.32-U\n")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("▸ Anchor detection...")

tier_rx = re.compile(r'\bconst (_v22_31_tier\s*=\s*)', re.MULTILINE)
cap_rx = re.compile(r'\bconst (_v22_31_cap\s*=\s*)', re.MULTILINE)

tier_hits = list(tier_rx.finditer(content))
cap_hits = list(cap_rx.finditer(content))

print(f"  const _v22_31_tier = ... : {len(tier_hits)} hit(s)")
for m in tier_hits:
    line_no = content[:m.start()].count('\n') + 1
    line_text = content[m.start():content.find('\n', m.start())][:120]
    print(f"    line {line_no}: {line_text}")

print(f"  const _v22_31_cap = ... : {len(cap_hits)} hit(s)")
for m in cap_hits:
    line_no = content[:m.start()].count('\n') + 1
    line_text = content[m.start():content.find('\n', m.start())][:120]
    print(f"    line {line_no}: {line_text}")

if len(tier_hits) != 1:
    print(f"\n✗ const _v22_31_tier must appear exactly once · found {len(tier_hits)} · ABORT")
    sys.exit(1)
if len(cap_hits) != 1:
    print(f"\n✗ const _v22_31_cap must appear exactly once · found {len(cap_hits)} · ABORT")
    sys.exit(1)
print()


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP} ({BACKUP.stat().st_size:,} bytes)\n")


# ─── APPLY ─────────────────────────────────────────────────────────────────
print("▸ Replacing const → let...")
new = tier_rx.sub(r'let \1', content, count=1)
new = cap_rx.sub(r'let \1', new, count=1)

if new == content:
    print("✗ no change applied · ABORT")
    sys.exit(1)

WORKER.write_text(new)
print(f"  ✓ written · {len(new):,} bytes (delta {len(new) - size_before:+d})\n")


# ─── GREP-VERIFY (Tenet 47.1) ──────────────────────────────────────────────
print("▸ Grep-verify...")
checks = [
    ("let _v22_31_tier present", "let _v22_31_tier" in new),
    ("let _v22_31_cap present", "let _v22_31_cap" in new),
    ("const _v22_31_tier removed", "const _v22_31_tier" not in new),
    ("const _v22_31_cap removed", "const _v22_31_cap" not in new),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print()


# ─── NODE SYNTAX CHECK ─────────────────────────────────────────────────────
print("▸ Node syntax check...")
result = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"✗ node --check FAILED · restoring")
    print(f"  stderr: {result.stderr[:600]}")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ node --check passed\n")


# ─── DONE ──────────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" CONST-TO-LET FIX APPLIED CLEAN · ready to redeploy")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker still V022.32-U · no version bump needed")
print(f" Backup: {BACKUP}")
print(f"")
print(f" NEXT: ./fc-deploy-dev.sh")
