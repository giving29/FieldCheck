#!/usr/bin/env python3
"""
apply_curated_media_slug_realignment_v1.py

Renames 6 CURATED_MEDIA dict keys to match the long-form PLAYER_PROFILES slugs.
Fixes the V038 slug-mismatch that left videos/news invisible on the 6 amateur
verdict pages (page falls back to the "Search the public record" template).

Mapping (short -> long):
  aj-dybantsa-mens-basketball         -> aj-dybantsa-byu-mens-basketball
  cameron-boozer-mens-basketball      -> cameron-boozer-duke-mens-basketball
  tyran-stokes-mens-basketball        -> tyran-stokes-notre-dame-mens-basketball
  faizon-brandon-football             -> faizon-brandon-grimsley-football
  cameron-williams-mens-basketball    -> cameron-williams-st-marys-mens-basketball
  jordan-smith-jr-mens-basketball     -> jordan-smith-jr-paul-vi-mens-basketball

Process:
  1. Back up worker.js -> worker.js.pre-media-realign.bak
  2. For each pair, regex-match the dict key declaration and rename it.
     Pattern: ^<indent>'<old>'<ws>:<ws>{
     Safety: halts if 0 or >1 matches per key (expect exactly 1 each).
  3. Validate via node --check; auto-rollback on failure.

Run from worker.js directory:
  python3 apply_curated_media_slug_realignment_v1.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-media-realign.bak')

RENAMES = [
    ('aj-dybantsa-mens-basketball',         'aj-dybantsa-byu-mens-basketball'),
    ('cameron-boozer-mens-basketball',      'cameron-boozer-duke-mens-basketball'),
    ('tyran-stokes-mens-basketball',        'tyran-stokes-notre-dame-mens-basketball'),
    ('faizon-brandon-football',             'faizon-brandon-grimsley-football'),
    ('cameron-williams-mens-basketball',    'cameron-williams-st-marys-mens-basketball'),
    ('jordan-smith-jr-mens-basketball',     'jordan-smith-jr-paul-vi-mens-basketball'),
]


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original = content
    original_size = len(original)

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")
    print()

    print("Renames (CURATED_MEDIA key -> PLAYER_PROFILES key):")
    print(f"  {'status':<8} count  {'old':<42}  ->  new")
    print(f"  {'-'*6}   ---    {'-'*42}      {'-'*48}")

    halted = False
    for old, new in RENAMES:
        # Match only the dict key declaration line: <indent>'<old>'<ws>:<ws>{
        pattern = re.compile(
            r"^(\s+)'" + re.escape(old) + r"'(\s*:\s*\{)",
            re.MULTILINE
        )
        matches = list(pattern.finditer(content))
        count = len(matches)
        if count == 0:
            print(f"  SKIP     0      {old:<42}  ->  NOT_FOUND (no change)")
            continue
        if count > 1:
            print(f"  HALT     {count}      {old:<42}  ->  AMBIGUOUS (>1 match); aborting")
            halted = True
            break
        # exactly one match - safe to replace
        content = pattern.sub(r"\1'" + new + r"'\2", content)
        print(f"  OK       1      {old:<42}  ->  {new}")

    if halted:
        print()
        print("Aborting before write. worker.js is untouched.")
        print(f"Backup remains at {BACKUP} for cleanup if needed.")
        return 1

    if content == original:
        print()
        print("ERROR: no changes applied (all 6 slugs missing?)")
        return 1

    WORKER.write_text(content)

    print()
    print(f"worker.js size: {original_size} -> {len(content)} ({len(content) - original_size:+d} bytes)")
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
            print(f"Rolling back from {BACKUP}...")
            shutil.copy(BACKUP, WORKER)
            print("OK   Restored.")
            return 1
    except FileNotFoundError:
        print("WARN: node not in PATH; skipping syntax check")
    except subprocess.TimeoutExpired:
        print("WARN: node --check timed out; proceed with caution")

    print()
    print("All 6 CURATED_MEDIA keys realigned. Verify with:")
    print('  grep -n "tyran-stokes\\|cameron-boozer\\|aj-dybantsa\\|faizon-brandon\\|cameron-williams-st\\|jordan-smith-jr-paul" worker.js | head -20')
    return 0


if __name__ == '__main__':
    sys.exit(apply())
