#!/usr/bin/env python3
"""
apply_frontend_genz_lookup_fix_v1.py

FCBase27 · Fixes the FE_CURATED_GENZ lookup to handle name variations.
Frontend strips "Jr." from display name (memory tenet), so when renderVerdict
gets called with "Jordan Smith" instead of "Jordan Smith Jr.", the lookup
for key 'jordansmithjr' fails. Fix: lookup tries multiple variations.

Also adds 'jordansmith' as a duplicate key for belt-and-suspenders coverage.
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-lookup-fix.bak')

OLD = """  /* Helper: case-insensitive lookup by normalized name */
  function _feGenzLookup(name) {
    if (!name) return null;
    var key = String(name).toLowerCase().replace(/[^a-z0-9]/g, '');
    return FE_CURATED_GENZ[key] || null;
  }"""

NEW = """  /* Helper: case-insensitive lookup that tries multiple name variations.
     Frontend may pass 'Jordan Smith' (Jr stripped) so we try with 'jr' suffix too. */
  function _feGenzLookup(name) {
    if (!name) return null;
    var raw = String(name).toLowerCase().replace(/[^a-z0-9]/g, '');
    return FE_CURATED_GENZ[raw]
      || FE_CURATED_GENZ[raw + 'jr']
      || FE_CURATED_GENZ[raw.replace(/jr$/, '')]
      || null;
  }"""

# Also add 'jordansmith' as duplicate key so lookups for the stripped form hit directly
DUPE_OLD = """    'jordansmithjr': {
      short_form: ["""

DUPE_NEW = """    'jordansmith': null,  /* alias — points to jordansmithjr below */
    'jordansmithjr': {
      short_form: ["""

# After FE_CURATED_GENZ block, add alias resolution
ALIAS_OLD = """    }
  };
  /* Helper: case-insensitive lookup that tries multiple name variations."""

ALIAS_NEW = """    }
  };
  /* Resolve aliases (null values point to the canonical entry by name pattern) */
  FE_CURATED_GENZ['jordansmith'] = FE_CURATED_GENZ['jordansmithjr'];
  /* Helper: case-insensitive lookup that tries multiple name variations."""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if OLD not in content:
        print("ERROR: Lookup function anchor not found. Previous patch may not have landed.")
        return 1
    if content.count(OLD) > 1:
        print(f"ERROR: Lookup anchor appears {content.count(OLD)} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    # Apply the lookup function replacement (also moves the helper comment)
    new_content = content.replace(OLD, NEW, 1)

    # Now also add the alias (jordansmith → jordansmithjr) for direct hits
    if DUPE_OLD in new_content and new_content.count(DUPE_OLD) == 1:
        new_content = new_content.replace(DUPE_OLD, DUPE_NEW, 1)
        if ALIAS_OLD in new_content and new_content.count(ALIAS_OLD) == 1:
            new_content = new_content.replace(ALIAS_OLD, ALIAS_NEW, 1)
            print("OK   Added alias mapping for stripped-Jr name form")
        else:
            print("WARN: Alias post-block anchor not found, lookup function still has fallbacks")
    else:
        print("WARN: Could not add direct alias, lookup function will use suffix-tries instead")

    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Patch applied  ({delta:+d} bytes)")
    print()
    print("Next:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("In devtools, BEFORE hard-refresh:")
    print("  1. F12 → Sources tab → top-right side panel → UNCHECK 'Pause on caught exceptions'")
    print("  2. Click the resume button (▶) if currently paused")
    print()
    print("Then hard refresh:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
