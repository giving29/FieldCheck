#!/usr/bin/env python3
"""
apply_attach_evidence_media_merge_v1.py

THE REAL FIX. Patches `attachEvidenceLayer` (line 8172) — which is in the
same module/scope as `const CURATED_MEDIA` (line 9612) and therefore CAN
see it. Every marquee response and every POST verdict passes through this
function. Adding the merge here fixes both paths in one place.

The patch is purely additive: ~38 lines inserted right after the function's
opening brace. Includes idempotency check (skips if already merged).

Anchor: the exact function signature `async function attachEvidenceLayer(verdictResult, env = null) {`
which appears exactly once in worker.js (per Sridhar's earlier grep).

Run from worker.js directory:
  python3 apply_attach_evidence_media_merge_v1.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-attach-merge.bak')

OLD = "async function attachEvidenceLayer(verdictResult, env = null) {\n"

NEW = """async function attachEvidenceLayer(verdictResult, env = null) {
  // FCBase26 · CURATED_MEDIA merge at the evidence layer (2026-06-06)
  // The marquee handler scope can't see CURATED_MEDIA directly, but THIS function
  // is in the same module/scope as the const declaration. Every marquee + POST
  // verdict passes through here, so merging once here fixes both paths.
  // Idempotent — skips if a prior merge (POST /verdict/player) already happened.
  try {
    if (verdictResult && typeof CURATED_MEDIA !== 'undefined') {
      const _alreadyHasVideos = verdictResult.encyclopedia
        && Array.isArray(verdictResult.encyclopedia.videos)
        && verdictResult.encyclopedia.videos.length > 0;
      if (!_alreadyHasVideos) {
        const _name = verdictResult.name || '';
        const _sport = verdictResult.sport || verdictResult.sport_label || '';
        if (_name && _sport) {
          const _mediaKey = (_name + '').toLowerCase()
            .replace(/[\\.']/g, '')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            + '-' + _sport;
          const _entry = CURATED_MEDIA[_mediaKey];
          if (_entry) {
            verdictResult.encyclopedia = verdictResult.encyclopedia || {};
            if (Array.isArray(_entry.videos) && _entry.videos.length) {
              verdictResult.encyclopedia.videos = _entry.videos.map(function(v) {
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
            if (Array.isArray(_entry.news) && _entry.news.length) {
              verdictResult.recent_news_mentions = _entry.news.map(function(n) {
                return {
                  headline: n.headline || n.title || '',
                  source_label: n.source || n.publisher || 'FieldCheck curated',
                  captured_at: n.date || n.captured_at || null,
                  url: n.url || null,
                  curated: true
                };
              });
            }
            verdictResult.curated_merge_applied = true;
            verdictResult.curated_lookup_succeeded = true;
            verdictResult.curated_lookup_slug = _mediaKey;
            if (!verdictResult.last_verified) verdictResult.last_verified = '2026-05-10';
          }
        }
      }
    }
  } catch (_e) { /* silent: never break attachEvidenceLayer */ }

"""


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original_size = len(content)

    count = content.count(OLD)
    if count == 0:
        print(f"ERROR: anchor not found: {OLD!r}")
        return 1
    if count > 1:
        print(f"ERROR: anchor appears {count} times. Ambiguous.")
        return 1

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(OLD, NEW, 1)
    WORKER.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Inserted CURATED_MEDIA merge at attachEvidenceLayer entry  ({delta:+d} bytes)")
    print()

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
    print("Next: ./fc-deploy-dev.sh")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
