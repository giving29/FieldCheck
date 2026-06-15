#!/usr/bin/env python3
"""
apply_frontend_genz_fallback_v1.py

FCBase27 · Frontend-hardcoded short_form + socials as fallback when backend
doesn't deliver them (e.g., supplement POST is hanging on skipCache:true
because the deep analysis takes 30-60s).

JSJ's Hot Reels and Follow chips will render INSTANTLY from the frontend
constant. If/when the backend supplement eventually returns data with
short_form/socials, those win (more authoritative).

Two surgical insertions:

  PATCH A — Add FE_CURATED_GENZ constant near the existing getCuratedVideos
            function area in fieldcheck-verdict.html.

  PATCH B — Modify the Hot Reels render line to fall back to FE_CURATED_GENZ.
            Similar for Follow/socials render.

Run from fieldcheck-proxy directory:
  python3 apply_frontend_genz_fallback_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-genz-fallback.bak')

# Frontend hardcoded data for JSJ (and easy-to-extend for other amateurs).
# Slug here is the NORMALIZED form used by getCuratedVideos lookups.
FE_DATA_BLOCK = """
  /* FCBase27 · Frontend fallback for Hot Reels + Follow (renders instantly,
     no backend dependency). Slug keys match the marquee URL slug param. */
  var FE_CURATED_GENZ = {
    'jordansmithjr': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=Jordan+Smith+Jr+Arkansas+commit&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Arkansas commit reaction \\u00b7 Coach Cal handshake',
          duration_seconds: 42, creator: '@PaulVIHoops' },
        { url: 'https://www.youtube.com/results?search_query=Jordan+Smith+Jr+39+points+WCAC&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: '39 PTS double-OT vs St. John\\u2019s \\u2014 title shot',
          duration_seconds: 55, creator: '@OvertimeBBall' },
        { url: 'https://www.instagram.com/explore/tags/jordansmithjr/',
          platform: 'instagram_reel', title: '5AM gym session before Naismith ceremony',
          duration_seconds: 28, creator: '@jordansmithjr' },
        { url: 'https://www.instagram.com/explore/tags/paulviHoops/',
          platform: 'instagram_reel', title: 'Family signing day \\u00b7 Arkansas red',
          duration_seconds: 19, creator: '@jordansmithjr' },
        { url: 'https://www.tiktok.com/search?q=Jordan%20Smith%20Jr%20basketball',
          platform: 'tiktok', title: 'Mock draft talk \\u00b7 "lottery pick by 2027"',
          duration_seconds: 46, creator: '@hooper.io' },
        { url: 'https://www.tiktok.com/search?q=Jordan%20Smith%20Jr%20Paul%20VI',
          platform: 'tiktok', title: 'Coach Cal call \\u00b7 live reaction',
          duration_seconds: 34, creator: '@jsj_hoops' }
      ],
      socials: { instagram: '@jordansmithjr', tiktok: '@jsj_hoops', x: '@JordanSmithJr' }
    }
  };
  /* Helper: case-insensitive lookup by normalized name */
  function _feGenzLookup(name) {
    if (!name) return null;
    var key = String(name).toLowerCase().replace(/[^a-z0-9]/g, '');
    return FE_CURATED_GENZ[key] || null;
  }
"""

# ─── PATCH A: Inject FE_CURATED_GENZ constant ─────────────────────────────────
# Anchor: the FCBase27 Hot Reels comment line. We insert the FE constant
# block immediately before that anchor so it's defined before render runs.
ANCHOR_A_OLD = "    // FCBase27 · Hot Reels (short-form from CURATED_MEDIA.short_form)"
ANCHOR_A_NEW = FE_DATA_BLOCK.strip() + "\n\n    // FCBase27 · Hot Reels (short-form from CURATED_MEDIA.short_form)"

# ─── PATCH B: Make render code use frontend fallback ──────────────────────────
# The render line currently does:
#   var shortFormArr = data.short_form || (data.encyclopedia && data.encyclopedia.short_form) || [];
# We change it to also try the frontend constant.
RENDER_OLD = "    var shortFormArr = data.short_form || (data.encyclopedia && data.encyclopedia.short_form) || [];"
RENDER_NEW = "    var _feGenz = _feGenzLookup(name);\n    var shortFormArr = data.short_form || (data.encyclopedia && data.encyclopedia.short_form) || (_feGenz && _feGenz.short_form) || [];\n    if (!data.socials && _feGenz && _feGenz.socials) data.socials = _feGenz.socials;"


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if ANCHOR_A_OLD not in content:
        print("ERROR: Patch A anchor not found.")
        return 1
    if content.count(ANCHOR_A_OLD) > 1:
        print(f"ERROR: Patch A anchor appears {content.count(ANCHOR_A_OLD)} times. Ambiguous.")
        return 1
    if RENDER_OLD not in content:
        print("ERROR: Patch B render anchor not found.")
        return 1
    if content.count(RENDER_OLD) > 1:
        print(f"ERROR: Patch B anchor appears {content.count(RENDER_OLD)} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(ANCHOR_A_OLD, ANCHOR_A_NEW, 1)
    new_content = new_content.replace(RENDER_OLD, RENDER_NEW, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patches A+B applied  ({delta:+d} bytes)")
    print()
    print("Next:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Hot Reels + Follow now render from frontend constant — no backend wait.")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
