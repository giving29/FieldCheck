#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
TENET 39 FIX · canonical reference V022.35-V5.1
═══════════════════════════════════════════════════════════════════════════
Worker bumped V022.34-V5 → V022.35-V5.1 in apply_v5_v2_phase_a2.
Canonical Tab 19 V5 Algorithm pane needs V022.35 reference so guard passes.

Run from ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════════
"""
import sys
from pathlib import Path

p = Path('FC_CANONICAL_STATE_V1.html')
if not p.exists():
    print("FAIL: canonical not found")
    sys.exit(1)

c = p.read_text()

# Add V022.35-V5.1 reference to Tab 19 V5 Algorithm pane subtitle
old = '<div class="pane-h">V5 <b>Algorithm</b></div>\n  <div class="pane-sub">// 10 is the only ceiling'
new = '<div class="pane-h">V5 <b>Algorithm</b></div>\n  <div class="pane-sub">// Latest applied: V022.35-V5.1 · May 26 nt refinement (ANTI-CONTAMINATION + HARD NUMERIC ANCHORS + 9.7+ RESERVED) · 10 is the only ceiling'

if 'V022.35' in c:
    print("✓ V022.35 already referenced in canonical (idempotent)")
    print(f"  count: {c.count('V022.35')}")
    sys.exit(0)

if old not in c:
    print("✗ anchor not found · checking variants")
    # Fallback: try just the pane-h match
    fallback_old = 'V5 <b>Algorithm</b></div>'
    fallback_new = 'V5 <b>Algorithm</b> · V022.35-V5.1</div>'
    if fallback_old in c and 'V022.35' not in c:
        c = c.replace(fallback_old, fallback_new, 1)
        p.write_text(c)
        print(f"  ✓ fallback applied · V022.35 added to Tab 19 header")
        print(f"  V022.35 count: {c.count('V022.35')}")
        sys.exit(0)
    print("  ✗ no anchor matched")
    sys.exit(1)

c = c.replace(old, new, 1)
p.write_text(c)
print(f"✓ canonical updated · V022.35-V5.1 reference added to Tab 19 pane subtitle")
print(f"  size: {p.stat().st_size:,} B")
print(f"  V022.35 count: {c.count('V022.35')}")
print(f"\nNEXT: ./fc-deploy-dev.sh")
