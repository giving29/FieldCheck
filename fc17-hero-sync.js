// ═══════════════════════════════════════════════════════════════════════
// FC17.S2A.3 · Hero Header v1.7 Sync · pre-implemented for Entry #005
// ═══════════════════════════════════════════════════════════════════════
//
// PURPOSE:
//   Resolves Entry #005 (hero header v1.7 alignment). For Cooper Flagg only,
//   the hero badge shows 9.6 ICON (legacy backend) but the v1.7 polygon
//   computes 9.30 ELITE+. Same player, two framework readings.
//
//   This module implements 3 of the 4 options from Canonical State V1.5
//   Entry #005 (options A/B/C). Option D (toggle UI) deferred.
//
// MODES:
//   'A' · LEGACY PRESERVED (default · no behavior change) · hero stays 9.6 ICON
//   'B' · V1.7 WINS FULLY · hero shows 9.30 + ELITE+ + 75% tier conversion
//   'C' · DUAL DISPLAY · hero shows "9.6 / 9.30 v1.7" + "ICON / ELITE+"
//
// HOW TO TEST (no redeploy required):
//   1. Deploy this module as part of Stage 1 ship (Block 14 sits inert in mode A)
//   2. Open Flagg verdict on dev
//   3. In browser console:  window.FC17_HERO_MODE = 'B'; FC17_HERO.apply();
//   4. Hero updates instantly. Try 'B', 'C', back to 'A' freely.
//
// HOW TO COMMIT A CHOICE (1-line code change):
//   Add to verdict.html before the hero-sync script tag:
//     <script>window.FC17_HERO_MODE = 'B';</script>   <!-- or 'C' -->
//
// ═══════════════════════════════════════════════════════════════════════

(function(){
  'use strict';

  // ─── slug normalization (matches fc17-polygon-mount.js) ─────────────
  function normalizeSlug(raw){
    if (!raw) return '';
    return String(raw).toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  // ─── canonical tier classifier (mirrors fieldcheck-verdict.html tc()) ──
  // v ≥ 9.5 → ICON · ≥ 8.5 → ELITE+ · ≥ 7.5 → ELITE · ≥ 6.5 → HIGH · else VERIFY
  function classifyTier(v){
    if (v == null) return { label: '--', cssClass: 't-nr' };
    if (v >= 9.5) return { label: 'ICON',   cssClass: 't-icon' };
    if (v >= 8.5) return { label: 'ELITE+', cssClass: 't-ep'   };
    if (v >= 7.5) return { label: 'ELITE',  cssClass: 't-ep'   };
    if (v >= 6.5) return { label: 'HIGH',   cssClass: 't-hi'   };
    return         { label: 'VERIFY', cssClass: 't-vf'   };
  }

  // ─── sport tier conversion baselines (mirrors verdict.html SPORT_TIER_BASELINES) ─
  // Tier conversion percentages by sport
  const SPORT_TIER_PCT = {
    'mens-basketball':   { ICON: 95, 'ELITE+': 75, ELITE: 45, HIGH: 18, VERIFY: 4 },
    'womens-basketball': { ICON: 88, 'ELITE+': 65, ELITE: 35, HIGH: 11, VERIFY: 3 },
    'womens-volleyball': { ICON: 94, 'ELITE+': 72, ELITE: 41, HIGH: 14, VERIFY: 3 },
    'mens-volleyball':   { ICON: 90, 'ELITE+': 68, ELITE: 38, HIGH: 12, VERIFY: 3 },
    'football':          { ICON: 98, 'ELITE+': 78, ELITE: 52, HIGH: 22, VERIFY: 8 },
    'baseball':          { ICON: 92, 'ELITE+': 70, ELITE: 38, HIGH: 12, VERIFY: 2 },
    'tennis':            { ICON: 90, 'ELITE+': 62, ELITE: 30, HIGH: 8,  VERIFY: 2 },
    'mens-soccer':       { ICON: 85, 'ELITE+': 58, ELITE: 28, HIGH: 9,  VERIFY: 2 },
    'default':           { ICON: 90, 'ELITE+': 68, ELITE: 38, HIGH: 14, VERIFY: 4 }
  };

  function getTierPct(sport, tierLabel){
    const key = String(sport || 'default').toLowerCase().trim().replace(/[_\s]+/g, '-');
    // Sport aliases (matches Block 9 adapter)
    const aliasMap = {
      'basketball':'mens-basketball',
      'volleyball':'womens-volleyball',
      'soccer':'mens-soccer'
    };
    const sportKey = aliasMap[key] || key;
    const baselines = SPORT_TIER_PCT[sportKey] || SPORT_TIER_PCT['default'];
    return baselines[tierLabel] || 0;
  }


  // ─── player data lookup (v1.7) ──────────────────────────────────────
  const PLAYER_GLOBALS = {
    'cooperflagg':  'FLAGG_V17',
    'calebwilliams': 'CALEB_V17',
    'caitlinclark': 'CAITLIN_V17',
    'averyskinner': 'SKINNER_V17'
  };
  function getPlayerData(playerName){
    const slug = normalizeSlug(playerName);
    const globalKey = PLAYER_GLOBALS[slug];
    if (!globalKey) return null;
    return window[globalKey] || null;
  }


  // ─── inject styles once (for Option C dual display + Option B animations) ─
  let stylesInjected = false;
  function injectStyles(){
    if (stylesInjected || document.getElementById('fc17-hero-styles')) return;
    const style = document.createElement('style');
    style.id = 'fc17-hero-styles';
    style.textContent = `
.fc17-hero-dual{
  display:inline-flex;align-items:baseline;gap:.18em;
  font-family:'Anton',sans-serif
}
.fc17-hero-dual .fc17-hero-legacy{
  color:#F5B800;font-size:1em;line-height:.95;letter-spacing:-.02em
}
.fc17-hero-dual .fc17-hero-sep{
  color:rgba(245,241,232,.32);font-size:.45em;font-weight:400;margin:0 .12em;line-height:1
}
.fc17-hero-dual .fc17-hero-v17{
  color:rgba(245,241,232,.74);font-size:.55em;line-height:1;letter-spacing:-.01em
}
.fc17-hero-dual .fc17-hero-v17-tag{
  font-family:'JetBrains Mono',monospace;font-size:.18em;font-weight:700;
  color:#6BAA5A;letter-spacing:1.5px;text-transform:uppercase;
  margin-left:.4em;vertical-align:.8em
}
.fc17-hero-tier-dual{
  display:inline-flex;gap:6px;align-items:center
}
.fc17-hero-tier-dual .fc17-tier-v17{
  font-size:.7em;opacity:.7;font-family:'JetBrains Mono',monospace;letter-spacing:.06em
}
.fc17-hero-mode-marker{
  display:none
}
[data-fc17-hero-mode]:not([data-fc17-hero-mode="A"]) .fc17-hero-mode-marker{
  display:inline-block;
  font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;
  color:rgba(78,201,192,.7);letter-spacing:.8px;text-transform:uppercase;
  background:rgba(78,201,192,.08);padding:2px 7px;border-radius:9999px;
  border:1px solid rgba(78,201,192,.25);margin-left:8px
}
@keyframes fc17-hero-fade-in{
  from{opacity:0;transform:translateY(2px)}
  to{opacity:1;transform:none}
}
.fc17-hero-fade{animation:fc17-hero-fade-in .4s ease}
    `;
    document.head.appendChild(style);
    stylesInjected = true;
  }


  // ─── snapshot original DOM state for revert capability ──────────────
  let snapshot = null;
  function snapshotOriginal(){
    if (snapshot) return;
    const snum = document.querySelector('.hscore .snum');
    const stier = document.querySelector('.hscore .stier');
    const trsLbl = document.querySelector('.tier-rate-strip .trs-lbl');
    const trsNum = document.querySelector('.tier-rate-strip .trs-num');
    snapshot = {
      snumHTML:  snum  ? snum.innerHTML  : null,
      stierHTML: stier ? stier.innerHTML : null,
      stierClass:stier ? stier.className : null,
      trsLblHTML:trsLbl? trsLbl.innerHTML : null,
      trsNumHTML:trsNum? trsNum.innerHTML : null
    };
  }

  function restoreOriginal(){
    if (!snapshot) return;
    const snum = document.querySelector('.hscore .snum');
    const stier = document.querySelector('.hscore .stier');
    const trsLbl = document.querySelector('.tier-rate-strip .trs-lbl');
    const trsNum = document.querySelector('.tier-rate-strip .trs-num');
    if (snum && snapshot.snumHTML  !== null) snum.innerHTML  = snapshot.snumHTML;
    if (stier && snapshot.stierHTML !== null) { stier.innerHTML = snapshot.stierHTML; stier.className = snapshot.stierClass; }
    if (trsLbl && snapshot.trsLblHTML !== null) trsLbl.innerHTML = snapshot.trsLblHTML;
    if (trsNum && snapshot.trsNumHTML !== null) trsNum.innerHTML = snapshot.trsNumHTML;
  }


  // ─── apply hero patch based on current mode ─────────────────────────
  function apply(){
    const mode = window.FC17_HERO_MODE || 'A';

    // Get current player name from FieldCheck's global state
    // __currentPlayer is an object {name, sport, school, ...} set by verdict render
    const cp = window.__currentPlayer;
    const playerName = (cp && cp.name) || null;
    if (!playerName) return false;

    // Only apply if this player has v1.7 data
    if (!getPlayerData(playerName)) return false;
    const playerData = getPlayerData(playerName);

    // Mode A · no behavior change · ensure clean slate
    if (mode === 'A') {
      if (snapshot) restoreOriginal();
      document.documentElement.removeAttribute('data-fc17-hero-mode');
      return true;
    }

    injectStyles();
    snapshotOriginal();
    document.documentElement.setAttribute('data-fc17-hero-mode', mode);

    const v17composite = playerData.posterior.composite.mean;       // 9.30
    const v17compFmt   = v17composite.toFixed(2);
    const v17tier      = classifyTier(v17composite);                // ELITE+
    const v17ciLow     = playerData.posterior.composite.ci_low;
    const v17ciHigh    = playerData.posterior.composite.ci_high;

    // Find DOM elements
    const snum  = document.querySelector('.hscore .snum');
    const stier = document.querySelector('.hscore .stier');
    const trsLbl= document.querySelector('.tier-rate-strip .trs-lbl');
    const trsNum= document.querySelector('.tier-rate-strip .trs-num');

    // Get sport from current player (used for tier conversion %)
    const sport = playerData.sport || 'basketball';
    const v17pct = getTierPct(sport, v17tier.label);

    if (mode === 'B') {
      // ─── OPTION B · V1.7 WINS FULLY ─────────────────────────────────
      if (snum)  { snum.textContent  = v17compFmt;                snum.classList.add('fc17-hero-fade'); }
      if (stier) { stier.textContent = v17tier.label;             stier.className = 'stier ' + v17tier.cssClass + ' fc17-hero-fade'; }
      if (trsLbl){ trsLbl.innerHTML  = '// ' + v17tier.label + ' tier conversion \u00b7 ' + sport.replace(/-/g,' ').replace(/\bmens\b/,'men\u2019s').replace(/\bwomens\b/,'women\u2019s'); }
      if (trsNum){ trsNum.textContent= v17pct + '%';              trsNum.classList.add('fc17-hero-fade'); }
    }
    else if (mode === 'C') {
      // ─── OPTION C · DUAL DISPLAY ────────────────────────────────────
      if (snum){
        snum.innerHTML = '<span class="fc17-hero-dual fc17-hero-fade">' +
          '<span class="fc17-hero-legacy">' + (snapshot.snumHTML || '9.6') + '</span>' +
          '<span class="fc17-hero-sep">/</span>' +
          '<span class="fc17-hero-v17">' + v17compFmt + '</span>' +
          '<span class="fc17-hero-v17-tag">v1.7</span>' +
        '</span>';
      }
      if (stier){
        // Preserve original legacy tier + append v1.7
        stier.innerHTML = '<span class="fc17-hero-tier-dual">' +
          '<span>' + (snapshot.stierHTML || 'ICON') + '</span>' +
          '<span class="fc17-tier-v17">/ ' + v17tier.label + '</span>' +
        '</span>';
      }
      if (trsLbl){
        trsLbl.innerHTML = '// dual tier reading \u00b7 legacy: ' + (snapshot.stierHTML || 'ICON') + ' \u00b7 v1.7: ' + v17tier.label;
      }
      // trsNum stays at legacy 95% (the dual display already shows the divergence)
    }

    return true;
  }


  // ─── auto-apply on DOM ready + on re-render ─────────────────────────
  function autoApply(){
    // Retry up to 30 times over ~3 seconds in case __currentPlayer not yet
    // populated by legacy verdict render (Caleb-style curated marquee profiles
    // can have slower DOM setup than non-curated paths). apply() returns true
    // on success so retries stop immediately. Preserves one-shot behavior for
    // fast-render players (Flagg/Caitlin/Skinner).
    let attempt = 0;
    const maxAttempts = 30;
    function tryOnce(){
      attempt++;
      if (apply() || attempt >= maxAttempts) return;
      setTimeout(tryOnce, 100);
    }
    setTimeout(tryOnce, 50);
  }


  // ─── EXPORT ─────────────────────────────────────────────────────────
  window.FC17_HERO = {
    apply: apply,
    autoApply: autoApply,
    classifyTier: classifyTier,
    getTierPct: getTierPct,
    // For ad-hoc testing
    setMode: function(mode){
      window.FC17_HERO_MODE = mode;
      return apply();
    }
  };

})();


// ═══════════════════════════════════════════════════════════════════════
// INTEGRATION INSTRUCTIONS
// ═══════════════════════════════════════════════════════════════════════
//
// 1. Add script tag to fieldcheck-verdict.html (alongside other FC17 scripts):
//
//      <script src="/fc17-s2b-flagg-data.js" defer></script>
//      <script src="/fc17-polygon-mount.js" defer></script>
//      <script src="/fc17-interpretation-panel.js" defer></script>
//      <script src="/fc17-sport-adapter.js" defer></script>  <!-- if Option C -->
//      <script src="/fc17-hero-sync.js" defer></script>      <!-- NEW · this module -->
//
// 2. In fieldcheck-verdict.html post-render hook, after FC17 polygon + interpretation
//    panel mount, add:
//
//      if (window.FC17_HERO) {
//        window.FC17_HERO.autoApply();   // applies current mode (default A = no-op)
//      }
//
// 3. Deploy via deploy-dev.sh. Mode A by default · zero behavior change.
//
// 4. To test alternative modes interactively (no redeploy):
//      Open browser console on Flagg verdict
//      > FC17_HERO.setMode('B')   // try Option B
//      > FC17_HERO.setMode('C')   // try Option C
//      > FC17_HERO.setMode('A')   // back to legacy
//
// 5. To commit a chosen mode globally (1-line code change):
//      Add inline script before the hero-sync script tag:
//        <script>window.FC17_HERO_MODE = 'B';</script>
//      Deploy. All Flagg loads use Option B from then on.
//
// ═══════════════════════════════════════════════════════════════════════


// ═══════════════════════════════════════════════════════════════════════
// CLAUDE'S RECOMMENDATION (from Canonical V1.5 Entry #005 row 005.7)
// ═══════════════════════════════════════════════════════════════════════
//
// Mode A (legacy preserved) for Phase 1 — keep production stable, transparent
// reframe via polygon. Move to Mode B when v1.7 backend lands (Phase 4.7) and
// all players have v1.7 numbers — at that point the legacy backend retires
// anyway so the divergence collapses naturally.
//
// Mode C (dual display) is interesting transitionally but visually busy on
// the hero — likely confusing for new users. Not recommended for default.
//
// ═══════════════════════════════════════════════════════════════════════
