// ═══════════════════════════════════════════════════════════════════════
// FC17 · v1.7 Interpretation Panel · standalone module
// ═══════════════════════════════════════════════════════════════════════
//
// Renders the v1.7 native interpretation that replaces the legacy
// .scpanel (Composite breakdown · Physical/Scoring/Pathway 3-axis rollup)
// and .ibox (FieldCheck interpretation · "Generational profile at 9.6")
// elements hidden by FC17.S2A.2.
//
// What it shows:
//   - 3 interpretation paragraphs (from FLAGG_V17.posterior.interpretation)
//   - Confidence disclosure (confident / not confident / what would change)
//   - Continuous learning cadence (last refinement, next refresh, reviewer)
//
// API:
//   window.FC17_INTERPRETATION.isAvailable(playerName)
//   window.FC17_INTERPRETATION.render(playerName)   → HTML string
//   window.FC17_INTERPRETATION.mount(container, opts)  → DOM mutation
//
// Consumed by: fieldcheck-verdict.html post-render hook
// Data source: window.FLAGG_V17 (loaded by fc17-s2b-flagg-data.js)
//
// Tenet 15.1: all CSS classes namespaced fc17-int-* to avoid collisions
// with existing FieldCheck styles.
//
// ═══════════════════════════════════════════════════════════════════════

(function(){
  'use strict';

  // ─── slug normalization (matches fc17-polygon-mount.js) ─────────────
  function normalizeSlug(raw){
    if (!raw) return '';
    return String(raw).toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  // ─── slug aliases · maps display name → window.X_V17 global ─────────
  const PLAYER_GLOBALS = {
    'cooperflagg':  'FLAGG_V17',
    'calebwilliams': 'CALEB_V17',
    'caitlinclark': 'CAITLIN_V17',
    'averyskinner': 'SKINNER_V17'
  };

  // ─── HTML escape helper ─────────────────────────────────────────────
  function esc(s){
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  // ─── lookup player data ──────────────────────────────────────────────
  function getPlayerData(playerName){
    const slug = normalizeSlug(playerName);
    const globalKey = PLAYER_GLOBALS[slug];
    if (!globalKey) return null;
    return window[globalKey] || null;
  }


  // ─── INJECT STYLES ONCE ─────────────────────────────────────────────
  let stylesInjected = false;
  function injectStyles(){
    if (stylesInjected || document.getElementById('fc17-int-styles')) return;
    const style = document.createElement('style');
    style.id = 'fc17-int-styles';
    style.textContent = `
.fc17-int-panel{
  background:linear-gradient(135deg,rgba(245,184,0,.03),rgba(13,12,18,.55));
  border:1px solid rgba(245,184,0,.18);
  border-radius:16px;
  padding:26px 28px;
  margin-top:18px;
  font-family:'Inter',-apple-system,sans-serif;
  color:rgba(245,241,232,.74);
  position:relative;
}
.fc17-int-panel::before{
  content:'';position:absolute;top:0;left:0;width:3px;height:100%;
  background:linear-gradient(180deg,#F5B800,rgba(245,184,0,.2));border-radius:16px 0 0 16px
}
.fc17-int-h{
  font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;
  color:#F5B800;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:14px;
  display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap
}
.fc17-int-h .fc17-int-rev{
  font-size:9.5px;color:rgba(245,241,232,.46);font-weight:500;letter-spacing:.6px;text-transform:none
}
.fc17-int-h .fc17-int-rev b{color:rgba(245,241,232,.74)}

.fc17-int-body{margin-bottom:20px}
.fc17-int-body p{
  font-family:'Cormorant Garamond',serif;font-style:italic;
  font-size:15.5px;line-height:1.7;color:#F5F1E8;
  margin-bottom:14px
}
.fc17-int-body p:last-child{margin-bottom:0}
.fc17-int-body p:first-child::first-letter{
  font-size:2.4em;line-height:1;float:left;
  margin:4px 8px 0 0;color:#F5B800;font-weight:700;font-style:normal
}

.fc17-int-disc{
  display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;
  padding-top:18px;border-top:1px solid rgba(255,252,245,.05)
}
@media(max-width:760px){.fc17-int-disc{grid-template-columns:1fr}}
.fc17-int-disc-card{
  padding:14px 16px;background:rgba(0,0,0,.25);
  border:1px solid rgba(255,252,245,.05);border-radius:10px
}
.fc17-int-disc-card.conf{border-left:2px solid #6BAA5A}
.fc17-int-disc-card.unconf{border-left:2px solid #4EC9C0}
.fc17-int-disc-card.change{border-left:2px solid #F5B800}
.fc17-int-disc-h{
  font-family:'JetBrains Mono',monospace;font-size:9.5px;font-weight:700;
  letter-spacing:1.1px;text-transform:uppercase;margin-bottom:10px
}
.fc17-int-disc-card.conf .fc17-int-disc-h{color:#6BAA5A}
.fc17-int-disc-card.unconf .fc17-int-disc-h{color:#4EC9C0}
.fc17-int-disc-card.change .fc17-int-disc-h{color:#F5B800}
.fc17-int-disc-card ul{list-style:none;padding:0;margin:0}
.fc17-int-disc-card li{
  font-size:12px;color:rgba(245,241,232,.74);line-height:1.5;
  padding:5px 0 5px 12px;position:relative;border-bottom:1px dashed rgba(255,252,245,.05)
}
.fc17-int-disc-card li:last-child{border-bottom:none}
.fc17-int-disc-card li::before{
  content:'•';position:absolute;left:0;top:5px;color:rgba(245,241,232,.46);font-weight:700
}

.fc17-int-foot{
  margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,252,245,.05);
  font-family:'JetBrains Mono',monospace;font-size:9.5px;
  color:rgba(245,241,232,.46);letter-spacing:.4px;
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px
}
.fc17-int-foot b{color:rgba(245,241,232,.74)}
.fc17-int-foot .fc17-int-foot-r{text-align:right}
.fc17-int-foot .fc17-int-foot-r .pip{
  display:inline-block;width:6px;height:6px;border-radius:50%;
  background:#6BAA5A;margin-right:5px;
  animation:fc17-int-pulse 2s ease-in-out infinite
}
@keyframes fc17-int-pulse{
  0%,100%{opacity:.4;transform:scale(.85)}
  50%{opacity:1;transform:scale(1.1)}
}
    `;
    document.head.appendChild(style);
    stylesInjected = true;
  }


  // ─── RENDER ─────────────────────────────────────────────────────────
  function render(playerName){
    const data = getPlayerData(playerName);
    if (!data || !data.posterior) return '';

    const p = data.posterior;
    const interp = p.interpretation;
    const disc = p.confidence_disclosure;
    const cont = p.continuous_learning;
    if (!interp || !interp.paragraphs) return '';

    let h = '<div class="fc17-int-panel">';

    // Header
    h += '<div class="fc17-int-h">';
    h += '<span>// FieldCheck v1.7 interpretation</span>';
    if (interp.reviewed_by) {
      h += '<span class="fc17-int-rev">Reviewed by <b>'+esc(interp.reviewed_by)+'</b>';
      if (interp.confidence) h += ' · confidence <b>'+esc(interp.confidence)+'</b>';
      h += '</span>';
    }
    h += '</div>';

    // Paragraphs
    h += '<div class="fc17-int-body">';
    interp.paragraphs.forEach(function(para){
      h += '<p>'+esc(para)+'</p>';
    });
    h += '</div>';

    // Confidence disclosure (3-column)
    if (disc) {
      h += '<div class="fc17-int-disc">';

      if (disc.confident_about && disc.confident_about.length) {
        h += '<div class="fc17-int-disc-card conf">';
        h += '<div class="fc17-int-disc-h">// Confident about</div>';
        h += '<ul>';
        disc.confident_about.forEach(function(item){
          h += '<li>'+esc(item)+'</li>';
        });
        h += '</ul></div>';
      }

      if (disc.not_confident_about && disc.not_confident_about.length) {
        h += '<div class="fc17-int-disc-card unconf">';
        h += '<div class="fc17-int-disc-h">// Not confident about</div>';
        h += '<ul>';
        disc.not_confident_about.forEach(function(item){
          h += '<li>'+esc(item)+'</li>';
        });
        h += '</ul></div>';
      }

      if (disc.what_would_change && disc.what_would_change.length) {
        h += '<div class="fc17-int-disc-card change">';
        h += '<div class="fc17-int-disc-h">// What would change</div>';
        h += '<ul>';
        disc.what_would_change.forEach(function(item){
          h += '<li>'+esc(item)+'</li>';
        });
        h += '</ul></div>';
      }

      h += '</div>';
    }

    // Footer · continuous learning cadence
    if (cont) {
      h += '<div class="fc17-int-foot">';
      h += '<span>';
      if (cont.last_refinement) h += 'Last refinement <b>'+esc(cont.last_refinement)+'</b>';
      if (cont.framework_lock) h += ' · Framework <b>'+esc(cont.framework_lock)+'</b>';
      if (cont.next_checkin) h += ' · Next cohort check-in <b>'+esc(cont.next_checkin)+'</b>';
      h += '</span>';
      h += '<span class="fc17-int-foot-r"><span class="pip"></span>Continuous learning · ';
      if (cont.cadence && cont.cadence.outcomes_ingestion) {
        h += esc(cont.cadence.outcomes_ingestion)+' ingestion';
      } else {
        h += 'active';
      }
      h += '</span>';
      h += '</div>';
    }

    h += '</div>'; // .fc17-int-panel
    return h;
  }


  // ─── MOUNT (DOM mutation) ────────────────────────────────────────────
  // opts.container = DOM element to append into
  // opts.playerName = player name string
  // opts.position = 'append' | 'replace' (default 'append')
  function mount(opts){
    if (!opts || !opts.container || !opts.playerName) {
      console.warn('FC17_INTERPRETATION.mount: missing container or playerName');
      return false;
    }
    injectStyles();
    const html = render(opts.playerName);
    if (!html) return false;

    if (opts.position === 'replace') {
      opts.container.innerHTML = html;
    } else {
      // Default: append (insertAdjacentHTML to avoid wiping siblings)
      opts.container.insertAdjacentHTML('beforeend', html);
    }
    return true;
  }


  // ─── AVAILABILITY CHECK ─────────────────────────────────────────────
  function isAvailable(playerName){
    const data = getPlayerData(playerName);
    return !!(data && data.posterior && data.posterior.interpretation);
  }


  // ─── EXPORT ─────────────────────────────────────────────────────────
  window.FC17_INTERPRETATION = {
    isAvailable: isAvailable,
    render: render,
    mount: mount
  };

})();
