#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V022.32-U · PATCH U APPLY · stage-tier consistency + HS-amateur-first gate
═══════════════════════════════════════════════════════════════════════════
Patches:
  U1 · HS-keyword amateur-first stage gate
       Inserts BEFORE prime_pro cascade at line ~11023:
         else if (isHSSig && !isLegendValidated) { stage = 'prep_amateur'; }
       Closes Tate Ivanyo / Antwan Kimmons regression where HS athletes get
       prime_pro because scout text mentions NBA comparisons.

  U2 · Stage-driven tier+cap consistency override
       Inserts BEFORE line 11399 const _v22_31_capped = Math.min(...):
         if (stage === 'prep_amateur') { tier='hs'; cap=5.4 }
         else if (stage === 'college_amateur' && unresolved tier) { tier='d1'; cap=7.4 }
       Closes "tier=unknown defaults UP to early_pro cap 7.9" regression
       (Caleb Gaskins composite=7.9 with stage=prep_amateur).

Doctrine compliance:
  Tenet 47.1 · grep-verify every patch · post-apply markers confirmed
  Tenet 47.2 · atomic version bumps · worker banner + cache version together
  Tenet 47.3 · fix only what's asked · NO scope expansion to U3 / V / etc

Atomicity:
  · Backup worker.js → worker.js.pre-V022.32-U-RECOVERY.bak BEFORE any change
  · If post-apply grep-verify fails → restore from backup, abort
  · If anchor strings don't match → abort BEFORE writing

Run:
  cd ~/Desktop/fieldcheck-proxy
  cp ~/Downloads/apply_patch_U.py .
  python3 apply_patch_U.py
═══════════════════════════════════════════════════════════════════════════
"""
import sys, re, shutil, hashlib
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.32-U-RECOVERY.bak')

# ─── PRE-FLIGHT ─────────────────────────────────────────────────────────────
print("═══ V022.32-U PATCH U · APPLY ═══\n")

if not WORKER.exists():
    print(f"✗ worker.js not found at {WORKER.absolute()}")
    sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")

# Check baseline version
if "V022.32-Q" not in content:
    print(f"✗ Worker is not on V022.32-Q baseline · ABORT")
    print(f"  expected version banner 'V022.32-Q' not found")
    sys.exit(1)
print(f"  ✓ baseline = V022.32-Q\n")

# ─── ANCHOR DISCOVERY ──────────────────────────────────────────────────────
print("▸ Anchor discovery...")

# U1 anchor: the prime_pro cascade comment block. Must appear EXACTLY once.
u1_old = """      // V022.32-Q · PATCH N3 + Q1 + Q3 · prime_pro cascade · BEFORE legend_pro check.
      // Pro-prefix REQUIRED in regex · Caitlin Clark's Wooden Award (college MVP) will NOT match.
      // Active multi-MVP/champion overrides projected-HOF text · Steph Curry routes to prime_pro
      // (cap 9.3) instead of legend_pro (cap 9.7) because he's ACTIVE."""

u1_hits = content.count(u1_old)
print(f"  U1 anchor (prime_pro cascade comment): {u1_hits} hit(s)", end='')
if u1_hits != 1:
    print(f"\n✗ U1 anchor must appear exactly once, found {u1_hits} · ABORT")
    sys.exit(1)
print(" ✓")

# U2 anchor: the _v22_31_capped Math.min line. Must appear EXACTLY once.
u2_old = """          const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);"""

u2_hits = content.count(u2_old)
print(f"  U2 anchor (_v22_31_capped Math.min): {u2_hits} hit(s)", end='')
if u2_hits != 1:
    print(f"\n✗ U2 anchor must appear exactly once, found {u2_hits} · ABORT")
    print("  Possible reasons: indentation differs, line changed since diagnostic, file modified")
    sys.exit(1)
print(" ✓")

# Banner anchor
banner_old = "// FIELDCHECK_WORKER_VERSION = V022.32-Q · TENET 47 ATOMIC"
banner_hits = content.count(banner_old)
print(f"  banner anchor: {banner_hits} hit(s)", end='')
if banner_hits != 1:
    print(f"\n✗ banner anchor must appear exactly once, found {banner_hits} · ABORT")
    sys.exit(1)
print(" ✓")

# Cache version anchor
cache_old = "const cacheVersion = 'v022.32q'"
cache_hits = content.count(cache_old)
print(f"  cache version anchor: {cache_hits} hit(s)", end='')
if cache_hits != 1:
    print(f"\n✗ cache version anchor must appear exactly once, found {cache_hits} · ABORT")
    sys.exit(1)
print(" ✓")

print("\n▸ All 4 anchors found exactly once · ready to apply\n")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"▸ Backup written: {BACKUP} ({BACKUP.stat().st_size:,} bytes)\n")


# ─── APPLY U1 ──────────────────────────────────────────────────────────────
u1_new = """      // V022.32-U · PATCH U1 · AMATEUR-FIRST STAGE GATE (May 26 2026)
      // HS keywords in corpus (5-star recruit, class of 2026, etc.) → athlete is HS regardless
      // of pro-text mentions in scout reports (those are projections/comparisons, not facts).
      // Closes Tate Ivanyo / Antwan Kimmons regression where HS athletes were getting prime_pro
      // because scout reports mention NBA comparisons. Only bypassed when isLegendValidated=true
      // (handles Coach K-style cases where HOF coach speaks at HS event).
      else if (isHSSig && !isLegendValidated) {
        stage = 'prep_amateur';
        stageSignals.push('u1_hs_keyword_amateur_first');
      }
      // V022.32-Q · PATCH N3 + Q1 + Q3 · prime_pro cascade · BEFORE legend_pro check.
      // Pro-prefix REQUIRED in regex · Caitlin Clark's Wooden Award (college MVP) will NOT match.
      // Active multi-MVP/champion overrides projected-HOF text · Steph Curry routes to prime_pro
      // (cap 9.3) instead of legend_pro (cap 9.7) because he's ACTIVE."""

print("▸ Applying U1 (HS-keyword amateur-first stage gate)...")
content_after_u1 = content.replace(u1_old, u1_new)
if content_after_u1 == content:
    print("✗ U1 str_replace produced no change · ABORT")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ U1 patched · delta {len(content_after_u1) - len(content):+d} bytes\n")


# ─── APPLY U2 ──────────────────────────────────────────────────────────────
u2_new = """          // V022.32-U · PATCH U2 · STAGE-DRIVEN TIER + CAP CONSISTENCY (May 26 2026)
          // Stage is the more trustworthy signal post-V022.32. Force tier and cap to match stage
          // so residual "tier=unknown defaults UP to early_pro cap 7.9" never punishes amateurs.
          // Closes Caleb Gaskins regression where stage=prep_amateur landed at composite 7.9.
          if (_v22_31_stage === 'prep_amateur') {
            _v22_31_tier = 'hs';
            _v22_31_cap = 5.4;
          } else if (_v22_31_stage === 'college_amateur') {
            if (!['d1','d2','d3','juco','naia'].includes(_v22_31_tier)) {
              _v22_31_tier = 'd1';
              _v22_31_cap = 7.4;
            }
          }
          const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);"""

print("▸ Applying U2 (stage-driven tier+cap consistency override)...")
content_after_u2 = content_after_u1.replace(u2_old, u2_new)
if content_after_u2 == content_after_u1:
    print("✗ U2 str_replace produced no change · ABORT + restore")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ U2 patched · delta {len(content_after_u2) - len(content_after_u1):+d} bytes\n")


# ─── BUMP VERSION BANNER (atomic with patches) ─────────────────────────────
banner_new = "// FIELDCHECK_WORKER_VERSION = V022.32-U · TENET 47 ATOMIC · 6 patches: O, N1a, N1b, N3+Q1+Q3, U1 (HS-amateur stage gate), U2 (stage-driven tier+cap) · TENET 47 ATOMIC"

print("▸ Bumping version banner V022.32-Q → V022.32-U...")
content_after_banner = content_after_u2.replace(banner_old, banner_new)
if content_after_banner == content_after_u2:
    print("✗ banner bump produced no change · ABORT + restore")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ banner bumped\n")


# ─── BUMP CACHE VERSION (atomic with patches) ──────────────────────────────
cache_new = "const cacheVersion = 'v022.32u'"

print("▸ Bumping cache version v022.32q → v022.32u...")
content_after_cache = content_after_banner.replace(cache_old, cache_new)
if content_after_cache == content_after_banner:
    print("✗ cache bump produced no change · ABORT + restore")
    shutil.copy(BACKUP, WORKER)
    sys.exit(1)
print(f"  ✓ cache version bumped\n")


# ─── WRITE WORKER ──────────────────────────────────────────────────────────
final = content_after_cache
WORKER.write_text(final)
size_after = len(final)
sha_after = hashlib.sha256(final.encode()).hexdigest()[:12]
print(f"▸ worker.js written · {size_after:,} bytes (delta {size_after - size_before:+d}) · sha={sha_after}\n")


# ─── POST-APPLY GREP-VERIFY (Tenet 47.1) ──────────────────────────────────
print("▸ Post-apply grep-verify (Tenet 47.1)...\n")

verifications = [
    ("U1 marker", "u1_hs_keyword_amateur_first"),
    ("U1 comment", "PATCH U1 · AMATEUR-FIRST STAGE GATE"),
    ("U2 comment", "PATCH U2 · STAGE-DRIVEN TIER + CAP CONSISTENCY"),
    ("U2 prep_amateur cap", "_v22_31_cap = 5.4"),
    ("U2 d1 cap", "_v22_31_cap = 7.4"),
    ("U2 tier hs", "_v22_31_tier = 'hs'"),
    ("U2 tier d1", "_v22_31_tier = 'd1'"),
    ("banner V022.32-U", "V022.32-U · TENET 47 ATOMIC · 6 patches"),
    ("cache v022.32u", "'v022.32u'"),
]

all_ok = True
for label, marker in verifications:
    if marker in final:
        print(f"  ✓ {label}: marker '{marker}' present")
    else:
        print(f"  ✗ {label}: marker '{marker}' MISSING")
        all_ok = False

# Anti-verifications (these should be GONE)
anti_verifications = [
    ("old V022.32-Q banner", "FIELDCHECK_WORKER_VERSION = V022.32-Q · TENET 47 ATOMIC · 4 patches"),
    ("old cache v022.32q", "const cacheVersion = 'v022.32q'"),
]
for label, marker in anti_verifications:
    if marker not in final:
        print(f"  ✓ {label}: marker '{marker[:50]}...' correctly removed")
    else:
        print(f"  ✗ {label}: stale marker '{marker[:50]}...' STILL PRESENT")
        all_ok = False

print()
if not all_ok:
    print("✗ GREP-VERIFY FAILED · restoring from backup")
    shutil.copy(BACKUP, WORKER)
    print(f"  worker.js restored from {BACKUP}")
    sys.exit(1)


# ─── SYNTAX CHECK ──────────────────────────────────────────────────────────
print("▸ Node syntax check...")
import subprocess
result = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"✗ Node syntax check FAILED · restoring from backup")
    print(f"  stderr: {result.stderr[:500]}")
    shutil.copy(BACKUP, WORKER)
    print(f"  worker.js restored from {BACKUP}")
    sys.exit(1)
print(f"  ✓ node --check passed\n")


# ─── DONE ──────────────────────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════════════")
print(" V022.32-U PATCH U APPLIED CLEAN · Tenet 47 grep-verify passed")
print("═══════════════════════════════════════════════════════════════════════")
print(f" Worker: V022.32-Q → V022.32-U · {size_before:,} → {size_after:,} bytes")
print(f" Cache:  v022.32q → v022.32u (forces fresh synthesis on read)")
print(f" Patches applied:")
print(f"   U1 · HS-keyword amateur-first stage gate")
print(f"        Closes Tate Ivanyo / Antwan Kimmons regression")
print(f"   U2 · Stage-driven tier+cap consistency override")
print(f"        Closes Caleb Gaskins comp=7.9 with stage=prep_amateur")
print(f"")
print(f" Backup: {BACKUP} ({BACKUP.stat().st_size:,} bytes)")
print(f" Rollback: cp {BACKUP} worker.js")
print(f"")
print(f" NEXT: deploy to dev → re-run battery → expect HS compliance ≥ 80%")
print(f"   ./fc-deploy-dev.sh   (or whatever your dev deploy is)")
print(f"   python3 v022_32_q_battery_v2.py")
print()
