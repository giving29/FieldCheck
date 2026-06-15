#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-Q · PATCH U DIAGNOSTIC · maps actual code anchors before patching
═══════════════════════════════════════════════════════════════════════════
DOES NOT MUTATE worker.js · read-only · prints surrounding context.

Purpose: locate the actual current-state code for:
  · CAP table definition (V4 caps · HS 5.4, D1 7.4, etc · from Patch O)
  · composite_v022_31 object construction (where tier/cap finalize)
  · tier assignment / tier classifier function
  · stage assignment / stage classifier function
  · school override absolute (Patch N1a/N1b sites)
  · tier=unknown fallback path (U2 target)

Output: prints each hit with file line numbers + ±15 lines of context.
Use this output to write the precise apply_patch_U.py.

Run:
  cd ~/Desktop/fieldcheck-proxy
  cp ~/Downloads/patch_U_diagnostic.py .
  python3 patch_U_diagnostic.py
═══════════════════════════════════════════════════════════════════════════
"""
import os, re, sys
from pathlib import Path

WORKER = Path('worker.js')
if not WORKER.exists():
    print(f"✗ worker.js not found at {WORKER.absolute()}")
    print("  cd ~/Desktop/fieldcheck-proxy first")
    sys.exit(1)

with open(WORKER, 'r') as f:
    lines = f.readlines()

print(f"▸ worker.js: {len(lines)} lines, {WORKER.stat().st_size:,} bytes")
print(f"▸ Searching for Patch U anchors...\n")


def find_all(pattern, label, context_before=2, context_after=12, max_hits=5):
    """Find regex pattern in worker.js · print line numbers + context."""
    hits = []
    rx = re.compile(pattern, re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if rx.search(line):
            hits.append(i)
    print(f"═══ {label}")
    print(f"    pattern: {pattern}")
    print(f"    hits: {len(hits)}")
    if not hits:
        print(f"    ✗ NOT FOUND")
        print()
        return []
    for hit_n, line_no in enumerate(hits[:max_hits]):
        start = max(0, line_no - 1 - context_before)
        end = min(len(lines), line_no - 1 + context_after + 1)
        print(f"\n    ── hit {hit_n+1} at line {line_no} ──")
        for j in range(start, end):
            marker = '  >>> ' if j + 1 == line_no else '      '
            print(f"    {j+1:>6}{marker}{lines[j].rstrip()[:130]}")
    if len(hits) > max_hits:
        print(f"\n    ... +{len(hits)-max_hits} more hits at lines: {hits[max_hits:max_hits+10]}")
    print()
    return hits


# ─── ANCHOR 1 · CAP table (Patch O values) ─────────────────────────────────
# We expect to find something like {hs: 5.4, d1: 7.4, d2: 6.8, ...}
find_all(
    r"hs\s*:\s*5\.4|d1\s*:\s*7\.4",
    "ANCHOR 1 · CAP table definition (Patch O caps)",
    context_before=3, context_after=15
)

# ─── ANCHOR 2 · composite_v022_31 object construction ──────────────────────
find_all(
    r"composite_v022_31\s*[:=]\s*\{|composite_v022_31\s*=\s*\{",
    "ANCHOR 2 · composite_v022_31 object construction",
    context_before=3, context_after=20
)

# ─── ANCHOR 3 · tier= assignment in synthesis ──────────────────────────────
find_all(
    r"\btier\s*[:=]\s*['\"]?(hs|d1|d2|d3|juco|naia|pro|unknown)['\"]?",
    "ANCHOR 3 · tier assignment sites",
    context_before=1, context_after=4,
    max_hits=8
)

# ─── ANCHOR 4 · stage= assignment in synthesis ─────────────────────────────
find_all(
    r"\bstage\s*[:=]\s*['\"]?(prep_amateur|college_amateur|early_pro|prime_pro|legend_pro|retired_pro|unknown)['\"]?",
    "ANCHOR 4 · stage assignment sites",
    context_before=1, context_after=4,
    max_hits=8
)

# ─── ANCHOR 5 · cap lookup / fallback (U2 target) ──────────────────────────
find_all(
    r"cap\s*=.*\[.*tier.*\]|CAPS\[|TIER_CAPS\[|cap_table\[",
    "ANCHOR 5 · cap lookup site (U2 fallback target)",
    context_before=3, context_after=10
)

# ─── ANCHOR 6 · early_pro fallback (U2 specific) ───────────────────────────
find_all(
    r"\|\|\s*7\.9|\?\?\s*7\.9|\|\|\s*['\"]?early_pro|fallback.*early_pro|default.*early_pro",
    "ANCHOR 6 · early_pro default fallback (U2 specific)",
    context_before=2, context_after=8
)

# ─── ANCHOR 7 · school override (Patch N1a/N1b) ────────────────────────────
find_all(
    r"prep_amateur.*school|school.*prep_amateur|isLegendValidated|school_override",
    "ANCHOR 7 · school override sites (N1a/N1b)",
    context_before=2, context_after=8
)

# ─── ANCHOR 8 · bbref_pro identity validation (Patch A · U3 verify) ────────
find_all(
    r"_adapterProfileNameValidates|identity_validated|name_mismatch_v022\.30|identityValidation",
    "ANCHOR 8 · bbref_pro identity validation (Patch A · U3 verify alive)",
    context_before=2, context_after=10
)

# ─── ANCHOR 9 · Tate Ivanyo / Antwan Kimmons handling? ─────────────────────
find_all(
    r"prime_pro.*cascade|cascade.*prime_pro|legend_pro.*cascade",
    "ANCHOR 9 · prime_pro / legend_pro cascade gates (Patch C · multi-source corroboration)",
    context_before=2, context_after=10
)

# ─── ANCHOR 10 · version banner (confirm V022.32-Q current) ────────────────
find_all(
    r"V022\.32-Q|V022\.32q|TENET 47|v022\.32q",
    "ANCHOR 10 · V022.32-Q version banner + Tenet 47 markers",
    context_before=1, context_after=4
)

# ─── SUMMARY ───────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" SUMMARY · paste this entire output back to Claude for Patch U apply")
print("═══════════════════════════════════════════════════════════════════════")
print(f" worker.js size: {WORKER.stat().st_size:,} bytes · {len(lines)} lines")
print(f" If ANCHOR 10 shows V022.32-Q hits, you're on the right baseline")
print(f" If ANCHOR 1 (caps) + ANCHOR 5 (lookup) + ANCHOR 6 (fallback) hit,")
print(f"   U1+U2 patches can be written precisely")
print(f" If ANCHOR 8 has hits, Patch A name validation IS still in worker")
print(f"   (U3 may be unnecessary; the Tate/Kimmons regression may be a different code path)")
