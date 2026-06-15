#!/usr/bin/env python3
"""
apply_curated_media_global_v1.py

ROOT CAUSE FIX. v3 diag confirmed CURATED_MEDIA is not visible in the marquee
handler scope (cm_via_direct='null', cm_via_global='absent', cm_keys_count=0).

Adds ONE STATEMENT right after the const declaration to expose CURATED_MEDIA
on globalThis. The existing v3 patch in the marquee handler has a globalThis
fallback that will then pick it up automatically.

Total worker.js change: ~3 lines added near line 9987.

Run from worker.js directory:
  python3 apply_curated_media_global_v1.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-curated-global.bak')

# Anchor: the closing `};` of `const CURATED_MEDIA = {` (at line ~9987) followed by
# a blank line and the unique "v0.24: merge player-uploaded videos" comment.
# This sequence is unique because of the comment text.

OLD = """};

    // v0.24: merge player-uploaded videos (from /social/video) into the videos list."""

NEW = """};

// FCBase26 · expose CURATED_MEDIA on globalThis (2026-06-06)
// Root cause: the marquee handler (~line 37149) is in a scope that can't see
// the module-scope `const CURATED_MEDIA` directly (v3 diag confirmed
// cm_via_direct: 'null'). Setting it on globalThis here makes it reachable
// from any handler in the worker.
if (typeof globalThis !== 'undefined') { globalThis.CURATED_MEDIA = CURATED_MEDIA; }

    // v0.24: merge player-uploaded videos (from /social/video) into the videos list."""


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original_size = len(content)

    count = content.count(OLD)
    if count == 0:
        print("ERROR: anchor not found in worker.js")
        print("Expected sequence: '};' + blank line + '    // v0.24: merge player-uploaded videos...'")
        return 1
    if count > 1:
        print(f"ERROR: anchor appears {count} times. Ambiguous. Aborting.")
        return 1

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(OLD, NEW, 1)
    WORKER.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Added globalThis.CURATED_MEDIA assignment  ({delta:+d} bytes)")
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
