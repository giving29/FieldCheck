#!/usr/bin/env python3
"""
q_amazed_audit_v1.py

Audits all 110 athletes in roster_100.json against the curated state in
worker.js. NO API CALLS. Pure local file analysis — runs in seconds.

Scores each athlete on 7 dimensions of "is the page amazing?":

  1. profile_present       — does PLAYER_PROFILES have an entry?
  2. profile_depth         — full profile (school, position, class, hometown, measurables) vs stub
  3. eval_grid             — eval_grid_override present + composite set
  4. awards_count          — number of awards in the list
  5. curated_videos        — count of entries in CURATED_MEDIA[key].videos[]
  6. curated_news          — count of entries in CURATED_MEDIA[key].news[]
  7. shorts_reels          — count of shorts/reels/tiktoks (currently always 0 — coming next)

Output: amazed_audit.html — sortable table, color-coded scores, sectioned
by bucket (amateur first per directive), with direct links to each verdict
page on prod.

Run from fieldcheck-proxy directory (where worker.js + roster_100.json live):
  python3 q_amazed_audit_v1.py

Then open amazed_audit.html in browser.
"""

import json
import re
import sys
import html
from pathlib import Path
from datetime import datetime

WORKER = Path('worker.js')
ROSTER = Path('roster_100.json')
OUTPUT = Path('amazed_audit.html')

PROD_BASE = 'https://fieldcheck-app.netlify.app'

# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────

def slugify_name(name: str) -> str:
    """Mirror the worker's mediaKey derivation."""
    if not name:
        return ''
    s = name.lower()
    s = re.sub(r"[.']", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s


def extract_block_keys(src: str, const_name: str) -> dict:
    """
    Return {slug_key: raw_body_text} for every top-level entry under a const
    declared as `const <const_name> = {`. Uses naive brace matching but
    handles the actual worker.js shape reliably for PLAYER_PROFILES and
    CURATED_MEDIA which are both flat top-level object literals.
    """
    decl = re.search(r'const\s+' + re.escape(const_name) + r'\s*=\s*\{', src)
    if not decl:
        return {}
    start = decl.end() - 1  # index of opening '{'
    depth = 0
    end = start
    in_str = None
    i = start
    while i < len(src):
        ch = src[i]
        if in_str:
            if ch == '\\':
                i += 2
                continue
            if ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", '`'):
                in_str = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        i += 1
    body = src[start + 1:end]

    # Walk the body to find top-level 'key': { ... } entries
    entries = {}
    j = 0
    while j < len(body):
        m = re.match(r"\s*'([^']+)'\s*:\s*\{", body[j:])
        if not m:
            # try to skip past current segment
            comma = body.find(',', j)
            if comma == -1:
                break
            j = comma + 1
            continue
        key = m.group(1)
        block_start = j + m.end() - 1  # position of '{'
        # match braces
        d = 0
        k = block_start
        in_s = None
        while k < len(body):
            c = body[k]
            if in_s:
                if c == '\\':
                    k += 2
                    continue
                if c == in_s:
                    in_s = None
            else:
                if c in ('"', "'", '`'):
                    in_s = c
                elif c == '{':
                    d += 1
                elif c == '}':
                    d -= 1
                    if d == 0:
                        break
            k += 1
        block_end = k
        entries[key] = body[block_start:block_end + 1]
        j = block_end + 1
    return entries


def count_array_items(block_text: str, field_name: str) -> int:
    """Count top-level items in `field_name: [ ... ]` within block_text."""
    m = re.search(re.escape(field_name) + r'\s*:\s*\[', block_text)
    if not m:
        return 0
    start = m.end() - 1  # '['
    d = 0
    in_s = None
    i = start
    while i < len(block_text):
        c = block_text[i]
        if in_s:
            if c == '\\':
                i += 2
                continue
            if c == in_s:
                in_s = None
        else:
            if c in ('"', "'", '`'):
                in_s = c
            elif c == '[':
                d += 1
            elif c == ']':
                d -= 1
                if d == 0:
                    break
        i += 1
    inner = block_text[start + 1:i]
    # Count top-level objects (each item starts with '{' at depth 0)
    count = 0
    dd = 0
    ins = None
    k = 0
    while k < len(inner):
        ch = inner[k]
        if ins:
            if ch == '\\':
                k += 2
                continue
            if ch == ins:
                ins = None
        else:
            if ch in ('"', "'", '`'):
                ins = ch
            elif ch == '{':
                if dd == 0:
                    count += 1
                dd += 1
            elif ch == '}':
                dd -= 1
        k += 1
    return count


def has_field(block_text: str, field_name: str) -> bool:
    return bool(re.search(re.escape(field_name) + r'\s*:', block_text))


def has_nonempty_string_field(block_text: str, field_name: str) -> bool:
    m = re.search(re.escape(field_name) + r"\s*:\s*['\"]([^'\"]*)['\"]", block_text)
    if not m:
        return False
    return len(m.group(1).strip()) > 0


# ─────────────────────────────────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────────────────────────────────

DIMS = [
    ('profile_present', 'Profile'),
    ('profile_depth',   'Depth'),
    ('eval_grid',       'Grid'),
    ('awards_count',    'Awards'),
    ('curated_videos',  'Videos'),
    ('curated_news',    'News'),
    ('shorts_reels',    'Shorts/Reels'),
]


def score_athlete(athlete: dict, profiles: dict, media: dict) -> dict:
    name = athlete.get('name') or athlete.get('display_name') or ''
    sport = athlete.get('sport') or ''
    school = athlete.get('school') or athlete.get('current_school') or ''
    bucket = athlete.get('bucket') or athlete.get('tier') or athlete.get('category') or 'unknown'

    name_slug = slugify_name(name)
    sport_slug = slugify_name(sport)

    # PLAYER_PROFILES key: long form '<name>-<school>-<sport>'
    profile_key = None
    profile_body = ''
    if name_slug:
        # Try direct: name-sport (rare for amateur HS players)
        candidate = name_slug + '-' + sport_slug
        if candidate in profiles:
            profile_key = candidate
        else:
            # Iterate keys looking for one that starts with name_slug + '-' and ends with '-' + sport_slug
            prefix = name_slug + '-'
            suffix = '-' + sport_slug if sport_slug else ''
            matches = [k for k in profiles
                       if k.startswith(prefix) and (not suffix or k.endswith(suffix))]
            if len(matches) == 1:
                profile_key = matches[0]
            elif matches:
                # multiple — take shortest (most likely the canonical)
                profile_key = sorted(matches, key=len)[0]
    if profile_key:
        profile_body = profiles[profile_key]

    # CURATED_MEDIA key: short form 'name-sport'
    media_key = name_slug + '-' + sport_slug if (name_slug and sport_slug) else None
    media_body = media.get(media_key, '') if media_key else ''

    # Score each dimension
    profile_present = 1 if profile_body else 0

    # Depth: count distinct "core" fields present
    core_fields = ['school', 'class_year', 'canonical_position', 'hometown', 'measurables']
    depth_hits = sum(1 for f in core_fields if has_field(profile_body, f))
    profile_depth = depth_hits  # 0–5

    eval_grid = 1 if (has_field(profile_body, 'eval_grid_override') or has_field(profile_body, 'eval_grid')) else 0

    awards_count = count_array_items(profile_body, 'awards') if profile_body else 0
    curated_videos = count_array_items(media_body, 'videos') if media_body else 0
    curated_news = count_array_items(media_body, 'news') if media_body else 0

    shorts_count = (
        (count_array_items(media_body, 'shorts') if media_body else 0)
        + (count_array_items(media_body, 'reels') if media_body else 0)
        + (count_array_items(media_body, 'tiktoks') if media_body else 0)
    )

    return {
        'name': name,
        'sport': sport,
        'school': school,
        'bucket': bucket,
        'profile_key': profile_key,
        'media_key': media_key if media_body else None,
        'profile_present': profile_present,
        'profile_depth': profile_depth,
        'eval_grid': eval_grid,
        'awards_count': awards_count,
        'curated_videos': curated_videos,
        'curated_news': curated_news,
        'shorts_reels': shorts_count,
    }


def amazed_score(s: dict) -> int:
    """Composite 0–100 — what fraction of 'amazing' criteria are met."""
    pts = 0
    pts += 10 if s['profile_present'] else 0
    pts += min(s['profile_depth'], 5) * 4        # 0–20
    pts += 5 if s['eval_grid'] else 0
    pts += min(s['awards_count'], 5) * 3          # 0–15
    pts += min(s['curated_videos'], 5) * 4        # 0–20
    pts += min(s['curated_news'], 5) * 4          # 0–20
    pts += min(s['shorts_reels'], 5) * 2          # 0–10
    return pts


# ─────────────────────────────────────────────────────────────────────────
# HTML rendering
# ─────────────────────────────────────────────────────────────────────────

def render_html(scores: list) -> str:
    scores_sorted = sorted(scores, key=lambda s: (amazed_score(s), s['name']))

    # Bucket grouping — amateur first per directive
    AMATEUR_HINT = re.compile(r'(hs|high.school|d1|d2|d3|juco|college|amateur|ncaa|prep)', re.I)
    amateurs = [s for s in scores_sorted if AMATEUR_HINT.search(s['bucket'] or '')]
    pros = [s for s in scores_sorted if not AMATEUR_HINT.search(s['bucket'] or '')]

    def row(s):
        url = (f"{PROD_BASE}/fieldcheck-verdict.html"
               f"?q={s['name'].replace(' ', '+')}&sport={s['sport']}")
        score = amazed_score(s)
        score_class = 'red' if score < 40 else ('amber' if score < 70 else 'green')
        def cell(v, thresh_good, thresh_bad=0):
            v_int = int(v) if v is True or v is False else v
            cls = 'red' if v_int <= thresh_bad else ('green' if v_int >= thresh_good else 'amber')
            return f'<td class="{cls}">{v_int}</td>'
        return (
            f'<tr class="row-{score_class}">'
            f'<td><a href="{html.escape(url)}" target="_blank">{html.escape(s["name"])}</a></td>'
            f'<td>{html.escape(s["sport"])}</td>'
            f'<td>{html.escape(s["bucket"])}</td>'
            f'<td class="score-{score_class}"><b>{score}</b></td>'
            f'{cell(s["profile_present"], 1, 0)}'
            f'{cell(s["profile_depth"], 4, 1)}'
            f'{cell(s["eval_grid"], 1, 0)}'
            f'{cell(s["awards_count"], 4, 1)}'
            f'{cell(s["curated_videos"], 3, 0)}'
            f'{cell(s["curated_news"], 3, 0)}'
            f'{cell(s["shorts_reels"], 2, 0)}'
            f'<td class="key">{html.escape(s["profile_key"] or "—")}</td>'
            f'<td class="key">{html.escape(s["media_key"] or "—")}</td>'
            f'</tr>'
        )

    def section(title, rows):
        return f"""
        <h2>{html.escape(title)} <span class="count">({len(rows)} athletes)</span></h2>
        <table>
          <thead>
            <tr><th>Name</th><th>Sport</th><th>Bucket</th><th>Score</th>
                <th>Prof</th><th>Depth</th><th>Grid</th><th>Awards</th>
                <th>Vids</th><th>News</th><th>Sh/R</th>
                <th>Profile key</th><th>Media key</th></tr>
          </thead>
          <tbody>{''.join(row(s) for s in rows)}</tbody>
        </table>
        """

    total = len(scores)
    avg = sum(amazed_score(s) for s in scores) / max(total, 1)
    have_videos = sum(1 for s in scores if s['curated_videos'] > 0)
    have_shorts = sum(1 for s in scores if s['shorts_reels'] > 0)
    have_profile = sum(1 for s in scores if s['profile_present'])

    summary = f"""
    <div class="summary">
      <div><b>{total}</b> athletes audited</div>
      <div><b>{avg:.1f}/100</b> average amazed score</div>
      <div><b>{have_profile}</b> with a profile</div>
      <div><b>{have_videos}</b> with curated videos</div>
      <div><b>{have_shorts}</b> with shorts/reels <span style="color:#888">(target ≥6)</span></div>
    </div>
    """

    css = """
    body { font: 13px/1.4 -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           margin: 24px; background: #0a0a0a; color: #e0e0e0; }
    h1 { margin: 0 0 6px; }
    h2 { margin: 32px 0 8px; font-size: 18px; }
    .meta { color: #888; font-size: 12px; margin-bottom: 18px; }
    .summary { display: flex; gap: 24px; padding: 14px 16px; background: #161616;
               border: 1px solid #2a2a2a; border-radius: 8px; margin-bottom: 20px; }
    .count { color: #888; font-size: 13px; font-weight: normal; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; }
    th { text-align: left; padding: 8px 6px; border-bottom: 1px solid #333;
         background: #161616; position: sticky; top: 0; }
    td { padding: 6px; border-bottom: 1px solid #1a1a1a; vertical-align: middle; }
    td.key { color: #777; font-family: ui-monospace, monospace; font-size: 10.5px; }
    a { color: #5bb4ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .red    { color: #ff6b6b; }
    .amber  { color: #ffaa3a; }
    .green  { color: #5cdc8a; }
    .score-red    { background: rgba(255,107,107,0.15); }
    .score-amber  { background: rgba(255,170,58,0.10); }
    .score-green  { background: rgba(92,220,138,0.10); }
    """

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>FieldCheck 110 — Amazed Audit</title>
<style>{css}</style></head><body>
<h1>FieldCheck 110 — Amazed Audit</h1>
<div class="meta">Generated {datetime.now().isoformat(timespec='seconds')} · sorted worst→best · click name to open prod page</div>
{summary}
{section('Amateurs (fix first per directive)', amateurs)}
{section('Pros and other buckets', pros)}
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found")
        return 1
    if not ROSTER.exists():
        print(f"ERROR: {ROSTER} not found")
        return 1

    print(f"Reading {WORKER} ({WORKER.stat().st_size:,} bytes)...")
    src = WORKER.read_text()

    print(f"Reading {ROSTER}...")
    roster = json.loads(ROSTER.read_text())

    # roster_100.json has a known shape (confirmed via inspect_roster.py):
    #   { "buckets": [
    #       { "bucket_id": "...", "name": "...", "sport": "...", "athletes": [...] },
    #       ... 11 buckets total ...
    #   ]}
    # Each athlete has a `name` but `sport` only appears for mixed-sport buckets;
    # otherwise inherit from bucket.sport.
    buckets = roster.get('buckets') if isinstance(roster, dict) else None
    if not isinstance(buckets, list):
        print("ERROR: expected r['buckets'] to be a list. Found:", type(buckets).__name__)
        return 1

    athletes = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        bucket_name = bucket.get('name', '(unnamed)')
        bucket_sport = bucket.get('sport', '')
        bucket_id = bucket.get('bucket_id', '')
        for ath in bucket.get('athletes', []) or []:
            if not isinstance(ath, dict) or 'name' not in ath:
                continue
            entry = dict(ath)
            # Inherit sport from bucket if athlete doesn't have one
            if not entry.get('sport'):
                entry['sport'] = bucket_sport
            entry['bucket'] = bucket_name
            entry['bucket_id'] = bucket_id
            athletes.append(entry)

    print(f"Found {len(athletes)} athletes across {len(buckets)} buckets")
    if athletes:
        from collections import Counter
        buckets_dist = Counter(a.get('bucket') or '(none)' for a in athletes)
        print("  bucket distribution:")
        for bk, ct in sorted(buckets_dist.items(), key=lambda x: -x[1]):
            preview = bk if len(bk) <= 70 else bk[:67] + '...'
            print(f"    {ct:3}  {preview}")
        sports_dist = Counter(a.get('sport') or '(none)' for a in athletes)
        print("  sport distribution:")
        for sp, ct in sorted(sports_dist.items(), key=lambda x: -x[1]):
            print(f"    {ct:3}  {sp}")

    print("Parsing PLAYER_PROFILES from worker.js...")
    profiles = extract_block_keys(src, 'PLAYER_PROFILES')
    print(f"  -> {len(profiles)} profiles found")

    print("Parsing CURATED_MEDIA from worker.js...")
    media = extract_block_keys(src, 'CURATED_MEDIA')
    print(f"  -> {len(media)} curated media entries found")

    print("Scoring each athlete...")
    scores = [score_athlete(a, profiles, media) for a in athletes]

    print(f"Writing {OUTPUT}...")
    OUTPUT.write_text(render_html(scores))
    print(f"OK  Open: open {OUTPUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
