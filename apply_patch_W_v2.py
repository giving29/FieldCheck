#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-W2 · PATCH W v2 · CORRECTED · explicit-rejection-only blocking
═══════════════════════════════════════════════════════════════════════════
v1 conflated adapter FAILURE (timeout/404/no-data) with name MISMATCH.
v2 blocks pro stages ONLY on explicit Patch A name_mismatch_v022.30 error.

Logic:
  explicitRejection = adapter returned !ok with error 'name_mismatch_v022.30'
  validatedPro = adapter returned ok with identity_validated === true
  blockProStages = explicitRejection > 0 && validatedPro === 0
  Gates: && !blockProStages on all 5 pro-tier stage clauses

Truth table:
  Tate Ivanyo · bbref rejects name match → rej=1, val=0 → block=true → FALLS THRU ✓
  Cooper Flagg · bbref validates → rej=0, val=1 → block=false → prime_pro fires ✓
  Tim Duncan · bbref validates → rej=0, val=1 → block=false → legend_pro fires ✓
  Cooper Flagg w/ timeout · no rejection → rej=0, val=0 → block=false → text path ✓
  Random HS w/ pro corpus → rej=1, val=0 → block=true → FALLS THRU ✓

Per-clause verification: counts `&& !_v22_w_blockProStages` in each specific
anchor context, not just total. Partial application impossible.

Atomicity: backup → patch → grep-verify → node-check → restore on failure
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, subprocess, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-W2.bak')

print("═══ V022.32-W2 · PATCH W v2 · CORRECTED LOGIC ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

# Baseline check
if "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content:
    print("✗ Not on V022.32-U baseline · ABORT"); sys.exit(1)
print("  ✓ baseline = V022.32-U (6 patches)\n")


# ─── ANCHOR DETECTION (each anchor must be exactly 1) ──────────────────────
print("▸ Anchor detection...")

# A1: cascade start
a1_rx = re.compile(
    r'(^[ \t]*)// ── STAGE DETECTION ──\n'
    r'[ \t]*let stage = \'unknown\';\n'
    r'[ \t]*let stageSignals = \[\];',
    re.MULTILINE
)
a1_match = a1_rx.search(content)
if not a1_match:
    print("✗ A1 cascade start not found · ABORT"); sys.exit(1)
indent = a1_match.group(1)
print(f"  ✓ A1 cascade start · indent {len(indent)}")

# A2-A6: each pro-stage clause via unique marker
def must_be_once(needle, label):
    n = content.count(needle)
    if n != 1:
        print(f"✗ {label} count={n} · ABORT"); sys.exit(1)
    print(f"  ✓ {label}")
    return n

must_be_once("stageSignals.push('q1_prime_pro_overrides_hof_projection');", "A2 N3+Q1+Q3")
must_be_once("stageSignals.push('legend+pro_keyword');", "A3 legend_pro")
must_be_once("else if (isRetiredSig) { stage = 'retired_pro'; stageSignals.push('retired_keyword'); }", "A4 retired_pro")
must_be_once("else if (isProSig && !isCollegeSig) { stage = 'prime_pro'; stageSignals.push('pro_keyword_no_college'); }", "A5 prime_pro text")
must_be_once("else if (isProSig && isCollegeSig) { stage = 'early_pro'; stageSignals.push('pro+college_keyword'); }", "A6 early_pro text")

# Banner + cache
banner_rx = re.compile(r'// FIELDCHECK_WORKER_VERSION = V022\.32-U · TENET 47 ATOMIC · 6 patches[^\n]*')
banner_m = banner_rx.search(content)
if not banner_m: print("✗ banner not found · ABORT"); sys.exit(1)
banner_old = banner_m.group(0)
print(f"  ✓ banner")

cache_old = "const cacheVersion = 'v022.32u'"
must_be_once(cache_old, "cache")
print()


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup: {BACKUP}\n")


# ─── P1: insert dual-counter blocking logic ────────────────────────────────
a1_old = a1_match.group(0)
a1_new = (
    f"{indent}// V022.32-W2 · PATCH W v2 · CROSS-ADAPTER IDENTITY VALIDATION (May 26 night)\n"
    f"{indent}// Block pro stages ONLY on explicit Patch A name_mismatch_v022.30 rejection.\n"
    f"{indent}// Adapter failures (timeout/404/no-data) are NOT contamination signal — leave alone.\n"
    f"{indent}// Closes Tate Ivanyo / Donovan Dent corpus contamination class WITHOUT regressing\n"
    f"{indent}// Cooper Flagg / Tim Duncan when their bbref/PFR adapters time out in dev.\n"
    f"{indent}let _v22_w_explicitRejectionCount = 0;\n"
    f"{indent}let _v22_w_validatedProCount = 0;\n"
    f"{indent}const _v22_w_checkSrc = (s) => {{\n"
    f"{indent}  if (!s) return;\n"
    f"{indent}  if (!s.ok && s.error && String(s.error).indexOf('name_mismatch') >= 0) _v22_w_explicitRejectionCount++;\n"
    f"{indent}  if (s.ok && s.identity_validated === true) _v22_w_validatedProCount++;\n"
    f"{indent}}};\n"
    f"{indent}try {{ if (typeof bbref !== 'undefined') _v22_w_checkSrc(bbref); }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof bbrefPro !== 'undefined') _v22_w_checkSrc(bbrefPro); }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof pfr !== 'undefined') _v22_w_checkSrc(pfr); }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof baseball !== 'undefined') _v22_w_checkSrc(baseball); }} catch(_e) {{}}\n"
    f"{indent}try {{ if (typeof baseballRef !== 'undefined') _v22_w_checkSrc(baseballRef); }} catch(_e) {{}}\n"
    f"{indent}const _v22_w_blockProStages = _v22_w_explicitRejectionCount > 0 && _v22_w_validatedProCount === 0;\n"
    f"\n"
    + a1_old
)
print("▸ P1: dual-counter blocking logic...")
content_v1 = content.replace(a1_old, a1_new, 1)
if content_v1 == content:
    print("✗ P1 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v1)-len(content):+d}\n")


# ─── P2: gate N3+Q1+Q3 prime_pro ────────────────────────────────────────────
n3_old_rx = re.compile(
    r"(&& !\(isRetiredSig && /\(\?:retired\|former\)\\s\+\(\?:nba\|wnba\|nfl\|mlb\)\\s\+\(\?:player\|star\|champion\|mvp\)/i\.test\(allText\)\))\n"
    r"([ \t]*)\) \{\n"
    r"([ \t]*)stage = 'prime_pro';\n"
    r"([ \t]*)stageSignals\.push\('q1_prime_pro_overrides_hof_projection'\);"
)
n3_match = n3_old_rx.search(content_v1)
if not n3_match:
    print("✗ P2 anchor not found · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
n3_old = n3_match.group(0)
n3_new = (
    f"{n3_match.group(1)}\n"
    f"{n3_match.group(2)}&& !_v22_w_blockProStages\n"
    f"{n3_match.group(2)}) {{\n"
    f"{n3_match.group(3)}stage = 'prime_pro';\n"
    f"{n3_match.group(4)}stageSignals.push('q1_prime_pro_overrides_hof_projection');"
)
print("▸ P2: gate N3+Q1+Q3 prime_pro...")
content_v2 = content_v1.replace(n3_old, n3_new, 1)
if content_v2 == content_v1:
    print("✗ P2 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v2)-len(content_v1):+d}\n")


# ─── P3: gate legend_pro ────────────────────────────────────────────────────
legend_rx = re.compile(
    r"(&& isLegendValidated)\n"
    r"([ \t]*)\) \{\n"
    r"([ \t]*)stage = 'legend_pro';"
)
legend_match = legend_rx.search(content_v2)
if not legend_match:
    print("✗ P3 anchor not found · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
legend_old = legend_match.group(0)
legend_new = (
    f"{legend_match.group(1)}\n"
    f"{legend_match.group(2)}&& !_v22_w_blockProStages\n"
    f"{legend_match.group(2)}) {{\n"
    f"{legend_match.group(3)}stage = 'legend_pro';"
)
print("▸ P3: gate legend_pro...")
content_v3 = content_v2.replace(legend_old, legend_new, 1)
if content_v3 == content_v2:
    print("✗ P3 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v3)-len(content_v2):+d}\n")


# ─── P4: gate retired_pro ───────────────────────────────────────────────────
retired_old = "else if (isRetiredSig) { stage = 'retired_pro'; stageSignals.push('retired_keyword'); }"
retired_new = "else if (isRetiredSig && !_v22_w_blockProStages) { stage = 'retired_pro'; stageSignals.push('retired_keyword'); }"
print("▸ P4: gate retired_pro...")
content_v4 = content_v3.replace(retired_old, retired_new, 1)
if content_v4 == content_v3:
    print("✗ P4 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v4)-len(content_v3):+d}\n")


# ─── P5: gate prime_pro text ────────────────────────────────────────────────
prime_old = "else if (isProSig && !isCollegeSig) { stage = 'prime_pro'; stageSignals.push('pro_keyword_no_college'); }"
prime_new = "else if (isProSig && !isCollegeSig && !_v22_w_blockProStages) { stage = 'prime_pro'; stageSignals.push('pro_keyword_no_college'); }"
print("▸ P5: gate prime_pro text...")
content_v5 = content_v4.replace(prime_old, prime_new, 1)
if content_v5 == content_v4:
    print("✗ P5 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v5)-len(content_v4):+d}\n")


# ─── P6: gate early_pro text ────────────────────────────────────────────────
early_old = "else if (isProSig && isCollegeSig) { stage = 'early_pro'; stageSignals.push('pro+college_keyword'); }"
early_new = "else if (isProSig && isCollegeSig && !_v22_w_blockProStages) { stage = 'early_pro'; stageSignals.push('pro+college_keyword'); }"
print("▸ P6: gate early_pro text...")
content_v6 = content_v5.replace(early_old, early_new, 1)
if content_v6 == content_v5:
    print("✗ P6 no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓ delta {len(content_v6)-len(content_v5):+d}\n")


# ─── BANNER + CACHE ─────────────────────────────────────────────────────────
banner_new = "// FIELDCHECK_WORKER_VERSION = V022.32-W2 · TENET 47 ATOMIC · 7 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, W2 (explicit-rejection-only blocks pro stages on Patch A name_mismatch)"
print("▸ Bumping banner V022.32-U → V022.32-W2...")
content_v7 = content_v6.replace(banner_old, banner_new, 1)
if content_v7 == content_v6:
    print("✗ banner no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓\n")

cache_new = "const cacheVersion = 'v022.32w2'"
print("▸ Bumping cache v022.32u → v022.32w2...")
content_final = content_v7.replace(cache_old, cache_new, 1)
if content_final == content_v7:
    print("✗ cache no-op · ABORT"); shutil.copy(BACKUP, WORKER); sys.exit(1)
print(f"  ✓\n")


# ─── WRITE ──────────────────────────────────────────────────────────────────
WORKER.write_text(content_final)
size_after = len(content_final)
sha_after = hashlib.sha256(content_final.encode()).hexdigest()[:12]
print(f"▸ worker.js · {size_after:,} bytes (delta {size_after-size_before:+d}) · sha={sha_after}\n")


# ─── PER-CLAUSE VERIFICATION (Tenet 47.1 strict) ──────────────────────────
print("▸ Per-clause verification...\n")

# Verify EACH of 5 pro-stage clauses has the gate, by checking specific neighbor text
gate = "!_v22_w_blockProStages"

# Each verification looks for the gate adjacent to its anchor (a context-specific match)
clause_checks = [
    # N3+Q1+Q3: gate must appear before stageSignals.push('q1_prime_pro_overrides_hof_projection')
    ("N3+Q1+Q3 gated",
     re.compile(r"&& " + re.escape(gate) + r"\s*\n\s*\) \{\s*\n\s*stage = 'prime_pro';\s*\n\s*stageSignals\.push\('q1_prime_pro_overrides_hof_projection'\);")),
    # legend_pro
    ("legend_pro gated",
     re.compile(r"&& isLegendValidated\s*\n\s*&& " + re.escape(gate) + r"\s*\n\s*\) \{\s*\n\s*stage = 'legend_pro';")),
    # retired_pro
    ("retired_pro gated",
     re.compile(r"else if \(isRetiredSig && " + re.escape(gate) + r"\) \{ stage = 'retired_pro';")),
    # prime_pro text
    ("prime_pro text gated",
     re.compile(r"else if \(isProSig && !isCollegeSig && " + re.escape(gate) + r"\) \{ stage = 'prime_pro';")),
    # early_pro text
    ("early_pro text gated",
     re.compile(r"else if \(isProSig && isCollegeSig && " + re.escape(gate) + r"\) \{ stage = 'early_pro';")),
]

all_ok = True
for label, rx in clause_checks:
    found = bool(rx.search(content_final))
    print(f"  {'✓' if found else '✗'} {label}")
    if not found: all_ok = False

# Additional checks
extras = [
    ("dual-counter present", "_v22_w_explicitRejectionCount" in content_final),
    ("blockProStages var present", "_v22_w_blockProStages" in content_final),
    ("checkSrc helper present", "_v22_w_checkSrc" in content_final),
    ("indexOf name_mismatch check", "indexOf('name_mismatch')" in content_final),
    ("identity_validated === true check", "s.identity_validated === true" in content_final),
    ("banner V022.32-W2", "V022.32-W2 · TENET 47 ATOMIC · 7 patches" in content_final),
    ("cache v022.32w2", "'v022.32w2'" in content_final),
    ("old V022.32-U banner removed", "V022.32-U · TENET 47 ATOMIC · 6 patches" not in content_final),
    ("old cache v022.32u removed", "const cacheVersion = 'v022.32u'" not in content_final),
]
for label, ok in extras:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

print()

if not all_ok:
    print("✗ VERIFICATION FAILED · restoring")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)


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
print(" V022.32-W2 PATCH W v2 APPLIED CLEAN · per-clause verified")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-U → V022.32-W2 · cache: v022.32u → v022.32w2")
print(f"")
print(f" Logic: block pro stages ONLY on explicit Patch A name_mismatch rejection.")
print(f" Adapter timeouts/404s do NOT block (no contamination signal).")
print(f"")
print(f" Expected:")
print(f"   Tate Ivanyo  9.3 → ≤6.8 (bbref rejects, block triggers, falls thru)")
print(f"   Donovan Dent 7.4/d1 stays correct (already validated)")
print(f"   Cooper Flagg 9.3 stays (bbref validates, no block)")
print(f"   Tim Duncan   should validate if bbref completes")
print(f"   Antwan Kimmons stays 5.4 (no false-positive blocking)")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: bump canonical V5.26 → V5.29 with V022.32-W2 marker, deploy, battery")
