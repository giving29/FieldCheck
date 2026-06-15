// ═══════════════════════════════════════════════════════════════════════
// FC17.S2D · Avery Skinner · v1.7 Posterior Data Payload
// ═══════════════════════════════════════════════════════════════════════
// Pre-registered May 20, 2026 · framework v1.7 · 24/25 PhD consensus
// Source of truth for: polygon, composite display, tier bars, refinements, comparables
// Used by: FC17.S2D frontend embed · FC17.S4 worker hardcoded data
// Update protocol: requires PhD panel review per Tenet 19 (predictions immutable until check-in)
// Cross-sport validation #3 (women's volleyball — Captain DNA + Size + Reach labels)
// ═══════════════════════════════════════════════════════════════════════

const SKINNER_V17 = {

  // ────────────────────────────────────────────────────────────────
  // META
  // ────────────────────────────────────────────────────────────────
  player_id: "avery_skinner",
  display_name: "Avery Skinner",
  position: "OH", // Outside Hitter
  team: "USA Volleyball · Athletes Unlimited",
  league: "US National Team",
  sport: "womens-volleyball",
  age: 27,
  framework_version: "1.7",
  computed_at: "2026-05-20T00:00:00Z",
  pre_registered: "2026-05-20",
  next_checkin: "2028-08-15",
  in_cohort: "v1.7.A", // 50-player predictions cohort
  immutable_until_checkin: true,

  // ────────────────────────────────────────────────────────────────
  // POSTERIOR
  // ────────────────────────────────────────────────────────────────
  posterior: {
    player_id: "avery_skinner",
    display_name: "Avery Skinner",
    framework_version: "1.7",

    composite: {
      mean: 8.80,
      sd: 0.36,
      ci_low: 8.20,
      ci_high: 9.30,
      tier_label: "elite_plus",
      tier_display: "ELITE+ · USA Volleyball Established"
    },

    tier_distribution: {
      pantheon: 0.02,
      inner_circle_hof: 0.08,
      hof_lock: 0.18,
      multi_all_star: 0.52,
      solid_starter: 0.18,
      below: 0.02
    },

    // 8 canonical pillars · clockwise from top (Character apex)
    pillars: {

      character: {
        position: 1, // apex
        angle_deg: 0,
        weight: 0.18,
        function: "min",
        mean: 9.0,
        sd: 0.30,
        ci_low: 8.4,
        ci_high: 9.5,
        confidence: 0.88,
        sub_dims: [
          { key: "honesty",        label: "Honesty",       mean: 9.5, conf: 0.90, flag: null },
          { key: "harm_avoidance", label: "Harm-avoid",    mean: 9.0, conf: 0.85, flag: null },
          { key: "reliability",    label: "Reliability",   mean: 9.5, conf: 0.92, flag: null },
          { key: "loyalty",        label: "Loyalty",       mean: 9.0, conf: 0.82, flag: null },
          { key: "composure",      label: "Composure",     mean: 9.0, conf: 0.88, flag: null }
        ],
        categorical_events: [],
        notes: "MIN function applied. All 5 sub-dimensions land 9.0+ with high observer agreement — adult-stress contexts tested across 4yr college + 4yr pro + national-team play, no flags raised. Cleanest character profile in v1.7.A cohort."
      },

      mindset: {
        position: 2, angle_deg: 45, weight: 0.12,
        mean: 9.5, sd: 0.20, ci_low: 9.1, ci_high: 9.8, confidence: 0.93,
        notes: "Captain DNA elite · documented team-first leadership at Kentucky (2020 NCAA champion) → Athletes Unlimited captain → USA National Team selection 2024. Locker-room signal uniformly strong across observers."
      },

      mental_strength: {
        position: 3, angle_deg: 90, weight: 0.12,
        mean: 8.5, sd: 0.32, ci_low: 7.9, ci_high: 9.1, confidence: 0.81,
        notes: "Closer DNA proven at college level (NCAA championship match clutch reps) + AU finals. International stage still building — 2024 was first major USA rotation, 2025 confirmed starter trajectory."
      },

      talent: {
        position: 4, angle_deg: 135, weight: 0.14,
        mean: 8.2, sd: 0.26, ci_low: 7.7, ci_high: 8.7, confidence: 0.86,
        notes: "Refined all-phase attacker · technical hitting + serve + pass · not elite-athletic ceiling but well-developed skill stack across attack, defense, and serve-receive."
      },

      physical: {
        position: 5, angle_deg: 180, weight: 0.12,
        mean: 8.2, sd: 0.24, ci_low: 7.7, ci_high: 8.7, confidence: 0.88,
        notes: "Size + Reach solid · 6'2\" frame + good vertical · not max-elite by USA Nat Team OH standards (vs Larson-era reference). No injury history of note, durable across college + pro seasons."
      },

      mental_iq: {
        position: 6, angle_deg: 225, weight: 0.12,
        mean: 8.8, sd: 0.24, ci_low: 8.3, ci_high: 9.3, confidence: 0.89,
        notes: "Court IQ elite · pass-read + defensive positioning above 90th percentile · captain-archetype IQ pattern — sees the floor a half-second ahead of action. Lifts entire rotation's defensive structure."
      },

      coachability: {
        position: 7, angle_deg: 270, weight: 0.10,
        mean: 9.5, sd: 0.22, ci_low: 9.0, ci_high: 9.9, confidence: 0.93,
        components: {
          coach_quotes: 9.7,
          anonymous_teammates: 9.4,
          independent_observers: 9.4
        },
        refinement_applied: "R4",
        notes: "R4 active · coach + teammate + observer signals converge tightly on 9.4-9.7 range. Gold-standard coachability reputation across Kentucky + AU + USA Nat Team. Tightest CI in v1.7.A cohort."
      },

      competitive: {
        position: 8, angle_deg: 315, weight: 0.10,
        mean: 9.0, sd: 0.24, ci_low: 8.5, ci_high: 9.5, confidence: 0.90,
        notes: "Sustained competitive engine · documented across 4yr college + 4yr pro arc · refuses-to-lose pattern in 5-set matches · clutch serve-receive in pressure rotations late-tournament."
      }
    },

    interpretation: {
      confidence: "HIGH",
      generated_at: "2026-05-20T00:00:00Z",
      next_refresh: "2026-09-01",
      reviewed_by: "25-PhD panel",
      paragraphs: [
        "Avery Skinner is the clean-profile ELITE+ established-pro archetype — the v1.7 cohort's reference example of what 'no red flags, all signals positive' looks like at age 27. The 8.80 composite with 8.20–9.30 credible interval reflects elite Captain DNA (9.5), Coachability (9.5 with the tightest CI in the entire cohort), Character (9.0 MIN-floor with all sub-dims 9.0+), and Court IQ (8.8) — balanced against good-but-not-elite Talent (8.2) and Size + Reach (8.2) athletic ceiling.",
        "Only one active refinement — R4 Coachability bias correction — and it tightens her score rather than lowering it (coach quotes 9.7 + anonymous teammates 9.4 + independent observers 9.4 converge near-perfectly). R1, R2, R3, R5, R6 are all inactive: no injury history flags Physical, no compressed-pressure context spotlights Mental Strength, Talent and Physical sit at parity (delta 0.0 well below the 0.8 threshold so R3 doesn't fire), Character signals are fully tested at adult-stress level across college and pro, and Character MIN 9.0 sits well above the 7.0 cascade threshold. This is what a low-refinement clean profile looks like in v1.7 — contrast Caitlin Clark's 5-refinement compressed-risk profile or Caleb Williams' 3-refinement transition profile.",
        "If Skinner becomes a sustained USA Volleyball starter at LA 2028 and her Closer DNA (8.5) climbs through international medal-round reps, the composite migrates toward the Jordan Larson 2014 trajectory (9.3 career · pantheon). If injuries compound late-career or rotation usage decreases as younger talent emerges, she compresses toward Kelsey Robinson 2017 (7.8 career · solid multi-AS rotation player). The Larson path is the median expectation; the system is most confident about her durability, Captain DNA, and coachability — the three pillars least likely to regress."
      ]
    },

    confidence_disclosure: {
      confident_about: [
        "Elite Captain DNA · Coachability · Character · Court IQ",
        "Durability — 4 years college + 4 years pro, no injury flags",
        "Coach optimism convergence — 9.7 quotes match 9.4 anon teammates",
        "Reliability — clean character signal across 8 evaluation contexts"
      ],
      not_confident_about: [
        "International ceiling — only 2 USA Nat Team rotations data",
        "Closer DNA at medal-round level — untested at Olympic stage",
        "Late-career durability — projecting forward 5-7 years",
        "Sustained starter vs rotation player at LA 2028"
      ],
      what_would_change: [
        "↑ LA 2028 Olympics gold medal contribution → lift toward Inner-Circle HOF",
        "↑ USA Nat Team starter role 2 consecutive cycles → confirm ceiling",
        "↓ Major injury event → compresses Physical to 7.0–7.5 range",
        "↓ Younger talent displacement → ceiling shifts to multi-AS rotation"
      ]
    },

    continuous_learning: {
      last_refinement: "2026-05-20",
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
  // REFINEMENTS
  // ────────────────────────────────────────────────────────────────
  refinements: {
    player_id: "avery_skinner",
    active: ["R4"],
    inactive: ["R1", "R2", "R3", "R5", "R6"],
    details: {
      R1: {
        name: "Physical injury risk",
        icon: "🩹",
        applies_to: "physical",
        active: false,
        explanation: "Not active · no injury history flags · durable across 8 seasons",
        reason_inactive: "no_injury_history"
      },
      R2: {
        name: "Mental Strength pressure factor",
        icon: "⚖️",
        applies_to: "mental_strength",
        active: false,
        explanation: "Not active · no #1-pick or compressed-spotlight context · established pro trajectory",
        reason_inactive: "no_spotlight_pressure"
      },
      R3: {
        name: "Talent × Physical interaction",
        icon: "🔄",
        applies_to: "talent_physical_product",
        active: false,
        explanation: "Not active · Talent 8.2 ≈ Physical 8.2 · delta 0.0 below 0.8 threshold",
        reason_inactive: "delta_below_threshold"
      },
      R4: {
        name: "Coachability bias correction",
        icon: "🎯",
        applies_to: "coachability",
        active: true,
        explanation: "Bias-corrected blend of coach quotes (9.7) + anonymous teammates (9.4) + independent observers (9.4) — tightens CI, doesn't lower mean",
        calc: {
          coach_quotes: 9.7,
          anonymous_teammates: 9.4,
          independent_observers: 9.4,
          weights: [0.4, 0.3, 0.3],
          result: 9.52
        }
      },
      R5: {
        name: "Context risk widening",
        icon: "📍",
        applies_to: "character",
        active: false,
        explanation: "Not active · Character signals fully tested at adult-stress level (4 years pro + national team) · no untested context flags",
        reason_inactive: "all_contexts_tested"
      },
      R6: {
        name: "Gravity softening (low Character)",
        icon: "⚖️",
        applies_to: "character",
        active: false,
        explanation: "Not active · Character MIN 9.0, well above 7.0 cascade threshold",
        reason_inactive: "character_above_mid_zone",
        threshold: 7
      }
    }
  },

  // ────────────────────────────────────────────────────────────────
  // COMPARABLES
  // ────────────────────────────────────────────────────────────────
  comparables: {
    player_id: "avery_skinner",
    comparables: [
      {
        name: "Jordan Larson 2014",
        slug: "larson_2014",
        age_at_snapshot: 27,
        career_composite: 9.30,
        career_tier: "pantheon",
        color: "gold",
        style: "dashed",
        rationale: "Ceiling comparable · same position (OH) · also USA Nat Team established at age 27 · also Captain DNA archetype · longtime starter trajectory through 4 Olympic cycles + 2020 Tokyo gold · clean-profile pantheon path",
        pillars: {
          character:   9.4,
          mindset:     9.7,
          mental_str:  9.6,
          talent:      8.5,
          physical:    8.8,
          mental_iq:   9.5,
          coachability: 9.6,
          competitive: 9.5
        }
      },
      {
        name: "Kelsey Robinson 2017",
        slug: "robinson_2017",
        age_at_snapshot: 25,
        career_composite: 7.80,
        career_tier: "multi_all_star",
        color: "red",
        style: "dashed",
        rationale: "Floor comparable · also USA Nat Team OH · also solid Captain DNA + Coachability · but Talent + Physical translated to rotation-player rather than sustained starter at international level · cautionary template for late-career displacement",
        pillars: {
          character:   8.5,
          mindset:     8.8,
          mental_str:  8.0,
          talent:      7.8,
          physical:    7.8,
          mental_iq:   8.2,
          coachability: 8.8,
          competitive: 8.5
        }
      }
    ]
  }
};

// ═══════════════════════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════════════════════
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SKINNER_V17 };
}
if (typeof window !== 'undefined') {
  window.SKINNER_V17 = SKINNER_V17;
}
