#!/usr/bin/env python3
"""
apply_marquee_media_merge_v2.py

Replaces the existing FCBase25 MEDIA MERGE FIX block in worker.js with a
more robust v2 version that:

  1. Tries multiple mediaKey strategies (short form, full slug, name variants)
  2. Falls back to a prefix-scan over CURATED_MEDIA keys if all computed keys miss
  3. Adds a __media_diag field to the response showing exactly what was tried
     and what was found (so we can verify or further diagnose with one curl)

Anchor: the existing FCBase25 marker comment. Failure-safe — restores
worker.js from backup if the anchor isn't found or syntax check fails.

Run from worker.js directory:
  python3 apply_marquee_media_merge_v2.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-marquee-merge-v2.bak')

# Anchor — match from "// FCBase25 · MEDIA MERGE FIX" through the closing
# "} catch (e) { /* silent: media merge is best-effort */ }" line.
OLD_PATTERN = re.compile(
    r'        // FCBase25 [\u00b7] MEDIA MERGE FIX.*?\} catch \(e\) \{ /\* silent: media merge is best-effort \*/ \}\n',
    re.DOTALL
)

# Replacement block — v2 with multi-strategy lookup + diagnostics.
NEW_BLOCK = """        // FCBase25v2 · MEDIA MERGE FIX (robust + diag, 2026-06-06)
        // Replaces v1: now tries multiple mediaKey strategies + falls back
        // to prefix scan, and emits __media_diag for verification.
        try {
          const _diag = {
            cm_type: typeof CURATED_MEDIA,
            cm_keys: 0,
            profile_name: profile ? profile.name : null,
            profile_sport: profile ? profile.sport : null,
            keys_tried: [],
            matched_key: null,
            matched_via: null
          };
          if (typeof CURATED_MEDIA !== 'undefined' && profile) {
            const cmKeys = Object.keys(CURATED_MEDIA);
            _diag.cm_keys = cmKeys.length;
            const slugify = (s) => ((s || '') + '')
              .toLowerCase()
              .replace(/[\\.']/g, '')
              .replace(/[^a-z0-9]+/g, '-')
              .replace(/^-+|-+$/g, '');
            const sportStr = (profile.sport || sportHint || '');
            const candidates = [];
            // Strategy 1: name + sport (short form — current convention)
            if (profile.name) candidates.push(slugify(profile.name) + '-' + sportStr);
            // Strategy 2: full resolved slug (long form)
            if (_resolved) candidates.push(_resolved);
            // Strategy 3: strip school from _resolved → reconstruct short form
            // e.g. 'jordan-smith-jr-paul-vi-mens-basketball' → 'jordan-smith-jr-mens-basketball'
            if (_resolved && sportStr && _resolved.endsWith('-' + sportStr)) {
              const noSport = _resolved.slice(0, -(sportStr.length + 1));
              const parts = noSport.split('-');
              for (let n = 1; n <= Math.min(parts.length, 5); n++) {
                candidates.push(parts.slice(0, n).join('-') + '-' + sportStr);
              }
            }
            // Strategy 4: prefix scan — any CURATED_MEDIA key that starts with
            // slugify(profile.name) + '-'
            if (profile.name) {
              const prefix = slugify(profile.name) + '-';
              for (const k of cmKeys) {
                if (k.indexOf(prefix) === 0) { candidates.push(k); break; }
              }
            }
            _diag.keys_tried = candidates.slice(0, 10);
            let entry = null;
            let matchedKey = null;
            let matchedVia = null;
            for (let i = 0; i < candidates.length; i++) {
              if (CURATED_MEDIA[candidates[i]]) {
                entry = CURATED_MEDIA[candidates[i]];
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
          verdict.__media_diag = _diag;
        } catch (e) {
          verdict.__media_diag = { err: String((e && e.message) || e) };
        }
"""


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original_size = len(content)

    matches = OLD_PATTERN.findall(content)
    if not matches:
        print("ERROR: existing FCBase25 block not found in worker.js")
        print("Cannot replace what isn't there. Aborting.")
        return 1
    if len(matches) > 1:
        print(f"ERROR: FCBase25 block matches {len(matches)} times. Ambiguous.")
        return 1

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = OLD_PATTERN.sub(NEW_BLOCK, content, count=1)
    WORKER.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patched: FCBase25 -> FCBase25v2 with multi-strategy + diag  ({delta:+d} bytes)")
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
    print("Verify:")
    print('  grep -n "FCBase25v2" worker.js')
    return 0


if __name__ == '__main__':
    sys.exit(apply())
