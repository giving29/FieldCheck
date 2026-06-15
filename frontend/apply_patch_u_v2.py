#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-U · PATCH U APPLY · v2 · indentation-aware
═══════════════════════════════════════════════════════════════════════════
v1 failed because it hardcoded indentation. v2 detects actual leading
whitespace from the file via regex capture, then builds patches that match.

Patches:
  U1 · HS-keyword amateur-first stage gate (closes Tate/Kimmons regression)
  U2 · Stage-driven tier+cap consistency (closes Caleb Gaskins comp=7.9)

Doctrine:
  Tenet 47.1 grep-verify · 47.2 atomic version bumps · 47.3 fix only U1+U2
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, hashlib, subprocess
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-U-RECOVERY.bak')

print("═══ V022.32-U PATCH U · APPLY v2 (indentation-aware) ═══\n")

if not WORKER.exists():
    print(f"✗ worker.js not found at {WORKER.absolute()}")
    sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

if "V022.32-Q" not in content:
    print(f"✗ Worker not on V022.32-Q baseline · ABORT")
    sys.exit(1)
print(f"  ✓ baseline = V022.32-Q\n")


# ─── U1 ANCHOR DETECTION (indentation-aware) ───────────────────────────────
print("▸ U1 anchor detection (indentation-aware)...")

u1_first_line_rx = re.compile(
    r'^([ \t]*)// V022\.32-Q · PATCH N3 \+ Q1 \+ Q3 · prime_pro cascade · BEFORE legend_pro check\.$',
    re.MULTILINE
)
u1_match = u1_first_line_rx.search(content)
if not u1_match:
    print("✗ U1 first line not found · ABORT")
    sys.exit(1)

u1_indent = u1_match.group(1)
print(f"  U1 indent: {len(u1_indent)} char(s) [{repr(u1_indent)}]")

# Build u1_old with detected indent (4 lines)
u1_old = (
    f"{u1_indent}// V022.32-Q · PATCH N3 + Q1 + Q3 · prime_pro cascade · BEFORE legend_pro check.\n"
    f"{u1_indent}// Pro-prefix REQUIRED in regex · Caitlin Clark's Wooden Award (college MVP) will NOT match.\n"
    f"{u1_indent}// Active multi-MVP/champion overrides projected-HOF text · Steph Curry routes to prime_pro\n"
    f"{u1_indent}// (cap 9.3) instead of legend_pro (cap 9.7) because he's ACTIVE."
)

u1_hits = content.count(u1_old)
print(f"  U1 4-line block: {u1_hits} hit(s)", end='')
if u1_hits != 1:
    print(f"\n✗ U1 4-line block found {u1_hits} times (must be 1) · ABORT")
    sys.exit(1)
print(" ✓\n")


# ─── U2 ANCHOR DETECTION (indentation-aware) ───────────────────────────────
print("▸ U2 anchor detection (indentation-aware)...")

u2_rx = re.compile(
    r'^([ \t]*)const _v22_31_capped = Math\.min\(_v22_31_raw, _v22_31_cap\);$',
    re.MULTILINE
)
u2_matches = list(u2_rx.finditer(content))
print(f"  U2 line matches: {len(u2_matches)}")
if len(u2_matches) != 1:
    print(f"✗ U2 anchor must match exactly once · found {len(u2_matches)} · ABORT")
    for i, m in enumerate(u2_matches):
        line_no = content[:m.start()].count('\n') + 1
        print(f"    hit {i+1} at line {line_no}: indent='{m.group(1)}' content='{m.group(0)[:80]}'")
    sys.exit(1)

u2_indent = u2_matches[0].group(1)
u2_old = u2_matches[0].group(0)
u2_line_no = content[:u2_matches[0].start()].count('\n') + 1
print(f"  U2 line: {u2_line_no} · indent: {len(u2_indent)} char(s) [{repr(u2_indent)}]")
print(" ✓\n")


# ─── BANNER + CACHE ANCHOR ─────────────────────────────────────────────────
print("▸ Banner + cache version anchors...")
banner_old_rx = re.compile(r'// FIELDCHECK_WORKER_VERSION = V022\.32-Q · TENET 47 ATOMIC[^\n]*')
banner_match = banner_old_rx.search(content)
if not banner_match:
    print("✗ banner anchor not found · ABORT")
    sys.exit(1)
banner_old = banner_match.group(0)
print(f"  banner: '{banner_old[:80]}...'")

cache_old = "const cacheVersion = 'v022.32q'"
if content.count(cache_old) != 1:
    print(f"✗ cache anchor must be exactly 1, found {content.count(cache_old)} · ABORT")
    sys.exit(1)
print(f"  cache: '{cache_old}'\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup written: {BACKUP} ({BACKUP.stat().st_size:,} bytes)\n")


# ─── BUILD U1 PATCH (with detected indent) ─────────────────────────────────
u1_new = (
    f"{u1_indent}// V022.32-U · PATCH U1 · AMATEUR-FIRST STAGE GATE (May 26 2026)\n"
    f"{u1_indent}// HS keywords in corpus (5-star recruit, class of 2026, etc.) → athlete is HS regardless\n"
    f"{u1_indent}// of pro-text mentions in scout reports (those are projections/comparisons, not facts).\n"
    f"{u1_indent}// Closes Tate Ivanyo / Antwan Kimmons regression where HS athletes were getting prime_pro\n"
    f"{u1_indent}// because scout reports mention NBA comparisons. Only bypassed when isLegendValidated=true\n"
    f"{u1_indent}// (handles Coach K-style cases where HOF coach speaks at HS event).\n"
    f"{u1_indent}else if (isHSSig && !isLegendValidated) {{\n"
    f"{u1_indent}  stage = 'prep_amateur';\n"
    f"{u1_indent}  stageSignals.push('u1_hs_keyword_amateur_first');\n"
    f"{u1_indent}}}\n"
    f"{u1_indent}// V022.32-Q · PATCH N3 + Q1 + Q3 · prime_pro cascade · BEFORE legend_pro check.\n"
    f"{u1_indent}// Pro-prefix REQUIRED in regex · Caitlin Clark's Wooden Award (college MVP) will NOT match.\n"
    f"{u1_indent}// Active multi-MVP/champion overrides projected-HOF text · Steph Curry routes to prime_pro\n"
    f"{u1_indent}// (cap 9.3) instead of legend_pro (cap 9.7) because he's ACTIVE."
)

print("▸ Applying U1 (HS-keyword amateur-first stage gate)...")
content_after_u1 = content.replace(u1_old, u1_new, 1)
if content_after_u1 == content:
    print("✗ U1 str_replace no-op · ABORT")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ U1 applied · delta {len(content_after_u1) - len(content):+d} bytes\n")


# ─── BUILD U2 PATCH (with detected indent) ─────────────────────────────────
u2_new = (
    f"{u2_indent}// V022.32-U · PATCH U2 · STAGE-DRIVEN TIER + CAP CONSISTENCY (May 26 2026)\n"
    f"{u2_indent}// Stage is the more trustworthy signal post-V022.32. Force tier and cap to match stage\n"
    f"{u2_indent}// so residual 'tier=unknown defaults UP to early_pro cap 7.9' never punishes amateurs.\n"
    f"{u2_indent}// Closes Caleb Gaskins regression where stage=prep_amateur landed at composite 7.9.\n"
    f"{u2_indent}if (_v22_31_stage === 'prep_amateur') {{\n"
    f"{u2_indent}  _v22_31_tier = 'hs';\n"
    f"{u2_indent}  _v22_31_cap = 5.4;\n"
    f"{u2_indent}}} else if (_v22_31_stage === 'college_amateur') {{\n"
    f"{u2_indent}  if (!['d1','d2','d3','juco','naia'].includes(_v22_31_tier)) {{\n"
    f"{u2_indent}    _v22_31_tier = 'd1';\n"
    f"{u2_indent}    _v22_31_cap = 7.4;\n"
    f"{u2_indent}  }}\n"
    f"{u2_indent}}}\n"
    f"{u2_indent}const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);"
)

print("▸ Applying U2 (stage-driven tier+cap consistency override)...")
content_after_u2 = content_after_u1.replace(u2_old, u2_new, 1)
if content_after_u2 == content_after_u1:
    print("✗ U2 str_replace no-op · ABORT + restore")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ U2 applied · delta {len(content_after_u2) - len(content_after_u1):+d} bytes\n")


# ─── BANNER BUMP ────────────────────────────────────────────────────────────
banner_new = "// FIELDCHECK_WORKER_VERSION = V022.32-U · TENET 47 ATOMIC · 6 patches: O, N1a, N1b, N3+Q1+Q3, U1 (HS-amateur stage gate), U2 (stage-driven tier+cap)"

print("▸ Bumping version banner V022.32-Q → V022.32-U...")
content_after_banner = content_after_u2.replace(banner_old, banner_new, 1)
if content_after_banner == content_after_u2:
    print("✗ banner bump no-op · ABORT + restore")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ banner bumped\n")


# ─── CACHE BUMP ─────────────────────────────────────────────────────────────
cache_new = "const cacheVersion = 'v022.32u'"
print("▸ Bumping cache version v022.32q → v022.32u...")
content_final = content_after_banner.replace(cache_old, cache_new, 1)
if content_final == content_after_banner:
    print("✗ cache bump no-op · ABORT + restore")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ cache bumped\n")


# ─── WRITE ──────────────────────────────────────────────────────────────────
WORKER.write_text(content_final)
size_after = len(content_final)
sha_after = hashlib.sha256(content_final.encode()).hexdigest()[:12]
print(f"▸ worker.js written · {size_after:,} bytes (delta {size_after - size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY (Tenet 47.1) ──────────────────────────────────────────────
print("▸ Post-apply grep-verify (Tenet 47.1)...\n")

verifications = [
    ("U1 marker", "u1_hs_keyword_amateur_first"),
    ("U1 comment", "PATCH U1 · AMATEUR-FIRST STAGE GATE"),
    ("U1 gate logic", "isHSSig && !isLegendValidated"),
    ("U2 comment", "PATCH U2 · STAGE-DRIVEN TIER + CAP CONSISTENCY"),
    ("U2 prep_amateur cap", "_v22_31_cap = 5.4"),
    ("U2 d1 cap", "_v22_31_cap = 7.4"),
    ("U2 tier hs", "_v22_31_tier = 'hs'"),
    ("U2 tier d1", "_v22_31_tier = 'd1'"),
    ("banner V022.32-U", "V022.32-U · TENET 47 ATOMIC · 6 patches"),
    ("cache v022.32u", "'v022.32u'"),
]
anti = [
    ("old V022.32-Q banner with 4 patches", "V022.32-Q · TENET 47 ATOMIC · 4 patches"),
    ("old cache v022.32q", "const cacheVersion = 'v022.32q'"),
]

all_ok = True
for label, marker in verifications:
    ok = marker in content_final
    print(f"  {'✓' if ok else '✗'} {label}: '{marker[:60]}'")
    if not ok: all_ok = False
for label, marker in anti:
    ok = marker not in content_final
    print(f"  {'✓' if ok else '✗'} {label} removed")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring from backup")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print()


# ─── NODE SYNTAX CHECK ──────────────────────────────────────────────────────
print("▸ Node syntax check...")
result = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"✗ node --check FAILED · restoring from backup")
    print(f"  stderr: {result.stderr[:600]}")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ node --check passed\n")


# ─── DONE ───────────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" V022.32-U PATCH U APPLIED CLEAN · Tenet 47 grep-verify + node check")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-Q → V022.32-U · {size_before:,} → {size_after:,} bytes")
print(f" Cache:  v022.32q → v022.32u (forces fresh synthesis)")
print(f"")
print(f" Patches applied:")
print(f"   U1 · HS-keyword amateur-first stage gate (inserted before prime_pro cascade)")
print(f"   U2 · Stage-driven tier+cap consistency (inserted before _v22_31_capped Math.min)")
print(f"")
print(f" Backup: {BACKUP}")
print(f" Rollback: cp {BACKUP} worker.js")
print(f"")
print(f" NEXT:")
print(f"   ./fc-deploy-dev.sh")
print(f"   python3 v022_32_q_battery_v2.py")
