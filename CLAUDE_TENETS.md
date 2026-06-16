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

## Tenet 58 - RIGHT-FILE-FIRST (June 15 2026, Sridhar — the day-killer)
Before editing ANY config/redirect/build file, find the file the platform ACTUALLY reads.
- Netlify reads **`/_redirects` at the publish root** AND root `netlify.toml` — it does NOT read `.netlify/netlify.toml`. June 15: hours lost editing `.netlify/netlify.toml` (ignored by Netlify) while the live `/_redirects` (a 3-line catch-all `/* /index.html 200`) sent every clean URL to home.
- ALWAYS run `find . -name _redirects -not -path "*/freezes/*"` and confirm the publish dir + which redirect source wins, BEFORE touching redirects.
- Read the SERVED bytes (`curl` the live URL, check `<title>`) and the REAL config file FIRST. Never edit blind.

## Tenet 59 - TEST-BEFORE-HANDOVER (June 15 2026)
Every script's core logic is dry-run in the container against representative data BEFORE it goes to Sridhar. No untested command leaves. If a parser/transform can be tested on a sample, it IS tested first. "Quality proof IS the work" applies to the scripts themselves, not just the output.

## Tenet 60 - REGRESSION-GATE-EVERYTHING (June 15 2026, Sridhar — "regression to the extreme length")
Every deploy ENDS with a verification gate that checks the ACTUAL LIVE result, and commits ONLY if all pass:
- **Site deploys:** curl EVERY nav link by `<title>`; if any serves the home title when it shouldn't, ABORT the commit. New page → verify the new page AND the adjacent existing nav still resolve.
- **Engine deploys:** run the athlete spread (target athlete moved + others held + HS still capped + varied, not clustered).
- New features test the currently-working adjacent paths too, not just the new thing. The gate physically blocks a broken ship.

## Tenet 61 - NEVER-BREAK-WHAT-WORKS (June 15 2026, Sridhar)
The proven Home Page / nav / live pages are SACRED. Touch the minimum. Back up before every edit. Changes near working surfaces are ADDITIVE and reversible in one line (e.g. one `<a>` nav item, one redirect). After any change, verify the working surfaces STILL work. A redesign is a separate, explicit phase — never bundled into a feature add.

## Tenet 62 - SIMPLEST-DEPLOY, FROM CLEAN SOURCE (June 15 2026, Sridhar)
One self-contained script, one command, downloads baked in. Build from a KNOWN-GOOD source (git commit), never from unknown/damaged on-disk state. PRINT the result (the full redirect list / the diff) BEFORE deploying so Sridhar sees it. Never run a transform on a file whose current contents I haven't just read — rebuild from git-clean source instead. June 15: repeated damage came from python edits on a file I couldn't see; the fix was to rebuild `_redirects` fresh from git 369579c.

## Tenet 63 - READ-STATE-BEFORE-EVERY-EDIT (June 15 2026)
The repeated June-15 damage (43 redirects → 6) came from editing files in a state I assumed instead of one I'd just read. ALWAYS `cat`/`grep` the actual current file immediately before editing it. Never trust assumed state. If a count looks wrong after an edit, STOP and read — don't patch on top.

## Tenet 64 - NEVER SUGGEST STOPPING (June 15 2026, Sridhar — emphatic)
It is NEVER Claude's place to suggest ending the session, calling it a day, or "a good stopping point." Sridhar decides when work stops, and only Sridhar. Claude does not editorialize about how long the day has been, how hard the stretch was, or whether to pause. After finishing any task, Claude moves straight to the next build — no wind-down language, no "clean stopping point," no offering to stop. The default is ALWAYS: keep building. Many things to ship before the day is called, and that call is Sridhar's alone.

## Tenet 65 - TWO ENVIRONMENTS · DEV-FIRST ALWAYS (June 15 2026, Sridhar — emphatic, after the dev-left-broken disaster)
FieldCheck has TWO environments. Nothing goes to prod without explicit agreement.

**SITES (Netlify, site 03408b50-33ef-4e80-b08f-a648c42eb2b4):**
- **DEV site** = `fieldcheck-dev--fieldcheck-app.netlify.app` — deploy with `netlify deploy --dir . --alias fieldcheck-dev --site 03408b50-...`. ALL site work goes here FIRST.
- **PROD site** = `fieldcheck-app.netlify.app` — deploy with `netlify deploy --prod ...` ONLY on Sridhar's explicit say-so. NEVER the default.

**WORKER (Cloudflare):**
- **DEV worker** = `fieldcheck-proxy-dev` (`wrangler deploy --env dev`). ALL engine/algorithm work goes here FIRST.
- **PROD worker** = `fieldcheck-proxy` (`wrangler deploy` with no env). Currently FCBase112. Promote ONLY on explicit agreement, gated by the athlete spread.

**THE FLOW:** build on DEV (dev site + dev worker) → verify → Sridhar agrees → promote to PROD (gated). `--prod` and bare `wrangler deploy` are NEVER defaults.

**THE BURNED-IN LESSON (the original sin, June 15):** during the redirect disaster, prod's redirects were recovered from git but the DEV site (which had ~600 files) was left broken at 404. NEVER recover/fix one environment and leave the other broken. When touching redirects/config/recovery, ALWAYS check and fix BOTH dev and prod. A fix that leaves an environment broken is not a fix.

**PROMOTION GATE:** promoting dev→prod (site or worker) runs the full verify gate (nav-by-title for sites, athlete-spread for worker) on the TARGET, and freezes first. Both environments end in a known-good state or the promotion rolls back.
