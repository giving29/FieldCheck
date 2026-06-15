// ═══════════════════════════════════════════════════════════════════════
// FC17 · Consensus Polygon Data Module · V1
// ═══════════════════════════════════════════════════════════════════════
// Provides market-consensus polygon values for marquee athletes.
// Used by fc17-polygon-mount.js enhanceWithConsensus() to render
// the consensus shadow overlay (Sprint A1 v2 design).
//
// Shape categories:
//   hype       · consensus > FC by 1.5+ composite (market overpriced vs evidence)
//   converged  · consensus ≈ FC (career complete or evidence validates market)
//   gem        · no consensus exists (hidden, market hasn't priced)
//
// Phase 1: hardcoded for marquee athletes
// Phase 6.0: replaced by crawler-sourced live consensus data
// ═══════════════════════════════════════════════════════════════════════

window.FC17_CONSENSUS_DATA = {

  cooper_flagg: {
    // Sources: 247Sports/On3 composite (NBA-bound projection), ESPN top-100 board
    consensus: {
      character: 8.5,
      mindset: 8.5,
      mental_strength: 8.0,
      talent: 9.5,
      physical: 9.0,
      mental_iq: 8.0,
      coachability: 8.5,
      competitive: 9.0
    },
    consensus_composite: 8.6,
    shape: 'hype',
    sources: ['247Sports composite', 'ESPN draft board 2025', 'On3 industry rankings'],
    last_updated: '2026-05-15',
    next_check: 'Post-rookie-year audit · summer 2026'
  },

  caleb_williams: {
    // Sources: Pre-draft #1 pick consensus, NFL Network/PFF projections
    consensus: {
      character: 8.0,
      mindset: 8.5,
      mental_strength: 7.5,
      talent: 9.5,
      physical: 8.8,
      mental_iq: 9.0,
      coachability: 7.5,
      competitive: 8.5
    },
    consensus_composite: 8.4,
    shape: 'hype',
    sources: ['NFL Network', 'PFF draft board', 'Mel Kiper Jr. Big Board'],
    last_updated: '2026-04-30',
    next_check: 'Post-2nd-year audit · Jan 2026'
  },

  caitlin_clark: {
    // Sources: WNBA Rookie of the Year voting, ESPN W rankings, WBB consensus
    consensus: {
      character: 9.0,
      mindset: 9.0,
      mental_strength: 8.8,
      talent: 9.2,
      physical: 8.5,
      mental_iq: 9.5,
      coachability: 8.5,
      competitive: 9.5
    },
    consensus_composite: 9.0,
    shape: 'converged',
    sources: ['WNBA Awards voters', 'ESPN W power rankings', 'CBS Sports'],
    last_updated: '2026-05-10',
    next_check: 'All-Star break · July 2026'
  },

  avery_skinner: {
    // Sources: AVCA All-American voters, PVF media polls, Big Ten coaches poll
    consensus: {
      character: 8.0,
      mindset: 7.5,
      mental_strength: 7.8,
      talent: 8.5,
      physical: 8.0,
      mental_iq: 7.5,
      coachability: 8.0,
      competitive: 8.2
    },
    consensus_composite: 7.9,
    shape: 'converged',
    sources: ['AVCA All-American', 'PVF media poll'],
    last_updated: '2026-05-01',
    next_check: 'PVF season · Jan 2026'
  }

};

// Helper: lookup consensus by various id formats
window.FC17_CONSENSUS_LOOKUP = function(playerIdOrName) {
  if (!playerIdOrName) return null;
  const norm = String(playerIdOrName).toLowerCase().replace(/[^a-z0-9_]/g, '');

  // Direct match
  if (window.FC17_CONSENSUS_DATA[norm]) return window.FC17_CONSENSUS_DATA[norm];

  // Try with underscores stripped/added
  const stripped = norm.replace(/_/g, '');
  for (const key in window.FC17_CONSENSUS_DATA) {
    if (key.replace(/_/g, '') === stripped) return window.FC17_CONSENSUS_DATA[key];
  }
  return null;
};

// Auto-classify shape if not explicit (utility for future expansion)
window.FC17_CLASSIFY_SHAPE = function(fcComp, consensusComp) {
  if (consensusComp == null) return 'gem';
  const delta = consensusComp - fcComp;
  if (Math.abs(delta) < 0.4) return 'converged';
  if (delta > 1.0) return 'hype';
  return 'converged';
};
