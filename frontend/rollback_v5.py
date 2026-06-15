#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
ROLLBACK · V022.33-V5 → V022.32-YX
═══════════════════════════════════════════════════════════════════════════
Restores worker.js from .pre-V022.33-V5.bak and removes V022.33-V5
reference from canonical so Tenet 39 guard passes.

Run from ~/Desktop/fieldcheck-proxy/
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, subprocess
from pathlib import Path

print("═══ ROLLBACK V022.33-V5 to V022.32-YX ═══\n")

WORKER = Path('worker.js')
WORKER_BAK = Path('worker.js.pre-V022.33-V5.bak')
CANON = Path('FC_CANONICAL_STATE_V1.html')

if not WORKER_BAK.exists():
    print(f"FAIL: {WORKER_BAK} not found")
    sys.exit(1)
if not CANON.exists():
    print(f"FAIL: {CANON} not found")
    sys.exit(1)


print("STEP 1 · restore worker.js from pre-V022.33-V5 backup")
shutil.copy(WORKER_BAK, WORKER)
size_w = WORKER.stat().st_size
print(f"  worker.js restored, {size_w:,} bytes")


print("\nSTEP 2 · node syntax check")
r = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"FAIL: {r.stderr}")
    sys.exit(1)
print("  syntax OK")


print("\nSTEP 3 · verify worker banner is V022.32-YX")
c = WORKER.read_text()
if "FIELDCHECK_WORKER_VERSION = V022.32-YX" in c:
    print("  banner confirmed V022.32-YX")
else:
    print("FAIL: banner not V022.32-YX after restore")
    sys.exit(1)


print("\nSTEP 4 · roll back canonical V022.33-V5 reference")
cc = CANON.read_text()
new_str = "<b>V022.32-YX worker</b> | Tim Duncan legend_pro fix"
old_str_v1 = "<b>V022.33-V5 worker | V5 algorithm applied May 26 nt</b> | cap removed from composite output, synthesis prompt rewritten with reference distribution + PHENOMS + EVIDENCE RIGOR clauses. Stage detection kept for routing not capping.<br><b>V022.32-YX worker (prior)</b> | Tim Duncan legend_pro fix"

old_str_v2 = '<b>V022.33-V5 worker \u00b7 V5 algorithm applied May 26 nt</b> \u2014 cap removed from composite output, synthesis prompt rewritten with reference distribution + PHENOMS + EVIDENCE RIGOR clauses. Stage detection kept for routing not capping.<br><b>V022.32-YX worker (prior)</b> \u00b7 Tim Duncan legend_pro fix'
new_str_v2 = '<b>V022.32-YX worker</b> \u00b7 Tim Duncan legend_pro fix'

did_replace = False
if old_str_v2 in cc:
    cc = cc.replace(old_str_v2, new_str_v2, 1)
    did_replace = True
    print("  V5 reference found and removed (unicode variant)")
elif "V022.33-V5 worker" in cc:
    import re
    cc = re.sub(
        r'<b>V022\.33-V5 worker[^<]*</b>[^<]*<br><b>V022\.32-YX worker \(prior\)</b>',
        '<b>V022.32-YX worker</b>',
        cc,
        count=1
    )
    if "V022.33-V5 worker" not in cc:
        did_replace = True
        print("  V5 reference found and removed (regex fallback)")

if not did_replace:
    print("  V022.33-V5 reference not found in canonical (already clean or different shape)")
else:
    CANON.write_text(cc)

v33_count = cc.count("V022.33")
print(f"  V022.33 reference count in canonical: {v33_count}")


print("\nSTEP 5 · final sanity check")
print(f"  worker.js: V022.32-YX")
print(f"  canonical V022.33 mentions: {v33_count}")
if v33_count > 0:
    print(f"  WARNING: still {v33_count} V022.33 reference(s) in canonical, may trip Tenet 39 guard")
    print(f"  Inspect with: grep -n V022.33 FC_CANONICAL_STATE_V1.html")


print("\n═══ ROLLBACK COMPLETE ═══")
print("NEXT: ./fc-deploy-dev.sh")
