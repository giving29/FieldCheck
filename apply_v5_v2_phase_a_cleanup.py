#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V5 v2 PHASE A · CLEANUP · line 4359 secondary anchor list
═══════════════════════════════════════════════════════════════════════════
Removes the last remaining "capped while active" phrase in a secondary
anchor reference list. After this, worker.js has zero V4 cap framing.

Run from ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════════
"""
import sys, hashlib, subprocess
from pathlib import Path

print("═══ V5 v2 PHASE A · CLEANUP ═══\n")

p = Path('worker.js')
if not p.exists():
    print("FAIL: worker.js not found")
    sys.exit(1)

c = p.read_text()
sha_before = hashlib.sha256(c.encode()).hexdigest()[:12]
size_before = p.stat().st_size

print(f"▸ worker.js · {size_before:,} bytes · sha={sha_before}\n")

# The single remaining V4 phrase
OLD = '  - 9.0-9.3 = Active multi-MVP (Steph/Jokic — capped while active)'
NEW = '  - 9.0-9.3 = Active multi-MVP (Steph/Jokic — active career still open)'

count_before = c.count('capped while active')
print(f"▸ 'capped while active' count before: {count_before}")

if count_before == 0:
    print("✓ already clean (idempotent · no V4 phrase to remove)")
    sys.exit(0)

if OLD not in c:
    print(f"✗ exact anchor not found")
    print(f"  expected: {OLD}")
    print(f"  but 'capped while active' appears {count_before} time(s)")
    print(f"  manual inspect: grep -nE 'capped while active' worker.js")
    sys.exit(1)

c = c.replace(OLD, NEW, 1)
count_after = c.count('capped while active')

if count_after > 0:
    print(f"✗ replace incomplete · still {count_after} occurrence(s) remain")
    sys.exit(1)

p.write_text(c)
sha_after = hashlib.sha256(c.encode()).hexdigest()[:12]
size_after = p.stat().st_size

print(f"  ✓ patched · count {count_before} → {count_after}")
print(f"  ✓ sha {sha_before} → {sha_after}")
print(f"  ✓ size {size_before:,} → {size_after:,} bytes (delta {size_after - size_before:+,})\n")


# ═══ broader scan for any other V4 cap framing we might have missed ═══
print("▸ Broader scan · any remaining V4 cap framing\n")

v4_patterns = [
    'capped while',
    'HARD CAP',
    'CEILING (Cooper Flagg',
    'CEILING (Caitlin',
    'HARD CAP — ',
    'NATIONAL HARD',
    'MAX 6 — never',
    'MAX 6 — no pro',
    'capped at 7.4',
    'capped at 5.4',
    '(active cap)',
    'PER-TIER FACET CEILINGS',
    'these are HARD CAPS',
    'HS athlete facet caps:',
    'D1 facet caps:',
]

still_present = []
for pat in v4_patterns:
    count = c.count(pat)
    if count > 0:
        still_present.append((pat, count))

if still_present:
    print("  ⚠ V4 patterns still present (review needed):")
    for pat, count in still_present:
        print(f"    {count}× '{pat}'")
    print("\n  These may be in comments / historical references / additional secondary blocks.")
    print("  Run: grep -nE 'capped while|HARD CAP|MAX 6' worker.js | head -30")
else:
    print("  ✓ no V4 cap framing found anywhere in worker.js")


# ═══ node syntax check ═══
print("\n▸ Node syntax check")
r = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"  ✗ FAIL: {r.stderr}")
    print(f"  Restore: cp worker.js.pre-V022.34-V5.bak worker.js")
    sys.exit(1)
print("  ✓ syntax OK")


# ═══ verify V5 v2 state ═══
print("\n▸ V5 v2 state verify")
v5_anchors = [
    ('banner V022.34-V5', 'FIELDCHECK_WORKER_VERSION = V022.34-V5'),
    ('cache v022.34v5', "cacheVersion = 'v022.34v5'"),
    ('PHENOM CRITERIA', 'PHENOM CRITERIA (must pass ALL 4'),
    ('ANTI-INFLATION', 'ANTI-INFLATION (these signals DO NOT'),
    ('DEFAULT-LOW', 'DEFAULT-LOW PRINCIPLE:'),
    ('CROSS-SPORT', 'CROSS-SPORT THEORETICAL 10 ANCHORS'),
    ('MOAT preserved', 'WITHIN-TIER DIFFERENTIATION (THE MOAT'),
    ('composite reads raw', 'result.composite = Math.round(_v22_31_raw * 10) / 10'),
    ('capped_legacy in metadata', 'capped_legacy:'),
]
all_ok = True
for label, anchor in v5_anchors:
    ok = anchor in c
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok:
        all_ok = False

if not all_ok:
    print("\n  ⚠ some V5 v2 anchors missing — review")
    sys.exit(1)


print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" V5 v2 PHASE A CLEANUP COMPLETE")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" worker.js · {size_after:,} bytes · sha={sha_after}")
print(f" V5 v2 banner · V022.34-V5 · cache v022.34v5 · ready to deploy")
print(f"")
print(f" NEXT:")
print(f"   ./fc-deploy-dev.sh")
print(f"   python3 v022_32_q_battery_v2.py    # cold cache · ~22min")
print(f"")
print(f" 16 test cases to watch:")
print(f"   Stokes 4.5-5.4 · Flagg 6.5-7.5 · Caitlin 7.0-7.8")
print(f"   Duncan 9.3-9.6 · Steph 9.0-9.3 · Jordan 9.9")
print(f"   Mahomes 8.8-9.2 · Brady 9.4-9.7 · Tiger 9.5-9.8 · Trout 9.0-9.4")
print(f"   Boozer 6.0-7.0 · Goodin 6.0-6.7 · Gauff 7.5-8.2")
print(f"   Kobe-17 6.0-7.0 · Ivanyo 3.5-5.5 · HS median 3.0-4.0")
