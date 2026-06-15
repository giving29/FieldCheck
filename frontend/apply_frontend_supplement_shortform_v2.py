#!/usr/bin/env python3
"""
apply_frontend_supplement_shortform_v2.py

FCBase27 · Expands the FCBase26 supplement so it also fires for short_form /
socials, not just missing videos. Two str_replace operations:

  PATCH A — Trigger: fires when videos OR short_form OR socials missing.
            Previously only fired on videos missing, which meant JSJ (who has
            marquee videos via getCuratedVideos fallback) never got short_form
            or socials data through the supplement path.

  PATCH B — Merge: copies short_form[] and socials{} from the supplement
            response into d, alongside the existing videos+news copies, so
            renderVerdict's Hot Reels + Follow blocks can find them.

Run from fieldcheck-proxy directory:
  python3 apply_frontend_supplement_shortform_v2.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-shortform-v2.bak')

# ─── PATCH A: Expand trigger condition ────────────────────────────────────────
TRIGGER_OLD = "if(d&&(!d.encyclopedia||!Array.isArray(d.encyclopedia.videos)||!d.encyclopedia.videos.length)){"
TRIGGER_NEW = "if(d&&(!d.encyclopedia||!Array.isArray(d.encyclopedia.videos)||!d.encyclopedia.videos.length||!Array.isArray(d.short_form)||!d.short_form.length||!d.socials)){"

# ─── PATCH B: Add short_form + socials merge ──────────────────────────────────
MERGE_OLD = """            if(Array.isArray(dS.recent_news_mentions)&&dS.recent_news_mentions.length){
              d.recent_news_mentions=dS.recent_news_mentions;
            }
            dbg.push('media_supplement_ok:vids='+(((d.encyclopedia||{}).videos)||[]).length+' news='+((d.recent_news_mentions)||[]).length);"""

MERGE_NEW = """            if(Array.isArray(dS.recent_news_mentions)&&dS.recent_news_mentions.length){
              d.recent_news_mentions=dS.recent_news_mentions;
            }
            if(Array.isArray(dS.short_form)&&dS.short_form.length){
              d.short_form=dS.short_form;
            }
            if(dS.socials&&typeof dS.socials==='object'){
              d.socials=dS.socials;
            }
            dbg.push('media_supplement_ok:vids='+(((d.encyclopedia||{}).videos)||[]).length+' news='+((d.recent_news_mentions)||[]).length+' sf='+((d.short_form)||[]).length+' soc='+(d.socials?'1':'0'));"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found in {Path.cwd()}")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    # Validate both anchors atomically
    if TRIGGER_OLD not in content:
        print("ERROR: Patch A trigger anchor not found.")
        return 1
    if content.count(TRIGGER_OLD) > 1:
        print(f"ERROR: Patch A anchor appears {content.count(TRIGGER_OLD)} times. Ambiguous.")
        return 1
    if MERGE_OLD not in content:
        print("ERROR: Patch B merge anchor not found.")
        return 1
    if content.count(MERGE_OLD) > 1:
        print(f"ERROR: Patch B anchor appears {content.count(MERGE_OLD)} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(TRIGGER_OLD, TRIGGER_NEW, 1)
    new_content = new_content.replace(MERGE_OLD, MERGE_NEW, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patches A+B applied  ({delta:+d} bytes)")
    print()
    print("Next:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Then HARD-REFRESH (Cmd+Shift+R):")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Expected: Hot Reels strip (6 cards) above Highlights, Follow chips (IG/TT/X) before public-record fallback.")
    print("Devtools console will show: media_supplement_ok:vids=4 news=4 sf=6 soc=1")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
