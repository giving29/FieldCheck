#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
TENET 39 FIX · canonical reference V022.36-V5.2
═══════════════════════════════════════════════════════════════════════════
Worker bumped V022.35-V5.1 → V022.36-V5.2 by apply_v5_v2_2_and_v2_3.
Canonical Tab 19 V5 Algorithm subtitle needs V022.36 reference.

Run AFTER apply_v5_v2_2_and_v2_3.py, BEFORE ./fc-deploy-dev.sh
From ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════════
"""
import sys
from pathlib import Path

p = Path('FC_CANONICAL_STATE_V1.html')
if not p.exists():
    print("FAIL: canonical not found")
    sys.exit(1)

c = p.read_text()

# Replace the V022.35 subtitle with V022.36 reference noting the architectural change
old = '// Latest applied: V022.35-V5.1 · May 26 nt refinement (ANTI-CONTAMINATION + HARD NUMERIC ANCHORS + 9.7+ RESERVED) · 10 is the only ceiling'
new = '// Latest applied: V022.36-V5.2 · May 26 nt · ARCHITECTURE: prompt does evidence eval, code does bright-line rules · 6 deterministic post-synthesis corrections (Jr/Sr suffix, HS non-phenom, D1 amateur, active 9.6, rookie 7.5, HS-pro mismatch flag) · audit trail in v5_corrections array · HARD NUMERIC ANCHORS removed (peer-association bias) · ANTI-CONTAMINATION + 9.7+ RESERVED kept · 10 is the only ceiling'

if 'V022.36' in c:
    print("✓ V022.36 already referenced (idempotent)")
    print(f"  count: {c.count('V022.36')}")
    sys.exit(0)

if old not in c:
    # Fallback: any V022.35 reference + first occurrence path
    if 'V022.35-V5.1' in c:
        # Just append V022.36 reference next to V022.35
        fallback_old = 'V022.35-V5.1'
        fallback_new = 'V022.35-V5.1 → V022.36-V5.2 (architecture: prompt + deterministic post-processing · 6 bright-line rules · audit trail)'
        c = c.replace(fallback_old, fallback_new, 1)
        p.write_text(c)
        print(f"  ✓ fallback applied · V022.36 added")
        print(f"  V022.36 count: {c.count('V022.36')}")
        sys.exit(0)
    print("✗ no anchor matched")
    sys.exit(1)

c = c.replace(old, new, 1)
p.write_text(c)
print(f"✓ canonical updated · V022.36-V5.2 reference added with architecture note")
print(f"  size: {p.stat().st_size:,} B")
print(f"  V022.36 count: {c.count('V022.36')}")
print(f"\nNEXT: ./fc-deploy-dev.sh")
