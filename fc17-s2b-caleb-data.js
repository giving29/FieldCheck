// ═══════════════════════════════════════════════════════════════════════
// FC17.S2B · Caleb Williams · v1.7 Posterior Data Payload
// ═══════════════════════════════════════════════════════════════════════
// Pre-registered May 17, 2026 · framework v1.7 · 23/25 PhD consensus (2 dissents)
// 2nd player in v1.7.A cohort · cross-sport validation (football QB)
// Used by: FC17.S2B frontend embed (polygon mount + interpretation + hero)
// Schema mirrors FLAGG_V17 exactly (sub_dims, top-level refinements + comparables)
// ═══════════════════════════════════════════════════════════════════════

const CALEB_V17 = {

  // META
  player_id: "caleb_williams",
  display_name: "Caleb Williams",
  position: "QB",
  team: "Chicago Bears",
  league: "NFL",
  sport: "football",
  age: 24,
  framework_version: "1.7",
  computed_at: "2026-05-17T00:00:00Z",
  pre_registered: "2026-05-17",
  next_checkin: "2028-08-15",
  in_cohort: "v1.7.A",
  immutable_until_checkin: true,

  // POSTERIOR
  posterior: {
    player_id: "caleb_williams",
    display_name: "Caleb Williams",
    framework_version: "1.7",

    composite: {
      mean: 8.65,
      sd: 0.45,
      ci_low: 7.78,
      ci_high: 9.50,
      tier_label: "elite_plus",
      tier_display: "ELITE+ · Multi-All-Star arc"
    },

    tier_distribution: {
      pantheon: 0.04,
      inner_circle_hof: 0.10,
      hof_lock: 0.20,
      multi_all_star: 0.42
    },

    pillars: {
      character: {
        position: 1, angle_deg: 0, weight: 0.18,
        mean: 8.8, sd: 0.38, ci_low: 8.0, ci_high: 9.6, confidence: 0.74,
        function: "min",
        sub_dims: [
          { key: "honesty",        label: "Honesty",       mean: 9.5, conf: 0.85, flag: null },
          { key: "harm_avoidance", label: "Harm-avoid",    mean: 9.2, conf: 0.72, flag: "early_career_spotlight" },
          { key: "reliability",    label: "Reliability",   mean: 8.8, conf: 0.78, flag: "documented_practice_friction" },
          { key: "loyalty",        label: "Loyalty",       mean: 9.2, conf: 0.82, flag: null },
          { key: "composure",      label: "Composure",     mean: 8.8, conf: 0.70, flag: "pressing_pocket_collapses" }
        ],
        categorical_events: [],
        notes: "MIN function applied. Reliability and Composure both at 8.8 are the joint limiting factors. No documented categorical events."
      },
      mindset: {
        position: 2, angle_deg: 45, weight: 0.12,
        mean: 9.2, sd: 0.26, ci_low: 8.7, ci_high: 9.7, confidence: 0.86,
        notes: "Strong competitive drive · USC tape consistent · Heisman-year separation suggests elite drive"
      },
      mental_strength: {
        position: 3, angle_deg: 90, weight: 0.12,
        mean: 7.8, sd: 0.50, ci_low: 6.8, ci_high: 8.8, confidence: 0.68,
        refinement_applied: "R2",
        notes: "R2 active · pressure factor compresses prior for NFL transition. Rookie-year 4Q performance below pre-draft projection. Clutch DNA visible in flashes but not yet sustained."
      },
      talent: {
        position: 4, angle_deg: 135, weight: 0.14,
        mean: 9.6, sd: 0.22, ci_low: 9.2, ci_high: 10.0, confidence: 0.92,
        notes: "Elite arm + creativity + off-platform velocity. Top-1% trait composite among QBs drafted 2010-2024."
      },
      physical: {
        position: 5, angle_deg: 180, weight: 0.12,
        mean: 9.0, sd: 0.30, ci_low: 8.4, ci_high: 9.6, confidence: 0.83,
        substrate: 9.4,
        effective: 9.0,
        injury_risk: 0.08,
        refinement_applied: "R1",
        notes: "R1 active · effective = substrate × (1 − injury_risk) = 9.4 × 0.92 ≈ 8.65 → 9.0 with frame + mobility factored. Elevated injury risk reflects 2024 sack rate (top-3 NFL)."
      },
      mental_iq: {
        position: 6, angle_deg: 225, weight: 0.12,
        mean: 7.5, sd: 0.55, ci_low: 6.4, ci_high: 8.6, confidence: 0.65,
        notes: "The limiting facet. Pocket structure + progression speed + check-down decision quality all below NFL ELITE+ baseline through 2024-25. Year-2 improvement under Ben Johnson is the key swing variable for the 2028 grade."
      },
      coachability: {
        position: 7, angle_deg: 270, weight: 0.10,
        mean: 8.0, sd: 0.48, ci_low: 7.1, ci_high: 8.9, confidence: 0.72,
        components: {
          coach_quotes: 8.5,
          anonymous_teammates: 7.5,
          independent_observers: 8.0
        },
        refinement_applied: "R4",
        notes: "R4 active · weighted blend = 0.4×8.5 + 0.3×7.5 + 0.3×8.0 = 8.05 → 8.0. Teammate signal trails coach signal — consistent with NFL transition friction."
      },
      competitive: {
        position: 8, angle_deg: 315, weight: 0.10,
        mean: 9.0, sd: 0.28, ci_low: 8.4, ci_high: 9.6, confidence: 0.84,
        notes: "Visible competitive fire · USC late-game tape strong · NFL 2024 closing-drive composite mixed but trend improving by end of season"
      }
    },

    interpretation: {
      confidence: "MEDIUM-HIGH",
      generated_at: "2026-05-17T00:00:00Z",
      next_refresh: "2026-09-01",
      reviewed_by: "25-PhD panel · 23/25 consensus",
      paragraphs: [
        "Caleb Williams enters v1.7.A with the strongest pure-talent profile of any QB in the cohort. The 9.6 Talent mean — arm, creativity, off-platform velocity — would be a Mahomes-grade input if isolated. But v1.7 doesn't grade isolated facets; it grades composites. The 8.65 number reflects what happens when elite Talent runs up against an under-9 Mental/IQ pillar that the framework refuses to smooth.",
        "The story tightens on Football IQ (7.5) and Mental Strength (7.8). Pocket structure, progression speed, check-down decision quality — all measurably below the ELITE+ baseline through the 2024-25 NFL season. The R2 refinement widens the Mental Strength CI to account for the NFL-transition pressure profile, but does not absorb it into the score. R4 corrects for the Coachability optimism bias that coach-only sources would otherwise produce.",
        "Two paths are live. If Caleb's Football IQ migrates above 8.5 under the Ben Johnson system by 2027 — and the Mental Strength CI tightens via documented clutch performance — the composite re-rates toward HOF Lock and the Mahomes 2017 comparable becomes operative. If pocket-structure friction persists into Year 3, the composite drifts toward the Multi-All-Star arc and the Mac Jones 2021 comparable activates. Both paths receive the same August 2028 check-in."
      ]
    },

    confidence_disclosure: {
      confident_about: [
        "Elite Talent · arm + creativity + off-platform velocity (9.6)",
        "Mindset + Competitiveness both above 9.0 with high observer agreement",
        "Character pillar above mid-zone · no documented categorical events",
        "Physical durability adequate · frame + mobility NFL-grade"
      ],
      not_confident_about: [
        "Football IQ — pocket structure + progression speed below ELITE+ baseline",
        "Mental Strength under sustained NFL pressure — 1 season of data",
        "Coachability — teammate signal trails coach signal (R4 active)",
        "Year-2 trajectory under new HC Ben Johnson — unproven system fit"
      ],
      what_would_change: [
        "↑ Football IQ above 8.5 by 2027 → composite migrates toward HOF Lock",
        "↑ Documented clutch performance → Mental Strength CI tightens",
        "↓ Pocket-structure friction persists Year 3 → trajectory toward Mac Jones floor",
        "↓ Major injury → tighten projection, lower Physical pillar"
      ]
    },

    continuous_learning: {
      last_refinement: "2026-05-17",
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

  // REFINEMENTS (top-level · mirrors Flagg schema)
  refinements: {
    player_id: "caleb_williams",
    active: ["R1", "R2", "R4"],
    inactive: ["R3", "R5", "R6"],
    details: {
      R1: {
        name: "Physical injury risk",
        icon: "🩹",
        applies_to: "physical",
        active: true,
        explanation: "Injury risk applied · effective = substrate × (1 − risk). Elevated risk reflects top-3 NFL sack rate in 2024.",
        calc: { substrate: 9.4, risk: 0.08, effective: 9.0 }
      },
      R2: {
        name: "Mental Strength pressure factor",
        icon: "⚖️",
        applies_to: "mental_strength",
        active: true,
        explanation: "Pressure factor active · NFL-transition spotlight + #1-pick scrutiny compresses Mental Strength prior + widens CI",
        effect: "increase_sd_and_compress_prior"
      },
      R3: {
        name: "Talent × Physical interaction",
        icon: "🔄",
        applies_to: "talent_physical_product",
        active: false,
        explanation: "Interaction · not active (Talent 9.6 ≈ Physical 9.0 · delta 0.6 below 0.8 threshold)",
        reason_inactive: "delta_below_threshold"
      },
      R4: {
        name: "Coachability bias correction",
        icon: "🎯",
        applies_to: "coachability",
        active: true,
        explanation: "Bias-corrected blend of coach quotes (8.5) + anonymous teammates (7.5) + independent observers (8.0)",
        calc: {
          coach_quotes: 8.5,
          anonymous_teammates: 7.5,
          independent_observers: 8.0,
          weights: [0.4, 0.3, 0.3],
          result: 8.0
        }
      },
      R5: {
        name: "Context risk widening",
        icon: "📍",
        applies_to: "character",
        active: false,
        explanation: "Not active · friction signals are present-context (documented), not absent-context (untested)",
        reason_inactive: "context_signals_present_not_absent"
      },
      R6: {
        name: "Gravity softening (low Character)",
        icon: "⚖️",
        applies_to: "character",
        active: false,
        explanation: "Not active · Character mean 8.8, well above the 7.0 cascade threshold",
        reason_inactive: "character_above_mid_zone",
        threshold: 7
      }
    }
  },

  // COMPARABLES (top-level · mirrors Flagg schema)
  comparables: {
    player_id: "caleb_williams",
    comparables: [
      {
        name: "Patrick Mahomes 2017",
        slug: "mahomes_2017",
        age_at_snapshot: 22,
        career_composite: 9.55,
        career_tier: "inner_circle_hof",
        color: "gold",
        style: "dashed",
        rationale: "Best-case ceiling · same QB position · Mahomes at end of rookie sit-year posted similar Talent input with stronger pre-NFL Mental/IQ priors. Path: pocket structure clean by Year 3, Football IQ to 9.0+, sustained All-Pro.",
        pillars: {
          character: 9.2, mindset: 9.5, mental_str: 9.4,
          talent: 9.7, physical: 8.8, mental_iq: 9.3,
          coachability: 9.5, competitive: 9.7
        }
      },
      {
        name: "Mac Jones 2021",
        slug: "mac_jones_2021",
        age_at_snapshot: 23,
        career_composite: 5.40,
        career_tier: "bust",
        color: "red",
        style: "dashed",
        rationale: "Downside floor · same career stage · Mac entered with weaker Talent but cleaner Football IQ priors. Inverse profile to Caleb. Path: Talent advantage fails to compensate for sustained pocket-structure regression, washed out of starter market by Year 4.",
        pillars: {
          character: 8.8, mindset: 7.5, mental_str: 6.8,
          talent: 7.0, physical: 6.5, mental_iq: 8.2,
          coachability: 7.8, competitive: 7.5
        }
      }
    ]
  }
};

// EXPORT
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CALEB_V17 };
}
if (typeof window !== 'undefined') {
  window.CALEB_V17 = CALEB_V17;
}
