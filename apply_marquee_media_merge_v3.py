#!/usr/bin/env python3
"""
apply_marquee_media_merge_v3.py

Replaces the FCBase25v2 (or v1) MEDIA MERGE block with v3 — a defensive
version that:

  1. Doesn't trust `typeof CURATED_MEDIA` — uses try/catch on direct access
     AND a globalThis fallback.
  2. Doesn't trust `profile.name` — also tries the URL slug as a key.
  3. Tries 5+ key strategies, including iterating CURATED_MEDIA keys and
     matching against slug substring.
  4. Emits a verbose __media_diag field showing exactly what was reached,
     what was tried, and what was found.

Run from worker.js directory:
  python3 apply_marquee_media_merge_v3.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-marquee-merge-v3.bak')

# Anchor — match either v1 (single-line catch) or v2 (multi-line catch) block.
# Pattern: from the "// FCBase25" comment through the FINAL closing `}` of the
# catch block and the blank line before the return statement.
# Use a lookahead so the return stays intact.
OLD_PATTERN = re.compile(
    r'        // FCBase25[a-z0-9]* [\u00b7] MEDIA MERGE FIX.*?\}\n\n(?=        return json\(\{ ok: true, \.\.\.verdict)',
    re.DOTALL
)

NEW_BLOCK = """        // FCBase25v3 · MEDIA MERGE FIX (defensive + verbose diag, 2026-06-06)
        const _diag = {
          step: 'enter',
          urlSlug: typeof slug === 'string' ? slug : null,
          resolved: typeof _resolved === 'string' ? _resolved : null,
          profile_present: !!profile,
          profile_name: (profile && typeof profile.name === 'string') ? profile.name : null,
          profile_sport: (profile && typeof profile.sport === 'string') ? profile.sport : null,
          cm_via_direct: null,
          cm_via_global: null,
          cm_keys_count: 0,
          cm_keys_sample: [],
          candidates: [],
          matched_key: null,
          matched_via: null,
          err: null
        };
        try {
          // Try multiple ways to access CURATED_MEDIA
          let CM = null;
          try {
            // eslint-disable-next-line no-undef
            CM = (typeof CURATED_MEDIA !== 'undefined') ? CURATED_MEDIA : null;
            _diag.cm_via_direct = CM ? typeof CM : 'null';
          } catch (e1) {
            _diag.cm_via_direct = 'threw:' + String((e1 && e1.message) || e1).slice(0, 60);
          }
          if (!CM) {
            try {
              if (typeof globalThis !== 'undefined' && globalThis.CURATED_MEDIA) {
                CM = globalThis.CURATED_MEDIA;
                _diag.cm_via_global = typeof CM;
              } else {
                _diag.cm_via_global = 'absent';
              }
            } catch (e2) {
              _diag.cm_via_global = 'threw:' + String((e2 && e2.message) || e2).slice(0, 60);
            }
          }

          if (CM && typeof CM === 'object') {
            const cmKeys = Object.keys(CM);
            _diag.cm_keys_count = cmKeys.length;
            _diag.cm_keys_sample = cmKeys.slice(0, 8);

            const slugify = (s) => ((s || '') + '')
              .toLowerCase()
              .replace(/[\\.']/g, '')
              .replace(/[^a-z0-9]+/g, '-')
              .replace(/^-+|-+$/g, '');

            const sportStr = (_diag.profile_sport || sportHint || '');
            const nameStr = _diag.profile_name || '';
            const urlSlugStr = _diag.urlSlug || '';
            const resolvedStr = _diag.resolved || urlSlugStr;

            const candidates = [];
            const tryAdd = (k) => {
              if (k && typeof k === 'string' && candidates.indexOf(k) === -1) candidates.push(k);
            };

            // Strategy 1: slugify(profile.name) + '-' + sport
            if (nameStr && sportStr) tryAdd(slugify(nameStr) + '-' + sportStr);
            // Strategy 2: full resolved slug (long form, e.g. 'jordan-smith-jr-paul-vi-mens-basketball')
            tryAdd(resolvedStr);
            // Strategy 3: URL slug raw
            tryAdd(urlSlugStr);
            // Strategy 4: strip school from resolved — try every prefix-of-name + sport
            if (resolvedStr && sportStr && resolvedStr.endsWith('-' + sportStr)) {
              const noSport = resolvedStr.slice(0, -(sportStr.length + 1));
              const parts = noSport.split('-');
              for (let n = parts.length; n >= 1; n--) {
                tryAdd(parts.slice(0, n).join('-') + '-' + sportStr);
              }
            }
            // Strategy 5: iterate ALL CURATED_MEDIA keys, find any that the resolved
            // slug contains (as a substring, ignoring sport suffix)
            for (const k of cmKeys) {
              const sportSuffix = '-' + sportStr;
              const kBase = sportStr && k.endsWith(sportSuffix) ? k.slice(0, -sportSuffix.length) : k;
              if (kBase && resolvedStr && resolvedStr.indexOf(kBase) !== -1) {
                tryAdd(k);
              }
              if (kBase && urlSlugStr && urlSlugStr.indexOf(kBase) !== -1) {
                tryAdd(k);
              }
            }

            _diag.candidates = candidates.slice(0, 12);

            // Find first match
            let entry = null;
            let matchedKey = null;
            let matchedVia = null;
            for (let i = 0; i < candidates.length; i++) {
              if (CM[candidates[i]]) {
                entry = CM[candidates[i]];
                matchedKey = candidates[i];
                matchedVia = 'strategy_' + (i + 1);
                break;
              }
            }
            _diag.matched_key = matchedKey;
            _diag.matched_via = matchedVia;

            if (entry) {
              verdict.encyclopedia = verdict.encyclopedia || {};
              if (Array.isArray(entry.videos) && entry.videos.length) {
                verdict.encyclopedia.videos = entry.videos.map(function(v) {
                  return {
                    url: v.url,
                    title: v.title || 'Highlight',
                    season: v.season || null,
                    source: v.source || 'Curated',
                    thumbnail: v.thumbnail || null,
                    duration_seconds: v.duration_seconds || null,
                    curated: true
                  };
                });
              }
              if (Array.isArray(entry.news) && entry.news.length) {
                verdict.recent_news_mentions = entry.news.map(function(n) {
                  return {
                    headline: n.headline || n.title || '',
                    source_label: n.source || n.publisher || 'FieldCheck curated',
                    captured_at: n.date || n.captured_at || null,
                    url: n.url || null,
                    curated: true
                  };
                });
              }
              verdict.curated_merge_applied = true;
              verdict.curated_lookup_succeeded = true;
              verdict.curated_lookup_slug = matchedKey;
              verdict.curated_profile_slug = matchedKey;
              if (!verdict.last_verified) verdict.last_verified = '2026-05-10';
              _diag.step = 'merged';
            } else {
              _diag.step = 'no_match';
            }
          } else {
            _diag.step = 'cm_unavailable';
          }
        } catch (e) {
          _diag.err = String((e && e.message) || e).slice(0, 200);
          _diag.step = 'caught_error';
        }
        verdict.__media_diag = _diag;

"""


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original_size = len(content)

    matches = OLD_PATTERN.findall(content)
    if not matches:
        print("ERROR: existing FCBase25/v2 block not found in worker.js")
        print("Cannot replace what isn't there. Aborting.")
        return 1
    if len(matches) > 1:
        print(f"ERROR: existing block matches {len(matches)} times. Ambiguous.")
        return 1

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = OLD_PATTERN.sub(NEW_BLOCK, content, count=1)
    WORKER.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patched: previous block -> FCBase25v3 (defensive)  ({delta:+d} bytes)")
    print()

    # Validate
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

    print()
    print("Next:")
    print("  ./fc-deploy-dev.sh")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
