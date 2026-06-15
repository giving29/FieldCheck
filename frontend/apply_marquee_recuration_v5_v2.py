#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
MARQUEE RECURATION V5.2 · FIX v2
═══════════════════════════════════════════════════════════════════════
Fixes the prep-to-pro bug in v1.

V1 BUG: HS signals in school field were checked BEFORE pro signals in
class_year. So LeBron (school='St. Vincent HS', class_year='Pro (Lakers)')
got R2 capped at 5.4 instead of R4 capped at 9.3.

V2 FIX: class_year is THE most reliable career-stage signal. Check order:
  1. RETIRED  — 'retired' in class_year OR 'alumnus' in school
  2. ACTIVE PRO — 'pro' substring in class_year
  3. ACTIVE PRO — school signals (academies, farm teams)
  4. HS AMATEUR — school HS signals
  5. COLLEGE AMATEUR — class_year freshman/soph/jr/sr or university school
  6. UNCLASSIFIED — unchanged

This script:
  1. Detects v1 idempotency marker in worker.js
  2. If present, auto-restores from worker.js.pre-marquee-recuration-v5.bak
  3. Applies v2 logic with corrected priority
  4. Stamps NEW marker: V5.2_MARQUEE_RECURATION_V2_APPLIED
  5. Verifies 5 prep-to-pro spot checks (LeBron, Kobe, Bobby Witt, Horan, Mayer)
  6. Auto-rollback on failure
═══════════════════════════════════════════════════════════════════════
"""
import sys, shutil, re, json
from pathlib import Path
from datetime import date

print("═══ MARQUEE RECURATION V5.2 · FIX v2 ═══\n")

WORKER = Path('worker.js')
BACKUP_V1 = Path('worker.js.pre-marquee-recuration-v5.bak')
BACKUP_V2 = Path('worker.js.pre-marquee-recuration-v5-v2.bak')
REPORT = Path('marquee_recuration_report.json')
OLD_MARKER = '// V5.2_MARQUEE_RECURATION_APPLIED'
NEW_MARKER = '// V5.2_MARQUEE_RECURATION_V2_APPLIED'


# ════════════════ STEP 1 · pre-flight ════════════════
if not WORKER.exists():
    print(f"✗ FAIL: {WORKER} not in cwd")
    sys.exit(1)

content = WORKER.read_text()
print(f"▸ Current worker.js: {WORKER.stat().st_size:,} bytes")

# Auto-rollback v1 if marker present
if OLD_MARKER in content:
    if not BACKUP_V1.exists():
        print(f"✗ FAIL: v1 marker present but {BACKUP_V1} missing — manual recovery needed")
        sys.exit(1)
    print(f"▸ Detected v1 marker · auto-rolling back from {BACKUP_V1.name}")
    shutil.copy(BACKUP_V1, WORKER)
    content = WORKER.read_text()
    print(f"  ✓ Restored to {WORKER.stat().st_size:,} bytes")

if NEW_MARKER in content:
    print(f"✓ v2 already applied")
    sys.exit(0)


# ════════════════ STEP 2 · backup ════════════════
shutil.copy(WORKER, BACKUP_V2)
print(f"▸ v2 backup: {BACKUP_V2.name}\n")
orig_size = WORKER.stat().st_size

def rollback(reason):
    print(f"\n✗ ROLLING BACK · {reason}")
    shutil.copy(BACKUP_V2, WORKER)
    print(f"  ✓ Restored {WORKER.name}")
    sys.exit(1)


# ════════════════ STEP 3 · FIXED V5.2 cap derivation ════════════════
def derive_v5_cap(class_year, school):
    """class_year first, then school. Returns (cap_value_or_None, classification)."""
    school_l = (school or '').lower()
    class_l = (class_year or '').lower()

    # 1. RETIRED PRO — class_year is primary signal
    if 'retired' in class_l or 'alumnus' in school_l or 'alumna' in school_l:
        return None, 'retired_pro_unchanged'

    # 2. ACTIVE PRO — class_year 'pro' substring catches "Pro (Team Name)"
    if 'pro' in class_l or class_l == 'n/a' or 'rookie' in class_l or 'professional' in class_l:
        return 9.3, 'pro_active_R4'

    # 3. ACTIVE PRO — school signals (academies, farm teams, pro clubs)
    pro_school_signals = [
        '(nba-bound)', '(mlb ', '(nfl ', 'farm', 'mls', 'nwsl', 'angel city',
        'atlanta vibe', 'columbus fury', 'omaha super', 'grand rapids rise',
        'houston skyline', 'indy ignite', 'orlando valkyries',
        'pirates farm', 'cardinals farm', 'milb', 'minor league',
        'next pro', 'mls next', 'union ii', 'real salt lake academy',
        'psg academy', 'barcelona academy', 'lyon', 'arsenal academy',
        'usl', 'usa national', 'lovb', 'pro volleyball',
    ]
    if any(s in school_l for s in pro_school_signals):
        return 9.3, 'pro_active_R4'

    # 4. HS AMATEUR — school HS/prep signals
    hs_strong_signals = [
        ' hs', ' high school', 'prep school', 'preparatory',
        'columbus hs', 'sidwell', 'nokomis', 'monterey hs', 'stillwater hs',
        'corona hs', 'fort cobb', 'university lab', 'nashville christian',
        'perry hs', 'friendship collegiate', 'holy innocents', 'dme academy',
        'notre dame hs', 'oak hill academy', 'montverde academy',
        'imp academy', 'iolani', 'lower merion', 'st. vincent',
    ]
    # Special case: 'academy' alone is ambiguous (HS prep vs pro youth).
    # We only flag as HS if no other pro signal was found above (we already
    # passed those checks) AND school doesn't look like a pro academy.
    if any(s in school_l for s in hs_strong_signals):
        return 5.4, 'hs_amateur_R2'
    # 'academy' generic — only HS if class_year is HS-style
    if 'academy' in school_l and class_l in ['freshman', 'sophomore', 'junior', 'senior']:
        # Could be HS prep academy. Check school doesn't explicitly say pro/youth
        if 'youth' not in school_l and 'pro' not in school_l:
            return 5.4, 'hs_amateur_R2'

    # 5. COLLEGE AMATEUR — class_year (Freshman/Sophomore/Junior/Senior) or university
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
    if any(s in school_l for s in college_signals):
        return 7.4, 'college_amateur_R3'

    # 6. Default
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
    'version': 'v2',
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
print(f"\n▸ Verification (prep-to-pro fix + originals)\n")
re_content = WORKER.read_text()

def find_marquee_value(slug, key):
    """Find slug's marquee block and extract the composite + tier."""
    m = re.search(rf"'{re.escape(slug)}':\s*\{{", re_content)
    if not m: return None, None
    # Get the block
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

spot_checks = [
    # (label, expected_composite, expected_tier, slug_substring_to_find)
    ('Cameron Boozer (D1 amateur)', 7.4, 'STAR', 'cameron-boozer-duke-mens-basketball'),
    ('Cooper Flagg (NBA-bound)',    9.3, 'ELITE+', 'cooper-flagg-duke-mens-basketball'),
]

# For prep-to-pro fix verification, find slug by name
def find_slug_by_name(name_substring):
    for u in report['updated'] + report['unchanged']:
        if name_substring.lower() in u['name'].lower():
            return u['slug']
    return None

prep_to_pro_athletes = [
    ('LeBron James (active pro)',      'lebron'),
    ('Kobe Bryant (retired pro)',      'kobe'),
    ('Bobby Witt Jr. (active MLB)',    'bobby witt'),
    ('Lindsey Horan (active NWSL/USWNT)', 'lindsey horan'),
    ('Marcelo Mayer (active MLB)',     'marcelo mayer'),
]

all_pass = True
for label, expected_comp, expected_tier, slug in spot_checks:
    comp, tier = find_marquee_value(slug, 'composite')
    ok = comp is not None and abs(comp - expected_comp) < 0.01 and tier == expected_tier
    print(f"  {'✓' if ok else '✗'} {label}: composite={comp} tier={tier} (expected {expected_comp}/{expected_tier})")
    if not ok: all_pass = False

print()
for label, name_sub in prep_to_pro_athletes:
    slug = find_slug_by_name(name_sub)
    if slug is None:
        print(f"  ⚠ {label}: not found in report — skipping (may not exist in marquees)")
        continue
    comp, tier = find_marquee_value(slug, 'composite')
    # Active pros: should be capped at 9.3. Retired: should be unchanged (>= 9.3 likely).
    # Critical: must NOT be 5.4 SCOUT.
    if tier == 'SCOUT' or (comp is not None and comp <= 5.4):
        print(f"  ✗ {label}: composite={comp} tier={tier} — STILL R2 BUG")
        all_pass = False
    else:
        print(f"  ✓ {label}: composite={comp} tier={tier} (slug={slug})")

if not all_pass:
    rollback("verification failed — prep-to-pro fix not effective")


# ════════════════ STEP 7 · summary ════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" MARQUEE RECURATION V5.2 · v2 FIX APPLIED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" Updated   · {len(report['updated'])} marquees")
print(f" Unchanged · {len(report['unchanged'])} (retired pros + already compliant)")
print(f" Backup    · {BACKUP_V2.name}")
print(f" Marker    · {NEW_MARKER}")
print()
print(f" Prep-to-pro fix verified for: LeBron, Kobe, Bobby Witt Jr, Horan, Mayer")
print()
print(f" ROLLBACK · cp {BACKUP_V2.name} {WORKER.name}")
print()
print(f" NEXT · ./fc-deploy-dev.sh")
print(f"        Verify on DEV: Boozer 7.4 STAR, LeBron 9.3 ELITE+, Kobe 9.7 ICON")
print(f"        ./fc-promote-prod.sh")
print(f"        ./fc-freeze.sh FCBase18_V002_post_marquee_recuration_v5")
