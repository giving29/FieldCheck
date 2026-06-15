#!/usr/bin/env python3
"""
apply_amateur_stub_enrichment_v1.py

Surgically replaces 4 V038 amateur stub profiles in worker.js with full
profiles matching the Cooper Flagg schema (line 20848).

Composites per V5.35 doctrine + Tenet 49 tier map:
  - HS amateurs naturally land at the top of SCOUT (3.5-5.4) because
    evidence-rigor produces that level; HS-only evidence cannot justify
    a higher number. D1 reps required before composite can climb.

Stubs replaced (all are HS senior signees, except Faizon = Tenn freshman):
  - jordan-smith-jr-paul-vi-mens-basketball  (Paul VI / Arkansas)   composite 5.3 SCOUT
  - tyran-stokes-notre-dame-mens-basketball  (Rainier Beach / KU)   composite 5.4 SCOUT
  - cameron-williams-st-marys-mens-basketball (St. Mary's / Duke)   composite 5.2 SCOUT
  - faizon-brandon-grimsley-football         (Tennessee fr)         composite 5.3 SCOUT

Process:
  1. Back up worker.js -> worker.js.pre-enrichment.bak
  2. For each slug, find its block via regex + brace-balanced match
  3. Replace block with enriched version (matching Flagg's schema)
  4. Validate via node --check (rolls back on failure)

Run from worker.js directory:
  python3 apply_amateur_stub_enrichment_v1.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-enrichment.bak')

# =============================================================================
# ENRICHED PROFILES
# =============================================================================
# Schema matches cooper-flagg-duke-mens-basketball at worker.js line 20848.
# Fields: slug, name, sport, canonical_position, school, class_year,
#         college_history, hometown, measurables, awards, pro_projection,
#         eval_grid_override (with composite), subjective_tier, verdict_override.
# =============================================================================

ENRICHED = {}

ENRICHED['jordan-smith-jr-paul-vi-mens-basketball'] = (
"""  'jordan-smith-jr-paul-vi-mens-basketball': {
    slug: 'jordan-smith-jr-paul-vi-mens-basketball',
    name: 'Jordan Smith Jr.', sport: 'mens-basketball', canonical_position: 'Combo Guard',
    school: 'Paul VI Catholic (Chantilly, VA) \\u2014 Arkansas signee', class_year: 'HS Senior',
    college_history: ['Paul VI Catholic (2022-2026)', 'Arkansas (incoming 2026-)'],
    hometown: 'Fairfax, Virginia',
    measurables: { height_display: '6\\u20192\\u201d', weight_display: '200 lb' },
    awards: [
      { year: 2026, award: 'Naismith High School Player of the Year', tier: 'national', sport_org: 'Naismith Awards' },
      { year: 2026, award: 'McDonald\\u2019s All-American', tier: 'national', sport_org: 'McDonald\\u2019s' },
      { year: 2026, award: 'Jordan Brand Classic selection', tier: 'national', sport_org: 'Jordan Brand' },
      { year: 2026, award: '#3 overall 247Sports Composite (2026 class)', tier: 'national', sport_org: '247Sports' },
      { year: 2026, award: 'WCAC Champion (Paul VI, 4x in 5 yrs)', tier: 'conference', sport_org: 'WCAC' },
      { year: 2026, award: 'Senior season: 33-2, VA state title, 26.6 PPG / 5.6 APG / 3.2 SPG / 56% FG', tier: 'state', sport_org: 'VA HS' }
    ],
    pro_projection: { nba_tier: 'PROJECTED_2_3_YR', nba_summary: 'NBA projection on a 2-3 year horizon. Elite HS production and winning pedigree at Paul VI. HS-only evidence; D1 reps required before composite can climb.' },
    eval_grid_override: {
      physical:      { size: { score: 6.0 }, athleticism: { score: 8.0 }, length: { score: 6.5 } },
      production:    { scoring: { score: 8.0 }, playmaking: { score: 7.5 }, defense: { score: 7.5 } },
      projectability:{ position_fit: { score: 7.0 }, character: { score: 8.0 }, ceiling: { score: 7.5 } },
      composite: 5.3
    },
    subjective_tier: 'SCOUT', verdict_override: 'GREATNESS_PATH'
  },"""
)

ENRICHED['tyran-stokes-notre-dame-mens-basketball'] = (
"""  'tyran-stokes-notre-dame-mens-basketball': {
    slug: 'tyran-stokes-notre-dame-mens-basketball',
    name: 'Tyran Stokes', sport: 'mens-basketball', canonical_position: 'Small Forward',
    school: 'Rainier Beach HS (Seattle, WA) \\u2014 Kansas signee', class_year: 'HS Senior',
    college_history: ['Prolific Prep (2022-2024)', 'Notre Dame Sherman Oaks (2024-2025)', 'Rainier Beach (2025-2026)', 'Kansas (incoming 2026-)'],
    hometown: 'Louisville, Kentucky',
    measurables: { height_display: '6\\u20197\\u201d', weight_display: '225 lb' },
    awards: [
      { year: 2026, award: '#1 overall 2026 class \\u2014 perfect 1.000 247Sports Composite', tier: 'national', sport_org: '247Sports' },
      { year: 2026, award: 'McDonald\\u2019s All-American', tier: 'national', sport_org: 'McDonald\\u2019s' },
      { year: 2026, award: 'Jordan Brand Classic MVP', tier: 'national', sport_org: 'Jordan Brand' },
      { year: 2026, award: 'Nike Hoop Summit', tier: 'national', sport_org: 'Nike' },
      { year: 2025, award: 'CIF Southern Section Open Division semifinal (Notre Dame)', tier: 'section', sport_org: 'CIF' },
      { year: 2025, award: 'Junior season: 21.0 PPG / 9.3 RPG / 4.0 APG / 1.5 SPG', tier: 'state', sport_org: 'CA HS' }
    ],
    pro_projection: { nba_tier: 'PROJECTED_1_2_YR', nba_summary: 'NBA projection on 1-2 year horizon. One of eight HS players ever with a perfect 1.000 247Sports composite (peers: LeBron, Dwight Howard, Wiggins, Barrett, Holmgren, Flagg). HS-only evidence; D1 reps required before composite can climb.' },
    eval_grid_override: {
      physical:      { size: { score: 9.0 }, athleticism: { score: 9.0 }, length: { score: 8.5 } },
      production:    { scoring: { score: 7.5 }, playmaking: { score: 6.5 }, defense: { score: 7.5 } },
      projectability:{ position_fit: { score: 8.0 }, character: { score: 7.0 }, ceiling: { score: 8.5 } },
      composite: 5.4
    },
    subjective_tier: 'SCOUT', verdict_override: 'GREATNESS_PATH'
  },"""
)

ENRICHED['cameron-williams-st-marys-mens-basketball'] = (
"""  'cameron-williams-st-marys-mens-basketball': {
    slug: 'cameron-williams-st-marys-mens-basketball',
    name: 'Cameron Williams', sport: 'mens-basketball', canonical_position: 'Power Forward',
    school: 'St. Mary\\u2019s Catholic HS (Phoenix, AZ) \\u2014 Duke signee', class_year: 'HS Senior',
    college_history: ['St. Mary\\u2019s Catholic HS (2022-2026)', 'Duke (incoming 2026-)'],
    hometown: 'Phoenix, Arizona',
    measurables: { height_display: '6\\u201911\\u201d', weight_display: '200 lb' },
    awards: [
      { year: 2026, award: '#4 overall 247Sports Composite, #1 PF nationally', tier: 'national', sport_org: '247Sports' },
      { year: 2026, award: 'McDonald\\u2019s All-American', tier: 'national', sport_org: 'McDonald\\u2019s' },
      { year: 2025, award: 'Arizona 4A State Championship (St. Mary\\u2019s, OT, 30 pts/11 reb/3 blk)', tier: 'state', sport_org: 'AIA' },
      { year: 2025, award: 'Junior season: 18.0 PPG / 11.1 RPG / 3.6 APG / 51% FG', tier: 'state', sport_org: 'AZ HS' },
      { year: 2025, award: 'Compton Magic (Adidas 3SSB): 15.4 PPG / 7.3 RPG / 2.6 BPG / 37% 3P', tier: 'national', sport_org: 'Adidas 3SSB' }
    ],
    pro_projection: { nba_tier: 'PROJECTED_2_3_YR', nba_summary: 'NBA projection on a 2-3 year horizon. 6-foot-11 skill forward with rare versatility; scout comparisons to Kevin Durant frame archetype. HS-only evidence; D1 reps required before composite can climb.' },
    eval_grid_override: {
      physical:      { size: { score: 9.5 }, athleticism: { score: 7.0 }, length: { score: 9.0 } },
      production:    { scoring: { score: 7.5 }, rebounding: { score: 8.0 }, defense: { score: 7.5 } },
      projectability:{ position_fit: { score: 7.5 }, character: { score: 7.5 }, ceiling: { score: 8.5 } },
      composite: 5.2
    },
    subjective_tier: 'SCOUT', verdict_override: 'GREATNESS_PATH'
  },"""
)

ENRICHED['faizon-brandon-grimsley-football'] = (
"""  'faizon-brandon-grimsley-football': {
    slug: 'faizon-brandon-grimsley-football',
    name: 'Faizon Brandon', sport: 'football', canonical_position: 'Quarterback',
    school: 'University of Tennessee (Grimsley HS, NC)', class_year: 'Freshman',
    college_history: ['Grimsley HS (2022-2025)', 'Tennessee (2026-)'],
    hometown: 'Greensboro, North Carolina',
    measurables: { height_display: '6\\u20194\\u201d', weight_display: '215 lb' },
    awards: [
      { year: 2025, award: '#9 overall Rivals Industry Ranking (2026 class)', tier: 'national', sport_org: 'Rivals' },
      { year: 2025, award: '#3 QB nationally, #1 player in North Carolina', tier: 'national', sport_org: '247Sports / Rivals' },
      { year: 2025, award: 'NC 4A State Champion (Grimsley, back-to-back)', tier: 'state', sport_org: 'NCHSAA' },
      { year: 2024, award: 'Junior season: 13-1, NC 4A title, 2,814 yards, 35 TD, 3 INT, 76.6% completion', tier: 'state', sport_org: 'Grimsley HS' },
      { year: 2023, award: 'Sophomore season: 3,026 yards, 36 TD, 3 INT, 69.0% completion', tier: 'state', sport_org: 'Grimsley HS' }
    ],
    pro_projection: { nba_tier: 'NFL_PROJECTED_3_4_YR', nba_summary: 'NFL projection on 3-4 year horizon. Box-checking QB with arm talent + dual-threat athleticism. Competing for Tennessee QB1 in fall 2026 against George MacIntyre. Scout comp archetype: Geno Smith at same stage. HS-only evidence; D1 reps required before composite climbs.' },
    eval_grid_override: {
      physical:      { size: { score: 8.5 }, athleticism: { score: 7.5 }, arm_strength: { score: 9.0 } },
      production:    { passing_efficiency: { score: 8.5 }, decision_making: { score: 8.0 }, dual_threat: { score: 7.5 } },
      projectability:{ position_fit: { score: 8.0 }, character: { score: 7.5 }, ceiling: { score: 8.0 } },
      composite: 5.3
    },
    subjective_tier: 'SCOUT', verdict_override: 'GREATNESS_PATH'
  },"""
)


# =============================================================================
# Brace-balanced block finder (respects string literals)
# =============================================================================

def find_balanced_block_end(text, brace_open_idx):
    """Given index of '{', return matching '}' index (inclusive)."""
    depth = 0
    i = brace_open_idx
    in_string = False
    string_char = None
    while i < len(text):
        c = text[i]
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == string_char:
                in_string = False
            i += 1
            continue
        if c in "\"'":
            in_string = True
            string_char = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def find_stub_block(text, slug):
    """Locate the existing block for a slug. Returns (start, end_inclusive) or None.
    Includes trailing comma if present."""
    pattern = re.compile(
        r"^\s*'" + re.escape(slug) + r"'\s*:\s*\{",
        re.MULTILINE
    )
    m = pattern.search(text)
    if not m:
        return None
    start = m.start()
    brace_idx = m.end() - 1
    end_idx = find_balanced_block_end(text, brace_idx)
    if end_idx == -1:
        return None
    after = end_idx + 1
    if after < len(text) and text[after] == ',':
        end_idx = after
    return (start, end_idx)


# =============================================================================
# Main
# =============================================================================

def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original = content
    original_size = len(original)

    # Backup
    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")
    print()

    # Apply each enrichment
    summary = []
    for slug, new_block in ENRICHED.items():
        loc = find_stub_block(content, slug)
        if loc is None:
            summary.append((slug, 'NOT_FOUND', 0, 0, False))
            continue
        start, end = loc
        old_block = content[start:end+1]
        was_stub = 'is_amateur_stub' in old_block
        content = content[:start] + new_block + content[end+1:]
        summary.append((slug, 'OK', len(old_block), len(new_block), was_stub))

    if content == original:
        print("ERROR: no changes applied (all 4 slugs missing?)")
        return 1

    WORKER.write_text(content)

    # Report
    print("Enrichment summary:")
    print(f"{'  status':<10} {'was_stub':<10} {'old':<7} {'new':<7} {'delta':<7}  slug")
    print(f"  {'-'*8} {'-'*8} {'-'*5} {'-'*5} {'-'*5}  {'-'*60}")
    for slug, status, old_len, new_len, was_stub in summary:
        delta = new_len - old_len
        delta_str = f"{delta:+d}"
        was_stub_str = 'YES' if was_stub else 'no'
        print(f"  {status:<8} {was_stub_str:<8} {old_len:<5} {new_len:<5} {delta_str:<5}  {slug}")
    print()
    print(f"worker.js: {original_size} -> {len(content)} bytes ({len(content) - original_size:+d})")
    print()

    # Validate JS syntax
    print("Validating JS syntax (node --check)...")
    try:
        result = subprocess.run(
            ['node', '--check', str(WORKER)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print("OK   node --check PASSED")
        else:
            print("ERROR: node --check FAILED:")
            print(result.stderr)
            print()
            print(f"Rolling back worker.js from {BACKUP}...")
            shutil.copy(BACKUP, WORKER)
            print(f"OK   Restored.")
            return 1
    except FileNotFoundError:
        print("WARN: node not in PATH; skipping syntax check (deploy will catch it)")
    except subprocess.TimeoutExpired:
        print("WARN: node --check timed out; proceed with caution")

    print()
    not_found = [s for s, st, *_ in summary if st == 'NOT_FOUND']
    if not_found:
        print(f"WARN: {len(not_found)} slug(s) not found in worker.js:")
        for s in not_found:
            print(f"  - {s}")
        print("Investigate before deploying.")
        return 2

    print("All 4 enrichments applied cleanly.")
    print()
    print("Verify a sample (one slug):")
    print('  grep -A 25 "jordan-smith-jr-paul-vi-mens-basketball" worker.js | head -30')
    print()
    return 0


if __name__ == '__main__':
    sys.exit(apply())
