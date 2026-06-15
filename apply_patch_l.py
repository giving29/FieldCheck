#!/usr/bin/env python3
"""
V022.31 · PATCH L · fixes 2 remaining issues from Patch K smoke:

  L1 · Cameron Boozer at Duke got classified as pro/early_pro instead of D1/college_amateur
       Reason: no college school override (Patch H only added HS override)
       Fix: Add _v22_31_isCollegeSchool detection + cascade entry BEFORE pro fallthrough

  L2 · Tim Duncan (NBA HOFer) got classified as early_pro instead of legend_pro
       Reason: isLegendValidated requires 2+ HOF sources, but bbref is 429-rate-limited
       Fix: Loosen to accept wikidataHOF alone (Wikidata HOF is structured/curated, reliable)
"""
import sys, shutil
from pathlib import Path

WORKER = Path("worker.js")
BACKUP = Path("worker.js.pre-V022.31-L.bak")
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
        print(f"✗ {label} · OLD NOT FOUND", file=sys.stderr); sys.exit(2)
    if c > 1:
        print(f"✗ {label} · {c} matches (ambiguous)", file=sys.stderr); sys.exit(2)
    src = src.replace(old, new)
    applied += 1
    print(f"✓ {label} (Δ {'+' if len(new)>=len(old) else ''}{len(new)-len(old)})")

# ─── PATCH L1 · loosen isLegendValidated to accept wikidataHOF alone ────────
PATCH_L1_OLD = """      const hofSourceCount = [wikidataHOF, pfrIsHOF, bbrefIsHOF].filter(Boolean).length;
      const hasStructuredAccolades = (bbrefAllStars > 0) || (bbrefChamps > 0) || (bbrefMVPs > 0) || (pfrProBowls > 0);
      const isLegendValidated = (hofSourceCount >= 2) || (hofSourceCount >= 1 && hasStructuredAccolades);"""

PATCH_L1_NEW = """      const hofSourceCount = [wikidataHOF, pfrIsHOF, bbrefIsHOF].filter(Boolean).length;
      const hasStructuredAccolades = (bbrefAllStars > 0) || (bbrefChamps > 0) || (bbrefMVPs > 0) || (pfrProBowls > 0);
      // V022.31 · PATCH L1 · loosened — Wikidata HOF status is structured/curated, reliable on its own.
      // The original 2-source requirement was to prevent fuzzy bbref/pfr matches from cascading to legend_pro.
      // But Wikidata HOF is a structured property, not fuzzy text matching — single source is sufficient.
      // Also: when bbref is rate-limited (429), we lose its HOF signal, so we need to trust wikidata alone.
      const isLegendValidated = wikidataHOF
        || (hofSourceCount >= 2)
        || (hofSourceCount >= 1 && hasStructuredAccolades);"""

apply("PATCH_L1_loosen_legend_validation", PATCH_L1_OLD, PATCH_L1_NEW)

# ─── PATCH L2 · add college school override ─────────────────────────────────
PATCH_L2_OLD = """      // V022.31 · PATCH H · HS-school override · prevents stray text mentions ("his father played
      // in the NBA", "retired jersey number", "the school produced NBA players") from misclassifying
      // HS athletes. If current_school matches HS patterns AND does NOT match college, force prep_amateur.
      const _v22_31_currentSchool = String((id && id.current_school) || '').toLowerCase();
      const _v22_31_isHSSchool = /\\b(high school|hs\\b|prep school|preparatory|academy|christian school|jesuit|catholic high|charter school|sierra canyon|montverde|prolific prep|spire academy|link academy|notre dame|imm?aculate|montverd|hebron christian|hill[- ]school)\\b/i.test(_v22_31_currentSchool)
        && !/\\b(college|university|institute|state college|community college|tech college|junior college)\\b/i.test(_v22_31_currentSchool);"""

PATCH_L2_NEW = """      // V022.31 · PATCH H · HS-school override · prevents stray text mentions ("his father played
      // in the NBA", "retired jersey number", "the school produced NBA players") from misclassifying
      // HS athletes. If current_school matches HS patterns AND does NOT match college, force prep_amateur.
      const _v22_31_currentSchool = String((id && id.current_school) || '').toLowerCase();
      const _v22_31_isHSSchool = /\\b(high school|hs\\b|prep school|preparatory|academy|christian school|jesuit|catholic high|charter school|sierra canyon|montverde|prolific prep|spire academy|link academy|notre dame|imm?aculate|montverd|hebron christian|hill[- ]school)\\b/i.test(_v22_31_currentSchool)
        && !/\\b(college|university|institute|state college|community college|tech college|junior college)\\b/i.test(_v22_31_currentSchool);

      // V022.31 · PATCH L2 · COLLEGE-school override · prevents pro-tier misclassification for college
      // freshmen (Cameron Boozer at Duke got tier=pro because NBA mentions in scout text + Duke not flagged
      // as HS). If school matches college patterns OR is a known D1 program by canonical name, force
      // college_amateur (unless legend_pro is validated — which handles NBA Hall-of-Famers who later coach at a college).
      const _v22_31_isCollegeSchool = (/\\b(university|college|institute|tech|state)\\b/i.test(_v22_31_currentSchool)
        && !/\\b(high school|hs\\b|prep school|preparatory|academy|charter school)\\b/i.test(_v22_31_currentSchool))
        || /^(duke|stanford|kentucky|kansas|north carolina|unc|gonzaga|ucla|usc|byu|tcu|villanova|connecticut|uconn|baylor|memphis|auburn|arkansas|tennessee|alabama|florida|georgia|texas|oklahoma|arizona|oregon|washington|michigan|purdue|illinois|indiana|iowa|wisconsin|nebraska|maryland|virginia|maryland|notre dame|miami|fsu|florida state|clemson|louisville|cincinnati|houston|creighton|marquette|providence|saint louis|fordham|vcu|colorado|utah|west virginia|wake forest|davidson|drexel|temple|la salle|saint joseph|loyola|liberty|grand canyon|long beach state|ucsb|uc san diego|santa barbara|fairfield|iona|niagara|saint peter|manhattan|monmouth|hofstra|princeton|harvard|yale|brown|cornell|penn|columbia|dartmouth|lehigh|bucknell|colgate|holy cross|navy|army|air force|texas tech|texas a&m|michigan state|ohio state|penn state|rutgers|northwestern|nebraska|minnesota|missouri|mississippi state|south carolina|ole miss|vanderbilt|lsu|miss state|georgia tech|virginia tech|nc state|pittsburgh|syracuse|boston college|rhode island|umass|north florida|west georgia|bellarmine|central arkansas|saint louis|texas tech|michigan state|texas longhorns)\\b/i.test(_v22_31_currentSchool);"""

apply("PATCH_L2_college_school_detection", PATCH_L2_OLD, PATCH_L2_NEW)

# ─── PATCH L2 cont · add college override entry in cascade ───────────────────
PATCH_L2B_OLD = """      // V022.31 · PATCH H · HS school override takes precedence over text signals
      // (unless legend_pro is validated with HOF + structured accolades - then the player is
      // actually a returning HOF coach speaking at HS, which is fine to flag as legend)
      if (_v22_31_isHSSchool && !isLegendValidated) {
        stage = 'prep_amateur';
        stageSignals.push('v022.31_hs_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

PATCH_L2B_NEW = """      // V022.31 · PATCH H · HS school override takes precedence over text signals
      // (unless legend_pro is validated with HOF + structured accolades - then the player is
      // actually a returning HOF coach speaking at HS, which is fine to flag as legend)
      if (_v22_31_isHSSchool && !isLegendValidated) {
        stage = 'prep_amateur';
        stageSignals.push('v022.31_hs_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.31 · PATCH L2 · COLLEGE school override · prevents Cameron-Boozer-style cascade where
      // college freshman gets pro tier because text mentions NBA projections
      else if (_v22_31_isCollegeSchool && !isLegendValidated) {
        stage = 'college_amateur';
        stageSignals.push('v022.31_college_school_override');
        if (_v22_31_currentSchool) stageSignals.push('school=' + _v22_31_currentSchool.slice(0, 30));
      }
      // V022.30 · legend_pro requires validation now
      else if (isLegendSig && isProSig && isLegendValidated) {"""

apply("PATCH_L2B_college_cascade_entry", PATCH_L2B_OLD, PATCH_L2B_NEW)

WORKER.write_text(src)
print(f"\n✓ Patch L applied · {applied} patches · {orig_len:,} → {len(src):,}")
print("\nNext:")
print("  node --check worker.js && ./fc-deploy-dev.sh")
print("\nThen re-smoke: Tim Duncan (want 9.7), Cameron Boozer (want d1, ~7.5), Tyran Stokes (want 6.5)")
