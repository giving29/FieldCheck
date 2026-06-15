#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
V5 ALGORITHM · PHASE 2 PATCH · V022.32-YX → V022.33-V5
═══════════════════════════════════════════════════════════════════════════
Sridhar V5 philosophy: 10 is the only ceiling. No caps, no buckets, no clamps.
Algorithm calculates real number from evidence vs theoretical-perfect-facet.
Phenoms emerge naturally when evidence justifies. UTR-inspired.

Patches:
  P1 · worker line 11477 · composite output reads _v22_31_raw (not _capped)
  P2 · synthesis prompt REFERENCE BANDS section · V4 HARD CAP language → V5 framing
  P3 · individual HARD CAP / CEILING / capped mentions → natural distribution language
  P4 · insert PHENOMS clause + EVIDENCE RIGOR clause
  P5 · line 4327 area · "capped while active" → "active career still open"
  P6 · version banner V022.32-YX → V022.33-V5
  P7 · cache key v022.32yx → v022.33v5

Cap variable (_v22_31_cap) STAYS in code — kept in composite_v022_31.cap field
for metadata transparency (audit: "what would V4 have capped this at?"). Just
doesn't affect output composite.

Stage detection (_v22_31_stage) STAYS for routing/UI but doesn't influence
the composite number.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, hashlib, subprocess
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-V022.33-V5.bak')

print("═══ V5 ALGORITHM PHASE 2 · V022.32-YX → V022.33-V5 ═══\n")

if not WORKER.exists():
    print("✗ worker.js not found · ABORT"); sys.exit(1)

content = WORKER.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ worker.js: {size_before:,} bytes · sha={sha_before}")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("\n▸ Anchor detection (all 7 anchors must be present)...")

anchors = {
    'A1_composite_assign': "result.composite = Math.round(_v22_31_capped * 10) / 10;",
    'A2_ref_bands_header': "REFERENCE BANDS — these are HARD CAPS, not suggestions:",
    'A3_active_capped': "9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — capped while active",
    'A4_rookie_ceiling': "7.5-7.9     NBA rookie / very-early-pro CEILING (Cooper Flagg, Caitlin Clark yr 2)",
    'A5_d1_hardcap': "7.0-7.4     D1 All-American HARD CAP — Cameron Boozer / AJ Dybantsa freshman ceiling",
    'A6_hs_hardcap': "5.0-5.4     HS #1 NATIONAL HARD CAP — Tyran Stokes, Saniyah Hall (no HS player exceeds 5.4)",
    'A7_within_tier': "WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):",
    'A8_steph_active_cap': "Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active cap)",
    'A9_v4_anchor_active': "- 9.0-9.3 = Active multi-MVP (Steph/Jokic — capped while active)",
    'A10_banner': "FIELDCHECK_WORKER_VERSION = V022.32-YX",
    'A11_cache_key': "v022.32yx",
}

missing = []
for key, anchor in anchors.items():
    if anchor not in content:
        missing.append(key)
        print(f"  ✗ {key}")
    else:
        print(f"  ✓ {key}")

if missing:
    print(f"\n✗ {len(missing)} anchors missing · ABORT")
    sys.exit(1)


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(WORKER, BACKUP)
print(f"\n▸ Backup: {BACKUP}")


# ─── P1: composite reads _v22_31_raw (no cap clamp on output) ─────────────
print("\n▸ P1: composite output reads _v22_31_raw (cap not applied to composite)...")
old_p1 = "result.composite = Math.round(_v22_31_capped * 10) / 10;"
new_p1 = "result.composite = Math.round(_v22_31_raw * 10) / 10;  // V5 (May 26 nt): 10 is only ceiling, cap retained in metadata only, not applied to composite"
content = content.replace(old_p1, new_p1, 1)
print(f"  ✓ replaced (delta {len(new_p1)-len(old_p1):+d})")


# ─── P2: REFERENCE BANDS header → V5 framing ───────────────────────────────
print("\n▸ P2: REFERENCE BANDS header → V5 SCORING PHILOSOPHY...")
old_p2 = "REFERENCE BANDS — these are HARD CAPS, not suggestions:"
new_p2 = "SCORING PHILOSOPHY · 10 IS THE ONLY CEILING. The distribution below is what evidence rigor NATURALLY PRODUCES — not enforcement, not clamps, not buckets. Every score is calculated against the theoretical perfect-facet (10 = unreachable perfection). Phenoms with elite evidence may exceed the reference for their category. Reference distribution:"
content = content.replace(old_p2, new_p2, 1)
print(f"  ✓ replaced (delta {len(new_p2)-len(old_p2):+d})")


# ─── P3a: 9.0-9.3 active multi-MVP framing ─────────────────────────────────
print("\n▸ P3a: 9.0-9.3 active framing · 'capped while active' → 'active career still open'...")
old_p3a = "9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — capped while active"
new_p3a = "9.0-9.3     Active multi-MVP + ring (Steph/Jokic/Giannis NOW) — naturally lands here, active career still has open questions"
content = content.replace(old_p3a, new_p3a, 1)
print(f"  ✓ replaced")


# ─── P3b: 7.5-7.9 rookie CEILING ──────────────────────────────────────────
print("\n▸ P3b: 7.5-7.9 rookie · CEILING → evidence range...")
old_p3b = "7.5-7.9     NBA rookie / very-early-pro CEILING (Cooper Flagg, Caitlin Clark yr 2)"
new_p3b = "7.5-7.9     NBA rookie / very-early-pro evidence range (Cooper Flagg, Caitlin Clark yr 2 — limited career body of work)"
content = content.replace(old_p3b, new_p3b, 1)
print(f"  ✓ replaced")


# ─── P3c: 7.0-7.4 D1 HARD CAP ─────────────────────────────────────────────
print("\n▸ P3c: 7.0-7.4 D1 · HARD CAP → evidence range...")
old_p3c = "7.0-7.4     D1 All-American HARD CAP — Cameron Boozer / AJ Dybantsa freshman ceiling"
new_p3c = "7.0-7.4     D1 All-American evidence range — Cameron Boozer / AJ Dybantsa freshman level (D1 evidence vs D1 competition)"
content = content.replace(old_p3c, new_p3c, 1)
print(f"  ✓ replaced")


# ─── P3d: 5.0-5.4 HS HARD CAP ─────────────────────────────────────────────
print("\n▸ P3d: 5.0-5.4 HS · HARD CAP → evidence range (HS-only justification)...")
old_p3d = "5.0-5.4     HS #1 NATIONAL HARD CAP — Tyran Stokes, Saniyah Hall (no HS player exceeds 5.4)"
new_p3d = "5.0-5.4     HS #1 NATIONAL evidence range — Tyran Stokes, Saniyah Hall (HS-only evidence naturally produces this; PHENOMS with pro-tier physical/production evidence may exceed — see PHENOMS section)"
content = content.replace(old_p3d, new_p3d, 1)
print(f"  ✓ replaced")


# ─── P3e: Steph active cap callout ────────────────────────────────────────
print("\n▸ P3e: Steph callout · 'active cap' → 'active career still open'...")
old_p3e = "Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active cap)"
new_p3e = "Steph Curry (active 2x MVP, 4x champ)      → composite 9.0-9.3 (active career still open)"
content = content.replace(old_p3e, new_p3e, 1)
print(f"  ✓ replaced")


# ─── P4: insert PHENOMS clause + EVIDENCE RIGOR clause before WITHIN-TIER ─
print("\n▸ P4: insert PHENOMS + EVIDENCE RIGOR sections before WITHIN-TIER...")
old_p4 = "WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):"
new_p4 = """PHENOMS (the V5 escape from the reference distribution):
A PHENOM is an athlete whose evidence at a young age ALREADY justifies higher scores than the reference distribution suggests for their category. Kobe at 17, LeBron at 17, KD at 18, Tiger Woods at 17 are the canonical cases — measurable physical traits at pro standards, production vs strong-older competition, multi-source corroboration of generational ability. When evidence is unambiguous and pro-tier, score HIGHER than the reference distribution for that category. Do NOT suppress the score to match the typical range. The reference distribution is what TYPICAL evidence produces; phenoms are by definition atypical evidence outliers. Lean conservative when evidence is ambiguous; lean bold when evidence is overwhelming.

EVIDENCE RIGOR (the only true limiter on every facet):
Every facet score 0-10 must be justified by SPECIFIC EVIDENCE in the athlete's actual record. Score 2-3 = "no evidence to justify higher" (default for unknown facets, not average 5). Score 5 = actual evidence of competence at the athlete's level. Score 7+ = elite production AND elite competition AND validated context. Score 8.5+ = multi-year sustained pro-level performance. Score 9+ = career-validated all-time-great evidence. Do NOT inflate scores based on potential, projection, hype, recruiting class, draft slot, or media narrative. Score WHAT THE EVIDENCE SHOWS NOW.

WITHIN-TIER DIFFERENTIATION (THE MOAT — read carefully):"""
content = content.replace(old_p4, new_p4, 1)
print(f"  ✓ inserted (delta +{len(new_p4)-len(old_p4)})")


# ─── P5: line 4327 area · active capped → active career still open ────────
print("\n▸ P5: secondary prompt block · 9.0-9.3 active framing...")
old_p5 = "- 9.0-9.3 = Active multi-MVP (Steph/Jokic — capped while active)"
new_p5 = "- 9.0-9.3 = Active multi-MVP (Steph/Jokic — active career still has open questions, naturally lands here)"
content = content.replace(old_p5, new_p5, 1)
print(f"  ✓ replaced")


# ─── P6: version banner bump ───────────────────────────────────────────────
print("\n▸ P6: version banner V022.32-YX → V022.33-V5...")
old_p6 = "FIELDCHECK_WORKER_VERSION = V022.32-YX · TENET 47 ATOMIC · 8 patches: O, N1a, N1b, N3+Q1+Q3, U1, U2, Y (stage=unknown fallback), X (decimal facet diff · THE MOAT)"
new_p6 = "FIELDCHECK_WORKER_VERSION = V022.33-V5 · TENET 46 V5 PHILOSOPHY · 10 is only ceiling · cap removed from composite output (kept in metadata only) · synthesis prompt rewritten with reference distribution + PHENOMS + EVIDENCE RIGOR clauses · stage detection kept for routing not capping"
content = content.replace(old_p6, new_p6, 1)
print(f"  ✓ banner bumped")


# ─── P7: cache key bump ────────────────────────────────────────────────────
print("\n▸ P7: cache key v022.32yx → v022.33v5...")
# Cache key may appear in multiple places — replace all
cache_count_before = content.count("v022.32yx")
content = content.replace("v022.32yx", "v022.33v5")
cache_count_after = content.count("v022.33v5")
print(f"  ✓ {cache_count_before} → {cache_count_after} cache references updated")


# ─── WRITE ─────────────────────────────────────────────────────────────────
WORKER.write_text(content)
size_after = len(content)
sha_after = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"\n▸ worker.js · {size_after:,} bytes (delta {size_after-size_before:+d}) · sha={sha_after}\n")


# ─── GREP-VERIFY (Tenet 47.1 + 47.6) ───────────────────────────────────────
print("▸ Grep-verify (Tenet 47.1 + 47.6)...")
checks = [
    # P1
    ("P1 composite uses _v22_31_raw not _capped", "result.composite = Math.round(_v22_31_raw * 10) / 10;" in content),
    ("P1 V5 comment present", "V5 (May 26 nt): 10 is only ceiling" in content),
    ("OLD capped composite line removed", "result.composite = Math.round(_v22_31_capped * 10) / 10;" not in content),
    # P2
    ("P2 V5 SCORING PHILOSOPHY header inserted", "SCORING PHILOSOPHY · 10 IS THE ONLY CEILING" in content),
    ("OLD REFERENCE BANDS HARD CAPS header removed", "REFERENCE BANDS — these are HARD CAPS, not suggestions:" not in content),
    # P3
    ("P3a active career still has open questions", "active career still has open questions, naturally lands here" in content),
    ("P3b NBA rookie evidence range", "NBA rookie / very-early-pro evidence range" in content),
    ("P3c D1 evidence range", "D1 All-American evidence range" in content),
    ("P3d HS evidence range with PHENOMS pointer", "HS #1 NATIONAL evidence range" in content),
    ("OLD HS HARD CAP removed", "5.0-5.4     HS #1 NATIONAL HARD CAP" not in content),
    ("OLD D1 HARD CAP removed", "D1 All-American HARD CAP" not in content),
    ("OLD rookie CEILING removed", "NBA rookie / very-early-pro CEILING" not in content),
    # P4
    ("P4 PHENOMS section inserted", "PHENOMS (the V5 escape from the reference distribution)" in content),
    ("P4 Kobe LeBron KD Tiger canonical cases", "Kobe at 17, LeBron at 17, KD at 18, Tiger Woods at 17" in content),
    ("P4 EVIDENCE RIGOR section inserted", "EVIDENCE RIGOR (the only true limiter on every facet)" in content),
    ("P4 Do NOT inflate on hype", "Do NOT inflate scores based on potential" in content),
    # P5
    ("P5 secondary active framing", "active career still has open questions, naturally lands here" in content),
    ("OLD 'capped while active' removed", "capped while active" not in content),
    # P6
    ("P6 V022.33-V5 banner present", "FIELDCHECK_WORKER_VERSION = V022.33-V5" in content),
    ("OLD V022.32-YX banner removed", "FIELDCHECK_WORKER_VERSION = V022.32-YX" not in content),
    # P7
    ("P7 cache v022.33v5 present", "v022.33v5" in content),
    ("OLD cache v022.32yx removed", "v022.32yx" not in content),
    # sanity
    ("WITHIN-TIER DIFFERENTIATION preserved", "WITHIN-TIER DIFFERENTIATION (THE MOAT" in content),
    ("8 facets array preserved", "['character', 'mindset', 'mental_strength', 'talent', 'physical', 'mental_iq', 'coachability', 'competitiveness']" in content),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring"); shutil.copy(BACKUP, WORKER); sys.exit(1)


# ─── NODE SYNTAX CHECK ─────────────────────────────────────────────────────
print("\n▸ Node syntax check...")
r = subprocess.run(['node', '--check', 'worker.js'], capture_output=True, text=True)
if r.returncode != 0:
    print(f"✗ syntax error · restoring\n{r.stderr}")
    shutil.copy(BACKUP, WORKER); sys.exit(1)
print("  ✓ passed")


# ─── DONE ──────────────────────────────────────────────────────────────────
print()
print("═══════════════════════════════════════════════════════════════════════")
print(" V5 ALGORITHM PHASE 2 APPLIED · V022.33-V5")
print("═══════════════════════════════════════════════════════════════════════")
print(f" worker.js · V022.32-YX → V022.33-V5 · {size_after:,} bytes (delta {size_after-size_before:+d})")
print(f"")
print(f" V5 changes:")
print(f"   ✓ Cap clamp REMOVED from composite output (line 11477)")
print(f"   ✓ Cap variable retained in metadata only (composite_v022_31.cap)")
print(f"   ✓ Synthesis prompt REFERENCE BANDS → reference distribution")
print(f"   ✓ All HARD CAP / CEILING / capped-while-active language replaced")
print(f"   ✓ PHENOMS clause inserted (Kobe/LeBron/KD/Tiger at 17 can exceed)")
print(f"   ✓ EVIDENCE RIGOR clause inserted (score what evidence shows now)")
print(f"   ✓ Cache invalidated · all 110 syntheses will re-run cold")
print(f"")
print(f" Expected battery V5 outcomes:")
print(f"   • Caitlin Clark · 9.05 → ~6.5-7.5 (rookie evidence only)")
print(f"   • Cooper Flagg · 9.3 → ~6.5-7.5 (rookie evidence only)")
print(f"   • Tim Duncan · 9.3 → unchanged (career-validated, naturally lands)")
print(f"   • Tyran Stokes · 5.4 → ~4.5-5.5 (HS evidence only)")
print(f"   • Phenom cases · should exceed reference if evidence justifies")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: ./fc-deploy-dev.sh, then python3 v022_32_q_battery_v2.py (cold cache, ~22min)")
print(f" If battery looks right, promote prod. If wrong, iterate prompt rigor (not add caps back).")
