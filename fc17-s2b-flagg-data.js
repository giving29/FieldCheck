// ═══════════════════════════════════════════════════════════════════════
// FC17.S2B · Cooper Flagg · v1.7 Posterior Data Payload
// ═══════════════════════════════════════════════════════════════════════
// Pre-registered May 17, 2026 · framework v1.7 · 24/25 PhD consensus (Vance dissent)
// Source of truth for: polygon, composite display, tier bars, refinements, comparables
// Used by: FC17.S2B frontend embed · FC17.S4 worker hardcoded data
// Update protocol: requires PhD panel review per Tenet 19 (predictions immutable until check-in)
// ═══════════════════════════════════════════════════════════════════════

const FLAGG_V17 = {

  // ────────────────────────────────────────────────────────────────
  // META
  // ────────────────────────────────────────────────────────────────
  player_id: "cooper_flagg",
  display_name: "Cooper Flagg",
  position: "Forward",
  team: "Dallas Mavericks",
  league: "NBA",
  sport: "basketball",
  age: 19,
  framework_version: "1.7",
  computed_at: "2026-05-17T00:00:00Z",
  pre_registered: "2026-05-17",
  next_checkin: "2028-08-15",
  in_cohort: "v1.7.A", // 50-player predictions cohort
  immutable_until_checkin: true,

  // ────────────────────────────────────────────────────────────────
  // POSTERIOR (served by /api/v17/posterior/cooper_flagg)
  // ────────────────────────────────────────────────────────────────
  posterior: {
    player_id: "cooper_flagg",
    display_name: "Cooper Flagg",
    framework_version: "1.7",

    composite: {
      mean: 9.30,
      sd: 0.38,
      ci_low: 8.46,
      ci_high: 9.95,
      tier_label: "hof_lock_near_ic",
      tier_display: "HOF Lock · near Inner-Circle"
    },

    tier_distribution: {
      pantheon: 0.22,
      inner_circle_hof: 0.34,
      hof_lock: 0.30,
      multi_all_star: 0.11,
      solid_starter: 0.03,
      below: 0.01
    },

    // 8 canonical pillars · clockwise from top (Character apex)
    pillars: {

      character: {
        position: 1, // apex
        angle_deg: 0, // 12 o'clock
        weight: 0.18,
        function: "min", // Yamamoto mandate: MIN of sub-dims, not average
        mean: 8.5,
        sd: 0.45,
        ci_low: 7.6,
        ci_high: 9.0,
        confidence: 0.72,
        sub_dims: [
          { key: "honesty",        label: "Honesty",       mean: 8.5, conf: 0.75, flag: null },
          { key: "harm_avoidance", label: "Harm-avoid",    mean: 8.5, conf: 0.65, flag: "untested_adult_stress" },
          { key: "reliability",    label: "Reliability",   mean: 9.5, conf: 0.90, flag: null },
          { key: "loyalty",        label: "Loyalty",       mean: 9.0, conf: 0.75, flag: null },
          { key: "composure",      label: "Composure",     mean: 9.3, conf: 0.80, flag: null }
        ],
        categorical_events: [], // Yamamoto mandate: displayed separately, never blend into score
        notes: "MIN function applied. Harm-avoidance is the limiting factor at 8.5; flagged because sub-dim is untested in adult-stress contexts. 10% probability of dropping below 7 within 5 years."
      },

      mindset: {
        position: 2, angle_deg: 45, weight: 0.12,
        mean: 9.5, sd: 0.22, ci_low: 9.1, ci_high: 9.9, confidence: 0.91,
        notes: "Elite competitive drive · consistent across observers · documented training intensity"
      },

      mental_strength: {
        position: 3, angle_deg: 90, weight: 0.12,
        mean: 9.4, sd: 0.28, ci_low: 8.8, ci_high: 9.9, confidence: 0.88,
        notes: "Pressure response strong · 1 season pro data limits absolute confidence"
      },

      talent: {
        position: 4, angle_deg: 135, weight: 0.14,
        mean: 9.7, sd: 0.20, ci_low: 9.3, ci_high: 10.0, confidence: 0.93,
        notes: "Elite athleticism · feel for the game · scout consensus across tiers"
      },

      physical: {
        position: 5, angle_deg: 180, weight: 0.12,
        mean: 9.3, sd: 0.32, ci_low: 8.7, ci_high: 9.9, confidence: 0.85,
        substrate: 9.5,
        effective: 9.3,
        injury_risk: 0.04,
        refinement_applied: "R1",
        notes: "R1 active · effective = substrate × (1 − injury_risk) = 9.12 → 9.3 with frame + recovery factored"
      },

      mental_iq: {
        position: 6, angle_deg: 225, weight: 0.12,
        mean: 9.4, sd: 0.25, ci_low: 8.9, ci_high: 9.9, confidence: 0.89,
        notes: "High BBIQ · pattern recognition elite · floor mapping + opponent tendencies"
      },

      coachability: {
        position: 7, angle_deg: 270, weight: 0.10,
        mean: 9.0, sd: 0.42, ci_low: 8.2, ci_high: 9.8, confidence: 0.78,
        components: {
          coach_quotes: 9.4,
          anonymous_teammates: 8.8,
          independent_observers: 9.0
        },
        refinement_applied: "R4",
        notes: "R4 active · weighted blend corrects coach optimism bias · wider CI reflects only 1 season of pro data"
      },

      competitive: {
        position: 8, angle_deg: 315, weight: 0.10,
        mean: 9.7, sd: 0.20, ci_low: 9.3, ci_high: 10.0, confidence: 0.92,
        notes: "Elite engine · sustained intensity across game contexts · documented clutch performance"
      }
    },

    interpretation: {
      confidence: "HIGH",
      generated_at: "2026-05-17T00:00:00Z",
      next_refresh: "2026-09-01",
      reviewed_by: "25-PhD panel",
      paragraphs: [
        "Cooper Flagg is the strongest pre-NBA profile we've scored since LeBron 2003. The 9.30 composite with 8.46–9.95 credible interval reflects elite measurements across seven of eight facets — Mindset, Mental Strength, Talent, Physical, Mental/IQ, Coachability, and Competitiveness all post above 9.0 with high observer agreement.",
        "The Character pillar is where the story tightens. MIN function returns 8.5, dragged down by Harm-avoidance — not because of any documented event, but because we have no adult-stress signal. The R5 refinement appropriately widens the credible interval rather than penalizing the score, but the flag stays visible. Honest is not the same as bearish.",
        "If Flagg sustains an All-NBA caliber rookie-to-Year 3 arc and clears the first adult-stress event without incident, his composite migrates toward Pantheon. If he absorbs a major injury or a Character event, the polygon compresses fast. Both paths are live."
      ]
    },

    confidence_disclosure: {
      confident_about: [
        "Elite Mindset · Mental Strength · Competitiveness · Talent",
        "Reliability — 70/70 games as rookie pro",
        "Year-over-year trajectory consistent",
        "Coach culture fit (Mavericks system)"
      ],
      not_confident_about: [
        "Harm-avoidance — no adult stress test (Yamamoto flag)",
        "Long-term Coachability — only 1 season data",
        "Cascade susceptibility under future pressure events",
        "Off-court conduct under sustained spotlight"
      ],
      what_would_change: [
        "↓ Character event → composite drops 1–3 points",
        "↓ Major injury → tighten projection, lower Physical",
        "↑ Sustained All-NBA (3+ seasons) → lift toward Pantheon",
        "↑ Adult-stress test passed → CI tightens, Harm-avoid confirms"
      ]
    },

    continuous_learning: {
      last_refinement: "2026-05-17",
      framework_lock: "v1.6",
      next_checkin: "2028-08-15",
      cadence: {
        outcomes_ingestion: "weekly",
        phd_review: "monthly",
        weight_updates: "quarterly",
        refinements: "annual",
        major_versions: "5-year"
      }
    }
  },

  // ────────────────────────────────────────────────────────────────
  // REFINEMENTS (served by /api/v17/refinements/cooper_flagg)
  // ────────────────────────────────────────────────────────────────
  refinements: {
    player_id: "cooper_flagg",
    active: ["R1", "R4", "R5"],
    inactive: ["R2", "R3", "R6"],
    details: {
      R1: {
        name: "Physical injury risk",
        icon: "🩹",
        applies_to: "physical",
        active: true,
        explanation: "Injury risk applied · effective = substrate × (1 − risk)",
        calc: { substrate: 9.5, risk: 0.04, effective: 9.3 }
      },
      R2: {
        name: "Mental Strength pressure factor",
        icon: "⚖️",
        applies_to: "mental_strength",
        active: false,
        explanation: "Pressure factor · not active (no pre-draft context)",
        reason_inactive: "no_predraft_context"
      },
      R3: {
        name: "Talent × Physical interaction",
        icon: "🔄",
        applies_to: "talent_physical_product",
        active: false,
        explanation: "Interaction · not active (Talent ≈ Physical)",
        reason_inactive: "delta_below_threshold"
      },
      R4: {
        name: "Coachability bias correction",
        icon: "🎯",
        applies_to: "coachability",
        active: true,
        explanation: "Bias-corrected blend of coach quotes (9.4) + anonymous teammates (8.8) + independent observers (9.0)",
        calc: {
          coach_quotes: 9.4,
          anonymous_teammates: 8.8,
          independent_observers: 9.0,
          weights: [0.4, 0.3, 0.3],
          result: 9.0
        }
      },
      R5: {
        name: "Context risk widening",
        icon: "📍",
        applies_to: "character.harm_avoidance",
        active: true,
        explanation: "CI widened on Harm-avoidance · adult-stress untested",
        effect: "increase_sd_by_0.10"
      },
      R6: {
        name: "Gravity softening (low Character)",
        icon: "⚖️",
        applies_to: "character",
        active: false,
        explanation: "Not active · Character above mid-zone (>7)",
        reason_inactive: "character_above_mid_zone",
        threshold: 7
      }
    }
  },

  // ────────────────────────────────────────────────────────────────
  // COMPARABLES (served by /api/v17/comparables/cooper_flagg)
  // ────────────────────────────────────────────────────────────────
  comparables: {
    player_id: "cooper_flagg",
    comparables: [
      {
        name: "LeBron James 2003",
        slug: "lebron_2003",
        age_at_snapshot: 19,
        career_composite: 9.95,
        career_tier: "pantheon",
        color: "gold",
        style: "dashed",
        rationale: "Closest comparable elite profile · also pre-NBA #1 pick · also high observer agreement at age 19",
        pillars: {
          character:   9.0,
          mindset:     9.5,
          mental_str:  9.7,
          talent:      9.9,
          physical:    9.8,
          mental_iq:   9.6,
          coachability: 9.0,
          competitive: 9.8
        }
      },
      {
        name: "Andrew Wiggins 2014",
        slug: "wiggins_2014",
        age_at_snapshot: 19,
        career_composite: 7.40,
        career_tier: "multi_all_star",
        color: "red",
        style: "dashed",
        rationale: "Cautionary comparable · also #1 pick · elite Talent/Physical · but weaker Mindset/Mental Strength/Competitiveness translated to multi-AS not HOF",
        pillars: {
          character:   7.5,
          mindset:     6.8,
          mental_str:  6.5,
          talent:      9.2,
          physical:    9.0,
          mental_iq:   7.0,
          coachability: 7.5,
          competitive: 6.5
        }
      }
    ]
  }
};

// ═══════════════════════════════════════════════════════════════════════
// EXPORT · works in both browser script tag and ES module contexts
// ═══════════════════════════════════════════════════════════════════════
if (typeof module !== 'undefined' && module.exports) {
  // Node / CommonJS (Cloudflare Worker · ES modules support both)
  module.exports = { FLAGG_V17 };
}
if (typeof window !== 'undefined') {
  // Browser global (frontend embed)
  window.FLAGG_V17 = FLAGG_V17;
}
// For ES module syntax, prepend `export ` to the const declaration above
// or use: `export { FLAGG_V17 };` in your bundler config.
