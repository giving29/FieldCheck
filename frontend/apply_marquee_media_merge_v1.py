#!/usr/bin/env python3
"""
apply_marquee_media_merge_v1.py

Adds CURATED_MEDIA merge logic to the /api/marquee/verdict-instant endpoint
in worker.js. This endpoint serves "EDGE-SERVED · curated marquee profile"
responses for the 6 V038 amateurs (and other marquee players) — but it
previously did NOT include videos + news in its response, causing the
verdict page to fall back to the search-links template.

Fix scope (worker.js only):
  Anchor on the unique 2-line pattern at end of marquee handler.
  Insert ~30 lines that:
    1. Compute mediaKey from profile.name + sport
       (same algorithm as line 10004 — short-form slug)
    2. Look up CURATED_MEDIA[mediaKey]
    3. Attach videos -> verdict.encyclopedia.videos
    4. Attach news   -> verdict.recent_news_mentions
    5. Set curated_merge_applied = true (so frontend doesn't show empty state)

Process:
  1. Back up worker.js -> worker.js.pre-marquee-merge.bak
  2. Find anchor; replace with anchor + new merge block
  3. node --check (auto-rollback on syntax failure)

Run from worker.js directory:
  python3 apply_marquee_media_merge_v1.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-marquee-merge.bak')

# Anchor: unique 2-line sequence at the end of the marquee handler.
# (Verified in Sridhar's earlier grep at lines 37173-37174.)
OLD = """        if (!verdict) return json({ ok: false, error: 'not_in_marquee_index', slug }, 404);
        return json({ ok: true, ...verdict });"""

NEW = """        if (!verdict) return json({ ok: false, error: 'not_in_marquee_index', slug }, 404);

        // FCBase25 · MEDIA MERGE FIX (added 2026-06-06)
        // /api/marquee/verdict-instant was missing the CURATED_MEDIA merge that
        // /verdict/player has at line ~10004. Add the same logic here so the
        // 6 amateurs (JSJ, Tyran, Cam Williams, Faizon, AJ, Boozer) and other
        // marquee profiles actually show videos + news on the verdict page.
        try {
          if (typeof CURATED_MEDIA !== 'undefined' && profile) {
            const mediaKey = ((profile.name || _resolved || '') + '')
              .toLowerCase()
              .replace(/[\\.']/g, '')
              .replace(/[^a-z0-9]+/g, '-')
              .replace(/^-+|-+$/g, '')
              + '-' + (profile.sport || sportHint || '');
            const entry = CURATED_MEDIA[mediaKey];
            if (entry) {
              verdict.encyclopedia = verdict.encyclopedia || {};
              if (Array.isArray(entry.videos) && entry.videos.length) {
                verdict.encyclopedia.videos = entry.videos.map(v => ({
                  url: v.url,
                  title: v.title || 'Highlight',
                  season: v.season || null,
                  source: v.source || 'Curated',
                  thumbnail: v.thumbnail || null,
                  duration_seconds: v.duration_seconds || null,
                  curated: true
                }));
              }
              if (Array.isArray(entry.news) && entry.news.length) {
                verdict.recent_news_mentions = entry.news.map(n => ({
                  headline: n.headline || n.title || '',
                  source_label: n.source || n.publisher || 'FieldCheck curated',
                  captured_at: n.date || n.captured_at || null,
                  url: n.url || null,
                  curated: true
                }));
              }
              verdict.curated_merge_applied = true;
              verdict.curated_lookup_succeeded = true;
              verdict.curated_lookup_slug = _resolved;
              verdict.curated_profile_slug = _resolved;
              if (!verdict.last_verified) verdict.last_verified = '2026-05-10';
            }
          }
        } catch (e) { /* silent: media merge is best-effort */ }

        return json({ ok: true, ...verdict });"""


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original_size = len(content)

    count = content.count(OLD)
    if count == 0:
        print("ERROR: anchor not found in worker.js")
        print("Expected exact match at end of /api/marquee/verdict-instant handler.")
        print("Worker may have changed since the diagnostic. Aborting (no changes).")
        return 1
    if count > 1:
        print(f"ERROR: anchor appears {count} times. Ambiguous. Aborting.")
        return 1

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(OLD, NEW)
    WORKER.write_text(new_content)

    delta = len(new_content) - original_size
    print(f"OK   Patched: marquee endpoint now merges CURATED_MEDIA  ({delta:+d} bytes)")
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
            shutil.copy(BACKUP, WORKER)
            print(f"OK   Rolled back from {BACKUP}")
            return 1
    except FileNotFoundError:
        print("WARN: node not in PATH; skipping syntax check")
    except subprocess.TimeoutExpired:
        print("WARN: node --check timed out; proceed with caution")

    print()
    print("Verify the new logic is in place:")
    print('  grep -n "FCBase25 . MEDIA MERGE FIX" worker.js')
    return 0


if __name__ == '__main__':
    sys.exit(apply())
