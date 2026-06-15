// ═══════════════════════════════════════════════════════════════════════
// FC17.S3 · Sport-Axis Adapter · Option C implementation
// ═══════════════════════════════════════════════════════════════════════
//
// IMPLEMENTS the recommended hybrid architecture from
// FC17_S3_SPORT_AXIS_LABELS_V1.html:
//
//   - 8 canonical pillars under the hood (math, posteriors, refinements)
//   - Sport-specific labels on UI display layer
//   - Adapter is a thin lookup, ~50 LOC per sport
//
// STATUS: ready-to-wire · waiting on Sridhar's Option C approval (Entry #004)
// Once approved:
//   1. Load this script in fieldcheck-verdict.html (defer)
//   2. Update fc17-polygon-mount.js to call FC17_SPORT_ADAPTER.getLabels(sport)
//      instead of hardcoded labels
//   3. Update fc17-interpretation-panel.js similarly
//   4. Add 1 line to FC17_S3 sprint spec: "wire adapter into mount module"
//
// SPORTS DEFINED (Phase 1):
//   - mens-basketball / womens-basketball (mostly canonical · ICON baseline)
//   - womens-volleyball / mens-volleyball  (most departure · validates pattern)
//   - football  (some adaptation)
//   - tennis    (some adaptation)
//   - default   (canonical fallback for unknown sports)
//
// API:
//   FC17_SPORT_ADAPTER.getLabels(sport)        → {character: '...', mindset: '...', ...}
//   FC17_SPORT_ADAPTER.getLabel(sport, pillar) → 'Captain DNA' (single pillar)
//   FC17_SPORT_ADAPTER.getCanonicalKey(label)  → 'mindset' (reverse lookup)
//   FC17_SPORT_ADAPTER.listSports()            → ['mens-basketball', ...]
//   FC17_SPORT_ADAPTER.PILLAR_ORDER            → canonical pillar key order
//
// ═══════════════════════════════════════════════════════════════════════

(function(){
  'use strict';

  // ─── Canonical pillar order (matches FLAGG_V17 polygon.angle_deg order) ──
  const PILLAR_ORDER = [
    'character',       // apex · 12 o'clock
    'mindset',         // 45°
    'mental_strength', // 90°
    'talent',          // 135°
    'physical',        // 180°
    'mental_iq',       // 225°
    'coachability',    // 270°
    'competitive'      // 315°
  ];


  // ─── SPORT LABEL DEFINITIONS ────────────────────────────────────────
  // Each sport defines display labels for the 8 canonical pillars.
  // Math layer NEVER sees these — they're UI-only.
  // Sports with sport-specific terms differ from canonical; otherwise
  // they fall through to canonical default.
  //
  // Rules for additions (Tenet for adapter discipline):
  //   1. Keep label length reasonable (fits on polygon axis · ~16 chars max)
  //   2. Avoid sport-specific jargon non-fans wouldn't recognize
  //   3. If unsure, USE canonical (Character / Mindset / etc.)
  //   4. Canonical key NEVER changes — only display label
  // ────────────────────────────────────────────────────────────────────

  const SPORT_LABELS = {

    // ─── BASKETBALL (mostly canonical · ICON baseline) ──────────────
    'mens-basketball': {
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Closer DNA',          // "clutch in basketball" → Closer
      talent:          'Talent',
      physical:        'Athleticism + Length', // size matters but reach matters more
      mental_iq:       'Court IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },
    'womens-basketball': {
      // Mirror mens-basketball · same sport, same lexicon
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Closer DNA',
      talent:          'Talent',
      physical:        'Athleticism + Length',
      mental_iq:       'Court IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },


    // ─── VOLLEYBALL (most departure · validates adapter pattern) ────
    // Volleyball coaches recognize: Captain DNA, Closer DNA, Hit %, Reach
    'womens-volleyball': {
      character:       'Character',
      mindset:         'Captain DNA',          // team-driven, captain-track
      mental_strength: 'Closer DNA',           // last-set, game-point execution
      talent:          'Talent',
      physical:        'Size + Reach',         // both critical in volleyball
      mental_iq:       'Court IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },
    'mens-volleyball': {
      // Same lexicon as womens-volleyball
      character:       'Character',
      mindset:         'Captain DNA',
      mental_strength: 'Closer DNA',
      talent:          'Talent',
      physical:        'Size + Reach',
      mental_iq:       'Court IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },


    // ─── FOOTBALL (some adaptation) ─────────────────────────────────
    'football': {
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Clutch gene',          // football-native term
      talent:          'Talent',
      physical:        'Athleticism',          // size varies hugely by position
      mental_iq:       'Football IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },


    // ─── TENNIS (some adaptation) ───────────────────────────────────
    'tennis': {
      character:       'Character',
      mindset:         'Mental Toughness',     // tennis-specific framing
      mental_strength: 'Closing Strength',
      talent:          'Talent',
      physical:        'Athleticism + Reach',
      mental_iq:       'Court IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },


    // ─── SOCCER (placeholder · ready for first v1.7 soccer player) ──
    'mens-soccer': {
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Closer DNA',
      talent:          'Talent',
      physical:        'Athleticism',
      mental_iq:       'Soccer IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },
    'womens-soccer': {
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Closer DNA',
      talent:          'Talent',
      physical:        'Athleticism',
      mental_iq:       'Soccer IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },


    // ─── BASEBALL (placeholder · ready for first v1.7 baseball player) ─
    'baseball': {
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Clutch gene',
      talent:          'Talent',
      physical:        'Athleticism',
      mental_iq:       'Baseball IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    },


    // ─── DEFAULT (fallback · pure canonical labels) ─────────────────
    'default': {
      character:       'Character',
      mindset:         'Mindset',
      mental_strength: 'Mental Strength',
      talent:          'Talent',
      physical:        'Physical',
      mental_iq:       'Mental / IQ',
      coachability:    'Coachability',
      competitive:     'Competitiveness'
    }
  };


  // ─── normalize sport key (handle hyphens, underscores, spaces, aliases) ──
  // Generic sport names map to canonical specific:
  //   'basketball' → 'mens-basketball' (basketball default · use mens lexicon)
  //   'volleyball' → 'womens-volleyball'
  //   'soccer' → 'mens-soccer'
  // Mens/womens specifics pass through unchanged.
  const SPORT_ALIASES = {
    'basketball':   'mens-basketball',
    'volleyball':   'womens-volleyball',
    'soccer':       'mens-soccer',
    'football':     'football',   // pass-through
    'tennis':       'tennis',     // pass-through
    'baseball':     'baseball'    // pass-through
  };

  function normalizeSport(sport){
    if (!sport) return 'default';
    var key = String(sport).toLowerCase().trim().replace(/[_\s]+/g, '-');
    // Apply alias if defined
    if (SPORT_ALIASES[key]) return SPORT_ALIASES[key];
    return key;
  }


  // ─── getLabels · returns full label object for a sport ──────────────
  function getLabels(sport){
    const key = normalizeSport(sport);
    return SPORT_LABELS[key] || SPORT_LABELS['default'];
  }


  // ─── getLabel · single-pillar lookup with fallback ──────────────────
  function getLabel(sport, pillarKey){
    const labels = getLabels(sport);
    return labels[pillarKey] || SPORT_LABELS['default'][pillarKey] || pillarKey;
  }


  // ─── getCanonicalKey · reverse lookup (label → canonical key) ───────
  // Useful for: parsing data that came in with sport-specific labels and
  // needs to be normalized to canonical pillar keys for math.
  // Returns null if no match (caller decides fallback).
  function getCanonicalKey(label){
    if (!label) return null;
    const lower = String(label).toLowerCase().trim();
    // Search all sports for a matching label
    for (const sport in SPORT_LABELS) {
      const labels = SPORT_LABELS[sport];
      for (const key in labels) {
        if (labels[key].toLowerCase().trim() === lower) return key;
      }
    }
    return null;
  }


  // ─── listSports · enumerate supported sports ────────────────────────
  function listSports(){
    return Object.keys(SPORT_LABELS).filter(function(k){ return k !== 'default'; });
  }


  // ─── validateSportDefinition · sanity check a sport entry ───────────
  // Returns array of issues ([] if valid).
  // Useful for adapter authoring — verify a new sport definition is complete.
  function validateSportDefinition(sport){
    const labels = SPORT_LABELS[normalizeSport(sport)];
    if (!labels) return ['sport_not_defined'];
    const issues = [];
    PILLAR_ORDER.forEach(function(pillar){
      if (!labels[pillar]) issues.push('missing_pillar:' + pillar);
      else if (labels[pillar].length > 24) issues.push('label_too_long:' + pillar);
    });
    return issues;
  }


  // ─── EXPORT ─────────────────────────────────────────────────────────
  window.FC17_SPORT_ADAPTER = {
    PILLAR_ORDER:           PILLAR_ORDER,
    SPORT_LABELS:           SPORT_LABELS,  // exposed for inspection/testing
    getLabels:              getLabels,
    getLabel:               getLabel,
    getCanonicalKey:        getCanonicalKey,
    listSports:             listSports,
    validateSportDefinition: validateSportDefinition,
    normalizeSport:         normalizeSport
  };


  // ─── SELF-TEST · runs at load time (silent unless issues found) ─────
  // Verifies every defined sport has all 8 canonical pillars.
  (function selfTest(){
    if (typeof console === 'undefined') return;
    let allOk = true;
    Object.keys(SPORT_LABELS).forEach(function(sport){
      const issues = validateSportDefinition(sport);
      if (issues.length > 0) {
        console.warn('FC17_SPORT_ADAPTER · sport '+sport+' has issues:', issues);
        allOk = false;
      }
    });
    if (allOk) {
      // Quiet success — only log to dev console under verbose mode
      if (window.FC17_VERBOSE) {
        console.log('FC17_SPORT_ADAPTER · '+listSports().length+' sports defined, all valid');
      }
    }
  })();

})();


// ═══════════════════════════════════════════════════════════════════════
// INTEGRATION PLAN (for Sridhar when Option C is approved)
// ═══════════════════════════════════════════════════════════════════════
//
// STEP 1 · Add script tag to fieldcheck-verdict.html (after fc17-polygon-mount.js):
//
//   <script src="/fc17-sport-adapter.js" defer></script>
//
// STEP 2 · Update fc17-polygon-mount.js to consume adapter:
//
//   In the polygon render function, replace hardcoded pillar labels like:
//     labels.push('Character');
//   With:
//     const adapterLabels = window.FC17_SPORT_ADAPTER
//       ? window.FC17_SPORT_ADAPTER.getLabels(playerData.sport)
//       : null;
//     labels.push(adapterLabels ? adapterLabels.character : 'Character');
//
//   (or refactor to loop over PILLAR_ORDER and call getLabel for each)
//
// STEP 3 · Update fc17-interpretation-panel.js similarly (if it references
//   pillar names in text · currently it just renders FLAGG_V17.posterior.interpretation
//   paragraphs as-is, so probably no change needed)
//
// STEP 4 · Validate with Cooper Flagg (mens-basketball):
//   - Polygon should still show "Closer DNA" (was canonical "Mental Strength")
//   - "Athleticism + Length" (was "Physical")
//   - "Court IQ" (was "Mental / IQ")
//   - Other labels unchanged
//
// STEP 5 · Add 2nd v1.7 player to validate volleyball labels:
//   - Madisen Skinner (per Sridhar's existing artwork)
//   - Polygon should show "Captain DNA", "Closer DNA", "Size + Reach", "Court IQ"
//   - Composite math identical to basketball — proves Option C works
//
// STEP 6 · Document sport-adapter onboarding in canonical state V1.5
//
// ═══════════════════════════════════════════════════════════════════════


// ═══════════════════════════════════════════════════════════════════════
// USAGE EXAMPLES (for ad-hoc testing in browser console)
// ═══════════════════════════════════════════════════════════════════════
//
//   // Get all labels for basketball
//   FC17_SPORT_ADAPTER.getLabels('mens-basketball')
//   //  → { character: 'Character', mindset: 'Mindset',
//   //      mental_strength: 'Closer DNA', talent: 'Talent',
//   //      physical: 'Athleticism + Length', mental_iq: 'Court IQ',
//   //      coachability: 'Coachability', competitive: 'Competitiveness' }
//
//   // Get one label
//   FC17_SPORT_ADAPTER.getLabel('womens-volleyball', 'mental_strength')
//   //  → 'Closer DNA'
//
//   // Reverse lookup
//   FC17_SPORT_ADAPTER.getCanonicalKey('Captain DNA')
//   //  → 'mindset'   (volleyball maps mindset → Captain DNA)
//
//   // List supported sports
//   FC17_SPORT_ADAPTER.listSports()
//   //  → ['mens-basketball', 'womens-basketball', 'womens-volleyball', ...]
//
//   // Validate a new sport definition
//   FC17_SPORT_ADAPTER.validateSportDefinition('mens-basketball')
//   //  → [] (no issues)
//
//   FC17_SPORT_ADAPTER.validateSportDefinition('lacrosse')
//   //  → ['sport_not_defined']
//
// ═══════════════════════════════════════════════════════════════════════
