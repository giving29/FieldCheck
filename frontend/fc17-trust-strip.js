// ═══════════════════════════════════════════════════════════════════════
// FC17 · Number-First Trust Strip · standalone component
// ═══════════════════════════════════════════════════════════════════════
//
// PURPOSE:
//   Implements the Hudl H9 adoption insight from HUDL_CASE_STUDY_V1.html:
//   "Lead with quantified social proof. Big specific numbers. Logo strip
//   is risky pre-traction — wait until 3+ real validators. Critical FC
//   differentiator: show the failures too."
//
//   This module renders a number-first trust strip with FieldCheck's
//   quantified credibility. Honest numbers only — no inflated claims.
//
// DEPLOYMENT TARGETS:
//   - homepage (index.html) · below hero, above cinematic
//   - verdict.html · footer, above legal
//   - methodology page · top, as trust anchor
//   - About page (when created)
//   - /predictions ledger · as confirmation header
//
// API:
//   FC17_TRUST.mount(container, opts)
//   FC17_TRUST.render(opts)  → HTML string
//   FC17_TRUST.getStats()     → current stats object
//   FC17_TRUST.updateStat(key, value)  → live update (for cohort growth)
//
// HONESTY DISCIPLINE:
//   Numbers in this module MUST reflect reality at the moment. When the
//   v1.7.A cohort closes Aug 15 2028 and calibration data comes in, this
//   module gets a 5th number: "X% predictions inside CI" — the killer
//   trust line that Hudl can't publish.
//
// ═══════════════════════════════════════════════════════════════════════

(function(){
  'use strict';

  // ─── STATS · current honest numbers as of May 19, 2026 ──────────────
  // Update these as the moat grows. Comments document the source/calculation.
  const STATS = {
    framework_version: {
      value: 'v1.7',
      label: 'unified framework',
      detail: '8 canonical facets · all sports'
    },
    facets: {
      value: '8',
      label: 'canonical facets',
      detail: 'Character · Mindset · Mental Strength · Talent · Physical · Mental/IQ · Coachability · Competitiveness'
    },
    phd_reviewers: {
      value: '25',
      label: 'PhD panel',
      detail: 'reviewed framework + first cohort verdicts · documented dissents (1: Vance on Flagg)'
    },
    pre_registered: {
      value: '50',
      label: 'pre-registered predictions',
      detail: 'v1.7.A cohort · locked May 17 2026 · check-in Aug 15 2028'
    }
    // Future stats (uncomment when honest):
    // calibration_accuracy: {  // after Aug 15 2028
    //   value: '—',
    //   label: 'predictions inside CI',
    //   detail: 'first cohort check-in pending'
    // },
    // refinements_versioned: {
    //   value: '6',
    //   label: 'refinement rules',
    //   detail: 'R1-R6 · Yamamoto MIN · injury risk · coachability bias · CI widening · cascade'
    // }
  };


  // ─── inject styles once ─────────────────────────────────────────────
  let stylesInjected = false;
  function injectStyles(){
    if (stylesInjected || document.getElementById('fc17-trust-styles')) return;
    const style = document.createElement('style');
    style.id = 'fc17-trust-styles';
    style.textContent = `
.fc17-trust-strip{
  background:linear-gradient(135deg,rgba(245,184,0,.04),rgba(13,12,18,.55));
  border:1px solid rgba(245,184,0,.18);
  border-radius:16px;
  padding:28px 32px;
  margin:24px 0;
  font-family:'Inter',-apple-system,sans-serif;
  position:relative;overflow:hidden
}
.fc17-trust-strip::before{
  content:'';position:absolute;top:0;left:0;width:3px;height:100%;
  background:linear-gradient(180deg,#F5B800,rgba(245,184,0,.2))
}
.fc17-trust-eyebrow{
  font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;
  color:#F5B800;letter-spacing:1.4px;text-transform:uppercase;
  margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;
  gap:14px;flex-wrap:wrap
}
.fc17-trust-eyebrow .fc17-trust-cohort{
  font-size:9.5px;color:rgba(245,241,232,.46);font-weight:500;
  letter-spacing:.6px;text-transform:none
}
.fc17-trust-eyebrow .fc17-trust-cohort b{color:rgba(245,241,232,.74)}

.fc17-trust-grid{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));
  gap:16px;margin-bottom:18px
}
.fc17-trust-cell{
  padding:14px 16px;
  background:rgba(0,0,0,.25);
  border:1px solid rgba(255,252,245,.05);
  border-radius:10px;
  position:relative
}
.fc17-trust-cell:nth-child(1){border-left:2px solid #F5B800}
.fc17-trust-cell:nth-child(2){border-left:2px solid #6BAA5A}
.fc17-trust-cell:nth-child(3){border-left:2px solid #4EC9C0}
.fc17-trust-cell:nth-child(4){border-left:2px solid #F5B800}

.fc17-trust-val{
  font-family:'Anton',sans-serif;font-size:32px;
  letter-spacing:-.015em;line-height:1;color:#F5F1E8;margin-bottom:6px
}
.fc17-trust-cell:nth-child(1) .fc17-trust-val{color:#F5B800}
.fc17-trust-cell:nth-child(2) .fc17-trust-val{color:#F5F1E8}
.fc17-trust-cell:nth-child(3) .fc17-trust-val{color:#4EC9C0}
.fc17-trust-cell:nth-child(4) .fc17-trust-val{color:#F5F1E8}

.fc17-trust-lbl{
  font-family:'JetBrains Mono',monospace;font-size:9.5px;font-weight:700;
  color:rgba(245,241,232,.74);letter-spacing:1.1px;text-transform:uppercase;
  margin-bottom:6px;line-height:1.3
}
.fc17-trust-detail{
  font-family:'Inter',sans-serif;font-size:11px;
  color:rgba(245,241,232,.46);line-height:1.5;letter-spacing:.1px
}

.fc17-trust-foot{
  padding-top:16px;border-top:1px solid rgba(255,252,245,.05);
  display:flex;justify-content:space-between;align-items:center;
  gap:14px;flex-wrap:wrap
}
.fc17-trust-foot-l{
  font-family:'Cormorant Garamond',serif;font-style:italic;
  font-size:14.5px;color:rgba(245,241,232,.74);line-height:1.5;flex:1;min-width:240px
}
.fc17-trust-foot-l b{
  color:#F5B800;font-style:normal;font-family:'Inter',sans-serif;font-weight:600
}
.fc17-trust-foot-r{
  font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;
  color:rgba(245,241,232,.46);letter-spacing:.6px;text-transform:uppercase
}
.fc17-trust-foot-r a{
  color:#F5B800;text-decoration:none;border-bottom:1px solid rgba(245,184,0,.3);
  padding-bottom:1px;transition:border-color .2s ease
}
.fc17-trust-foot-r a:hover{border-color:#F5B800}
.fc17-trust-foot-r .pip{
  display:inline-block;width:6px;height:6px;border-radius:50%;
  background:#6BAA5A;margin-right:6px;vertical-align:middle;
  animation:fc17-trust-pulse 2s ease-in-out infinite
}
@keyframes fc17-trust-pulse{
  0%,100%{opacity:.4;transform:scale(.85)}
  50%{opacity:1;transform:scale(1.1)}
}

/* compact variant · for footer placement */
.fc17-trust-strip.compact{padding:18px 22px}
.fc17-trust-strip.compact .fc17-trust-val{font-size:22px}
.fc17-trust-strip.compact .fc17-trust-grid{gap:10px;margin-bottom:12px}
.fc17-trust-strip.compact .fc17-trust-cell{padding:10px 12px}
.fc17-trust-strip.compact .fc17-trust-detail{font-size:10px}
.fc17-trust-strip.compact .fc17-trust-foot-l{font-size:13px}

/* dark variant · for use over images / video */
.fc17-trust-strip.over-media{
  background:rgba(6,5,10,.85);backdrop-filter:blur(12px);
  -webkit-backdrop-filter:blur(12px)
}
    `;
    document.head.appendChild(style);
    stylesInjected = true;
  }


  // ─── HTML escape helper ─────────────────────────────────────────────
  function esc(s){
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }


  // ─── render(opts) → HTML string ─────────────────────────────────────
  // opts.variant = 'default' | 'compact' | 'over-media'
  // opts.eyebrow = override default eyebrow text
  // opts.foot = override default footer text
  // opts.linkPredictionLedger = boolean (default true)
  function render(opts){
    opts = opts || {};
    const variant = opts.variant === 'compact' ? ' compact'
                  : opts.variant === 'over-media' ? ' over-media'
                  : '';
    const eyebrow = opts.eyebrow || '// trust by the numbers · honest stats only';
    const cohortNote = opts.cohortNote || 'v1.7.A cohort · locked <b>May 17 2026</b> · first check-in <b>Aug 15 2028</b>';
    const linkLedger = opts.linkPredictionLedger !== false;
    const footText = opts.foot ||
      'Everything above is verifiable. When the August 2028 check-in arrives, this strip gains a <b>5th number</b> — predictions-inside-CI accuracy. We publish the wrong ones, by name, on the ledger.';

    let h = '<div class="fc17-trust-strip' + variant + '">';

    h += '<div class="fc17-trust-eyebrow">';
    h += '<span>' + esc(eyebrow) + '</span>';
    h += '<span class="fc17-trust-cohort">' + cohortNote + '</span>';
    h += '</div>';

    h += '<div class="fc17-trust-grid">';
    Object.keys(STATS).forEach(function(key){
      const s = STATS[key];
      h += '<div class="fc17-trust-cell">';
      h += '<div class="fc17-trust-val">' + esc(s.value) + '</div>';
      h += '<div class="fc17-trust-lbl">// ' + esc(s.label) + '</div>';
      h += '<div class="fc17-trust-detail">' + esc(s.detail) + '</div>';
      h += '</div>';
    });
    h += '</div>';

    h += '<div class="fc17-trust-foot">';
    h += '<div class="fc17-trust-foot-l">' + footText + '</div>';
    if (linkLedger) {
      h += '<div class="fc17-trust-foot-r">';
      h += '<span class="pip"></span>';
      h += '<a href="/predictions">View ledger →</a>';
      h += '</div>';
    }
    h += '</div>';

    h += '</div>'; // .fc17-trust-strip

    return h;
  }


  // ─── mount(container, opts) → DOM mutation ──────────────────────────
  // container can be: DOM Element, OR string selector (e.g. '#trust-anchor')
  function mount(container, opts){
    if (!container) {
      console.warn('FC17_TRUST.mount: missing container');
      return false;
    }
    // Resolve string selectors → DOM Element
    if (typeof container === 'string') {
      const el = document.querySelector(container);
      if (!el) {
        console.warn('FC17_TRUST.mount: selector "' + container + '" matched no element');
        return false;
      }
      container = el;
    }
    if (!container.insertAdjacentHTML) {
      console.warn('FC17_TRUST.mount: container is not a DOM Element', container);
      return false;
    }
    injectStyles();
    const html = render(opts);
    if (opts && opts.position === 'replace') {
      container.innerHTML = html;
    } else {
      container.insertAdjacentHTML('beforeend', html);
    }
    return true;
  }


  // ─── getStats() ─ for ad-hoc inspection ─────────────────────────────
  function getStats(){
    return JSON.parse(JSON.stringify(STATS));
  }


  // ─── updateStat(key, value) ─ for live cohort growth ────────────────
  // Future use: when the cohort grows to 75, 100, etc., or when calibration
  // accuracy publishes, call FC17_TRUST.updateStat('pre_registered', '75').
  function updateStat(key, value){
    if (STATS[key]) {
      STATS[key].value = value;
      // Update any mounted instances
      const cells = document.querySelectorAll('.fc17-trust-strip .fc17-trust-cell');
      const keys = Object.keys(STATS);
      const idx = keys.indexOf(key);
      if (idx >= 0 && cells[idx]) {
        const valEl = cells[idx].querySelector('.fc17-trust-val');
        if (valEl) valEl.textContent = value;
      }
      return true;
    }
    return false;
  }


  // ─── EXPORT ─────────────────────────────────────────────────────────
  window.FC17_TRUST = {
    render: render,
    mount: mount,
    getStats: getStats,
    updateStat: updateStat
  };

})();


// ═══════════════════════════════════════════════════════════════════════
// INTEGRATION EXAMPLES
// ═══════════════════════════════════════════════════════════════════════
//
// HOMEPAGE (index.html):
//   <div id="trust-anchor"></div>
//   <script src="/fc17-trust-strip.js" defer></script>
//   <script>
//     window.addEventListener('DOMContentLoaded', function(){
//       FC17_TRUST.mount(document.getElementById('trust-anchor'), {
//         eyebrow: '// trust by the numbers',
//         variant: 'default'
//       });
//     });
//   </script>
//
// VERDICT.HTML FOOTER (compact variant):
//   FC17_TRUST.mount(footerEl, { variant: 'compact', linkPredictionLedger: true });
//
// PREDICTION LEDGER PAGE (no link to itself):
//   FC17_TRUST.mount(headerEl, {
//     eyebrow: '// the ledger · by the numbers',
//     linkPredictionLedger: false
//   });
//
// METHODOLOGY PAGE (over hero image):
//   FC17_TRUST.mount(heroEl, { variant: 'over-media' });
//
// ═══════════════════════════════════════════════════════════════════════


// ═══════════════════════════════════════════════════════════════════════
// HONESTY UPGRADE PATH · when these stats earn upgrades
// ═══════════════════════════════════════════════════════════════════════
//
// Aug 15 2028 (first cohort check-in):
//   - Add calibration_accuracy stat: "X% predictions inside CI"
//   - Update STATS[pre_registered].value to reflect cohort closures
//   - Add closed_wrong stat if useful: "N predictions we got wrong (see ledger)"
//
// Cohort growth (per added 25 players in a sport):
//   - Update STATS[pre_registered].value
//   - Detail field can list sport breakdowns
//
// Framework v1.8 publishes (5-year cycle):
//   - Update STATS[framework_version].value
//   - Honor v1.7's locked verdicts · v1.8 only applies to v1.8.A cohort
//
// First real revenue tier validation (3+ named case studies):
//   - At that point, logo strip becomes defensible
//   - Build separate fc17-logo-strip.js · keep this module pure-numbers
//
// ═══════════════════════════════════════════════════════════════════════
