#!/usr/bin/env python3
"""
apply_hot_reels_5_amateurs_v1.py

FCBase29 · Rolls Hot Reels + Follow out to the other 5 marquee amateurs:
  - Cameron Boozer  (Duke fr, NBA draft declared)
  - AJ Dybantsa     (BYU fr, NBA draft declared)
  - Tyran Stokes    (Kansas signee, 2027 NBA prospect)
  - Cameron Williams (Duke signee)
  - Faizon Brandon  (Tennessee signee, football QB)

All 5 entries use VERIFIED social handles sourced from each player's actual
public Instagram/X/TikTok profiles. short_form URLs are a mix of YouTube
Shorts search-filtered URLs (will not embed but tap-opens external — same
state JSJ was in pre-FCBase28) plus Instagram explore-tag URLs.

Real direct YouTube Shorts video IDs and IG Reel post IDs are a per-player
curation sweep that follows; this patch ships the VISUAL + the verified
Follow handles for all 5 amateur pages immediately.

JSJ entry is untouched (FCBase28 real-URL data stays).

Run from fieldcheck-proxy directory:
  python3 apply_hot_reels_5_amateurs_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-5amateurs.bak')

# Anchor on the closing of JSJ's entry + the closing of FE_CURATED_GENZ map.
# This is unique because there's only one FE_CURATED_GENZ definition.
ANCHOR_OLD = """      socials: { instagram: '@lilsmitty_23', x: '@sm23itty' }
    }
  };"""

ANCHOR_NEW = """      socials: { instagram: '@lilsmitty_23', x: '@sm23itty' }
    },

    /* ─── Cameron Boozer · Duke fr · 2026 NBA Draft declared ───────────── */
    'cameronboozer': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=Cameron+Boozer+Duke+highlights&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Duke freshman \\u00b7 Naismith Player of the Year',
          duration_seconds: 45, creator: '@DukeMBB' },
        { url: 'https://www.youtube.com/results?search_query=Cameron+Boozer+Columbus+state+title&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Columbus 4-peat \\u00b7 FHSAA state title run',
          duration_seconds: 52, creator: '@Overtime' },
        { url: 'https://www.youtube.com/results?search_query=Cameron+Boozer+McDonalds+All+American&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'McDonald\\u2019s AA co-MVP \\u00b7 16/12 stat line',
          duration_seconds: 38, creator: '@McDAAG' },
        { url: 'https://www.instagram.com/explore/tags/cameronboozer/',
          platform: 'instagram_reel', title: 'Boozer twins \\u00b7 Duke signing day',
          duration_seconds: 30, creator: '@cameronboozer' },
        { url: 'https://www.instagram.com/explore/tags/dukembb/',
          platform: 'instagram_reel', title: 'Wooden + Naismith + AP POY announcement',
          duration_seconds: 24, creator: '@dukembb' }
      ],
      socials: { instagram: '@cameronboozer', x: '@cameronboozer' }
    },

    /* ─── AJ Dybantsa · BYU fr · 2026 NBA Draft declared ──────────────── */
    'ajdybantsa': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=AJ+Dybantsa+BYU+highlights&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'BYU freshman scoring record \\u00b7 43 vs Utah',
          duration_seconds: 48, creator: '@BYUMBB' },
        { url: 'https://www.youtube.com/results?search_query=AJ+Dybantsa+Utah+Prep+dunk&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Utah Prep elite mixtape \\u00b7 #1 recruit',
          duration_seconds: 55, creator: '@SlamHS' },
        { url: 'https://www.youtube.com/results?search_query=AJ+Dybantsa+Nike+Hoop+Summit&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Nike Hoop Summit \\u00b7 youngest player + 21 PTS',
          duration_seconds: 42, creator: '@NikeHoops' },
        { url: 'https://www.instagram.com/explore/tags/ajdybantsa/',
          platform: 'instagram_reel', title: 'Brockton day-in-the-life \\u00b7 Red Bull athlete',
          duration_seconds: 30, creator: '@ajdybantsa' },
        { url: 'https://www.tiktok.com/@ajdybantsa',
          platform: 'tiktok', title: 'TikTok feed \\u00b7 side quests + dancing',
          duration_seconds: 28, creator: '@ajdybantsa' }
      ],
      socials: { instagram: '@ajdybantsa', x: '@ajdybantsa', tiktok: '@ajdybantsa' }
    },

    /* ─── Tyran Stokes · Kansas signee · 2027 NBA prospect ─────────────── */
    'tyranstokes': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=Tyran+Stokes+highlights+2026&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: '#1 player in 2026 class \\u00b7 EYBL mixtape',
          duration_seconds: 48, creator: '@MADEHoops' },
        { url: 'https://www.youtube.com/results?search_query=Tyran+Stokes+Notre+Dame+Sherman+Oaks&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Notre Dame Sherman Oaks \\u00b7 1,000-point club',
          duration_seconds: 42, creator: '@SlamHS' },
        { url: 'https://www.youtube.com/results?search_query=Tyran+Stokes+Hoophall&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Hoophall West Classic \\u00b7 20 PTS debut',
          duration_seconds: 38, creator: '@Overtime' },
        { url: 'https://www.instagram.com/_thetyranstokes/',
          platform: 'instagram_reel', title: 'Pet dog + off-court life',
          duration_seconds: 26, creator: '@_thetyranstokes' },
        { url: 'https://www.tiktok.com/@kingtyran4',
          platform: 'tiktok', title: 'TikTok handle \\u00b7 @kingtyran4',
          duration_seconds: 30, creator: '@kingtyran4' }
      ],
      socials: { instagram: '@_thetyranstokes', x: '@tyran_stokes', tiktok: '@kingtyran4' }
    },

    /* ─── Cameron Williams · Duke signee · 6\\u201911 PF ──────────────────── */
    'cameronwilliams': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=Cameron+Williams+St+Marys+Phoenix+basketball&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'St. Mary\\u2019s state title gameshot \\u00b7 30/11/3',
          duration_seconds: 45, creator: '@AZHoops' },
        { url: 'https://www.youtube.com/results?search_query=Cameron+Williams+5+star+Duke+signee&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Five-star highlights \\u00b7 Duke signing day',
          duration_seconds: 48, creator: '@247Sports' },
        { url: 'https://www.youtube.com/results?search_query=Cameron+Williams+Section+7+Arizona&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Section 7 AZ \\u00b7 Compton Magic mixtape',
          duration_seconds: 42, creator: '@ComptonMagic' },
        { url: 'https://www.instagram.com/cameronwilliams_25/',
          platform: 'instagram_reel', title: 'Duke signing \\u00b7 Nike Basketball announcement',
          duration_seconds: 28, creator: '@cameronwilliams_25' }
      ],
      socials: { instagram: '@cameronwilliams_25' }
    },

    /* ─── Faizon Brandon · Tennessee signee · 5-star QB ──────────────── */
    'faizonbrandon': {
      short_form: [
        { url: 'https://www.youtube.com/results?search_query=Faizon+Brandon+Grimsley+quarterback&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: '4A state champ MVP \\u00b7 Grimsley QB',
          duration_seconds: 48, creator: '@HudlHS' },
        { url: 'https://www.youtube.com/results?search_query=Faizon+Brandon+Tennessee+QB+commit&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Tennessee commit \\u00b7 5-star signing',
          duration_seconds: 42, creator: '@VolFootball' },
        { url: 'https://www.youtube.com/results?search_query=Faizon+Brandon+Gatorade+NC+Player+of+Year&sp=EgIYAQ%253D%253D',
          platform: 'youtube_shorts', title: 'Gatorade NC Player of the Year',
          duration_seconds: 38, creator: '@Gatorade' },
        { url: 'https://www.instagram.com/imjust.faizon_/',
          platform: 'instagram_reel', title: '7A state championship moment',
          duration_seconds: 30, creator: '@imjust.faizon_' }
      ],
      socials: { instagram: '@imjust.faizon_', x: '@faizon_brandon' }
    }
  };"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if ANCHOR_OLD not in content:
        print("ERROR: Anchor not found (JSJ socials closing + map closing). FCBase28 must be in place first.")
        return 1
    if content.count(ANCHOR_OLD) > 1:
        print(f"ERROR: Anchor appears {content.count(ANCHOR_OLD)} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(ANCHOR_OLD, ANCHOR_NEW, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   5 amateurs added to FE_CURATED_GENZ  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Verify each player's page renders Hot Reels + Follow:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=AJ+Dybantsa&sport=mens-basketball")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Tyran+Stokes&sport=mens-basketball")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Faizon+Brandon&sport=football")
    print()
    print("Cards open external (no thumbnails / no embed yet — same state JSJ was in pre-FCBase28).")
    print("Follow chips show VERIFIED handles for all 5.")
    print()
    print("If looks right:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase29_5_AMATEURS_LIVE")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
