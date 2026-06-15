#!/usr/bin/env python3
"""
apply_frontend_supplement_skipcache_v1.py

FCBase27 · One-line frontend fix: force skipCache=true on the FCBase26
supplement POST so the frontend always gets fresh merged data (including
short_form + socials from PLAYER_PROFILES), bypassing stale KV cache entries
that pre-date the schema change.

Only affects the supplement call (line 4583 in fieldcheck-verdict.html), which
already only fires when the marquee response is missing curated videos —
i.e., on the curated-player path. Performance cost: one un-cached POST per
curated-player page load. Tradeoff: schema changes show up immediately.

Run from fieldcheck-proxy directory:
  python3 apply_frontend_supplement_skipcache_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-skipcache.bak')

OLD = "var rS=await fetch(W+'/verdict/player',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payloadS)});"
NEW = "var rS=await fetch(W+'/verdict/player',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({},payloadS,{skipCache:true}))});"


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found in {Path.cwd()}")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if OLD not in content:
        print("ERROR: Anchor not found. FCBase26 supplement code may have already been modified.")
        return 1
    if content.count(OLD) > 1:
        print(f"ERROR: Anchor appears {content.count(OLD)} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(OLD, NEW, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patch applied  ({delta:+d} bytes)")
    print()
    print("Next:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Then HARD-REFRESH:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Expected: Hot Reels strip (6 cards) above Highlights, Follow chips (IG/TT/X) before public-record fallback.")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
