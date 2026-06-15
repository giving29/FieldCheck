#!/usr/bin/env python3
"""
apply_frontend_genz_precedence_fix_v1.py

FCBase28 · Flips precedence so FE_CURATED_GENZ wins over backend data.short_form
when present. The verified curated URLs (real YT Shorts video IDs + IG Reel IDs)
should always beat the backend's PLAYER_PROFILES search-URL placeholders.

Root cause: backend supplement now returns short_form from PLAYER_PROFILES (after
worker cache refresh earlier today), but PLAYER_PROFILES still has the prototype
search URLs that can't be embedded. FE constant has verified real URLs.

Two surgical changes:

  PATCH A — shortFormArr: FE wins if present, else fall back to backend.
  PATCH B — data.socials: FE always wins when present (was: only set if backend
            didn't already have socials).

After this patch:
  Cards render with real YouTube Shorts IDs and IG Reel post IDs.
  Modal player embeds them via iframe and stays on FieldCheck.

Run from fieldcheck-proxy directory:
  python3 apply_frontend_genz_precedence_fix_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-precedence-fix.bak')

# ─── PATCH A: Flip shortFormArr precedence ─────────────────────────────────
SHORTFORM_OLD = "    var shortFormArr = data.short_form || (data.encyclopedia && data.encyclopedia.short_form) || (_feGenz && _feGenz.short_form) || [];"
SHORTFORM_NEW = "    var shortFormArr = (_feGenz && Array.isArray(_feGenz.short_form) && _feGenz.short_form.length) ? _feGenz.short_form : (data.short_form || (data.encyclopedia && data.encyclopedia.short_form) || []);"

# ─── PATCH B: Make FE socials always win ──────────────────────────────────
SOCIALS_OLD = "    if (!data.socials && _feGenz && _feGenz.socials) data.socials = _feGenz.socials;"
SOCIALS_NEW = "    if (_feGenz && _feGenz.socials) data.socials = _feGenz.socials;"


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if SHORTFORM_OLD not in content:
        print("ERROR: Patch A anchor not found. Lookup line may have changed.")
        return 1
    if content.count(SHORTFORM_OLD) > 1:
        print(f"ERROR: Patch A anchor appears {content.count(SHORTFORM_OLD)} times. Ambiguous.")
        return 1
    if SOCIALS_OLD not in content:
        print("ERROR: Patch B anchor not found. Socials line may have changed.")
        return 1
    if content.count(SOCIALS_OLD) > 1:
        print(f"ERROR: Patch B anchor appears {content.count(SOCIALS_OLD)} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(SHORTFORM_OLD, SHORTFORM_NEW, 1)
    new_content = new_content.replace(SOCIALS_OLD, SOCIALS_NEW, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patches A+B applied  ({delta:+d} bytes)")
    print()
    print("Deploy sequence:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh dev (Cmd+Shift+R):")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Tap any Hot Reel card. Modal should now show the actual embedded video.")
    print()
    print("If verified clean on dev:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase28_HOTREELS_EMBED")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
