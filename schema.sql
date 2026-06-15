-- FieldCheck v0.1 — D1 schema
--
-- Apply with:
--   wrangler d1 execute fieldcheck_db --remote --file=schema.sql
--
-- Two verdict tables (one per track), one shared catalyst corpus.
-- Same architectural pattern as EdgeCheck: separate verdict log per
-- product surface, single catalyst corpus that any verdict can cite.

-- ─── Player verdicts ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS player_verdicts (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  sport TEXT NOT NULL,
  verdict TEXT NOT NULL,         -- WALK_AWAY | VERIFY_FURTHER | REASONABLE_ADD | EDGE_DETECTED
  scores_json TEXT NOT NULL,     -- {trajectory, coachability, stability, verification}
  reasons_json TEXT,             -- per-dimension reasoning trace
  sources_json TEXT,             -- snapshot of all source data at verdict time
  narrative TEXT,                -- 3-paragraph Claude-generated summary
  created_at INTEGER NOT NULL,
  feedback_useful INTEGER,       -- 1=useful, 0=not, NULL=no feedback
  feedback_action TEXT,          -- 'recruited' | 'passed' | 'verified_further' | 'overrode'
  feedback_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_player_verdicts_slug ON player_verdicts(slug);
CREATE INDEX IF NOT EXISTS idx_player_verdicts_created ON player_verdicts(created_at DESC);

-- ─── Program verdicts ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS program_verdicts (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  sport TEXT NOT NULL,
  verdict TEXT NOT NULL,         -- WALK_AWAY | WORTH_A_LOOK | REASONABLE_CHOICE | EDGE_DETECTED
  scores_json TEXT NOT NULL,     -- {development, retention, cultural_health, promise_delivery}
  reasons_json TEXT,
  sources_json TEXT,
  narrative TEXT,
  created_at INTEGER NOT NULL,
  feedback_useful INTEGER,
  feedback_action TEXT,           -- 'committed' | 'passed' | 'transferred_in' | 'overrode'
  feedback_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_program_verdicts_slug ON program_verdicts(slug);
CREATE INDEX IF NOT EXISTS idx_program_verdicts_created ON program_verdicts(created_at DESC);

-- ─── Sports catalyst corpus (the moat) ─────────────────────
-- Same pattern as EdgeCheck's catalysts table. Every news event,
-- coaching change, NCAA infraction, transfer event, NIL deal becomes
-- a structured, time-stamped, source-attributed catalyst.
CREATE TABLE IF NOT EXISTS sport_catalysts (
  id TEXT PRIMARY KEY,
  source_url TEXT,
  source_label TEXT,
  captured_at TEXT NOT NULL,
  type TEXT NOT NULL,            -- coaching_change | ncaa_infraction | transfer_event | injury_report | recruiting_event | nil_deal | academic_event | cultural_event | other
  sentiment TEXT NOT NULL,       -- positive | negative | neutral
  summary TEXT NOT NULL,
  key_phrases_json TEXT,
  entities_json TEXT,
  affects_for_json TEXT,         -- player or program slugs this affects
  confidence INTEGER NOT NULL,   -- 1-10
  thesis_change TEXT,
  expires_at TEXT NOT NULL,
  hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sport_catalysts_expires ON sport_catalysts(expires_at);
CREATE INDEX IF NOT EXISTS idx_sport_catalysts_captured ON sport_catalysts(captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_sport_catalysts_type ON sport_catalysts(type, sentiment);
CREATE INDEX IF NOT EXISTS idx_sport_catalysts_hash ON sport_catalysts(hash);

-- ─── Verdict ↔ Catalyst attribution (provenance) ───────────
CREATE TABLE IF NOT EXISTS verdict_sport_catalysts (
  verdict_id TEXT NOT NULL,
  verdict_track TEXT NOT NULL,    -- 'player' | 'program'
  catalyst_id TEXT NOT NULL,
  weight REAL,
  attached_at TEXT NOT NULL,
  PRIMARY KEY (verdict_id, catalyst_id)
);
CREATE INDEX IF NOT EXISTS idx_verdict_sport_catalysts_v ON verdict_sport_catalysts(verdict_id);

-- ─── Stripe subscribers (substrate carryover) ──────────────
CREATE TABLE IF NOT EXISTS subscribers (
  email TEXT PRIMARY KEY,
  tier TEXT NOT NULL,             -- 'pro' | 'edge' | 'free'
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  status TEXT NOT NULL,           -- 'active' | 'canceled' | 'past_due' | 'trialing'
  founding_member INTEGER DEFAULT 0,  -- 1 if among first 1000 of tier
  created_at INTEGER NOT NULL,
  updated_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_subscribers_tier ON subscribers(tier);
