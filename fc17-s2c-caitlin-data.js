// ═══════════════════════════════════════════════════════════════════════
// FC17.S2C · Caitlin Clark · v1.7 Posterior Data Payload
// ═══════════════════════════════════════════════════════════════════════
// Pre-registered May 19, 2026 · framework v1.7 · 23/25 PhD consensus
// Source of truth for: polygon, composite display, tier bars, refinements, comparables
// Used by: FC17.S2C frontend embed · FC17.S4 worker hardcoded data
// Update protocol: requires PhD panel review per Tenet 19 (predictions immutable until check-in)
// ═══════════════════════════════════════════════════════════════════════

const CAITLIN_V17 = {

  // ────────────────────────────────────────────────────────────────
  // META
  // ────────────────────────────────────────────────────────────────
  player_id: "caitlin_clark",
  display_name: "Caitlin Clark",
  position: "Guard",
  team: "Indiana Fever",
  league: "WNBA",
  sport: "womens-basketball",
  age: 24,
  framework_version: "1.7",
  computed_at: "2026-05-19T00:00:00Z",
  pre_registered: "2026-05-19",
  next_checkin: "2028-08-15",
  in_cohort: "v1.7.A", // 50-player predictions cohort
  immutable_until_checkin: true,

  // ────────────────────────────────────────────────────────────────
  // POSTERIOR (served by /api/v17/posterior/caitlin_clark)
  // ────────────────────────────────────────────────────────────────
  posterior: {
    player_id: "caitlin_clark",
    display_name: "Caitlin Clark",
    framework_version: "1.7",

    composite: {
      mean: 9.05,
      sd: 0.42,
      ci_low: 8.20,
      ci_high: 9.65,
      tier_label: "icon",
      tier_display: "ICON · WNBA Franchise Tier"
    },

    tier_distribution: {
      pantheon: 0.04,
      inner_circle_hof: 0.18,
      hof_lock: 0.32,
      multi_all_star: 0.38,
      solid_starter: 0.07,
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
        confidence: 0.74,
        sub_dims: [
          { key: "honesty",        label: "Honesty",       mean: 9.0, conf: 0.80, flag: null },
          { key: "harm_avoidance", label: "Harm-avoid",    mean: 8.5, conf: 0.62, flag: "untested_adult_stress" },
          { key: "reliability",    label: "Reliability",   mean: 9.5, conf: 0.88, flag: null },
          { key: "loyalty",        label: "Loyalty",       mean: 9.0, conf: 0.76, flag: null },
          { key: "composure",      label: "Composure",     mean: 8.5, conf: 0.72, flag: "documented_ref_frustration" }
        ],
        categorical_events: [], // Yamamoto mandate: displayed separately, never blend into score
        notes: "MIN function applied. Harm-avoidance and Composure tied at 8.5 — Harm-avoid flagged for untested adult-stress; Composure flagged for documented on-court referee frustration (low-severity, repeated)."
      },

      mindset: {
        position: 2, angle_deg: 45, weight: 0.12,
        mean: 9.4, sd: 0.24, ci_low: 8.9, ci_high: 9.8, confidence: 0.89,
        notes: "Elite competitive drive · documented training intensity · 'I can do anything' confidence pattern · transformative Iowa-era impact on women's basketball viewership"
      },

      mental_strength: {
        position: 3, angle_deg: 90, weight: 0.12,
        mean: 9.2, sd: 0.34, ci_low: 8.5, ci_high: 9.8, confidence: 0.82,
        refinement_applied: "R2",
        notes: "R2 active · #1-pick + media-spotlight pressure factor compresses prior · widens CI. Iowa Final Four runs (2023, 2024) provide ceiling evidence."
      },

      talent: {
        position: 4, angle_deg: 135, weight: 0.14,
        mean: 9.6, sd: 0.22, ci_low: 9.1, ci_high: 9.9, confidence: 0.92,
        notes: "Generational shooting range · elite court vision + passing · pattern recognition + read-the-floor IQ baked into Talent signal"
      },

      physical: {
        position: 5, angle_deg: 180, weight: 0.12,
        mean: 7.2, sd: 0.38, ci_low: 6.4, ci_high: 7.9, confidence: 0.78,
        substrate: 7.6,
        effective: 7.2,
        injury_risk: 0.05,
        refinement_applied: "R1",
        notes: "R1 active · effective = substrate × (1 − injury_risk) = 7.22. Smaller frame caps athletic ceiling vs WNBA peers · documented quad/groin issues rookie year warrant elevated risk band."
      },

      mental_iq: {
        position: 6, angle_deg: 225, weight: 0.12,
        mean: 9.5, sd: 0.22, ci_low: 9.0, ci_high: 9.9, confidence: 0.90,
        notes: "Court IQ elite · defensive read-rate + passing-lane recognition above 95th percentile · pre-pass anticipation pattern documented across Iowa + WNBA tape"
      },

      coachability: {
        position: 7, angle_deg: 270, weight: 0.10,
        mean: 8.8, sd: 0.46, ci_low: 7.9, ci_high: 9.6, confidence: 0.74,
        components: {
          coach_quotes: 9.3,
          anonymous_teammates: 8.2,
          independent_observers: 8.7
        },
        refinement_applied: "R4",
        notes: "R4 active · blend corrects coach optimism bias. Teammate signal slightly cooler than coach signal — friction with veterans documented but not pattern-level. Wider CI reflects 2 seasons pro data."
      },

      competitive: {
        position: 8, angle_deg: 315, weight: 0.10,
        mean: 9.6, sd: 0.22, ci_low: 9.1, ci_high: 9.9, confidence: 0.91,
        notes: "Elite engine · sustained intensity · documented clutch performance from college through pro · refuses-to-lose pattern across all observed contexts"
      }
    },

    interpretation: {
      confidence: "HIGH",
      generated_at: "2026-05-19T00:00:00Z",
      next_refresh: "2026-09-01",
      reviewed_by: "25-PhD panel",
      paragraphs: [
        "Caitlin Clark is a compressed-risk ICON profile — elite signal across Mindset, Talent, Mental/IQ, Competitiveness, with the Physical pillar acting as the gravity-well that defines her ceiling and floor. The 9.05 composite with 8.20–9.65 credible interval reflects exceptional skill and competitive engine balanced against frame-driven Physical ceiling (7.2 effective).",
        "Five active refinements (R1, R2, R3, R4, R5) make this one of the most actively-corrected profiles in the v1.7 cohort. R3 fires because of the 2.4-delta between Talent (9.6) and Physical (7.2) — interaction tension, not multiplicative gain. R1 compresses Physical for injury history + frame. R2 widens Mental Strength CI for #1-pick spotlight pressure. R4 blends Coachability across coach + teammate + observer. R5 widens Character CI on Harm-avoid (untested adult stress) and Composure (documented ref-frustration pattern).",
        "If Clark sustains a 5-year All-WNBA arc and her body holds against the 36-game grind, the composite migrates toward Inner-Circle HOF — the path Diana Taurasi 2006 (9.7 career) walked. If injuries compound or the spotlight metastasizes into composure events, the profile compresses toward the Kelsey Plum 2018 trajectory (7.5 career · solid multi-AS). Both paths are live and the next 24 months will move the needle hard."
      ]
    },

    confidence_disclosure: {
      confident_about: [
        "Elite Mindset · Talent · Mental/IQ · Competitiveness",
        "Court IQ · pattern recognition · pre-pass anticipation",
        "Reliability — durability through 38-game college seasons",
        "Generational shooting range (50+ ft pull-up evidenced)"
      ],
      not_confident_about: [
        "Long-term Physical durability — frame + WNBA grind compound risk",
        "Harm-avoidance — no adult stress test (Yamamoto flag)",
        "Composure under sustained media spotlight — early friction signals",
        "Locker-room veteran integration — only 2 seasons data"
      ],
      what_would_change: [
        "↓ Major injury event → compresses Physical further, lowers composite 0.5–1.0",
        "↓ Composure event (escalated ref/teammate friction) → CI compresses on Character",
        "↑ Sustained All-WNBA (3+ seasons) → lift toward Inner-Circle HOF",
        "↑ International gold (Olympics 2028) → confirms ceiling, tightens CI"
      ]
    },

    continuous_learning: {
      last_refinement: "2026-05-19",
      framework_lock: "v1.7",
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
  // REFINEMENTS (served by /api/v17/refinements/caitlin_clark)
  // ────────────────────────────────────────────────────────────────
  refinements: {
    player_id: "caitlin_clark",
    active: ["R1", "R2", "R3", "R4", "R5"],
    inactive: ["R6"],
    details: {
      R1: {
        name: "Physical injury risk",
        icon: "🩹",
        applies_to: "physical",
        active: true,
        explanation: "Injury risk applied · effective = substrate × (1 − risk). Elevated risk reflects smaller frame + documented quad/groin issues rookie WNBA year.",
        calc: { substrate: 7.6, risk: 0.05, effective: 7.2 }
      },
      R2: {
        name: "Mental Strength pressure factor",
        icon: "⚖️",
        applies_to: "mental_strength",
        active: true,
        explanation: "Pressure factor active · #1-pick spotlight + women's-basketball-cultural-moment scrutiny compresses Mental Strength prior + widens CI",
        effect: "increase_sd_by_0.12"
      },
      R3: {
        name: "Talent × Physical interaction",
        icon: "🔄",
        applies_to: "talent_physical_product",
        active: true,
        explanation: "Interaction active · Talent 9.6 vs Physical 7.2 · delta 2.4 above 0.8 threshold · tension dampens raw multiplicative gain",
        calc: { talent: 9.6, physical: 7.2, delta: 2.4, threshold: 0.8, effect: "dampen_multiplicative" }
      },
      R4: {
        name: "Coachability bias correction",
        icon: "🎯",
        applies_to: "coachability",
        active: true,
        explanation: "Bias-corrected blend of coach quotes (9.3) + anonymous teammates (8.2) + independent observers (8.7)",
        calc: {
          coach_quotes: 9.3,
          anonymous_teammates: 8.2,
          independent_observers: 8.7,
          weights: [0.4, 0.3, 0.3],
          result: 8.79
        }
      },
      R5: {
        name: "Context risk widening",
        icon: "📍",
        applies_to: "character.harm_avoidance + character.composure",
        active: true,
        explanation: "CI widened on Harm-avoid (adult-stress untested) + Composure (documented ref-frustration pattern · low severity, repeated)",
        effect: "increase_sd_by_0.10"
      },
      R6: {
        name: "Gravity softening (low Character)",
        icon: "⚖️",
        applies_to: "character",
        active: false,
        explanation: "Not active · Character MIN 8.5, well above 7.0 cascade threshold",
        reason_inactive: "character_above_mid_zone",
        threshold: 7
      }
    }
  },

  // ────────────────────────────────────────────────────────────────
  // COMPARABLES (served by /api/v17/comparables/caitlin_clark)
  // ────────────────────────────────────────────────────────────────
  comparables: {
    player_id: "caitlin_clark",
    comparables: [
      {
        name: "Diana Taurasi 2006",
        slug: "taurasi_2006",
        age_at_snapshot: 24,
        career_composite: 9.70,
        career_tier: "pantheon",
        color: "gold",
        style: "dashed",
        rationale: "Ceiling comparable · also #1-pick WNBA · also generational scorer with elite IQ · 2-year-pro arc at age 24 mirror · sustained 18-year pantheon trajectory",
        pillars: {
          character:   9.0,
          mindset:     9.6,
          mental_str:  9.7,
          talent:      9.7,
          physical:    8.4,
          mental_iq:   9.7,
          coachability: 9.0,
          competitive: 9.8
        }
      },
      {
        name: "Kelsey Plum 2018",
        slug: "plum_2018",
        age_at_snapshot: 24,
        career_composite: 7.50,
        career_tier: "multi_all_star",
        color: "red",
        style: "dashed",
        rationale: "Floor comparable · also #1-pick WNBA · also elite-shooter college profile · but slower Physical + Mental Strength translation to pro = multi-AS not HOF arc · cautionary template",
        pillars: {
          character:   8.0,
          mindset:     8.5,
          mental_str:  7.2,
          talent:      8.8,
          physical:    7.5,
          mental_iq:   8.2,
          coachability: 8.0,
          competitive: 8.5
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
  module.exports = { CAITLIN_V17 };
}
if (typeof window !== 'undefined') {
  // Browser global (frontend embed)
  window.CAITLIN_V17 = CAITLIN_V17;
}
// For ES module syntax, prepend `export ` to the const declaration above
// or use: `export { CAITLIN_V17 };` in your bundler config.
