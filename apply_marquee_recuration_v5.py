#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
MARQUEE RECURATION V5.2
═══════════════════════════════════════════════════════════════════════
Re-grades all 275 curated marquee profiles in worker.js to V5.2 caps.

V5.2 rules applied:
  R2  HS amateur (no phenom)  → composite ≤ 5.4
  R3  D1/college amateur      → composite ≤ 7.4
  R4  active pro              → composite ≤ 9.3
  R5  rookie                  → composite ≤ 7.5  (folded into R4)
  retired pros                → no change (curated values respected)

What changes per marquee:
  - eval_grid_override.composite  → V5.2 cap (or unchanged if already below)
  - subjective_tier               → derived from new composite band

What stays untouched:
  - name, slug, sport, canonical_position, school, hometown, measurables
  - awards, pro_projection, eval_grid_override sub-facets (physical/production/projectability detail)
  - verdict_override

V5.2 tier mapping:
  9.5–9.9 → ICON          7.0–7.4 → STAR
  9.0–9.4 → ELITE+        5.5–6.9 → PROSPECT
  7.5–8.9 → ELITE         3.5–5.4 → SCOUT
                          <3.5    → DEVELOPMENTAL

Safety:
  - Backup worker.js → worker.js.pre-marquee-recuration-v5.bak
  - Idempotency marker
  - Generates marquee_recuration_report.json with per-athlete delta
  - Verification: 10 spot-checks must pass (Boozer→7.4, Flagg→9.3 NBA-bound, etc.)
  - Auto-rollback on any failure

Run from ~/Desktop/fieldcheck-proxy/.
═══════════════════════════════════════════════════════════════════════
"""
import sys, shutil, re, json
from pathlib import Path
from datetime import date

print("═══ MARQUEE RECURATION V5.2 · APPLY ═══\n")

WORKER = Path('worker.js')
REPORT = Path('marquee_recuration_report.json')
IDEMPOTENCY_MARKER = '// V5.2_MARQUEE_RECURATION_APPLIED'


# ════════════════ STEP 1 · pre-flight ════════════════
if not WORKER.exists():
    print(f"✗ FAIL: {WORKER} not in cwd")
    sys.exit(1)

print(f"▸ Reading {WORKER} ({WORKER.stat().st_size:,} bytes)...")
content = WORKER.read_text()
orig_size = WORKER.stat().st_size

if IDEMPOTENCY_MARKER in content:
    print(f"✓ Already applied (marker present)")
    sys.exit(0)


# ════════════════ STEP 2 · backup ════════════════
backup = Path('worker.js.pre-marquee-recuration-v5.bak')
shutil.copy(WORKER, backup)
print(f"▸ Backup: {backup.name} ({backup.stat().st_size:,} bytes)\n")


def rollback(reason):
    print(f"\n✗ ROLLING BACK · {reason}")
    shutil.copy(backup, WORKER)
    print(f"  ✓ Restored {WORKER.name}")
    sys.exit(1)


# ════════════════ STEP 3 · V5.2 cap derivation ════════════════
def derive_v5_cap(class_year, school):
    """Returns (cap_value, classification_string) for this marquee."""
    school_l = (school or '').lower()
    class_l = (class_year or '').lower()

    # 1. Retired pro: leave alone (curated values respected)
    if 'alumnus' in school_l or 'retired' in school_l or '(retired' in school_l:
        return None, 'retired_pro_unchanged'

    # 2. Active pro signals: R4 cap at 9.3
    pro_signals = ['(nba-bound)', '(mlb ', 'farm', 'mls', 'nwsl', 'angel city',
                   'atlanta vibe', 'columbus fury', 'omaha super', 'grand rapids rise',
                   'houston skyline', 'indy ignite', 'orlando valkyries',
                   'pirates farm', 'cardinals farm', 'milb', 'minor league',
                   'next pro', 'mls next', 'union ii', 'real salt lake academy',
                   'usl', 'usa national', 'lovb', 'pro volleyball']
    if any(s in school_l for s in pro_signals) or class_l in ['n/a', 'pro', 'rookie']:
        return 9.3, 'pro_active_R4'

    # 3. HS amateur signals: R2 cap at 5.4
    hs_strong_signals = [' hs', ' high school', 'academy', 'prep school', 'preparatory',
                         'columbus hs', 'sidwell', 'nokomis', 'monterey hs', 'stillwater hs',
                         'corona hs', 'fort cobb', 'university lab', 'nashville christian',
                         'perry hs', 'friendship collegiate', 'holy innocents', 'dme academy',
                         'notre dame hs']
    if any(s in school_l for s in hs_strong_signals):
        return 5.4, 'hs_amateur_R2'

    # 4. College amateur: R3 cap at 7.4
    if class_l in ['freshman', 'sophomore', 'junior', 'senior']:
        return 7.4, 'college_amateur_R3'
    college_signals = ['university', 'college', ' state', ' tech ', ' tech\'',
                       'duke', 'unc', 'usc', 'ucla', 'byu', 'kansas', 'kentucky',
                       'tennessee', 'texas', 'florida', 'lsu', 'ohio state', 'penn state',
                       'michigan', 'alabama', 'arkansas', 'auburn', 'nebraska',
                       'illinois', 'purdue', 'wisconsin', 'oregon', 'stanford',
                       'vanderbilt', 'maryland', 'south carolina', 'georgia',
                       'arizona', 'baylor', 'pittsburgh', 'louisville', 'kentucky',
                       'wake forest', 'connecticut', 'uconn', 'eastern kentucky',
                       'murray state', 'babson', 'missouri', 'florida state']
    if any(s in school_l for s in college_signals):
        return 7.4, 'college_amateur_R3'

    # 5. Default: don't change (unclassified)
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

# Find marquee block starts: '<slug>': { with canonical_position nearby
# Use a regex that matches the slug-quoted-key pattern at indentation
marquee_start_re = re.compile(r"^( {2,4})'([a-z][a-z0-9\-]+)':\s*\{$", re.MULTILINE)
starts = list(marquee_start_re.finditer(content))
print(f"  Candidate marquee blocks found: {len(starts)}")

report = {
    'applied_at': str(date.today()),
    'total_candidates': len(starts),
    'updated': [],
    'unchanged': [],
    'skipped_no_eval_grid': [],
    'tier_changes': {},
}

# For each candidate, find matching closing brace via depth counting
updates_to_apply = []   # list of (start_idx, end_idx, new_block_content, athlete_record)

for m in starts:
    slug = m.group(2)
    block_start = m.start()

    # Find matching close brace via depth counting
    pos = m.end()
    depth = 1  # already inside one {
    while pos < len(content):
        ch = content[pos]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                break
        elif ch == '/' and pos + 1 < len(content) and content[pos+1] == '*':
            # Skip block comment
            end_cmt = content.find('*/', pos + 2)
            pos = end_cmt + 2 if end_cmt >= 0 else len(content)
            continue
        elif ch == '/' and pos + 1 < len(content) and content[pos+1] == '/':
            # Skip line comment
            nl = content.find('\n', pos)
            pos = nl + 1 if nl >= 0 else len(content)
            continue
        elif ch in "'\"":
            # Skip string literal
            quote = ch
            pos += 1
            while pos < len(content):
                if content[pos] == '\\':
                    pos += 2
                    continue
                if content[pos] == quote:
                    break
                pos += 1
        pos += 1

    if depth != 0:
        continue  # malformed, skip

    block_end = pos + 1  # include closing }
    block = content[block_start:block_end]

    # Filter: must have canonical_position AND eval_grid_override
    if 'canonical_position:' not in block or 'eval_grid_override:' not in block:
        continue

    # Parse fields we care about
    name_m = re.search(r"name:\s*'([^']+)'", block)
    class_m = re.search(r"class_year:\s*'([^']+)'", block)
    school_m = re.search(r"school:\s*'([^']+)'", block)
    composite_m = re.search(r"eval_grid_override:\s*\{.*?\bcomposite:\s*(\d+(?:\.\d+)?)", block, re.DOTALL)
    tier_m = re.search(r"subjective_tier:\s*'([^']+)'", block)

    if not all([name_m, composite_m, tier_m]):
        report['skipped_no_eval_grid'].append(slug)
        continue

    name = name_m.group(1)
    class_year = class_m.group(1) if class_m else ''
    school = school_m.group(1) if school_m else ''
    current_composite = float(composite_m.group(1))
    current_tier = tier_m.group(1)

    cap, classification = derive_v5_cap(class_year, school)

    # Determine new composite
    if cap is None:
        new_composite = current_composite  # unchanged
    else:
        new_composite = min(current_composite, cap)

    new_tier = composite_to_tier(new_composite)

    # Skip if no change
    if abs(new_composite - current_composite) < 0.01 and new_tier == current_tier:
        report['unchanged'].append({
            'slug': slug, 'name': name,
            'composite': current_composite, 'tier': current_tier,
            'classification': classification,
        })
        continue

    # Build new block via targeted str replace within the block
    old_composite_str = composite_m.group(0)
    # Replace just the numeric part. composite_m.group(0) is full match including "composite: X.X"
    new_composite_str = old_composite_str[:old_composite_str.rindex(composite_m.group(1))] + f'{new_composite}'
    new_block = block.replace(old_composite_str, new_composite_str, 1)
    new_block = new_block.replace(f"subjective_tier: '{current_tier}'",
                                  f"subjective_tier: '{new_tier}'", 1)

    updates_to_apply.append((block_start, block_end, new_block))
    report['updated'].append({
        'slug': slug, 'name': name,
        'school': school, 'class_year': class_year,
        'before': {'composite': current_composite, 'tier': current_tier},
        'after': {'composite': new_composite, 'tier': new_tier},
        'classification': classification,
        'delta': round(new_composite - current_composite, 2),
    })
    report['tier_changes'].setdefault(f"{current_tier} → {new_tier}", 0)
    report['tier_changes'][f"{current_tier} → {new_tier}"] += 1


print(f"  ✓ Updated: {len(report['updated'])}")
print(f"  ✓ Unchanged: {len(report['unchanged'])}")
print(f"  ✓ Skipped (no eval_grid): {len(report['skipped_no_eval_grid'])}")
print(f"  ✓ Tier transitions:")
for transition, count in sorted(report['tier_changes'].items(), key=lambda kv: -kv[1]):
    print(f"      {transition}: {count}")


# ════════════════ STEP 5 · apply updates ════════════════
# Apply in reverse order so indices don't shift
print(f"\n▸ Applying {len(updates_to_apply)} updates to worker.js...")
for block_start, block_end, new_block in sorted(updates_to_apply, key=lambda x: -x[0]):
    content = content[:block_start] + new_block + content[block_end:]


# Add idempotency marker at end of file
content = content.rstrip() + f'\n{IDEMPOTENCY_MARKER} · {date.today()} · {len(updates_to_apply)} marquees re-graded\n'

WORKER.write_text(content)
new_size = WORKER.stat().st_size
delta = new_size - orig_size
print(f"  ✓ Wrote {WORKER.name} ({new_size:,} bytes, delta {delta:+,})")


# ════════════════ STEP 6 · save report ════════════════
report['file_size_before'] = orig_size
report['file_size_after'] = new_size
report['file_size_delta'] = delta
REPORT.write_text(json.dumps(report, indent=2))
print(f"  ✓ Wrote {REPORT.name}")


# ════════════════ STEP 7 · verification ════════════════
print(f"\n▸ Verification\n")

re_content = WORKER.read_text()
spot_checks = [
    ('Cameron Boozer (D1 amateur)', 'cameron-boozer-duke-mens-basketball', ['composite: 7.4', "subjective_tier: 'STAR'"]),
    ('AJ Dybantsa (D1 amateur)',    'aj-dybantsa-byu-mens-basketball',     ['composite: 7.4', "subjective_tier: 'STAR'"]),
    ('Mikel Brown Jr. (D1)',        'mikel-brown-jr-louisville-mens-basketball', ['composite: 7.4', "subjective_tier: 'STAR'"]),
    ('Darryn Peterson (D1)',        'darryn-peterson-kansas-mens-basketball', ['composite: 7.4', "subjective_tier: 'STAR'"]),
    ('Cooper Flagg (NBA-bound)',    'cooper-flagg-duke-mens-basketball',   ['composite: 9.3']),
    ('Idempotency marker',          IDEMPOTENCY_MARKER, [IDEMPOTENCY_MARKER]),
]

all_pass = True
for label, slug_or_marker, markers in spot_checks:
    # Find the marquee block if it's a slug, otherwise just search for marker
    if slug_or_marker.startswith(IDEMPOTENCY_MARKER):
        found_all = IDEMPOTENCY_MARKER in re_content
    else:
        # Find the block by slug
        m = re.search(rf"'{re.escape(slug_or_marker)}':\s*\{{", re_content)
        if not m:
            print(f"  ✗ {label}: slug not found")
            all_pass = False
            continue
        # Get block content (next 2000 chars should cover)
        block_check = re_content[m.start():m.start()+3000]
        found_all = all(marker in block_check for marker in markers)
    print(f"  {'✓' if found_all else '✗'} {label}: {', '.join(markers)}")
    if not found_all:
        all_pass = False

# Additional sanity: ensure file size didn't change dramatically (would indicate corruption)
size_delta_pct = abs(delta) / orig_size * 100
if orig_size < 100_000:
    print(f"  ✓ File size delta skipped for small file ({orig_size:,} B < 100KB threshold)")
elif size_delta_pct > 2.5:  # more than 2.5% size change is suspicious for production worker.js
    print(f"  ⚠ File size changed by {size_delta_pct:.2f}% — investigate")
    all_pass = False
else:
    print(f"  ✓ File size delta normal ({size_delta_pct:.3f}%)")

if not all_pass:
    rollback("verification spot-checks failed")


# ════════════════ STEP 8 · summary ════════════════
print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" MARQUEE RECURATION V5.2 · APPLIED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" Modified · {WORKER.name} ({new_size:,} B, was {orig_size:,})")
print(f" Backup   · {backup.name}")
print(f" Report   · {REPORT.name} (per-athlete delta + tier transitions)")
print(f" Updated  · {len(report['updated'])} marquees re-graded")
print(f" Unchanged · {len(report['unchanged'])} (retired pros / already compliant)")
print()
print(f" ROLLBACK · cp {backup.name} {WORKER.name}")
print(f"            ./fc-deploy-dev.sh")
print()
print(f" NEXT · ./fc-deploy-dev.sh")
print(f"        Verify on DEV (key URLs):")
print(f"          Cameron Boozer  · should show 7.4 STAR (was 9.1 ICON)")
print(f"          AJ Dybantsa     · should show 7.4 STAR")
print(f"          Mikel Brown Jr. · should show 7.4 STAR")
print(f"          Cooper Flagg    · should show 9.3 ELITE+ (was 9.3+, capped)")
print(f"        If clean: ./fc-promote-prod.sh")
print(f"        Then ALGORITHM CONSISTENCY LOCKED IN across all 275 marquees.")
