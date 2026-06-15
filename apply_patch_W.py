#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-W · PATCH W · CROSS-ADAPTER IDENTITY VALIDATION
═══════════════════════════════════════════════════════════════════════════
Patch A validates names at bbref/bbref_pro/PFR/baseball_ref adapters via
_adapterProfileNameValidates. When name mismatch: ok=false, identity_validated
never set.

Patch W gates ALL pro-tier stage assignments on having at least 1 pro source
with identity_validated=true. Closes the corpus contamination class where
Wikipedia/Tavily/news bring HOFer text into an amateur's corpus, causing
prime_pro/early_pro to fire on text alone.

For Tate Ivanyo: 0 pro sources validate → all pro stages blocked → cascade
falls through to college_amateur or prep_amateur (per Patch L2/N1/U1).
For Tim Duncan: bbref validates → count ≥ 1 → pro stages fire normally.

Six surgical operations:
  1. Insert validatedProSourceCount + validatedProAvailable computation
     RIGHT BEFORE `let stage = 'unknown';`
  2-6. Add `&& validatedProAvailable` to 5 pro-stage clauses:
     - PATCH N3+Q1+Q3 prime_pro (multi-MVP/champion regex)
     - legend_pro (HOF regex + isLegendValidated)
     - retired_pro (isRetiredSig)
     - prime_pro text fallback (isProSig && !isCollegeSig)
     - early_pro text fallback (isProSig && isCollegeSig)

Variable detection: uses `typeof X !== 'undefined'` guards so missing
adapter variable names don't crash. Safe to over-include candidate names.

Atomicity:
  Backup → worker.js.pre-V022.32-W.bak
  Bump V022.32-U → V022.32-W, cache v022.32u → v022.32w
  Full grep-verify + node check; restore on failure
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-W.bak')

print("═══ V022.32-W · PATCH W · CROSS-ADAPTER IDENTITY VALIDATION ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

# Confirm V022.32-U baseline (NOT V022.32-U1 since we reverted)
if "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content:
    print("✗ Worker not on V022.32-U baseline (6 patches) · ABORT")
    print("  Run revert first if needed: cp worker.js.pre-V022.32-U1.bak worker.js")
    sys.exit(1)
print("  ✓ baseline = V022.32-U (6 patches)\n")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("▸ Anchor detection...")

# Anchor 1: insertion point — find `let stage = 'unknown';` and `let stageSignals = [];`
# This is the start of the stage cascade.
anchor_cascade_start = re.compile(
    r'(^[ \t]*)// ── STAGE DETECTION ──\n'
    r'[ \t]*let stage = \'unknown\';\n'
    r'[ \t]*let stageSignals = \[\];',
    re.MULTILINE
)
cascade_start_match = anchor_cascade_start.search(content)
if not cascade_start_match:
    print("✗ Cascade start anchor not found · ABORT"); sys.exit(1)
indent = cascade_start_match.group(1)
print(f"  ✓ Cascade start at line {content[:cascade_start_match.start()].count(chr(10)) + 1}")
print(f"  ✓ Indent: {len(indent)} char(s) [{repr(indent)}]")

# Anchor 2: PATCH N3+Q1+Q3 prime_pro
# Unique marker: stageSignals.push('q1_prime_pro_overrides_hof_projection')
anchor_n3 = "stageSignals.push('q1_prime_pro_overrides_hof_projection');"
if content.count(anchor_n3) != 1:
    print(f"✗ N3+Q1+Q3 anchor count = {content.count(anchor_n3)} · ABORT"); sys.exit(1)
print(f"  ✓ N3+Q1+Q3 prime_pro anchor found")

# Anchor 3: legend_pro
anchor_legend = "stageSignals.push('legend+pro_keyword');"
if content.count(anchor_legend) != 1:
    print(f"✗ legend_pro anchor count = {content.count(anchor_legend)} · ABORT"); sys.exit(1)
print(f"  ✓ legend_pro anchor found")

# Anchor 4: retired_pro
anchor_retired = "else if (isRetiredSig) { stage = 'retired_pro'; stageSignals.push('retired_keyword'); }"
if content.count(anchor_retired) != 1:
    print(f"✗ retired_pro anchor count = {content.count(anchor_retired)} · ABORT"); sys.exit(1)
print(f"  ✓ retired_pro anchor found")

# Anchor 5: prime_pro text fallback
anchor_prime_text = "else if (isProSig && !isCollegeSig) { stage = 'prime_pro'; stageSignals.push('pro_keyword_no_college'); }"
if content.count(anchor_prime_text) != 1:
    print(f"✗ prime_pro text anchor count = {content.count(anchor_prime_text)} · ABORT"); sys.exit(1)
print(f"  ✓ prime_pro text anchor found")

# Anchor 6: early_pro text fallback
anchor_early_text = "else if (isProSig && isCollegeSig) { stage = 'early_pro'; stageSignals.push('pro+college_keyword'); }"
if content.count(anchor_early_text) != 1:
    print(f"✗ early_pro text anchor count = {content.count(anchor_early_text)} · ABORT"); sys.exit(1)
print(f"  ✓ early_pro text anchor found")

# Banner & cache anchors
banner_old_rx = re.compile(r'// FIELDCHECK_WORKER_VERSION = V022\.32-U · TENET 47 ATOMIC · 6 patches[^\n]*')
banner_match = banner_old_rx.search(content)
if not banner_match:
    print("✗ banner anchor not found · ABORT"); sys.exit(1)
banner_old = banner_match.group(0)
print(f"  ✓ banner anchor found")

cache_old = "const cacheVersion = 'v022.32u'"
if content.count(cache_old) != 1:
    print(f"✗ cache anchor count = {content.count(cache_old)} · ABORT"); sys.exit(1)
print(f"  ✓ cache anchor found\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP} ({BACKUP.stat().st_size:,} bytes)\n")


# ─── BUILD PATCH 1: validatedProSourceCount computation ────────────────────
# Insert BEFORE `// ── STAGE DETECTION ──`
patch1_old = cascade_start_match.group(0)
patch1_new = (
    f"{indent}// V022.32-W · PATCH W · CROSS-ADAPTER IDENTITY VALIDATION (May 26 2026)\n"
    f"{indent}// Count Patch-A-validated pro sources (bbref/bbref_pro/PFR/baseball_ref).\n"
    f"{indent}// If 0, ALL pro-tier stage assignments are blocked downstream.\n"
    f"{indent}// Closes Tate Ivanyo / Antwan Kimmons / Donovan Dent corpus contamination class.\n"
    f"{indent}// Legit pros (Tim Duncan/Steph Curry/Cooper Flagg) pass through normally because\n"
    f"{indent}// their bbref/PFR queries validate identity (Patch A line 5455+).\n"
    f"{indent}let _v22_w_validatedProSourceCount = 0;\n"
    f"{indent}try {{ if (typeof bbref !== 'undefined' && bbref && bbref.ok && bbref.identity_validated) _v22_w_validatedProSourceCount++; }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof bbrefPro !== 'undefined' && bbrefPro && bbrefPro.ok && bbrefPro.identity_validated) _v22_w_validatedProSourceCount++; }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof pfr !== 'undefined' && pfr && pfr.ok && pfr.identity_validated) _v22_w_validatedProSourceCount++; }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof baseball !== 'undefined' && baseball && baseball.ok && baseball.identity_validated) _v22_w_validatedProSourceCount++; }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof baseballRef !== 'undefined' && baseballRef && baseballRef.ok && baseballRef.identity_validated) _v22_w_validatedProSourceCount++; }} catch(_e) {{}}\n"
    f"{indent}const _v22_w_validatedProAvailable = _v22_w_validatedProSourceCount > 0;\n"
    f"\n"
    + patch1_old  # original cascade start follows
)


# ─── APPLY PATCH 1 ──────────────────────────────────────────────────────────
print("▸ Applying P1: validatedProSourceCount computation...")
content_v1 = content.replace(patch1_old, patch1_new, 1)
if content_v1 == content:
    print("✗ P1 no-op · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ P1 applied · delta {len(content_v1) - len(content):+d} bytes\n")


# ─── APPLY PATCH 2: gate PATCH N3+Q1+Q3 prime_pro ──────────────────────────
# Find the structure around stageSignals.push('q1_prime_pro_overrides_hof_projection')
# Need to find the closing `) {` line above the stage assignment
# The clause is: else if ( ... regex ... && isProSig && !(...) ) { stage = 'prime_pro'; stageSignals.push(...) }
# We add `&& _v22_w_validatedProAvailable` before the closing `)`.
# Pattern matches: the test condition's `!(isRetiredSig && /(?:retired|former)...test(allText))` followed by `) {`

# Use a regex to find the closing of the N3 condition expression
n3_old_rx = re.compile(
    r"(&& !\(isRetiredSig && /\(\?:retired\|former\)\\s\+\(\?:nba\|wnba\|nfl\|mlb\)\\s\+\(\?:player\|star\|champion\|mvp\)/i\.test\(allText\)\))\n"
    r"([ \t]*)\) \{\n"
    r"([ \t]*)stage = 'prime_pro';\n"
    r"([ \t]*)stageSignals\.push\('q1_prime_pro_overrides_hof_projection'\);"
)
n3_match = n3_old_rx.search(content_v1)
if not n3_match:
    print("✗ P2 anchor pattern not found · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)

n3_old = n3_match.group(0)
n3_new = (
    f"{n3_match.group(1)}\n"
    f"{n3_match.group(2)}&& _v22_w_validatedProAvailable\n"
    f"{n3_match.group(2)}) {{\n"
    f"{n3_match.group(3)}stage = 'prime_pro';\n"
    f"{n3_match.group(4)}stageSignals.push('q1_prime_pro_overrides_hof_projection');"
)

print("▸ Applying P2: gate N3+Q1+Q3 prime_pro on validatedProAvailable...")
content_v2 = content_v1.replace(n3_old, n3_new, 1)
if content_v2 == content_v1:
    print("✗ P2 no-op · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ P2 applied · delta {len(content_v2) - len(content_v1):+d} bytes\n")


# ─── APPLY PATCH 3: gate legend_pro ────────────────────────────────────────
# Pattern: && isLegendValidated\n) {\n... stage = 'legend_pro'
legend_old_rx = re.compile(
    r"(&& isLegendValidated)\n"
    r"([ \t]*)\) \{\n"
    r"([ \t]*)stage = 'legend_pro';"
)
legend_match = legend_old_rx.search(content_v2)
if not legend_match:
    print("✗ P3 legend_pro pattern not found · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)

legend_old = legend_match.group(0)
legend_new = (
    f"{legend_match.group(1)}\n"
    f"{legend_match.group(2)}&& _v22_w_validatedProAvailable\n"
    f"{legend_match.group(2)}) {{\n"
    f"{legend_match.group(3)}stage = 'legend_pro';"
)

print("▸ Applying P3: gate legend_pro on validatedProAvailable...")
content_v3 = content_v2.replace(legend_old, legend_new, 1)
if content_v3 == content_v2:
    print("✗ P3 no-op · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ P3 applied · delta {len(content_v3) - len(content_v2):+d} bytes\n")


# ─── APPLY PATCH 4: gate retired_pro ────────────────────────────────────────
retired_new = "else if (isRetiredSig && _v22_w_validatedProAvailable) { stage = 'retired_pro'; stageSignals.push('retired_keyword'); }"
print("▸ Applying P4: gate retired_pro on validatedProAvailable...")
content_v4 = content_v3.replace(anchor_retired, retired_new, 1)
if content_v4 == content_v3:
    print("✗ P4 no-op · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ P4 applied · delta {len(content_v4) - len(content_v3):+d} bytes\n")


# ─── APPLY PATCH 5: gate prime_pro text fallback ────────────────────────────
prime_text_new = "else if (isProSig && !isCollegeSig && _v22_w_validatedProAvailable) { stage = 'prime_pro'; stageSignals.push('pro_keyword_no_college'); }"
print("▸ Applying P5: gate prime_pro text fallback on validatedProAvailable...")
content_v5 = content_v4.replace(anchor_prime_text, prime_text_new, 1)
if content_v5 == content_v4:
    print("✗ P5 no-op · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ P5 applied · delta {len(content_v5) - len(content_v4):+d} bytes\n")


# ─── APPLY PATCH 6: gate early_pro text fallback ────────────────────────────
early_text_new = "else if (isProSig && isCollegeSig && _v22_w_validatedProAvailable) { stage = 'early_pro'; stageSignals.push('pro+college_keyword'); }"
print("▸ Applying P6: gate early_pro text fallback on validatedProAvailable...")
content_v6 = content_v5.replace(anchor_early_text, early_text_new, 1)
if content_v6 == content_v5:
    print("✗ P6 no-op · ABORT")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ P6 applied · delta {len(content_v6) - len(content_v5):+d} bytes\n")


# ─── BUMP BANNER + CACHE ───────────────────────────────────────────────────
banner_new = "// FIELDCHECK_WORKER_VERSION = V022.32-W · TENET 47 ATOMIC · 7 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, W (cross-adapter identity validation gates pro stages on Patch-A-validated source count)"
print("▸ Bumping banner V022.32-U → V022.32-W...")
content_v7 = content_v6.replace(banner_old, banner_new, 1)
if content_v7 == content_v6:
    print("✗ banner no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ banner bumped\n")

cache_new = "const cacheVersion = 'v022.32w'"
print("▸ Bumping cache v022.32u → v022.32w...")
content_final = content_v7.replace(cache_old, cache_new, 1)
if content_final == content_v7:
    print("✗ cache no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ cache bumped\n")


# ─── WRITE ──────────────────────────────────────────────────────────────────
WORKER.write_text(content_final)
size_after = len(content_final)
sha_after = hashlib.sha256(content_final.encode()).hexdigest()[:12]
print(f"▸ worker.js written · {size_after:,} bytes (delta {size_after - size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY (Tenet 47.1) ──────────────────────────────────────────────
print("▸ Grep-verify (Tenet 47.1)...")
checks = [
    ("Patch W marker (count var)", "_v22_w_validatedProSourceCount" in content_final),
    ("Patch W marker (avail var)", "_v22_w_validatedProAvailable" in content_final),
    ("Patch W comment", "PATCH W · CROSS-ADAPTER IDENTITY VALIDATION" in content_final),
    ("bbref typeof guard", "typeof bbref !== 'undefined'" in content_final),
    ("pfr typeof guard", "typeof pfr !== 'undefined'" in content_final),
    ("N3 gated", "_v22_w_validatedProAvailable\n      ) {" in content_final or content_final.count("&& _v22_w_validatedProAvailable") >= 5),
    ("legend_pro still references isLegendValidated", "&& isLegendValidated" in content_final),
    ("retired_pro gated", "isRetiredSig && _v22_w_validatedProAvailable" in content_final),
    ("prime_pro text gated", "isProSig && !isCollegeSig && _v22_w_validatedProAvailable" in content_final),
    ("early_pro text gated", "isProSig && isCollegeSig && _v22_w_validatedProAvailable" in content_final),
    ("banner V022.32-W", "V022.32-W · TENET 47 ATOMIC · 7 patches" in content_final),
    ("cache v022.32w", "'v022.32w'" in content_final),
    ("old V022.32-U banner removed", "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content_final),
    ("old cache v022.32u removed", "const cacheVersion = 'v022.32u'" not in content_final),
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
print(f"  ✓ node --check passed\n")


# ─── DONE ──────────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" V022.32-W PATCH W APPLIED CLEAN")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-U → V022.32-W · {size_before:,} → {size_after:,} bytes")
print(f" Cache:  v022.32u → v022.32w (forces fresh synthesis)")
print(f"")
print(f" Gates 5 pro-tier stage clauses on validatedProSourceCount > 0:")
print(f"   1. PATCH N3+Q1+Q3 prime_pro (multi-MVP/champion regex)")
print(f"   2. legend_pro (HOF regex + isLegendValidated)")
print(f"   3. retired_pro (isRetiredSig)")
print(f"   4. prime_pro text fallback")
print(f"   5. early_pro text fallback")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: bump canonical V5.26 → V5.28, ./fc-deploy-dev.sh, re-run battery")
print(f" Expected wins: Tate Ivanyo 9.3 → ≤6.8 · Donovan Dent 7.9 → ≤6.8 · Antwan stays 5.4")
print(f" Test for regressions: Cooper Flagg should stay 9.3 (bbref validates),")
print(f"   Caitlin Clark stays 7.9 (bbref validates), Steph Curry NOT regressed.")
