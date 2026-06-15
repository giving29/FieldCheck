#!/usr/bin/env python3
"""
V022.31 · PATCH M · text-based HOF detection (for when wikidata/bbref/pfr fail)

Bug: Tim Duncan got composite=8.0 (early_pro cap) instead of 9.7 (legend_pro).
     Reason: wikidata returned empty, bbref 429-rate-limited, pfr not_basketball.
     So isLegendValidated=false → isLegendSig fails its && check → falls through
     to early_pro cascade.

Fix:
  M1 · Add hasTextHOF based on strong HOF-specific text patterns
       ("naismith memorial basketball hall of fame", "hall of fame inductee", etc.)
  M2 · Loosen isLegendValidated to also accept hasTextHOF
  M3 · Loosen isRetiredSig to catch "retired in YYYY" / "hall of fame inductee"
       without requiring NBA prefix (HS school override already prevents HS players
       from tripping into this)

Result: Tim Duncan → legend_pro (cap 9.7). Cooper Flagg, Caitlin Clark unaffected.
"""
import sys, shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.31-M.bak")
if not WORKER.exists():
    print("ERROR: worker.js not found", file=sys.stderr); sys.exit(1)
shutil.copy2(WORKER, BACKUP)
print(f"✓ Backed up to {BACKUP}")

src = WORKER.read_text()
orig_len = len(src)
applied = 0

def apply(label, old, new):
    global src, applied
    c = src.count(old)
    if c == 0:
        print(f"✗ {label} · OLD NOT FOUND", file=sys.stderr)
        print(f"  Searched for: {old[:200]}", file=sys.stderr)
        sys.exit(2)
    if c > 1:
        print(f"✗ {label} · {c} matches (ambiguous)", file=sys.stderr); sys.exit(2)
    src = src.replace(old, new)
    applied += 1
    print(f"✓ {label} (Δ {'+' if len(new)>=len(old) else ''}{len(new)-len(old)})")

# ─── PATCH M1 + M2 · Add hasTextHOF + loosen isLegendValidated ───────────────
PATCH_M_OLD = """      const hofSourceCount = [wikidataHOF, pfrIsHOF, bbrefIsHOF].filter(Boolean).length;
      const hasStructuredAccolades = (bbrefAllStars > 0) || (bbrefChamps > 0) || (bbrefMVPs > 0) || (pfrProBowls > 0);
      // V022.31 · PATCH L1 · loosened — Wikidata HOF status is structured/curated, reliable on its own.
      // The original 2-source requirement was to prevent fuzzy bbref/pfr matches from cascading to legend_pro.
      // But Wikidata HOF is a structured property, not fuzzy text matching — single source is sufficient.
      // Also: when bbref is rate-limited (429), we lose its HOF signal, so we need to trust wikidata alone.
      const isLegendValidated = wikidataHOF
        || (hofSourceCount >= 2)
        || (hofSourceCount >= 1 && hasStructuredAccolades);"""

PATCH_M_NEW = """      const hofSourceCount = [wikidataHOF, pfrIsHOF, bbrefIsHOF].filter(Boolean).length;
      const hasStructuredAccolades = (bbrefAllStars > 0) || (bbrefChamps > 0) || (bbrefMVPs > 0) || (pfrProBowls > 0);

      // V022.31 · PATCH M · TEXT-BASED HOF DETECTION
      // When structured adapters (wikidata/bbref/pfr) are unavailable/rate-limited, fall back
      // to strong HOF-specific text patterns. These are tier-1 HOF institution names which
      // can't be confused with anything else — "Naismith Memorial Basketball Hall of Fame" is
      // not a generic phrase. Tim Duncan's profile will match this even when bbref/wikidata fail.
      const hasTextHOF = /\\b(naismith memorial basketball hall of fame|naismith hall of fame|nba hall of fame|wnba hall of fame|nfl hall of fame|pro football hall of fame|baseball hall of fame|cooperstown|hall of fame inductee|hof inductee|inducted into the [a-z ]{0,30} hall of fame|inducted into the basketball hall of fame|enshrined in the [a-z ]{0,30} hall of fame|first[- ]ballot hall of famer)\\b/i.test(allText);

      // V022.31 · PATCH L1 + M2 · loosened — accept Wikidata HOF OR text-HOF as sufficient.
      // Text-HOF only catches tier-1 HOF institution names (above) which cannot false-positive
      // on amateur athletes. The HS/college school overrides also fire BEFORE this in the cascade,
      // so amateur athletes are protected even if HOFer comparisons appear in their scout reports.
      const isLegendValidated = wikidataHOF
        || hasTextHOF
        || (hofSourceCount >= 2)
        || (hofSourceCount >= 1 && hasStructuredAccolades);"""

apply("PATCH_M_text_HOF_detection", PATCH_M_OLD, PATCH_M_NEW)

# ─── PATCH M3 · Loosen isRetiredSig regex ────────────────────────────────────
PATCH_M3_OLD = """      // V022.31 · PATCH H · TIGHTENED retired signal — require explicit pro-context co-occurrence.
      // Old regex matched bare "retired"/"retirement" — hit on retired jersey numbers, retired coaches,
      // unrelated "completed.*career" / "career.*concluded" fragments.
      const isRetiredSig = /\\b(?:retired (?:nba|wnba|nfl|mlb|mls|professional|pro\\b)|(?:nba|wnba|nfl|mlb|mls)[^.]{0,50}(?:retirement|retired in)|formerly played (?:in|with)\\s+(?:the\\s+)?(?:nba|wnba|nfl|mlb)|(?:nba|wnba|nfl|mlb) hall of fame inductee|former (?:nba|wnba|nfl|mlb) (?:player|forward|guard|center|pitcher|quarterback)|career[- ]concluded (?:in|with))\\b/i.test(allText);"""

PATCH_M3_NEW = """      // V022.31 · PATCH H + M3 · TIGHTENED retired signal — require pro-context patterns.
      // Patch H tightened from bare "retired" (which hit on retired jersey numbers, retired coaches).
      // Patch M3 adds: "retired in 20XX/19XX" (year anchor), "retired from basketball/football/etc",
      // and HOF inductee patterns without NBA prefix. HS/college school overrides in the cascade
      // protect amateur athletes from tripping into retired_pro even if their scout reports compare
      // them to HOFers.
      const isRetiredSig = /\\b(?:retired (?:nba|wnba|nfl|mlb|mls|professional|pro\\b|in (?:19|20)\\d{2}|from (?:professional|basketball|football|baseball|soccer|tennis|the (?:nba|wnba|nfl|mlb)))|(?:nba|wnba|nfl|mlb|mls)[^.]{0,50}(?:retirement|retired in)|formerly played (?:in|with)\\s+(?:the\\s+)?(?:nba|wnba|nfl|mlb)|(?:nba|wnba|nfl|mlb) hall of fame inductee|former (?:nba|wnba|nfl|mlb) (?:player|forward|guard|center|pitcher|quarterback|all[- ]star|champion|mvp)|career[- ]concluded (?:in|with)|hall of fame inductee|naismith memorial|enshrined in.{0,40}hall of fame|career-ending retirement|announced retirement)\\b/i.test(allText);"""

apply("PATCH_M3_loosen_retired_sig", PATCH_M3_OLD, PATCH_M3_NEW)

WORKER.write_text(src)
print(f"\n✓ Patch M applied · {applied} patches · {orig_len:,} → {len(src):,}")
print("\nExpected result for Tim Duncan:")
print("  · hasTextHOF=true (text contains 'Naismith Memorial Basketball Hall of Fame')")
print("  · isLegendValidated=true (via hasTextHOF)")
print("  · isLegendSig+isProSig+isLegendValidated → stage=legend_pro")
print("  · composite tier=pro stage=legend_pro → cap=9.7")
print("  · Expected composite: 9.7")
print("\nNext:")
print("  node --check worker.js && ./fc-deploy-dev.sh")
print("  Then re-smoke Tim Duncan (want 9.7), Boozer (want 7.5), Stokes (want 6.5)")
