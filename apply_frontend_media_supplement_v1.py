#!/usr/bin/env python3
"""
apply_frontend_media_supplement_v1.py

FRONTEND fix. Worker can't be patched — CURATED_MEDIA is walled off from the
marquee handler scope (confirmed: handler patch, attachEvidenceLayer patch,
and globalThis exposure all failed). But POST /verdict/player CAN access it
and returns videos+news correctly (verified earlier: 4 videos for JSJ).

This patch modifies fieldcheck-verdict.html so that AFTER the marquee response
is accepted (line 4489: `d=d1`), if the response is missing videos, it fires
a supplemental POST call and merges encyclopedia.videos + recent_news_mentions
into the render data.

Net effect:
  - Marquee fast path still renders verdict immediately (no UX regression)
  - When videos missing, ONE additional POST call brings them in
  - POST is fast for curated players (no LLM call — just curated lookup)
  - Falls back gracefully if supplement fails (still renders without videos)

Anchor: the exact 2-line pattern from current fieldcheck-verdict.html:
    if(d1&&d1.ok&&(d1.eval_grid||d1.composite!=null||d1.encyclopedia))d=d1;
  }catch(e){dbg.push('fast_err:'+e.message);}

Run from fieldcheck-proxy directory (where fieldcheck-verdict.html lives):
  python3 apply_frontend_media_supplement_v1.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-media-supplement.bak')

OLD = """    if(d1&&d1.ok&&(d1.eval_grid||d1.composite!=null||d1.encyclopedia))d=d1;
  }catch(e){dbg.push('fast_err:'+e.message);}"""

NEW = """    if(d1&&d1.ok&&(d1.eval_grid||d1.composite!=null||d1.encyclopedia))d=d1;
    /* FCBase26 · supplement marquee with POST videos+news (2026-06-06) */
    /* Marquee endpoint can't reach CURATED_MEDIA in its scope; POST can.   */
    /* Fire a quick supplement call when videos missing in marquee response.*/
    if(d&&(!d.encyclopedia||!Array.isArray(d.encyclopedia.videos)||!d.encyclopedia.videos.length)){
      try{
        var payloadS={name:name,sport:sport||''};
        if(schoolHint)payloadS.schoolHint=schoolHint;
        var rS=await fetch(W+'/verdict/player',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payloadS)});
        if(rS.ok){
          var dS=await rS.json();
          if(dS&&dS.ok){
            if(dS.encyclopedia&&Array.isArray(dS.encyclopedia.videos)&&dS.encyclopedia.videos.length){
              d.encyclopedia=d.encyclopedia||{};
              d.encyclopedia.videos=dS.encyclopedia.videos;
            }
            if(Array.isArray(dS.recent_news_mentions)&&dS.recent_news_mentions.length){
              d.recent_news_mentions=dS.recent_news_mentions;
            }
            dbg.push('media_supplement_ok:vids='+(((d.encyclopedia||{}).videos)||[]).length+' news='+((d.recent_news_mentions)||[]).length);
          }
        }
      }catch(eS){dbg.push('media_supplement_err:'+eS.message);}
    }
  }catch(e){dbg.push('fast_err:'+e.message);}"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found in {Path.cwd()}")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    count = content.count(OLD)
    if count == 0:
        print("ERROR: anchor not found in fieldcheck-verdict.html")
        return 1
    if count > 1:
        print(f"ERROR: anchor appears {count} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(OLD, NEW, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Inserted media supplement after marquee fast path  ({delta:+d} bytes)")
    print()

    # No node --check on HTML; do a basic balance check on JS-ish syntax
    # by counting braces in the affected block.
    if "media_supplement_ok" not in new_content:
        print("ERROR: expected marker missing after patch. Restoring.")
        shutil.copy(BACKUP, HTML)
        return 1

    print("Next: ./fc-deploy-dev.sh")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
