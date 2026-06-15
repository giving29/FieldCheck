#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
MARQUEE RECURATION V5.2 · FIX v3
═══════════════════════════════════════════════════════════════════════
Fixes the alumnus bug in v2 (which fixed the prep-to-pro bug in v1).

V2 BUG: 'alumnus'/'alumna' in school was treated as a RETIRED signal. But
"LSU (alumnus)" just means the athlete went to LSU — Joe Burrow is an LSU
alumnus AND an active NFL pro. So Burrow/Lawrence/Tatum got flagged
retired_pro_unchanged and skipped the R4 9.3 cap (stayed at 9.5-9.6 ICON).

V3 FIX: drop 'alumnus' as a retired signal entirely. Distinguish by
class_year FORMAT (the actual data convention):
  - "Pro (retired YYYY)"  → RETIRED   (Kobe)        → unchanged
  - "Pro / achievement"   → LEGACY    (Misty, Foluke) → unchanged
  - "Pro (Team Name)"     → ACTIVE    (Burrow, Tatum)  → R4 cap 9.3

Check order (class_year first — most reliable career-stage signal):
  1. RETIRED      — 'retired' in class_year/school
  2. LEGACY       — 'pro /' slash format in class_year (career summary)
  3. ACTIVE PRO   — 'pro (' paren format in class_year
  4. ACTIVE PRO   — school signals (academies, farm teams)
  5. HS AMATEUR   — school HS signals
  6. COLLEGE AMATEUR — class_year freshman/soph/jr/sr or university school
  7. UNCLASSIFIED — unchanged

BACKLOG (NOT this sprint): active-pro sub-cap calibration. R4 9.3 is a
CEILING — it pulls 9.6→9.3 but doesn't differentiate Mahomes-tier (9.x)
from Burrow/Lawrence (should be ~8.x). Needs a per-athlete active-pro pass.

This script:
  1. Detects v1 OR v2 marker in worker.js
  2. Auto-restores from worker.js.pre-marquee-recuration-v5.bak (clean original)
  3. Applies v3 logic
  4. Stamps NEW marker: V5.2_MARQUEE_RECURATION_V3_APPLIED
  5. Verifies: Burrow/Lawrence/Tatum → 9.3 ELITE+ (active),
     Misty/Foluke → unchanged (legacy), Kobe → unchanged (retired),
     LeBron → 9.3, Boozer → 7.4, Flagg → 9.3
  6. Auto-rollback on failure
═══════════════════════════════════════════════════════════════════════
"""
import sys, shutil, re, json
from pathlib import Path
from datetime import date

print("═══ MARQUEE RECURATION V5.2 · FIX v3 ═══\n")

WORKER = Path('worker.js')
BACKUP_CLEAN = Path('worker.js.pre-marquee-recuration-v5.bak')   # clean original (pre-v1)
BACKUP_V3 = Path('worker.js.pre-marquee-recuration-v5-v3.bak')
REPORT = Path('marquee_recuration_report.json')
V1_MARKER = '// V5.2_MARQUEE_RECURATION_APPLIED'
V2_MARKER = '// V5.2_MARQUEE_RECURATION_V2_APPLIED'
NEW_MARKER = '// V5.2_MARQUEE_RECURATION_V3_APPLIED'


# ════════════════ STEP 1 · pre-flight ════════════════
if not WORKER.exists():
    print(f"✗ FAIL: {WORKER} not in cwd")
    sys.exit(1)

content = WORKER.read_text()
print(f"▸ Current worker.js: {WORKER.stat().st_size:,} bytes")

# Auto-rollback any prior recuration from the CLEAN original
if V1_MARKER in content or V2_MARKER in content:
    if not BACKUP_CLEAN.exists():
        print(f"✗ FAIL: prior marker present but {BACKUP_CLEAN} missing — manual recovery needed")
        sys.exit(1)
    which = 'v2' if V2_MARKER in content else 'v1'
    print(f"▸ Detected {which} marker · auto-rolling back from {BACKUP_CLEAN.name} (clean original)")
    shutil.copy(BACKUP_CLEAN, WORKER)
    content = WORKER.read_text()
    print(f"  ✓ Restored to {WORKER.stat().st_size:,} bytes")

if NEW_MARKER in content:
    print(f"✓ v3 already applied")
    sys.exit(0)


# ════════════════ STEP 2 · backup ════════════════
shutil.copy(WORKER, BACKUP_V3)
print(f"▸ v3 backup: {BACKUP_V3.name}\n")
orig_size = WORKER.stat().st_size

def rollback(reason):
    print(f"\n✗ ROLLING BACK · {reason}")
    shutil.copy(BACKUP_V3, WORKER)
    print(f"  ✓ Restored {WORKER.name}")
    sys.exit(1)


# ════════════════ STEP 3 · FIXED V5.2 cap derivation ════════════════
def derive_v5_cap(class_year, school):
    """class_year format is the reliable signal. Returns (cap_or_None, classification)."""
    school_l = (school or '').lower()
    class_l = (class_year or '').lower()

    # 1. RETIRED — explicit "retired" keyword (Kobe "Pro (retired 2016)")
    #    NOTE: 'alumnus'/'alumna' is NOT a retired signal — it just means
    #    the athlete attended that college. Active pros are college alumni too.
    if 'retired' in class_l or 'retired' in school_l:
        return None, 'retired_pro_unchanged'

    # 2. LEGACY — "pro /" slash format = career-achievement summary, used for
    #    retired legends (Misty May-Treanor "Pro / 3× Olympic Gold",
    #    Foluke "Pro / USA Olympic gold medalist"). Active rostered pros use
    #    the "Pro (Team)" paren format instead.
    if 'pro /' in class_l or 'pro/' in class_l:
        return None, 'legacy_pro_unchanged'

    # 3. ACTIVE PRO — "pro (" paren format = current team
    #    (Burrow "Pro (Cincinnati Bengals)", Tatum "Pro (Boston Celtics)",
    #     Lawrence, Richardson, Lexi Sun "Pro (Overseas + USA pool)")
    if ('pro (' in class_l or 'pro(' in class_l or class_l == 'pro'
            or class_l == 'n/a' or 'rookie' in class_l or 'professional' in class_l):
        return 9.3, 'pro_active_R4'

    # 4. ACTIVE PRO — school signals (academies, farm teams, pro clubs)
    pro_school_signals = [
        '(nba-bound)', '(mlb ', '(nfl ', 'farm', 'mls', 'nwsl', 'angel city',
        'atlanta vibe', 'columbus fury', 'omaha super', 'grand rapids rise',
        'houston skyline', 'indy ignite', 'orlando valkyries',
        'pirates farm', 'cardinals farm', 'milb', 'minor league',
        'next pro', 'mls next', 'union ii', 'real salt lake academy',
        'psg academy', 'barcelona academy', 'arsenal academy',
        'usl', 'usa national', 'lovb', 'pro volleyball',
    ]
    if any(s in school_l for s in pro_school_signals):
        return 9.3, 'pro_active_R4'

    # 5. HS AMATEUR — school HS/prep signals
    hs_strong_signals = [
        ' hs', ' high school', 'prep school', 'preparatory',
        'columbus hs', 'sidwell', 'nokomis', 'monterey hs', 'stillwater hs',
        'corona hs', 'fort cobb', 'university lab', 'nashville christian',
        'perry hs', 'friendship collegiate', 'holy innocents', 'dme academy',
        'notre dame hs', 'oak hill academy', 'montverde academy',
        'imp academy', 'iolani', 'lower merion', 'st. vincent',
    ]
    if any(s in school_l for s in hs_strong_signals):
        return 5.4, 'hs_amateur_R2'
    # 'academy' generic — only HS if class_year is HS-style and not pro/youth
    if 'academy' in school_l and class_l in ['freshman', 'sophomore', 'junior', 'senior']:
        if 'youth' not in school_l and 'pro' not in school_l:
            return 5.4, 'hs_amateur_R2'

    # 6. COLLEGE AMATEUR — class_year or university school
    college_class_years = ['freshman', 'sophomore', 'junior', 'senior',
                           'redshirt', 'graduate']
    if any(c in class_l for c in college_class_years):
        return 7.4, 'college_amateur_R3'
    college_signals = ['university', 'college', ' state', ' tech ', ' tech\'',
                       'duke', 'unc', 'usc', 'ucla', 'byu', 'kansas', 'kentucky',
                       'tennessee', 'texas', 'florida', 'lsu', 'ohio state', 'penn state',
                       'michigan', 'alabama', 'arkansas', 'auburn', 'nebraska',
                       'illinois', 'purdue', 'wisconsin', 'oregon', 'stanford',
                       'vanderbilt', 'maryland', 'south carolina', 'georgia',
                       'arizona', 'baylor', 'pittsburgh', 'louisville', 'connecticut',
                       'wake forest', 'uconn', 'eastern kentucky',
                       'murray state', 'babson', 'missouri', 'florida state']
    # Only apply college cap if NOT already flagged as alumnus-of-college-but-active-pro
    # (those were caught in step 3). Here, a bare university name with no pro class_year
    # means a current college athlete.
    if any(s in school_l for s in college_signals) and 'alumn' not in school_l:
        return 7.4, 'college_amateur_R3'

    # 7. Default
    return None, 'unclassified_unchanged'


def composite_to_tier(comp):
    if comp >= 9.5:  return 'ICON'
    if comp >= 9.0:  return 'ELITE+'
    if comp >= 7.5:  return 'ELITE'
    if comp >= 7.0:  return 'STAR'
    if comp >= 5.5:  return 'PROSPECT'
    if comp >= 3.5:  return 'SCOUT'
    return 'DEVELOPMENTAL'


# ════════════════ STEP 4 · parse marquees ════════════════
print(f"▸ Parsing marquee profiles...")

marquee_start_re = re.compile(r"^( {2,4})'([a-z][a-z0-9\-]+)':\s*\{$", re.MULTILINE)
starts = list(marquee_start_re.finditer(content))
print(f"  Candidate marquee blocks found: {len(starts)}")

report = {
    'applied_at': str(date.today()),
    'version': 'v3',
    'total_candidates': len(starts),
    'updated': [], 'unchanged': [], 'skipped_no_eval_grid': [],
    'tier_changes': {},
}

updates_to_apply = []

for m in starts:
    slug = m.group(2)
    block_start = m.start()
    pos = m.end()
    depth = 1
    while pos < len(content):
        ch = content[pos]
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: break
        elif ch == '/' and pos+1 < len(content) and content[pos+1] == '*':
            end_cmt = content.find('*/', pos+2)
            pos = end_cmt + 2 if end_cmt >= 0 else len(content); continue
        elif ch == '/' and pos+1 < len(content) and content[pos+1] == '/':
            nl = content.find('\n', pos)
            pos = nl + 1 if nl >= 0 else len(content); continue
        elif ch in "'\"":
            quote = ch; pos += 1
            while pos < len(content):
                if content[pos] == '\\': pos += 2; continue
                if content[pos] == quote: break
                pos += 1
        pos += 1
    if depth != 0: continue

    block_end = pos + 1
    block = content[block_start:block_end]
    if 'canonical_position:' not in block or 'eval_grid_override:' not in block: continue

    name_m = re.search(r"name:\s*'([^']+)'", block)
    class_m = re.search(r"class_year:\s*'([^']+)'", block)
    school_m = re.search(r"school:\s*'([^']+)'", block)
    composite_m = re.search(r"eval_grid_override:\s*\{.*?\bcomposite:\s*(\d+(?:\.\d+)?)", block, re.DOTALL)
    tier_m = re.search(r"subjective_tier:\s*'([^']+)'", block)

    if not all([name_m, composite_m, tier_m]):
        report['skipped_no_eval_grid'].append(slug); continue

    name = name_m.group(1)
    class_year = class_m.group(1) if class_m else ''
    school = school_m.group(1) if school_m else ''
    current_composite = float(composite_m.group(1))
    current_tier = tier_m.group(1)

    cap, classification = derive_v5_cap(class_year, school)
    new_composite = current_composite if cap is None else min(current_composite, cap)
    new_tier = composite_to_tier(new_composite)

    if abs(new_composite - current_composite) < 0.01 and new_tier == current_tier:
        report['unchanged'].append({
            'slug': slug, 'name': name, 'school': school, 'class_year': class_year,
            'composite': current_composite, 'tier': current_tier,
            'classification': classification,
        })
        continue

    old_composite_str = composite_m.group(0)
    new_composite_str = old_composite_str[:old_composite_str.rindex(composite_m.group(1))] + f'{new_composite}'
    new_block = block.replace(old_composite_str, new_composite_str, 1)
    new_block = new_block.replace(f"subjective_tier: '{current_tier}'",
                                  f"subjective_tier: '{new_tier}'", 1)

    updates_to_apply.append((block_start, block_end, new_block))
    report['updated'].append({
        'slug': slug, 'name': name, 'school': school, 'class_year': class_year,
        'before': {'composite': current_composite, 'tier': current_tier},
        'after': {'composite': new_composite, 'tier': new_tier},
        'classification': classification,
        'delta': round(new_composite - current_composite, 2),
    })
    key = f"{current_tier} → {new_tier}"
    report['tier_changes'].setdefault(key, 0)
    report['tier_changes'][key] += 1


print(f"  ✓ Updated: {len(report['updated'])}")
print(f"  ✓ Unchanged: {len(report['unchanged'])}")
print(f"  ✓ Skipped (no eval_grid): {len(report['skipped_no_eval_grid'])}")
print(f"  ✓ Tier transitions:")
for k, v in sorted(report['tier_changes'].items(), key=lambda kv: -kv[1]):
    print(f"      {k}: {v}")


# ════════════════ STEP 5 · apply ════════════════
print(f"\n▸ Applying {len(updates_to_apply)} updates...")
for block_start, block_end, new_block in sorted(updates_to_apply, key=lambda x: -x[0]):
    content = content[:block_start] + new_block + content[block_end:]

content = content.rstrip() + f'\n{NEW_MARKER} · {date.today()} · {len(updates_to_apply)} marquees re-graded\n'
WORKER.write_text(content)
new_size = WORKER.stat().st_size
delta = new_size - orig_size
print(f"  ✓ Wrote worker.js ({new_size:,} bytes, delta {delta:+,})")

REPORT.write_text(json.dumps(report, indent=2))
print(f"  ✓ Wrote {REPORT.name}")


# ════════════════ STEP 6 · verification ════════════════
print(f"\n▸ Verification (alumnus fix + prep-to-pro + originals)\n")
re_content = WORKER.read_text()

def find_marquee_value(slug):
    m = re.search(rf"'{re.escape(slug)}':\s*\{{", re_content)
    if not m: return None, None
    pos = m.end(); depth = 1
    while pos < len(re_content):
        if re_content[pos] == '{': depth += 1
        elif re_content[pos] == '}':
            depth -= 1
            if depth == 0: break
        pos += 1
    block = re_content[m.start():pos+1]
    comp_m = re.search(r"composite:\s*(\d+(?:\.\d+)?)", block)
    tier_m = re.search(r"subjective_tier:\s*'([^']+)'", block)
    return (float(comp_m.group(1)) if comp_m else None,
            tier_m.group(1) if tier_m else None)

def find_slug_by_name(name_substring):
    for u in report['updated'] + report['unchanged']:
        if name_substring.lower() in u['name'].lower():
            return u['slug'], u
    return None, None

all_pass = True

# Originals — exact expected values
exact_checks = [
    ('Cameron Boozer (D1 amateur)', 7.4, 'STAR', 'cameron-boozer-duke-mens-basketball'),
    ('Cooper Flagg (NBA-bound)',    9.3, 'ELITE+', 'cooper-flagg-duke-mens-basketball'),
]
for label, ec, et, slug in exact_checks:
    comp, tier = find_marquee_value(slug)
    ok = comp is not None and abs(comp - ec) < 0.01 and tier == et
    print(f"  {'✓' if ok else '✗'} {label}: composite={comp} tier={tier} (expected {ec}/{et})")
    if not ok: all_pass = False

print()
# ACTIVE PRO ALUMNI — must be capped to 9.3, must NOT be retired_pro_unchanged
print("  ── Active college-alumni pros (v3 fix · must be R4 9.3, NOT retired) ──")
active_alumni = [
    ('Joe Burrow (active Bengals)',     'joe burrow'),
    ('Trevor Lawrence (active Jaguars)', 'trevor lawrence'),
    ('Jayson Tatum (active Celtics)',   'jayson tatum'),
    ('Anthony Richardson (active Colts)', 'anthony richardson'),
]
for label, name_sub in active_alumni:
    slug, rec = find_slug_by_name(name_sub)
    if slug is None:
        print(f"  ⚠ {label}: not found — skipping")
        continue
    comp, tier = find_marquee_value(slug)
    cls = rec.get('classification', '?')
    # Must be classified active (pro_active_R4) and capped ≤ 9.3
    ok = cls == 'pro_active_R4' and comp is not None and comp <= 9.3
    print(f"  {'✓' if ok else '✗'} {label}: composite={comp} tier={tier} [{cls}]")
    if not ok: all_pass = False

print()
# LEGACY / RETIRED — must stay unchanged at their high composite
print("  ── Legacy/retired legends (must stay unchanged, NOT capped) ──")
legacy = [
    ('Misty May-Treanor (retired legend)', 'misty may', 9.0),
    ('Foluke Gunderson (retired legend)',  'foluke', 9.0),
    ('Kobe Bryant (retired)',              'kobe', 9.0),
]
for label, name_sub, min_expected in legacy:
    slug, rec = find_slug_by_name(name_sub)
    if slug is None:
        print(f"  ⚠ {label}: not found — skipping")
        continue
    comp, tier = find_marquee_value(slug)
    cls = rec.get('classification', '?')
    # Must NOT be capped down — composite should remain high (≥ 9.0 for these legends)
    ok = comp is not None and comp >= min_expected and cls in ('legacy_pro_unchanged', 'retired_pro_unchanged')
    print(f"  {'✓' if ok else '✗'} {label}: composite={comp} tier={tier} [{cls}]")
    if not ok: all_pass = False

print()
# PREP-TO-PRO (v2 fix must still hold)
print("  ── Prep-to-pro (v2 fix must still hold · NOT SCOUT) ──")
prep = [
    ('LeBron James (active)', 'lebron'),
    ('Bobby Witt Jr. (active MLB)', 'bobby witt'),
    ('Lindsey Horan (active)', 'lindsey horan'),
]
for label, name_sub in prep:
    slug, rec = find_slug_by_name(name_sub)
    if slug is None:
        print(f"  ⚠ {label}: not found — skipping")
        continue
    comp, tier = find_marquee_value(slug)
    ok = tier != 'SCOUT' and (comp is None or comp > 5.4)
    print(f"  {'✓' if ok else '✗'} {label}: composite={comp} tier={tier}")
    if not ok: all_pass = False

if not all_pass:
    rollback("verification failed")


# ════════════════ STEP 7 · summary ════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" MARQUEE RECURATION V5.2 · v3 FIX APPLIED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" Updated   · {len(report['updated'])} marquees")
print(f" Unchanged · {len(report['unchanged'])} (retired/legacy pros + already compliant)")
print(f" Backup    · {BACKUP_V3.name}")
print(f" Marker    · {NEW_MARKER}")
print()
print(f" v3 fixes: active college-alumni pros (Burrow/Lawrence/Tatum) now R4 9.3,")
print(f"           legacy legends (Misty/Foluke) preserved, prep-to-pro (LeBron) held.")
print()
print(f" BACKLOG (separate sprint): active-pro sub-cap — Burrow/Lawrence should")
print(f"           be 8.x not 9.x; only Mahomes-tier 9.x. R4 9.3 is a ceiling only.")
print()
print(f" ROLLBACK · cp {BACKUP_V3.name} {WORKER.name}")
print()
print(f" NEXT · ./fc-deploy-dev.sh")
print(f"        Verify DEV: Boozer 7.4 STAR, LeBron 9.3 ELITE+, Burrow 9.3 ELITE+,")
print(f"                    Kobe 9.7 ICON, Misty 9.7 ICON")
print(f"        ./fc-promote-prod.sh")
print(f"        ./fc-freeze.sh FCBase18_V002_post_marquee_recuration_v5")
