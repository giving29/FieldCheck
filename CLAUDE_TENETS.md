# CLAUDE TENETS - FieldCheck IQ

## Tenet 54 - FULL DIRECTORY BACKUP DISCIPLINE
Before any ship that modifies frontend/ or worker.js:
1. TRUE FREEZE FIRST: tar -czf freezes/base_FULL_pre.tar.gz frontend/ worker.js wrangler.toml
2. RECORD FILE COUNT: BEFORE=count
3. EXECUTE CHANGES
4. VERIFY: AFTER=count
5. HARD ABORT if AFTER less than BEFORE - restore from FULL freeze
6. POST-SHIP FREEZE: tar -czf freezes/base_FULL_post.tar.gz frontend/ worker.js

The old freeze pattern (selected files) is now called ship-manifest.
TRUE freezes are FULL DIRECTORY tarballs.
NEVER trust a ship to be add-only without file-count verification.

## Tenet 55 - DUPLICATE-NAME SYNC (Netlify shadowing)
Netlify pretty-URLs serve clean-named files (deck.html) for extensionless
routes (/deck) BEFORE applying non-forced redirects. Therefore:
1. Any page existing as both name.html and fieldcheck-name.html MUST be
   synced in the same ship that touches either.
2. Ship templates verify: for each fieldcheck-X.html touched, if X.html
   exists, byte-compare and sync.
3. Route tests alone are insufficient - always grep route output for the
   feature marker, not just HTTP 200.

## CANONICAL RECOVERY POINT - THE OWN-NUMBER FREEZE (June 11 2026)
FCBase89_GOLDEN_OWN_NUMBER_20260611_2154 | SHA256 6a67f879af19d4a2d41655d8804a6512bf3a858cef12a4dc50daa1770cd42c91
Three verified locations: project freezes/ + ~/Desktop/FieldCheck-Backups + ~/Documents/FieldCheck-Backups.
Contains: full frontend (516 files), worker (FCBase89 fine pass live), all ops tools, seals, battery artifacts, battle card.
Restore: tar -xzf <archive> in project root. Tested-extraction verified at freeze time.

## Tenet 57 - THE 9.0 LINE (June 12 2026, Sridhar)
No athlete grades above 9.0 unless they are at Hall-of-Fame level (career-proven legend
or active generational HOF-lock). Active accomplishment alone - even multiple titles/
MVPs early in a career - caps at ELITE 8.9. Applies to curated marquees AND fresh
evaluations. WVB corpus sweep pending Sridhar review: Logan Tom 9.4, Jordan Larson 9.3,
Ogbogu 9.3, Robinson-Cook 9.2, Eggleston 9.0. KWJ/May-Treanor/Akinradewo are HOF, stand.
