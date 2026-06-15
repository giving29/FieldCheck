#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V5 v2.2 + v2.3 COMBINED · V022.35-V5.1 → V022.36-V5.2
═══════════════════════════════════════════════════════════════════════════
Architecture: prompt does evidence evaluation, code does bright-line rules.

PATCH A · v2.2 prompt rollback:
  Remove HARD NUMERIC ANCHORS section (caused Saniyah Hall 3.5→9.0,
  Cameron Williams 5.5→7.5 regressions via peer-association bias).
  Keep ANTI-CONTAMINATION (Caleb Gaskins/Kate Harpring/Carlos Medlock wins)
  Keep CRITICAL 9.7+ RESERVED (Duncan benefit)

PATCH B · v2.3 deterministic post-synthesis correction layer:
  6 bright-line rules with full audit:
    R1: Jr/Sr/II/III/IV suffix + amateur → evidence ceiling (5.5 HS, 7.4 D1)
    R2: HS non-phenom → ceiling 5.4
    R3: D1 amateur non-phenom → ceiling 7.4
    R4: Active player career stage → ceiling 9.3 (Jordan singular at 9.9 retired)
    R5: Rookie → ceiling 7.5
    R6: HS-pro classification mismatch → flag (identity-review-needed)
  composite output reads v5_corrected, raw preserved in metadata.

PATCH C · banner V022.36-V5.2 + cache v022.36v52

Run from ~/Desktop/fieldcheck-proxy/ on top of V022.35-V5.1 state
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, subprocess, hashlib
from pathlib import Path

print("═══ V5 v2.2 + v2.3 · V022.35-V5.1 → V022.36-V5.2 ═══\n")

WORKER = Path('worker.js')
if not WORKER.exists():
    print("FAIL: worker.js not found")
    sys.exit(1)

c = WORKER.read_text()
orig_bytes = WORKER.stat().st_size
orig_sha = hashlib.sha256(c.encode()).hexdigest()[:12]
print(f"▸ worker.js · {orig_bytes:,} bytes · sha={orig_sha}\n")


# ══════════════════════════════════════════════════════════════════════════
# PRE-FLIGHT · verify V022.35-V5.1 state
# ══════════════════════════════════════════════════════════════════════════
print("▸ Pre-flight · verify V022.35-V5.1 state\n")

required = [
    ('banner V022.35-V5.1', 'FIELDCHECK_WORKER_VERSION = V022.35-V5.1'),
    ('cache v022.35v51', "cacheVersion = 'v022.35v51'"),
    ('HARD NUMERIC ANCHORS to remove', 'HARD NUMERIC ANCHORS (STRICT'),
    ('ANTI-CONTAMINATION present (keep)', 'ANTI-CONTAMINATION (CRITICAL'),
    ('CRITICAL 9.7+ RESERVED present (keep)', 'CRITICAL 9.7+ IS RESERVED'),
    ('composite reads raw', 'result.composite = Math.round(_v22_31_raw * 10) / 10'),
    ('capped_legacy in metadata', 'capped_legacy: Math.round(_v22_31_capped * 10) / 10'),
    ('MOAT anchor', 'WITHIN-TIER DIFFERENTIATION (THE MOAT'),
]
missing = []
for label, anchor in required:
    if anchor in c:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label}  ← NOT FOUND")
        missing.append(label)
if missing:
    print(f"\n✗ PRE-FLIGHT FAILED · {len(missing)} anchor(s) missing")
    sys.exit(1)
print(f"\n✓ V022.35-V5.1 state verified · proceeding\n")


# ══════════════════════════════════════════════════════════════════════════
# BACKUP
# ══════════════════════════════════════════════════════════════════════════
backup = WORKER.with_suffix('.js.pre-V022.36-V5.2.bak')
shutil.copy(WORKER, backup)
print(f"▸ Backup: {backup}\n")


# ══════════════════════════════════════════════════════════════════════════
# PATCH A · REMOVE HARD NUMERIC ANCHORS section
# ══════════════════════════════════════════════════════════════════════════
print("▸ PATCH A · remove HARD NUMERIC ANCHORS section (caused regressions)")

p_a_old = '''HARD NUMERIC ANCHORS (STRICT · these athletes must produce scores in these ranges):

  Michael Jordan retired             = 9.9 (singular reference · no one else)
  Tim Duncan retired                 = 9.3 (career complete · NOT 9.9 · he is NOT Jordan)
  Steph Curry active                 = 9.0-9.3 (active career still open)
  LeBron James active                = 9.4-9.7 (extended career body)
  Cooper Flagg NBA rookie            = 6.5-7.5 (rookie · limited sample · NOT 9+)
  Caitlin Clark WNBA-yr2             = 7.0-7.8 (pro evidence · 1+ year)
  Cameron Boozer Duke freshman       = 6.0-7.0 (D1 freshman · single year)
  AJ Dybantsa BYU freshman           = 6.0-7.0 (D1 freshman · single year)
  Tyran Stokes HS #1                 = 5.0-5.4 (HS-only evidence · top of pool)
  Saniyah Hall HS #1 girls           = 5.0-5.4 (HS-only evidence)
  Kenyon Goodin D1 mid-major         = 6.0-6.7 (multi-year D1 starter)
  Median HS varsity                  = 3.0-4.0

CRITICAL 9.7+ IS RESERVED:'''

p_a_new = '''CRITICAL 9.7+ IS RESERVED:'''

if p_a_old not in c:
    print("  ✗ HARD NUMERIC ANCHORS block not found exactly")
    sys.exit(1)

c = c.replace(p_a_old, p_a_new, 1)
print(f"  ✓ HARD NUMERIC ANCHORS section removed (~700 chars)")


# ══════════════════════════════════════════════════════════════════════════
# PATCH B · INSERT deterministic post-synthesis correction layer
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ PATCH B · insert v2.3 post-synthesis correction layer at composite output")

p_b_old = '''        const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);
      // V5 v2: composite reads RAW directly. cap retained in metadata only for transparency.
      result.composite = Math.round(_v22_31_raw * 10) / 10;
      result.composite_v022_31 = {
        raw: Math.round(_v22_31_raw * 100) / 100,
        capped_legacy: Math.round(_v22_31_capped * 10) / 10,
        cap: _v22_31_cap,
        tier: _v22_31_tier,
        stage: _v22_31_stage,
        cap_applied: _v22_31_raw > _v22_31_cap,
        source: _v22_31_source
      };'''

p_b_new = r'''        const _v22_31_capped = Math.min(_v22_31_raw, _v22_31_cap);

      // V5 v2.3 · deterministic post-synthesis bright-line corrections
      // Different from V4 caps: conditional based on identity+stage+tier signals,
      // auditable (v5_corrections array), raw preserved in metadata, derived from design doc.
      const _v5_apply_corrections = (rawComposite, identity, careerStage, tier, phenomFlag) => {
        let corrected = rawComposite;
        const corrections = [];
        const name = (identity && (identity.full_name || identity.name || identity.displayName)) || '';
        const suffixRegex = /\b(Jr\.?|Sr\.?|II|III|IV|2nd|3rd)\b\s*$/i;
        const hasSuffix = suffixRegex.test(name.trim());
        const activeStages = ['rookie', 'early_pro', 'prime_pro', 'late_pro'];

        // R1 · Jr/Sr/II/III/IV suffix + amateur tier → likely parent career contamination
        if (hasSuffix && (careerStage === 'prep_amateur' || careerStage === 'college_amateur')) {
          const ceiling = careerStage === 'prep_amateur' ? 5.5 : 7.4;
          if (corrected > ceiling) {
            corrections.push({ rule: 'suffix-amateur-ceiling', from: corrected, to: ceiling, reason: 'Jr/Sr/II/III suffix at amateur tier - parent career data likely contaminated synthesis' });
            corrected = ceiling;
          }
        }

        // R2 · HS evidence ceiling for non-phenoms
        if (tier === 'hs' && careerStage === 'prep_amateur' && !phenomFlag && corrected > 5.4) {
          corrections.push({ rule: 'hs-evidence-ceiling-non-phenom', from: corrected, to: 5.4, reason: 'HS-only evidence, no phenom criteria met (4 of 4 required)' });
          corrected = 5.4;
        }

        // R3 · D1 amateur ceiling for non-phenoms
        if (tier === 'd1' && careerStage === 'college_amateur' && !phenomFlag && corrected > 7.4) {
          corrections.push({ rule: 'd1-college-amateur-ceiling', from: corrected, to: 7.4, reason: 'D1 amateur evidence ceiling' });
          corrected = 7.4;
        }

        // R4 · Active player ceiling - Jordan retired singular at 9.9; active careers cap 9.3
        if (activeStages.includes(careerStage) && corrected > 9.6) {
          corrections.push({ rule: 'active-player-ceiling', from: corrected, to: 9.3, reason: '9.7+ reserved for Jordan retired singular; active multi-MVP cap 9.3' });
          corrected = 9.3;
        }

        // R5 · Rookie evidence ceiling (1st-2nd pro year)
        if (careerStage === 'rookie' && corrected > 7.5) {
          corrections.push({ rule: 'rookie-evidence-ceiling', from: corrected, to: 7.5, reason: 'Rookie sample - draft slot/recruiting rank does not elevate' });
          corrected = 7.5;
        }

        // R6 · HS tier + pro stage = identity classification mismatch (flag only, no correction)
        if (tier === 'hs' && activeStages.includes(careerStage)) {
          corrections.push({ rule: 'identity-classification-mismatch', flag: 'review-needed', reason: 'HS tier classified with pro stage - likely name collision (Antwan Kimmons, Tate Ivanyo pattern)' });
        }

        return { composite: corrected, raw_synthesis: rawComposite, corrections };
      };

      const _v5_identity = ((_v22_31_enc || {}).facts || {}).identity || {};
      const _v5_phenom_flag = !!((_v22_31_enc || {}).synthesis && _v22_31_enc.synthesis.phenom_qualified);
      const _v5_result = _v5_apply_corrections(_v22_31_raw, _v5_identity, _v22_31_stage, _v22_31_tier, _v5_phenom_flag);

      // V5 v2.3: composite reads v5-corrected. raw + corrections retained in metadata for audit/transparency.
      result.composite = Math.round(_v5_result.composite * 10) / 10;
      result.composite_v022_31 = {
        raw: Math.round(_v22_31_raw * 100) / 100,
        capped_legacy: Math.round(_v22_31_capped * 10) / 10,
        v5_corrected: Math.round(_v5_result.composite * 100) / 100,
        v5_corrections: _v5_result.corrections,
        v5_corrections_applied: _v5_result.corrections.length > 0,
        cap: _v22_31_cap,
        tier: _v22_31_tier,
        stage: _v22_31_stage,
        cap_applied: _v22_31_raw > _v22_31_cap,
        source: _v22_31_source
      };'''

if p_b_old not in c:
    print("  ✗ V5 v2 composite assignment anchor not found")
    sys.exit(1)

c = c.replace(p_b_old, p_b_new, 1)
print(f"  ✓ v5_apply_corrections function inserted with 6 bright-line rules")
print(f"  ✓ composite output reads v5_corrected · raw + corrections in metadata")


# ══════════════════════════════════════════════════════════════════════════
# PATCH C · banner + cache bump
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ PATCH C · banner V022.35-V5.1 → V022.36-V5.2 · cache v022.36v52")

p_c_banner_old = '// FIELDCHECK_WORKER_VERSION = V022.35-V5.1 · V5 v2.1 REFINEMENT · 10 is only ceiling · evidence rigor only limiter · phenom criteria (4 reqs) · anti-inflation explicit (8 signals) · default-low principle · cross-sport anchors · ANTI-CONTAMINATION (Jr/Sr/family-lineage) · HARD NUMERIC ANCHORS (12 named athletes) · 9.7+ RESERVED imperative · cap kept in metadata only'
p_c_banner_new = '// FIELDCHECK_WORKER_VERSION = V022.36-V5.2 · V5 v2.2+v2.3 · PROMPT + DETERMINISTIC POST-PROCESSING · prompt does evidence eval · code does 6 bright-line rules (Jr/Sr suffix · HS non-phenom · D1 non-phenom · active 9.6 · rookie 7.5 · HS-pro mismatch flag) · HARD NUMERIC ANCHORS removed (peer-association bias) · ANTI-CONTAMINATION + 9.7+ RESERVED kept · audit trail in v5_corrections array'

if p_c_banner_old not in c:
    print("  ✗ V022.35-V5.1 banner not found")
    sys.exit(1)
c = c.replace(p_c_banner_old, p_c_banner_new, 1)
print("  ✓ banner V022.35-V5.1 → V022.36-V5.2")

p_c_cache_old = "cacheVersion = 'v022.35v51';"
p_c_cache_new = "cacheVersion = 'v022.36v52';"
cache_count = c.count(p_c_cache_old)
c = c.replace(p_c_cache_old, p_c_cache_new)
print(f"  ✓ cache v022.35v51 → v022.36v52 ({cache_count} occurrence)")


# ══════════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════════
WORKER.write_text(c)
new_bytes = WORKER.stat().st_size
new_sha = hashlib.sha256(c.encode()).hexdigest()[:12]
delta = new_bytes - orig_bytes
print(f"\n▸ worker.js · {new_bytes:,} bytes (delta {delta:+,}) · sha={new_sha}\n")


# ══════════════════════════════════════════════════════════════════════════
# VERIFY
# ══════════════════════════════════════════════════════════════════════════
print("▸ Post-patch verification\n")
checks = [
    ('PATCH A · HARD NUMERIC ANCHORS removed', 'HARD NUMERIC ANCHORS (STRICT' not in c),
    ('PATCH A · CRITICAL 9.7+ kept', 'CRITICAL 9.7+ IS RESERVED' in c),
    ('PATCH A · ANTI-CONTAMINATION kept', 'ANTI-CONTAMINATION (CRITICAL' in c),
    ('PATCH B · _v5_apply_corrections function', '_v5_apply_corrections' in c),
    ('PATCH B · R1 suffix-amateur-ceiling', 'suffix-amateur-ceiling' in c),
    ('PATCH B · R2 hs-evidence-ceiling', 'hs-evidence-ceiling-non-phenom' in c),
    ('PATCH B · R3 d1-amateur-ceiling', 'd1-college-amateur-ceiling' in c),
    ('PATCH B · R4 active-player-ceiling', 'active-player-ceiling' in c),
    ('PATCH B · R5 rookie-evidence-ceiling', 'rookie-evidence-ceiling' in c),
    ('PATCH B · R6 identity-mismatch flag', 'identity-classification-mismatch' in c),
    ('PATCH B · suffix regex Jr/Sr/II/III/IV', r'\b(Jr\.?|Sr\.?|II|III|IV|2nd|3rd)\b' in c),
    ('PATCH B · composite reads v5_corrected', 'result.composite = Math.round(_v5_result.composite * 10) / 10' in c),
    ('PATCH B · v5_corrected in metadata', 'v5_corrected:' in c),
    ('PATCH B · v5_corrections array', 'v5_corrections:' in c),
    ('PATCH B · v5_corrections_applied', 'v5_corrections_applied' in c),
    ('PATCH B · raw preserved', 'raw: Math.round(_v22_31_raw * 100) / 100' in c),
    ('PATCH B · capped_legacy preserved', 'capped_legacy: Math.round(_v22_31_capped * 10) / 10' in c),
    ('PATCH B · OLD V5 v2 composite line removed', 'result.composite = Math.round(_v22_31_raw * 10) / 10' not in c),
    ('PATCH C · banner V022.36-V5.2', 'V022.36-V5.2' in c),
    ('PATCH C · OLD V022.35-V5.1 banner removed', 'FIELDCHECK_WORKER_VERSION = V022.35-V5.1 ·' not in c),
    ('PATCH C · cache v022.36v52', "cacheVersion = 'v022.36v52'" in c),
    ('MOAT preserved', 'WITHIN-TIER DIFFERENTIATION (THE MOAT' in c),
    ('PHENOM CRITERIA still present', 'PHENOM CRITERIA (must pass ALL 4' in c),
    ('ANTI-INFLATION still present', 'ANTI-INFLATION (these signals DO NOT' in c),
    ('DEFAULT-LOW still present', 'DEFAULT-LOW PRINCIPLE:' in c),
    ('cap variable structure intact', 'let _v22_31_cap = 10.0;' in c),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok:
        all_ok = False
if not all_ok:
    print(f"\n✗ POST-PATCH VERIFICATION FAILED")
    print(f"  Restore: cp {backup} worker.js")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# NODE CHECK
# ══════════════════════════════════════════════════════════════════════════
print("\n▸ Node syntax check")
r = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"  ✗ SYNTAX FAIL:")
    print(r.stderr)
    print(f"  Restore: cp {backup} worker.js")
    sys.exit(1)
print("  ✓ syntax OK")


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" V5 v2.2 + v2.3 APPLIED · V022.36-V5.2")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" worker.js · V022.35-V5.1 → V022.36-V5.2 · {new_bytes:,} bytes ({delta:+,})")
print(f" sha · {orig_sha} → {new_sha}")
print(f"")
print(f" Architecture: prompt does evidence eval, code does bright-line rules.")
print(f"")
print(f" PATCH A · prompt v2.2:")
print(f"   ✗ REMOVED HARD NUMERIC ANCHORS section (peer-association bias culprit)")
print(f"   ✓ KEPT ANTI-CONTAMINATION (Caleb Gaskins/Harpring/Medlock win driver)")
print(f"   ✓ KEPT CRITICAL 9.7+ RESERVED (Duncan benefit)")
print(f"")
print(f" PATCH B · code v2.3 · 6 deterministic post-synthesis rules:")
print(f"   R1 · suffix Jr/Sr/II/III amateur → ceiling 5.5(HS) / 7.4(D1)")
print(f"   R2 · HS non-phenom → ceiling 5.4")
print(f"   R3 · D1 amateur non-phenom → ceiling 7.4")
print(f"   R4 · active player career stage → ceiling 9.3 (Jordan singular)")
print(f"   R5 · rookie → ceiling 7.5")
print(f"   R6 · HS tier + pro stage → flag (identity-review-needed)")
print(f"   All rules audited in v5_corrections[] array · raw preserved")
print(f"")
print(f" Backup: {backup}")
print(f"")
print(f" NEXT:")
print(f"   1. Update canonical for Tenet 39 guard (V022.36 reference)")
print(f"   2. ./fc-deploy-dev.sh")
print(f"   3. python3 v022_32_q_battery_v2.py  (cold cache · ~24min)")
print(f"")
print(f" Expected V5 v2.2+v2.3 deltas:")
print(f"   Saniyah Hall · 9.0 → ~4-5 (anchor list removed)")
print(f"   Cameron Williams · 7.5 → ~5.5 (anchor list removed)")
print(f"   Jordan Smith Jr · 9.8 → 5.5 (R1 suffix rule fires deterministically)")
print(f"   Deron Rippey Jr · 8.2 → 5.5 (R1 suffix)")
print(f"   Carlos Medlock Jr · 6.0 → 5.5 (R1 suffix)")
print(f"   Brandon Bass Jr · 6.6 → 5.5 (R1 suffix)")
print(f"   Obinna Ekezie Jr · 8.3 → 5.5 (R1 suffix)")
print(f"   Eric Booth Jr · 7.5 → 5.5 (R1 suffix)")
print(f"   Chris Henry Jr · 7.5 → 5.5 (R1 suffix)")
print(f"   Terrence Hill Jr · 9.0 → 7.4 (R1 D1 ceiling)")
print(f"   Cooper Flagg · 9.7 → 9.3 (R4 active ceiling, if classified pro)")
print(f"   Caitlin Clark · 8.2 → 5.4 if still tier=hs (R2 + R6 flag)")
print(f"   Cameron Boozer · 9.1 → 7.4 (R3 D1 amateur)")
print(f"   AJ Dybantsa · 9.3 → 7.4 (R3 D1 amateur)")
print(f"   Antwan Kimmons / Donovan Dent / Tate Ivanyo → R6 flag for review")
print(f"")
print(f" composite_v022_31 metadata now includes:")
print(f"   raw · capped_legacy · v5_corrected · v5_corrections[] · v5_corrections_applied")
print(f"   Every correction has rule + from + to + reason for full audit.")
