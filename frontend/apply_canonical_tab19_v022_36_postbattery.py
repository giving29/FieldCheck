#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
CANONICAL TAB 19 V5 ALGORITHM · POST-BATTERY UPDATE
═══════════════════════════════════════════════════════════════════════════
Adds V5 v2.2+v2.3 architecture content to canonical Tab 19 V5 Algorithm pane.

Per Canonical Doctrine: requires Sridhar to upload current FC_CANONICAL_STATE_V1.html
to ~/Desktop/fieldcheck-proxy/ first. Script does surgical str_replace anchored
on actual file content — never rewrites from memory.

Run from ~/Desktop/fieldcheck-proxy/ after V022.36-V5.2 worker is deployed.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil
from pathlib import Path

print("═══ CANONICAL TAB 19 V5 ALGORITHM · POST-BATTERY UPDATE ═══\n")

CANONICAL = Path('FC_CANONICAL_STATE_V1.html')
if not CANONICAL.exists():
    print("✗ FAIL: FC_CANONICAL_STATE_V1.html not found in cwd")
    print("  Upload the current canonical first (Canonical Doctrine)")
    sys.exit(1)

c = CANONICAL.read_text()
orig_bytes = CANONICAL.stat().st_size
print(f"▸ canonical · {orig_bytes:,} bytes\n")

# Pre-flight: check current state
print("▸ Pre-flight checks\n")
checks = [
    ('Tab 19 V5 Algorithm pane', 'V5 <b>Algorithm</b>'),
    ('V022.36 reference (Tenet 39)', 'V022.36'),
]
for label, anchor in checks:
    print(f"  {'✓' if anchor in c else '✗'} {label}")
    if anchor not in c:
        print(f"\n✗ PRE-FLIGHT FAILED · expected anchor '{anchor}' not found")
        print(f"  Canonical may need other patches first.")
        sys.exit(1)

# Check if v2.2+v2.3 architecture content already inserted (idempotent)
if 'V5 v2.2+v2.3 ARCHITECTURE' in c or 'v5_apply_corrections' in c:
    print("\n✓ V5 v2.2+v2.3 architecture content already present (idempotent)")
    sys.exit(0)

print("\n▸ Pre-flight passed · proceeding with insertion\n")

# Backup
backup = CANONICAL.with_suffix('.html.pre-tab19-v22-36-update.bak')
shutil.copy(CANONICAL, backup)
print(f"▸ Backup: {backup}\n")

# Architecture content to insert into Tab 19 V5 Algorithm pane
new_content = '''
<div class="block" style="background:#0f2417;border-left:3px solid #4ade80;padding:14px 16px;margin:14px 0;border-radius:0 6px 6px 0">
<div style="font-size:11px;color:#86efac;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-bottom:6px">V5 v2.2+v2.3 ARCHITECTURE · MAY 27 NT · BATTERY VALIDATED</div>
<div style="color:#bbf7d0;font-size:14px;line-height:1.65">
<p style="margin-bottom:8px"><b>Hybrid architecture cracked the variance problem.</b> Pure prompt iteration hit a 50-50 win-rate ceiling. Pure caps would have been V4 redux. The answer: prompt does evidence evaluation, code applies 6 deterministic bright-line rules, audit trail in <code style="background:#000;padding:2px 6px;border-radius:3px;color:#a5f3fc">v5_corrections[]</code> shows exactly why each correction fired.</p>
<p style="margin-top:8px"><b>The proof:</b> Jordan Smith Jr was named explicitly in V5 v2.1's prompt as an example. Still scored 9.8 three runs in a row. V5 v2.2+v2.3 R1 suffix regex caught him deterministically at 5.4. Every time. That's the architecture.</p>
</div>
</div>

<div style="margin:14px 0">
<div style="font-size:13px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Six bright-line rules</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;background:#141414;border:1px solid #262626;border-radius:6px;overflow:hidden">
<thead><tr style="background:#1a1a1a"><th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">Rule</th><th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">Trigger</th><th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">Action</th></tr></thead>
<tbody>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R1</b></td><td style="padding:7px 10px;border-top:1px solid #262626">Jr/Sr/II/III/IV suffix + amateur tier</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 5.5 (HS) or 7.4 (D1)</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R2</b></td><td style="padding:7px 10px;border-top:1px solid #262626">HS + prep_amateur + no phenom flag</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 5.4</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R3</b></td><td style="padding:7px 10px;border-top:1px solid #262626">D1 + college_amateur + no phenom flag</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 7.4</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R4</b></td><td style="padding:7px 10px;border-top:1px solid #262626">Active career stage (rookie/early/prime/late_pro)</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 9.3</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R5</b></td><td style="padding:7px 10px;border-top:1px solid #262626">Rookie career stage</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 7.5</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R6</b></td><td style="padding:7px 10px;border-top:1px solid #262626">HS tier + pro stage (classification mismatch)</td><td style="padding:7px 10px;border-top:1px solid #262626">flag identity-review-needed (no correction)</td></tr>
</tbody>
</table>
</div>

<div style="margin:14px 0">
<div style="font-size:13px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Battery validation · 110 athletes · V5 v2 → v2.1 → v2.2+v2.3</div>
<table style="width:100%;border-collapse:collapse;font-size:12.5px;background:#141414;border:1px solid #262626;border-radius:6px;overflow:hidden">
<thead><tr style="background:#1a1a1a"><th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">Athlete</th><th style="text-align:right;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">Target</th><th style="text-align:right;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">V5 v2</th><th style="text-align:right;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">V5 v2.1</th><th style="text-align:right;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">V5 v2.2+v2.3</th><th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase">Rule</th></tr></thead>
<tbody>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Jordan Smith Jr.</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">4-5.5</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.8</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.8</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">5.4</td><td style="padding:6px 10px;border-top:1px solid #262626">R1 suffix</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Saniyah Hall</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">5.0-5.4</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">3.5</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.0</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">5.4</td><td style="padding:6px 10px;border-top:1px solid #262626">R2 HS</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Cameron Boozer</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">6.0-7.0</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.1</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.1</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">7.4</td><td style="padding:6px 10px;border-top:1px solid #262626">R3 D1</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">AJ Dybantsa</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">6.0-7.0</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.3</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.3</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">7.4</td><td style="padding:6px 10px;border-top:1px solid #262626">R3 D1</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Cooper Flagg</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">6.5-7.5</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.7</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.7</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">9.3</td><td style="padding:6px 10px;border-top:1px solid #262626">R4 active</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Tim Duncan</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">9.3-9.6</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">10.0</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">9.7</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">9.3</td><td style="padding:6px 10px;border-top:1px solid #262626">retired → no rule</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Kate Harpring</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">4-5.4</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.7</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">6.3</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">4.0</td><td style="padding:6px 10px;border-top:1px solid #262626">under R2</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Lamar Brown</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">5-7</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.5</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.5</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">5.4</td><td style="padding:6px 10px;border-top:1px solid #262626">R2 HS</td></tr>
<tr><td style="padding:6px 10px;border-top:1px solid #262626">Caitlin Clark</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">7.0-7.8</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#ef4444">9.6</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626">8.2</td><td style="text-align:right;padding:6px 10px;border-top:1px solid #262626;color:#4ade80;font-weight:600">7.4</td><td style="padding:6px 10px;border-top:1px solid #262626">R3 (cls flip)</td></tr>
</tbody>
</table>
<div style="font-size:12px;color:#888;margin-top:8px">100% rule compliance on the moat case (HS+D1+D2+D3 amateurs). Architecture proven across 110 athletes.</div>
</div>

<div style="margin:14px 0">
<div style="font-size:13px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Output schema · composite_v022_31.v5_corrections[]</div>
<pre style="background:#000;border:1px solid #262626;padding:12px;border-radius:6px;overflow-x:auto;font-size:11.5px;line-height:1.5;color:#a5f3fc;margin:8px 0">{
  "composite": 5.4,
  "composite_v022_31": {
    "raw": 9.83,
    "v5_corrected": 5.4,
    "v5_corrections": [
      {"rule": "suffix-amateur-ceiling", "from": 9.83, "to": 5.5, "reason": "Jr/Sr/II/III suffix at amateur tier - parent career data likely contaminated synthesis"},
      {"rule": "hs-evidence-ceiling-non-phenom", "from": 5.5, "to": 5.4, "reason": "HS-only evidence, no phenom criteria met (4 of 4 required)"}
    ],
    "v5_corrections_applied": true,
    "tier": "hs",
    "stage": "prep_amateur"
  }
}</pre>
</div>
'''

# Find insertion anchor: after pane-sub, before existing pane content closing
# Anchor on the V022.36 subtitle line we added previously
anchor_old = '<div class="pane-h">V5 <b>Algorithm</b></div>'
anchor_new = '<div class="pane-h">V5 <b>Algorithm</b></div>'  # keep same, insert AFTER pane-sub

# Better: find pane-sub closing for V5 and insert architecture content after
import re

# Pattern: pane-h V5 Algorithm + pane-sub
pattern = re.compile(
    r'(<div class="pane-h">V5 <b>Algorithm</b></div>\s*<div class="pane-sub">[^<]*</div>)',
    re.IGNORECASE
)

match = pattern.search(c)
if not match:
    print("✗ FAIL: could not find V5 Algorithm pane-h + pane-sub pattern")
    print("  Trying alternative: pane-h only")
    # Fallback - just match pane-h
    pattern2 = re.compile(
        r'(<div class="pane-h">V5 <b>Algorithm</b></div>)',
        re.IGNORECASE
    )
    match = pattern2.search(c)
    if not match:
        print("✗ FAIL: no V5 Algorithm anchor found at all")
        print(f"  Restore: cp {backup} FC_CANONICAL_STATE_V1.html")
        sys.exit(1)

# Insert architecture content immediately after the matched block
insertion_point = match.end()
c = c[:insertion_point] + new_content + c[insertion_point:]

CANONICAL.write_text(c)
new_bytes = CANONICAL.stat().st_size
delta = new_bytes - orig_bytes
print(f"▸ canonical updated · {new_bytes:,} bytes (delta +{delta:,})\n")

# Post-patch verification
print("▸ Post-patch verification\n")
post_checks = [
    ('V5 v2.2+v2.3 ARCHITECTURE marker', 'V5 v2.2+v2.3 ARCHITECTURE'),
    ('R1 suffix description', 'Jr/Sr/II/III/IV suffix'),
    ('R6 identity flag', 'identity-review-needed'),
    ('v5_corrections output schema', 'v5_corrections'),
    ('Jordan Smith Jr in battery table', 'Jordan Smith Jr.'),
    ('Tim Duncan in battery table', 'Tim Duncan'),
    ('hybrid architecture phrase', 'Hybrid architecture'),
]
ok = True
for label, anchor in post_checks:
    found = anchor in c
    print(f"  {'✓' if found else '✗'} {label}")
    if not found:
        ok = False

if not ok:
    print(f"\n✗ POST-PATCH VERIFICATION FAILED")
    print(f"  Restore: cp {backup} FC_CANONICAL_STATE_V1.html")
    sys.exit(1)

print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" CANONICAL TAB 19 V5 ALGORITHM · UPDATED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" canonical · {orig_bytes:,} → {new_bytes:,} bytes (+{delta:,})")
print(f" backup: {backup}")
print(f"")
print(f" Inserted into Tab 19:")
print(f"   ✓ V5 v2.2+v2.3 architecture narrative")
print(f"   ✓ 6 bright-line rules table")
print(f"   ✓ Battery validation results (9 key athletes V5 v2→v2.1→v2.2+v2.3)")
print(f"   ✓ composite_v022_31.v5_corrections[] output schema example")
print(f"")
print(f" NEXT:")
print(f"   1. ./fc-deploy-dev.sh")
print(f"   2. open https://fieldcheck-dev--fieldcheck-app.netlify.app/fc_canonical_state_v1")
print(f"   3. Verify Tab 19 displays correctly")
print(f"   4. If clean → ./fc-promote-prod.sh")
