#!/usr/bin/env python3
"""
inspect_roster.py — print the structure of roster_100.json so we can write
a bullet-proof athlete extractor in v3 of the audit.

Run:
  python3 inspect_roster.py
"""

import json
import sys
from pathlib import Path

ROSTER = Path('roster_100.json')

def main():
    if not ROSTER.exists():
        print(f"ERROR: {ROSTER} not found")
        return 1

    r = json.loads(ROSTER.read_text())
    print(f"TOP-LEVEL TYPE: {type(r).__name__}")
    if isinstance(r, dict):
        print(f"TOP-LEVEL KEYS: {list(r.keys())[:10]}")
    elif isinstance(r, list):
        print(f"TOP-LEVEL: list of {len(r)}")

    # Find the container of buckets
    if isinstance(r, dict) and 'buckets' in r:
        container = r['buckets']
        path = "r['buckets']"
    elif isinstance(r, list):
        container = r
        path = "r"
    elif isinstance(r, dict):
        container = list(r.values())
        path = "list(r.values())"
    else:
        print("Unknown structure")
        return 1

    print(f"\nBUCKET CONTAINER ({path}): {type(container).__name__} of {len(container)}")
    print("=" * 80)

    for i, b in enumerate(container):
        if not isinstance(b, dict):
            print(f"\n[{i}] type={type(b).__name__} value={str(b)[:80]}")
            continue
        name = b.get('name', '(no name)')
        if len(name) > 60:
            name = name[:57] + '...'
        keys = list(b.keys())
        print(f"\n[{i}] {name}")
        print(f"     all keys: {keys}")
        # Find list-shaped children
        for k, v in b.items():
            if isinstance(v, list):
                first = v[0] if v else None
                if isinstance(first, dict):
                    sample_keys = list(first.keys())
                    print(f"     -> {k!r}: list of {len(v)}, item keys: {sample_keys}")
                    # Print one full sample item
                    print(f"        sample[0]: {json.dumps(first, default=str)[:200]}")
                else:
                    print(f"     -> {k!r}: list of {len(v)}, items are {type(first).__name__ if first else 'empty'}")
            elif isinstance(v, dict):
                print(f"     -> {k!r}: dict with keys {list(v.keys())[:6]}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
