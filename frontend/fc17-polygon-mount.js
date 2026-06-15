// ═══════════════════════════════════════════════════════════════════════
// FC17.S2A · Polygon Mount Module
// ═══════════════════════════════════════════════════════════════════════
// Self-contained · scoped CSS (.fc17-*) · IIFE scope · zero global pollution
// Requires window.FLAGG_V17 to be loaded (from fc17-s2b-flagg-data.js)
// Public API on window.FC17_POLYGON:
//   .isAvailable(playerId)   → true/false (player has v17 data ready?)
//   .mount(container, opts)  → renders polygon into container element
//   .unmount(container)      → removes polygon from container
// Usage in fieldcheck-verdict.html (Eval Grid > Polygon sub-tab):
//   if (window.FC17_POLYGON?.isAvailable(playerId)) {
//     existingPolygonEl.style.display = 'none';
//     window.FC17_POLYGON.mount(polygonContainerEl, { playerId });
//   } else { /* existing legacy polygon code runs */ }
// ═══════════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  // ────────────────────────────────────────────────────────────────
  // PLAYER REGISTRY · expand as players migrate to v17
  // SLUG_MAP normalizes any input form (Cooper Flagg / cooper_flagg / cooperflagg)
  // to canonical player_id used by data files
  // ────────────────────────────────────────────────────────────────
  const SLUG_MAP = {
    'cooperflagg':  'cooper_flagg',
    'cooper_flagg': 'cooper_flagg',
    'calebwilliams':  'caleb_williams',
    'caleb_williams': 'caleb_williams',
    'caitlinclark':  'caitlin_clark',
    'caitlin_clark': 'caitlin_clark',
    'averyskinner':  'avery_skinner',
    'avery_skinner': 'avery_skinner'
    // Future migrations: 'stephencurry': 'stephen_curry', etc.
  };

  function normalizeSlug(input) {
    if (!input) return null;
    const norm = String(input).toLowerCase().replace(/[^a-z0-9_]/g, '');
    return SLUG_MAP[norm] || SLUG_MAP[norm.replace(/_/g,'')] || null;
  }

  function getPlayerData(canonicalId) {
    if (canonicalId === 'cooper_flagg' && window.FLAGG_V17) return window.FLAGG_V17;
    if (canonicalId === 'caleb_williams' && window.CALEB_V17) return window.CALEB_V17;
    if (canonicalId === 'caitlin_clark' && window.CAITLIN_V17) return window.CAITLIN_V17;
    if (canonicalId === 'avery_skinner' && window.SKINNER_V17) return window.SKINNER_V17;
    return null;
  }

  // ────────────────────────────────────────────────────────────────
  // SCOPED CSS · injected once · all classes prefixed .fc17-
  // ────────────────────────────────────────────────────────────────
  const CSS = `
.fc17-polygon-root{font-family:'Inter',-apple-system,sans-serif;color:#F5F1E8;background:rgba(13,12,18,.55);border:1px solid rgba(255,252,245,.09);border-radius:20px;padding:22px 22px 26px;position:relative;overflow:hidden;backdrop-filter:blur(8px);--fc17-gold:#F5B800;--fc17-goldb:#FFD24A;--fc17-bg:#06050A;--fc17-t:#F5F1E8;--fc17-t2:rgba(245,241,232,.74);--fc17-t3:rgba(245,241,232,.46);--fc17-t4:rgba(245,241,232,.24);--fc17-ge:rgba(255,252,245,.09);--fc17-ge2:rgba(255,252,245,.05);--fc17-goldl:rgba(245,184,0,.28);--fc17-golds:rgba(245,184,0,.09);--fc17-moss:#6BAA5A;--fc17-mossl:rgba(107,170,90,.14);--fc17-mossd:rgba(107,170,90,.30);--fc17-red:#FF5C3A;line-height:1.6;width:100%}
.fc17-polygon-root *{box-sizing:border-box;margin:0;padding:0}
.fc17-polygon-root::before{content:"";position:absolute;top:50%;left:50%;width:600px;height:600px;background:radial-gradient(circle,rgba(245,184,0,.06) 0%,transparent 65%);transform:translate(-50%,-50%);pointer-events:none}
.fc17-eyebrow{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--fc17-t4);margin-bottom:6px;position:relative}
.fc17-title{font-family:'Anton',sans-serif;font-size:26px;letter-spacing:-.01em;margin-bottom:6px;position:relative}
.fc17-title b{color:var(--fc17-gold)}
.fc17-cap{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:var(--fc17-t3);margin-bottom:18px;position:relative}
.fc17-layout{display:flex;flex-direction:column;gap:22px;position:relative;width:100%}
.fc17-svg-wrap{width:100%;display:flex;justify-content:center;padding:8px 0}
.fc17-svg{width:100%;height:auto;display:block;max-width:760px;margin:0 auto;filter:drop-shadow(0 8px 32px rgba(0,0,0,.4))}
.fc17-axis-line{stroke:rgba(255,252,245,.08);stroke-width:1}
.fc17-axis-line.apex{stroke:rgba(245,184,0,.18);stroke-width:1.4}
.fc17-scale-ring{fill:none;stroke:rgba(255,252,245,.04);stroke-width:1}
.fc17-scale-ring.outer{stroke:rgba(255,252,245,.14)}
.fc17-scale-label{font-family:'JetBrains Mono',monospace;font-size:9px;fill:rgba(245,241,232,.32);font-weight:600;letter-spacing:.5px}
.fc17-axis-label{font-family:'Anton',sans-serif;font-size:14px;letter-spacing:.5px;fill:var(--fc17-t);text-transform:uppercase;font-weight:400;transition:fill .2s}
.fc17-axis-label.apex{fill:var(--fc17-gold);font-size:16px;letter-spacing:.7px;cursor:pointer}
.fc17-axis-label.apex:hover{fill:var(--fc17-goldb)}
.fc17-axis-value{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;fill:var(--fc17-gold);letter-spacing:.3px}
.fc17-axis-value.apex{font-size:13px}
.fc17-ci-band{stroke:none;opacity:0;animation:fc17-fadeIn 1s .8s both}
.fc17-mean-polygon{fill:rgba(245,184,0,.10);stroke-width:2;stroke-linejoin:round;stroke-linecap:round;filter:drop-shadow(0 0 12px rgba(245,184,0,.3));stroke-dasharray:1600;animation:fc17-drawIn 1.6s .3s both,fc17-fadeIn .6s .3s both}
.fc17-mean-vertex{fill:var(--fc17-gold);stroke:var(--fc17-bg);stroke-width:2.5;opacity:0;animation:fc17-fadeIn .5s both}
.fc17-ghost-lebron{fill:rgba(245,184,0,.03);stroke:rgba(245,184,0,.55);stroke-width:1.5;stroke-dasharray:5 4;stroke-linejoin:round;pointer-events:none;opacity:0;transition:opacity .4s}
.fc17-ghost-lebron.visible{opacity:1}
.fc17-ghost-wiggins{fill:rgba(255,92,58,.03);stroke:rgba(255,92,58,.7);stroke-width:1.5;stroke-dasharray:5 4;stroke-linejoin:round;pointer-events:none;opacity:0;transition:opacity .4s}
.fc17-ghost-wiggins.visible{opacity:1}
.fc17-refine-icon{cursor:help;transition:transform .2s}
.fc17-refine-icon:hover{transform:scale(1.2)}
@keyframes fc17-fadeIn{from{opacity:0}to{opacity:1}}
@keyframes fc17-drawIn{from{stroke-dashoffset:1600}to{stroke-dashoffset:0}}
@keyframes fc17-fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes fc17-pulse{0%,100%{opacity:1}50%{opacity:.45}}
.fc17-tooltip{position:fixed;background:rgba(6,5,10,.96);backdrop-filter:blur(16px);border:1px solid var(--fc17-goldl);border-radius:10px;padding:14px 18px;font-family:'Inter',sans-serif;font-size:12.5px;color:var(--fc17-t);box-shadow:0 8px 32px rgba(0,0,0,.5),0 0 24px rgba(245,184,0,.15);pointer-events:none;z-index:9999;max-width:280px;opacity:0;transform:translateY(4px);transition:opacity .15s,transform .15s}
.fc17-tooltip.visible{opacity:1;transform:translateY(0)}
.fc17-tt-name{font-family:'Anton',sans-serif;font-size:18px;letter-spacing:-.005em;margin-bottom:6px;color:var(--fc17-gold)}
.fc17-tt-row{display:flex;justify-content:space-between;gap:14px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--fc17-t2);padding:3px 0}
.fc17-tt-row b{color:var(--fc17-t)}
.fc17-tt-refine{margin-top:8px;padding-top:8px;border-top:1px solid var(--fc17-ge);font-size:11.5px;color:var(--fc17-t3);line-height:1.5}
.fc17-controls{display:flex;flex-direction:column;gap:14px}
.fc17-ctrl-card{background:rgba(13,12,18,.55);border:1px solid var(--fc17-ge);border-radius:14px;padding:18px 20px}
.fc17-ctrl-h{font-family:'JetBrains Mono',monospace;font-size:9.5px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:var(--fc17-t3);margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.fc17-ctrl-h .live{color:var(--fc17-moss);font-size:9px;letter-spacing:1.2px}
.fc17-ctrl-h .live::before{content:"●";margin-right:5px;color:var(--fc17-moss);animation:fc17-pulse 1.8s infinite}
.fc17-refine-list{display:flex;flex-direction:column;gap:6px}
.fc17-refine-row{display:flex;align-items:center;gap:10px;padding:8px 11px;background:rgba(0,0,0,.28);border-radius:8px;border-left:2px solid var(--fc17-goldl);transition:all .15s}
.fc17-refine-row:hover{background:rgba(245,184,0,.06);border-left-color:var(--fc17-gold);transform:translateX(2px)}
.fc17-refine-row.inactive{opacity:.42;border-left-color:var(--fc17-ge)}
.fc17-refine-row.inactive:hover{transform:none;background:rgba(0,0,0,.28)}
.fc17-refine-row .ic{font-size:14px;width:20px;text-align:center}
.fc17-refine-row .info{flex:1;min-width:0}
.fc17-refine-row .id{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;letter-spacing:1px;color:var(--fc17-gold);text-transform:uppercase}
.fc17-refine-row.inactive .id{color:var(--fc17-t3)}
.fc17-refine-row .desc{font-size:10.5px;color:var(--fc17-t2);line-height:1.45;margin-top:1px}
.fc17-compare-list{display:flex;flex-direction:column;gap:7px}
.fc17-compare-btn{display:flex;align-items:center;gap:11px;padding:10px 13px;background:rgba(13,12,18,.4);border:1px solid var(--fc17-ge);border-radius:9px;cursor:pointer;text-align:left;color:var(--fc17-t2);font-family:'Inter',sans-serif;font-size:12.5px;transition:all .2s;font-weight:500;width:100%}
.fc17-compare-btn:hover{border-color:var(--fc17-t3);color:var(--fc17-t);transform:translateY(-1px)}
.fc17-compare-btn.active{border-color:var(--fc17-gold);background:rgba(245,184,0,.08);color:var(--fc17-t)}
.fc17-compare-btn.active.wiggins{border-color:var(--fc17-red);background:rgba(255,92,58,.08)}
.fc17-compare-btn .sw{width:13px;height:13px;border-radius:50%;flex-shrink:0;border:2px solid transparent}
.fc17-compare-btn .sw.lebron{border-color:var(--fc17-gold);border-style:dashed}
.fc17-compare-btn .sw.wiggins{border-color:var(--fc17-red);border-style:dashed}
.fc17-compare-btn .sw.gold-solid{background:var(--fc17-gold);border-color:var(--fc17-gold)}
.fc17-compare-btn .meta{font-family:'JetBrains Mono',monospace;font-size:9.5px;color:var(--fc17-t4);margin-left:auto}
.fc17-drill{margin-top:24px;background:rgba(13,12,18,.55);border:1px solid var(--fc17-ge);border-radius:16px;padding:26px 28px;display:none;position:relative;overflow:hidden}
.fc17-drill::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--fc17-gold),transparent);opacity:.4}
.fc17-drill.open{display:block;animation:fc17-fadeUp .45s cubic-bezier(.2,.7,.3,1) both}
.fc17-drill-h-row{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:14px}
.fc17-drill-h{font-family:'Anton',sans-serif;font-size:24px;letter-spacing:-.01em;display:flex;align-items:center;flex-wrap:wrap;gap:12px}
.fc17-drill-h b{color:var(--fc17-gold)}
.fc17-drill-close{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--fc17-t3);padding:6px 12px;border:1px solid var(--fc17-ge);border-radius:9999px;background:none;cursor:pointer;transition:all .18s}
.fc17-drill-close:hover{color:var(--fc17-t);border-color:var(--fc17-t3)}
.fc17-drill-min{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:9.5px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--fc17-gold);padding:4px 9px;background:var(--fc17-golds);border:1px solid var(--fc17-goldl);border-radius:9999px}
.fc17-drill-body{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center}
@media(max-width:820px){.fc17-drill-body{grid-template-columns:1fr}}
.fc17-drill-svg{width:100%;max-width:340px;margin:0 auto;display:block}
.fc17-drill-list{display:flex;flex-direction:column;gap:9px}
.fc17-subdim-row{display:flex;align-items:center;gap:12px;padding:11px 14px;background:rgba(0,0,0,.32);border-radius:10px;border-left:3px solid var(--fc17-moss);transition:transform .15s}
.fc17-subdim-row:hover{transform:translateX(3px)}
.fc17-subdim-row.warn-strong{border-left-color:var(--fc17-red)}
.fc17-subdim-name{font-family:'JetBrains Mono',monospace;font-size:10.5px;font-weight:700;letter-spacing:.5px;color:var(--fc17-t2);width:96px;flex-shrink:0;text-transform:uppercase}
.fc17-subdim-bar{flex:1;height:6px;background:rgba(255,252,245,.05);border-radius:9999px;overflow:hidden;min-width:50px}
.fc17-subdim-bar-fill{height:100%;background:var(--fc17-moss);border-radius:9999px}
.fc17-subdim-row.warn-strong .fc17-subdim-bar-fill{background:var(--fc17-red)}
.fc17-subdim-score{font-family:'Anton',sans-serif;font-size:20px;color:var(--fc17-t);width:34px;text-align:right;letter-spacing:-.005em}
.fc17-subdim-conf{font-family:'JetBrains Mono',monospace;font-size:9.5px;color:var(--fc17-t3);min-width:44px;text-align:right;letter-spacing:.3px}
.fc17-subdim-flag{font-size:13px;width:20px;text-align:center}
.fc17-drill-note{margin-top:22px;padding:16px 20px;background:rgba(245,184,0,.06);border-left:2px solid var(--fc17-gold);border-radius:0 10px 10px 0;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:15px;color:var(--fc17-t2);line-height:1.55}
.fc17-drill-note b{color:var(--fc17-gold);font-style:normal;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase}

/* ── consensus shadow overlay · Sprint A1 v2 ────────────────── */
.fc17-consensus-polygon{fill:rgba(160,150,140,.10);stroke:rgba(160,150,140,.55);stroke-width:1.4;stroke-dasharray:3 3;stroke-linejoin:round;pointer-events:none}
.fc17-consensus-dot{fill:rgba(160,150,140,.6);stroke:#06050A;stroke-width:.8;pointer-events:none}
.fc17-asym-callout{margin-top:22px;padding:14px 18px;border-left:3px solid var(--fc17-gold);background:rgba(245,184,0,.04);border-radius:0 8px 8px 0;position:relative;animation:fc17-fadeIn .6s 1.6s both}
.fc17-asym-callout.converged{border-left-color:var(--fc17-moss);background:rgba(107,170,90,.04)}
.fc17-asym-callout.gem{border-left-color:var(--fc17-goldb);background:rgba(255,210,74,.04)}
.fc17-asym-lbl{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.6px;color:var(--fc17-gold);text-transform:uppercase;margin-bottom:6px}
.fc17-asym-callout.converged .fc17-asym-lbl{color:var(--fc17-moss)}
.fc17-asym-callout.gem .fc17-asym-lbl{color:var(--fc17-goldb)}
.fc17-asym-txt{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:16px;color:var(--fc17-t);line-height:1.55}
.fc17-asym-txt strong{font-family:'Anton',sans-serif;font-style:normal;font-weight:400;color:var(--fc17-gold);letter-spacing:.005em}
.fc17-asym-callout.converged .fc17-asym-txt strong{color:var(--fc17-moss)}
.fc17-asym-callout.gem .fc17-asym-txt strong{color:var(--fc17-goldb)}
.fc17-asym-meta{margin-top:10px;padding-top:10px;border-top:1px solid var(--fc17-ge2);font-family:'JetBrains Mono',monospace;font-size:9.5px;color:var(--fc17-t4);letter-spacing:.6px;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
.fc17-asym-legend{display:flex;gap:18px;justify-content:center;flex-wrap:wrap;margin:14px 0 4px;padding:10px 0;border-top:1px solid var(--fc17-ge2);border-bottom:1px solid var(--fc17-ge2)}
.fc17-asym-legend .leg-item{display:flex;align-items:center;gap:7px;font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.5px;color:var(--fc17-t3);text-transform:uppercase;font-weight:700}
.fc17-asym-legend .leg-sw{width:18px;height:3px;border-radius:2px}
.fc17-asym-legend .leg-sw.fc{background:var(--fc17-gold);box-shadow:0 0 6px rgba(245,184,0,.5)}
.fc17-asym-legend .leg-sw.cons{background:rgba(160,150,140,.55)}
.fc17-asym-legend .leg-sw.ci{background:linear-gradient(90deg,transparent,var(--fc17-gold),transparent);opacity:.4}
`;

  let stylesInjected = false;
  function injectStyles() {
    if (stylesInjected) return;
    const style = document.createElement('style');
    style.id = 'fc17-polygon-styles';
    style.textContent = CSS;
    document.head.appendChild(style);
    stylesInjected = true;
  }

  // ────────────────────────────────────────────────────────────────
  // GEOMETRY
  // ────────────────────────────────────────────────────────────────
  const CX = 380, CY = 380, MAX_R = 260;
  const DRILL_CX = 190, DRILL_CY = 190, DRILL_R = 140;

  function pointAt(angleDeg, value, cx, cy, maxR) {
    const rad = (angleDeg - 90) * Math.PI / 180;
    const r = (value / 10) * maxR;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  const SVG_NS = 'http://www.w3.org/2000/svg';
  function svg(tag, attrs) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }

  // ────────────────────────────────────────────────────────────────
  // BUILD AXES from posterior data
  // ────────────────────────────────────────────────────────────────
  function buildAxes(posterior, sport) {
    const p = posterior.pillars;
    const ref = function(key) {
      // map pillar key to refinement icon if applicable
      const dets = (posterior.refinements && posterior.refinements.details) || {};
      for (const r of (posterior.refinements && posterior.refinements.active) || []) {
        if (dets[r] && dets[r].applies_to && dets[r].applies_to.indexOf(key) !== -1) return dets[r].icon;
      }
      return null;
    };
    // FC17.S3 · sport-adapter wiring (v1.1) · falls back to canonical labels if adapter not loaded
    // When fc17-sport-adapter.js is loaded, labels become sport-specific (basketball: "Closer DNA",
    // volleyball: "Captain DNA", etc.). When not loaded, identical canonical labels as v1.0.
    function lbl(pillarKey, fallback) {
      if (window.FC17_SPORT_ADAPTER && sport) {
        try {
          var sportLabel = window.FC17_SPORT_ADAPTER.getLabel(sport, pillarKey);
          if (sportLabel) return sportLabel;
        } catch (e) { /* fall through to fallback */ }
      }
      return fallback;
    }
    return [
      { key:'character', label:lbl('character','Character'), angle:0, value:p.character.mean, sd:p.character.sd, conf:p.character.confidence, refinement:null, apex:true, note:p.character.notes },
      { key:'mindset', label:lbl('mindset','Mindset'), angle:45, value:p.mindset.mean, sd:p.mindset.sd, conf:p.mindset.confidence, refinement:null, note:p.mindset.notes },
      { key:'mental_str', label:lbl('mental_strength','Mental Strength'), angle:90, value:p.mental_strength.mean, sd:p.mental_strength.sd, conf:p.mental_strength.confidence, refinement:null, note:p.mental_strength.notes },
      { key:'talent', label:lbl('talent','Talent'), angle:135, value:p.talent.mean, sd:p.talent.sd, conf:p.talent.confidence, refinement:null, note:p.talent.notes },
      { key:'physical', label:lbl('physical','Physical'), angle:180, value:p.physical.mean, sd:p.physical.sd, conf:p.physical.confidence, refinement:p.physical.refinement_applied === 'R1' ? '🩹' : null, refineDetail:p.physical.notes },
      { key:'mental_iq', label:lbl('mental_iq','Mental / IQ'), angle:225, value:p.mental_iq.mean, sd:p.mental_iq.sd, conf:p.mental_iq.confidence, refinement:null, note:p.mental_iq.notes },
      { key:'coachability', label:lbl('coachability','Coachability'), angle:270, value:p.coachability.mean, sd:p.coachability.sd, conf:p.coachability.confidence, refinement:p.coachability.refinement_applied === 'R4' ? '🎯' : null, refineDetail:p.coachability.notes },
      { key:'competitive', label:lbl('competitive','Competitiveness'), angle:315, value:p.competitive.mean, sd:p.competitive.sd, conf:p.competitive.confidence, refinement:null, note:p.competitive.notes }
    ];
  }

  function buildSubDims(charData) {
    return charData.sub_dims.map(function(s, i) {
      return {
        key: s.key,
        label: s.label,
        angle: i * 72,
        value: s.mean,
        conf: s.conf,
        warn: s.flag !== null
      };
    });
  }

  // ────────────────────────────────────────────────────────────────
  // BUILD DOM
  // ────────────────────────────────────────────────────────────────
  function buildPolygonDOM(data) {
    const posterior = data.posterior || data;
    posterior.refinements = data.refinements || {};
    const axes = buildAxes(posterior, data.sport);
    const subDims = buildSubDims(posterior.pillars.character);

    const root = document.createElement('div');
    root.className = 'fc17-polygon-root';
    root.innerHTML = `
      <div class="fc17-eyebrow">// Profile across 8 facets · shaded 95% credible interval bands · v1.7</div>
      <div class="fc17-title">The <b>Polygon</b></div>
      <div class="fc17-cap">Click "Character" at the apex to drill into the 5 sub-dimensions · hover any vertex for detail</div>
      <div class="fc17-layout">
        <svg class="fc17-svg" viewBox="0 0 760 760" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <radialGradient id="fc17-ci-gradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="rgba(245,184,0,0.06)"/>
              <stop offset="100%" stop-color="rgba(245,184,0,0.18)"/>
            </radialGradient>
            <linearGradient id="fc17-mean-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#FFD24A"/><stop offset="100%" stop-color="#F5B800"/>
            </linearGradient>
          </defs>
          <g class="fc17-scale-rings"></g>
          <g class="fc17-axes"></g>
          <polygon class="fc17-ghost-lebron"/>
          <polygon class="fc17-ghost-wiggins"/>
          <path class="fc17-ci-band" fill="url(#fc17-ci-gradient)" fill-rule="evenodd"/>
          <polygon class="fc17-mean-polygon" stroke="url(#fc17-mean-gradient)"/>
          <g class="fc17-vertices"></g>
          <g class="fc17-labels"></g>
          <g class="fc17-refines"></g>
        </svg>
        <div class="fc17-controls">
          <div class="fc17-ctrl-card">
            <div class="fc17-ctrl-h"><span>Active refinements</span><span class="live">${(posterior.refinements.active || []).join(' · ')}</span></div>
            <div class="fc17-refine-list">${buildRefineList(posterior.refinements)}</div>
          </div>
          <div class="fc17-ctrl-card">
            <div class="fc17-ctrl-h">Comparable trajectories<span style="color:var(--fc17-t4);font-weight:400;letter-spacing:.2px;text-transform:none">at age ' + (data.age || 19) + '</span></div>
            <div class="fc17-compare-list">${buildCompareList(data.comparables)}</div>
          </div>
          <div class="fc17-ctrl-card">
            <div class="fc17-ctrl-h">Character drill-in</div>
            <button class="fc17-compare-btn fc17-drill-btn"><div class="sw gold-solid"></div>5 sub-dims · MIN function<span class="meta">click apex →</span></button>
          </div>
        </div>
      </div>
      <div class="fc17-drill">
        <div class="fc17-drill-h-row">
          <div>
            <div class="fc17-eyebrow">// Apex axis · sub-dim composition · weight ${posterior.pillars.character.weight} · MIN function</div>
            <div class="fc17-drill-h">Character <b>profile</b><span class="fc17-drill-min">MIN ${posterior.pillars.character.mean}</span></div>
          </div>
          <button class="fc17-drill-close">close ✕</button>
        </div>
        <div class="fc17-drill-body">
          <svg class="fc17-drill-svg" viewBox="0 0 380 380" xmlns="http://www.w3.org/2000/svg">
            <g class="fc17-drill-rings"></g>
            <g class="fc17-drill-axes"></g>
            <polygon class="fc17-drill-mean" fill="rgba(245,184,0,.12)" stroke="url(#fc17-mean-gradient)" stroke-width="2" stroke-linejoin="round"/>
            <g class="fc17-drill-vertices"></g>
            <g class="fc17-drill-labels"></g>
          </svg>
          <div class="fc17-drill-list">${buildSubDimList(subDims, posterior.pillars.character.sub_dims)}</div>
        </div>
        <div class="fc17-drill-note">${escapeHtml(posterior.pillars.character.notes || '')}</div>
      </div>
    `;

    renderSVG(root, axes, data, subDims, posterior);
    return root;
  }

  function buildRefineList(refinements) {
    if (!refinements || !refinements.details) return '';
    const order = ['R1','R2','R3','R4','R5','R6'];
    return order.map(function(rid) {
      const d = refinements.details[rid];
      if (!d) return '';
      const active = (refinements.active || []).indexOf(rid) !== -1;
      return `<div class="fc17-refine-row${active ? '' : ' inactive'}">
        <div class="ic">${d.icon || '·'}</div>
        <div class="info">
          <div class="id">${rid} · ${escapeHtml(d.applies_to || '').replace(/_/g,' ')}</div>
          <div class="desc">${escapeHtml(d.explanation || '')}</div>
        </div>
      </div>`;
    }).join('');
  }

  function buildCompareList(comparablesObj) {
    if (!comparablesObj || !comparablesObj.comparables) return '';
    return comparablesObj.comparables.map(function(c) {
      const cls = c.slug === 'wiggins_2014' ? 'wiggins' : 'lebron';
      return `<button class="fc17-compare-btn fc17-ghost-btn ${cls}" data-slug="${c.slug}"><div class="sw ${cls}"></div>${escapeHtml(c.name)}<span class="meta">${c.career_composite} career</span></button>`;
    }).join('');
  }

  function buildSubDimList(subDims, subDimsRaw) {
    return subDimsRaw.map(function(s) {
      const warn = s.flag !== null ? 'warn-strong' : '';
      const flagIcon = s.flag !== null ? '⚠' : (s.mean >= 9.4 ? '✓✓' : '✓');
      const flagColor = s.flag !== null ? 'var(--fc17-red)' : 'var(--fc17-moss)';
      return `<div class="fc17-subdim-row ${warn}">
        <div class="fc17-subdim-name">${escapeHtml(s.label)}</div>
        <div class="fc17-subdim-bar"><div class="fc17-subdim-bar-fill" style="width:${s.mean * 10}%"></div></div>
        <div class="fc17-subdim-score">${s.mean}</div>
        <div class="fc17-subdim-conf">${Math.round(s.conf * 100)}% conf</div>
        <div class="fc17-subdim-flag" style="color:${flagColor}">${flagIcon}</div>
      </div>`;
    }).join('');
  }

  function escapeHtml(s) {
    if (typeof s !== 'string') return '';
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ────────────────────────────────────────────────────────────────
  // RENDER SVG (axes, polygon, vertices, labels)
  // ────────────────────────────────────────────────────────────────
  function renderSVG(root, axes, data, subDims, posterior) {
    const svgEl = root.querySelector('.fc17-svg');
    const ringsG = svgEl.querySelector('.fc17-scale-rings');
    const axesG = svgEl.querySelector('.fc17-axes');
    const vertG = svgEl.querySelector('.fc17-vertices');
    const labelG = svgEl.querySelector('.fc17-labels');
    const refineG = svgEl.querySelector('.fc17-refines');

    // Scale rings
    [2,4,6,8,10].forEach(function(v) {
      const r = (v/10) * MAX_R;
      ringsG.appendChild(svg('circle', {cx:CX, cy:CY, r:r, class:'fc17-scale-ring' + (v===10 ? ' outer' : '')}));
      if (v === 4 || v === 8 || v === 10) {
        const p = pointAt(0, v, CX, CY, MAX_R);
        const lbl = svg('text', {x:p.x + 7, y:p.y + 3, class:'fc17-scale-label'});
        lbl.textContent = v;
        ringsG.appendChild(lbl);
      }
    });

    // Axes
    axes.forEach(function(a) {
      const p = pointAt(a.angle, 10, CX, CY, MAX_R);
      axesG.appendChild(svg('line', {x1:CX, y1:CY, x2:p.x, y2:p.y, class:'fc17-axis-line' + (a.apex ? ' apex' : '')}));
    });

    // CI band
    function ciCoords(dir) {
      return axes.map(function(a) {
        let v = a.value + dir * 1.96 * a.sd;
        v = Math.max(0, Math.min(10, v));
        const p = pointAt(a.angle, v, CX, CY, MAX_R);
        return [p.x.toFixed(1), p.y.toFixed(1)];
      });
    }
    const outerCI = ciCoords(+1), innerCI = ciCoords(-1);
    svgEl.querySelector('.fc17-ci-band').setAttribute('d',
      'M ' + outerCI.map(function(p){return p.join(',');}).join(' L ') + ' Z M ' +
      innerCI.map(function(p){return p.join(',');}).join(' L ') + ' Z');

    // Mean polygon
    const meanPts = axes.map(function(a) {
      const p = pointAt(a.angle, a.value, CX, CY, MAX_R);
      return p.x.toFixed(1) + ',' + p.y.toFixed(1);
    }).join(' ');
    svgEl.querySelector('.fc17-mean-polygon').setAttribute('points', meanPts);

    // Vertices with tooltip targets
    axes.forEach(function(a, i) {
      const p = pointAt(a.angle, a.value, CX, CY, MAX_R);
      const hit = svg('circle', {cx:p.x, cy:p.y, r:18, fill:'transparent', style:'cursor:pointer'});
      hit.addEventListener('mouseenter', function(e) { showTooltip(e, a); });
      hit.addEventListener('mousemove', moveTooltip);
      hit.addEventListener('mouseleave', hideTooltip);
      if (a.apex) hit.addEventListener('click', function() { toggleDrill(root); });
      vertG.appendChild(hit);
      vertG.appendChild(svg('circle', {cx:p.x, cy:p.y, r:5.5, class:'fc17-mean-vertex', style:'animation-delay:' + (1 + i*0.06) + 's;pointer-events:none'}));
    });

    // Labels
    axes.forEach(function(a, i) {
      const lblP = pointAt(a.angle, 11.6, CX, CY, MAX_R);
      const txt = svg('text', {x:lblP.x, y:lblP.y, 'text-anchor':'middle', 'dominant-baseline':'middle', class:'fc17-axis-label' + (a.apex ? ' apex' : ''), style:'opacity:0;animation:fc17-fadeIn .5s ' + (1.2 + i*0.05) + 's both'});
      if (a.apex) txt.addEventListener('click', function() { toggleDrill(root); });
      txt.textContent = a.label;
      labelG.appendChild(txt);

      const valOffset = (a.angle > 90 && a.angle < 270) ? 16 : -14;
      const valP = pointAt(a.angle, 10.6, CX, CY, MAX_R);
      const val = svg('text', {x:valP.x, y:valP.y + valOffset, 'text-anchor':'middle', 'dominant-baseline':'middle', class:'fc17-axis-value' + (a.apex ? ' apex' : ''), style:'opacity:0;animation:fc17-fadeIn .5s ' + (1.4 + i*0.05) + 's both'});
      val.textContent = a.value.toFixed(1);
      labelG.appendChild(val);

      if (a.refinement) {
        const refP = pointAt(a.angle, 12.7, CX, CY, MAX_R);
        const refTxt = svg('text', {x:refP.x, y:refP.y, 'text-anchor':'middle', 'dominant-baseline':'middle', 'font-size':'17', class:'fc17-refine-icon', style:'opacity:0;animation:fc17-fadeIn .5s ' + (1.6 + i*0.05) + 's both'});
        refTxt.textContent = a.refinement;
        refTxt.addEventListener('mouseenter', function(e) { showTooltip(e, a); });
        refTxt.addEventListener('mousemove', moveTooltip);
        refTxt.addEventListener('mouseleave', hideTooltip);
        refineG.appendChild(refTxt);
      }
    });

    // Ghost polygons
    if (data.comparables && data.comparables.comparables) {
      data.comparables.comparables.forEach(function(c) {
        const cls = c.slug === 'wiggins_2014' ? 'wiggins' : 'lebron';
        const ghost = svgEl.querySelector('.fc17-ghost-' + cls);
        if (ghost) {
          const pts = axes.map(function(a) {
            const v = c.pillars[a.key === 'mental_str' ? 'mental_str' : a.key];
            const p = pointAt(a.angle, v, CX, CY, MAX_R);
            return p.x.toFixed(1) + ',' + p.y.toFixed(1);
          }).join(' ');
          ghost.setAttribute('points', pts);
        }
      });
    }

    // Drill-in SVG
    renderDrillSVG(root, subDims, posterior.pillars.character.sub_dims);
  }

  function renderDrillSVG(root, subDims, subDimsRaw) {
    const dsvg = root.querySelector('.fc17-drill-svg');
    const ringsG = dsvg.querySelector('.fc17-drill-rings');
    const axesG = dsvg.querySelector('.fc17-drill-axes');
    const vertG = dsvg.querySelector('.fc17-drill-vertices');
    const labelG = dsvg.querySelector('.fc17-drill-labels');

    [2,4,6,8,10].forEach(function(v) {
      ringsG.appendChild(svg('circle', {cx:DRILL_CX, cy:DRILL_CY, r:(v/10)*DRILL_R, class:'fc17-scale-ring' + (v===10 ? ' outer' : '')}));
    });
    subDims.forEach(function(s) {
      const p = pointAt(s.angle, 10, DRILL_CX, DRILL_CY, DRILL_R);
      axesG.appendChild(svg('line', {x1:DRILL_CX, y1:DRILL_CY, x2:p.x, y2:p.y, class:'fc17-axis-line'}));
    });
    const meanPts = subDims.map(function(s) {
      const p = pointAt(s.angle, s.value, DRILL_CX, DRILL_CY, DRILL_R);
      return p.x.toFixed(1) + ',' + p.y.toFixed(1);
    }).join(' ');
    root.querySelector('.fc17-drill-mean').setAttribute('points', meanPts);
    subDims.forEach(function(s) {
      const p = pointAt(s.angle, s.value, DRILL_CX, DRILL_CY, DRILL_R);
      const c = svg('circle', {cx:p.x, cy:p.y, r:4.5, class:'fc17-mean-vertex', style:'animation-delay:.3s'});
      if (s.warn) c.setAttribute('fill', 'var(--fc17-red)');
      vertG.appendChild(c);
      const lblP = pointAt(s.angle, 12, DRILL_CX, DRILL_CY, DRILL_R);
      const txt = svg('text', {x:lblP.x, y:lblP.y, 'text-anchor':'middle', 'dominant-baseline':'middle', class:'fc17-axis-label', style:'font-size:11px'});
      if (s.warn) txt.setAttribute('fill', 'var(--fc17-red)');
      txt.textContent = s.label + (s.warn ? ' ⚠' : '');
      labelG.appendChild(txt);
    });
  }

  // ────────────────────────────────────────────────────────────────
  // TOOLTIP
  // ────────────────────────────────────────────────────────────────
  let tooltipEl = null;
  function ensureTooltip() {
    if (tooltipEl) return tooltipEl;
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'fc17-tooltip';
    tooltipEl.innerHTML = `
      <div class="fc17-tt-name"></div>
      <div class="fc17-tt-row"><span>Posterior mean</span><b class="fc17-tt-mean"></b></div>
      <div class="fc17-tt-row"><span>95% credible</span><b class="fc17-tt-ci"></b></div>
      <div class="fc17-tt-row"><span>Confidence</span><b class="fc17-tt-conf"></b></div>
      <div class="fc17-tt-refine" style="display:none"></div>`;
    document.body.appendChild(tooltipEl);
    return tooltipEl;
  }
  function showTooltip(e, a) {
    const t = ensureTooltip();
    t.querySelector('.fc17-tt-name').textContent = a.label;
    t.querySelector('.fc17-tt-mean').textContent = a.value.toFixed(2);
    t.querySelector('.fc17-tt-ci').textContent =
      Math.max(0, a.value - 1.96*a.sd).toFixed(2) + ' – ' + Math.min(10, a.value + 1.96*a.sd).toFixed(2);
    t.querySelector('.fc17-tt-conf').textContent = Math.round(a.conf*100) + '%';
    const ref = t.querySelector('.fc17-tt-refine');
    if (a.refineDetail) { ref.innerHTML = (a.refinement || '') + ' ' + escapeHtml(a.refineDetail); ref.style.display = 'block'; }
    else if (a.note) { ref.innerHTML = escapeHtml(a.note); ref.style.display = 'block'; }
    else { ref.style.display = 'none'; }
    moveTooltip(e);
    t.classList.add('visible');
  }
  function moveTooltip(e) {
    const t = ensureTooltip();
    t.style.left = Math.min(e.clientX + 16, window.innerWidth - 300) + 'px';
    t.style.top = Math.min(e.clientY + 16, window.innerHeight - 180) + 'px';
  }
  function hideTooltip() { if (tooltipEl) tooltipEl.classList.remove('visible'); }

  // ────────────────────────────────────────────────────────────────
  // INTERACTIONS
  // ────────────────────────────────────────────────────────────────
  function wireInteractions(root, data) {
    root.querySelector('.fc17-drill-close').addEventListener('click', function() { toggleDrill(root); });
    root.querySelector('.fc17-drill-btn').addEventListener('click', function() { toggleDrill(root); });
    root.querySelectorAll('.fc17-ghost-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        const slug = btn.getAttribute('data-slug');
        const cls = slug === 'wiggins_2014' ? 'wiggins' : 'lebron';
        const ghost = root.querySelector('.fc17-ghost-' + cls);
        if (ghost) {
          ghost.classList.toggle('visible');
          btn.classList.toggle('active');
        }
      });
    });
  }
  function toggleDrill(root) {
    const drill = root.querySelector('.fc17-drill');
    drill.classList.toggle('open');
    if (drill.classList.contains('open')) {
      setTimeout(function() { drill.scrollIntoView({behavior:'smooth', block:'start'}); }, 100);
    }
  }

  // ────────────────────────────────────────────────────────────────
  // PUBLIC API
  // ────────────────────────────────────────────────────────────────
  window.FC17_POLYGON = {
    version: '1.7.0',
    normalizeSlug: normalizeSlug,

    isAvailable: function(slug) {
      const canonical = normalizeSlug(slug);
      return !!canonical && !!getPlayerData(canonical);
    },

    mount: function(container, opts) {
      opts = opts || {};
      const canonical = normalizeSlug(opts.playerId);
      if (!canonical) {
        console.warn('FC17_POLYGON: unrecognized player slug:', opts.playerId);
        return false;
      }
      const data = getPlayerData(canonical);
      if (!data) {
        console.warn('FC17_POLYGON: data not loaded for ' + canonical);
        return false;
      }
      injectStyles();
      this.unmount(container);
      // FC17.S2A.1 fix · clear container so legacy SVG (from buildRadar) gets removed before mount
      container.innerHTML = '';
      const root = buildPolygonDOM(data);
      container.appendChild(root);
      enhanceWithConsensus(root, canonical);
      return true;
    },

    unmount: function(container) {
      const existing = container.querySelector('.fc17-polygon-root');
      if (existing) existing.remove();
    }
  };

  // ════════════════════════════════════════════════════════════════
  // ENHANCE WITH CONSENSUS · Sprint A1 v2 · Polygon polish
  // ════════════════════════════════════════════════════════════════
  // ZERO-RISK ADDITION pattern: runs AFTER existing renderSVG completes.
  // Only inserts consensus polygon + asymmetry callout when consensus
  // data exists for this player. Existing rendering completely untouched.
  function enhanceWithConsensus(root, canonical) {
    if (!window.FC17_CONSENSUS_DATA) return;
    var cdata = window.FC17_CONSENSUS_DATA[canonical];
    if (!cdata || !cdata.consensus) {
      // No consensus data for this player — render NOTHING extra (graceful degradation)
      return;
    }

    var svgEl = root.querySelector('.fc17-svg');
    if (!svgEl) return;

    // Match FC17 polygon geometry exactly (CX/CY/MAX_R, pointAt, SVG_NS in scope)
    var axisDefs = [
      ['character', 0], ['mindset', 45], ['mental_strength', 90], ['talent', 135],
      ['physical', 180], ['mental_iq', 225], ['coachability', 270], ['competitive', 315]
    ];

    // Consensus polygon points
    var consensusPoints = axisDefs.map(function(def) {
      var v = Math.max(0, Math.min(10, cdata.consensus[def[0]] || 0));
      var p = pointAt(def[1], v, CX, CY, MAX_R);
      return p.x.toFixed(1) + ',' + p.y.toFixed(1);
    }).join(' ');

    // Insert consensus polygon BEFORE the FC mean polygon (renders underneath)
    var meanPoly = svgEl.querySelector('.fc17-mean-polygon');
    if (meanPoly) {
      var consPoly = document.createElementNS(SVG_NS, 'polygon');
      consPoly.setAttribute('class', 'fc17-consensus-polygon');
      consPoly.setAttribute('points', consensusPoints);
      meanPoly.parentNode.insertBefore(consPoly, meanPoly);

      // Consensus vertex dots (subtle, beneath FC dots)
      axisDefs.forEach(function(def) {
        var v = Math.max(0, Math.min(10, cdata.consensus[def[0]] || 0));
        var p = pointAt(def[1], v, CX, CY, MAX_R);
        var dot = document.createElementNS(SVG_NS, 'circle');
        dot.setAttribute('class', 'fc17-consensus-dot');
        dot.setAttribute('cx', p.x.toFixed(1));
        dot.setAttribute('cy', p.y.toFixed(1));
        dot.setAttribute('r', '2.5');
        meanPoly.parentNode.insertBefore(dot, meanPoly);
      });
    }

    // Legend below the polygon (FC · Consensus · CI band)
    var layout = root.querySelector('.fc17-layout');
    var legend = document.createElement('div');
    legend.className = 'fc17-asym-legend';
    legend.innerHTML =
      '<div class="leg-item"><span class="leg-sw fc"></span><span>FieldCheck · calculated</span></div>' +
      '<div class="leg-item"><span class="leg-sw cons"></span><span>Market consensus · shadow</span></div>' +
      '<div class="leg-item"><span class="leg-sw ci"></span><span>95% CI band</span></div>';
    if (layout && layout.parentNode) {
      layout.parentNode.insertBefore(legend, layout.nextSibling);
    }

    // Asymmetry callout (below legend, shape-based)
    var shape = cdata.shape || 'hype';
    var callout = document.createElement('div');
    callout.className = 'fc17-asym-callout ' + shape;

    var label, text;
    if (shape === 'converged') {
      label = '▌ The convergence';
      text = 'Consensus and FieldCheck <strong>align</strong> on every axis — the asymmetry has collapsed into truth. This is what the algorithm gravitates toward over time: validated evidence eliminates the gap.';
    } else if (shape === 'gem') {
      label = '▌ The asymmetry · hidden gem';
      text = '<strong>The polygon stands alone</strong>. No market consensus exists — the gem is hidden because the market wasn\'t looking.';
    } else {
      label = '▌ The asymmetry';
      text = 'Market grades on <strong>projection</strong>. We grade on <strong>evidence-against-10</strong>. The consensus polygon overshoots the FC polygon — that gap is the bet. Every axis above shows where the market priced production, athleticism, or character the evidence hasn\'t yet delivered.';
    }

    var metaHtml = '';
    if (cdata.sources && cdata.sources.length) {
      metaHtml = '<div class="fc17-asym-meta"><span>Consensus sources: ' + cdata.sources.join(' · ') + '</span>';
      if (cdata.last_updated) metaHtml += '<span>Last updated: ' + cdata.last_updated + '</span>';
      metaHtml += '</div>';
    }

    callout.innerHTML = '<div class="fc17-asym-lbl">' + label + '</div><div class="fc17-asym-txt">' + text + '</div>' + metaHtml;

    if (legend && legend.parentNode) {
      legend.parentNode.insertBefore(callout, legend.nextSibling);
    } else if (layout && layout.parentNode) {
      layout.parentNode.insertBefore(callout, layout.nextSibling);
    }
  }

})();
