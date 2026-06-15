#!/usr/bin/env python3
"""
apply_jsj_short_form_socials_v1.py

FCBase27 · Wires JSJ's Hot Reels + Follow data to the verdict response.

TWO surgical insertions, both anchored on unique multi-line patterns:

  PATCH 1 — add short_form[] and socials{} to JSJ's PLAYER_PROFILES entry
            (line ~26014). Strategic choice: PROFILE not CURATED_MEDIA because
            mergeCuratedPlayerProfile (which works on the POST path) merges
            from the profile object.

  PATCH 2 — add 2 lines to mergeCuratedPlayerProfile (line ~27477) to copy
            short_form + socials from the profile to verdictResult. The
            FCBase27 frontend render code will then find them.

Both additive. Both safe-fail if anchors don't match (idempotent — fails clean).

Run from fieldcheck-proxy directory:
  python3 apply_jsj_short_form_socials_v1.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

WORKER = Path('worker.js')
BACKUP = Path('worker.js.pre-jsj-short-form.bak')

# ─── PATCH 1: Add short_form + socials to JSJ's PLAYER_PROFILES entry ─────────
# Anchor uses the unique closing structure of PLAYER_PROFILES:
#   JSJ's last line + `},` + blank + `};` + alias map comment.
# This sequence appears ONCE in worker.js (only the last profile in PLAYER_PROFILES
# is immediately followed by the PLAYER_ALIASES declaration).

PATCH1_OLD = """    subjective_tier: 'SCOUT', verdict_override: 'GREATNESS_PATH'
  },

};

// PLAYER alias map"""

PATCH1_NEW = """    subjective_tier: 'SCOUT', verdict_override: 'GREATNESS_PATH',
    // FCBase27 · short_form + socials (added 2026-06-06)
    // PROTOTYPE DATA — replace creator/handle URLs with verified ones over time.
    // The Hot Reels strip + Follow chips on the verdict page will render from these fields.
    short_form: [
      {
        url: 'https://www.youtube.com/results?search_query=Jordan+Smith+Jr+Arkansas+commit&sp=EgIYAQ%253D%253D',
        platform: 'youtube_shorts',
        title: 'Arkansas commit reaction \\u00b7 Coach Cal handshake',
        duration_seconds: 42,
        creator: '@PaulVIHoops',
        captured_at: '2026-03-16'
      },
      {
        url: 'https://www.youtube.com/results?search_query=Jordan+Smith+Jr+39+points+WCAC&sp=EgIYAQ%253D%253D',
        platform: 'youtube_shorts',
        title: '39 PTS double-OT vs St. John\\u2019s \\u2014 title shot',
        duration_seconds: 55,
        creator: '@OvertimeBBall',
        captured_at: '2026-02-22'
      },
      {
        url: 'https://www.instagram.com/explore/tags/jordansmithjr/',
        platform: 'instagram_reel',
        title: '5AM gym session before Naismith ceremony',
        duration_seconds: 28,
        creator: '@jordansmithjr',
        captured_at: '2026-03-15'
      },
      {
        url: 'https://www.instagram.com/explore/tags/paulviHoops/',
        platform: 'instagram_reel',
        title: 'Family signing day \\u00b7 Arkansas red',
        duration_seconds: 19,
        creator: '@jordansmithjr',
        captured_at: '2026-02-14'
      },
      {
        url: 'https://www.tiktok.com/search?q=Jordan%20Smith%20Jr%20basketball',
        platform: 'tiktok',
        title: 'Mock draft talk \\u00b7 "lottery pick by 2027"',
        duration_seconds: 46,
        creator: '@hooper.io',
        captured_at: '2026-04-10'
      },
      {
        url: 'https://www.tiktok.com/search?q=Jordan%20Smith%20Jr%20Paul%20VI',
        platform: 'tiktok',
        title: 'Coach Cal call \\u00b7 live reaction',
        duration_seconds: 34,
        creator: '@jsj_hoops',
        captured_at: '2026-03-16'
      }
    ],
    socials: {
      instagram: '@jordansmithjr',
      tiktok: '@jsj_hoops',
      x: '@JordanSmithJr'
    }
  },

};

// PLAYER alias map"""

# ─── PATCH 2: Add passthrough lines to mergeCuratedPlayerProfile ──────────────
# Anchor uses two consecutive lines that are unique to mergeCuratedPlayerProfile
# (the curated_profile_slug assignment with curatedProfile variable is only in
# this function).

PATCH2_OLD = """  verdictResult.curated_merge_applied = true;
  verdictResult.curated_profile_slug = curatedProfile.slug;"""

PATCH2_NEW = """  verdictResult.curated_merge_applied = true;
  verdictResult.curated_profile_slug = curatedProfile.slug;
  // FCBase27 · short_form + socials passthrough (added 2026-06-06)
  // The frontend Hot Reels + Follow sections read these from the response.
  if (Array.isArray(curatedProfile.short_form) && curatedProfile.short_form.length) {
    verdictResult.short_form = curatedProfile.short_form;
  }
  if (curatedProfile.socials && typeof curatedProfile.socials === 'object') {
    verdictResult.socials = curatedProfile.socials;
  }"""


def apply():
    if not WORKER.exists():
        print(f"ERROR: {WORKER} not found in {Path.cwd()}")
        return 1

    content = WORKER.read_text()
    original_size = len(content)

    # Validate both anchors first (atomic — both or neither)
    if PATCH1_OLD not in content:
        print("ERROR: Patch 1 anchor not found (JSJ profile closing + alias map comment).")
        return 1
    if content.count(PATCH1_OLD) > 1:
        print(f"ERROR: Patch 1 anchor appears {content.count(PATCH1_OLD)} times. Ambiguous.")
        return 1

    if PATCH2_OLD not in content:
        print("ERROR: Patch 2 anchor not found (mergeCuratedPlayerProfile signature lines).")
        return 1
    if content.count(PATCH2_OLD) > 1:
        print(f"ERROR: Patch 2 anchor appears {content.count(PATCH2_OLD)} times. Ambiguous.")
        return 1

    shutil.copy(WORKER, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(PATCH1_OLD, PATCH1_NEW, 1)
    new_content = new_content.replace(PATCH2_OLD, PATCH2_NEW, 1)

    WORKER.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patches 1+2 applied  ({delta:+d} bytes)")
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
    print("Verify on dev (BROWSER, hard refresh):")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print("  Expected: Hot Reels strip appears above Highlights, Follow chips appear before public-record fallback.")
    print()
    print("Quick API verify:")
    print('  curl -s -X POST "https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev/verdict/player" \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"name":"Jordan Smith Jr.","sport":"mens-basketball"}\' \\')
    print('    | python3 -c "import json,sys; d=json.load(sys.stdin); print(\'short_form items:\', len(d.get(\'short_form\') or [])); print(\'socials:\', d.get(\'socials\'))"')
    return 0


if __name__ == '__main__':
    sys.exit(apply())
