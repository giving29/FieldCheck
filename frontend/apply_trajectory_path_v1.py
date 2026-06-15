#!/usr/bin/env python3
"""
apply_trajectory_path_v1.py

FCBase34 · Phase 5 Strike 5 · Trajectory + Path-to-Tier.

The psychological hook from Tenet 40 — every athlete sees their PATH.
Inserts a "// TRAJECTORY" section on every verdict page showing:

  - Horizontal progress bar from current tier to next tier
  - Marker at the player's exact composite position
  - Gap-to-next-tier readout (e.g. "0.2 to PROSPECT")
  - "Closest path" — 3 lowest facets with targets and delta needed
  - For ICON-tier players: "Standout facets" instead

Tier ladder from Tenet 49:
  ICON     9.5\\u201310.0
  ELITE+   9.0\\u20139.49
  ELITE    7.5\\u20138.99
  STAR     7.0\\u20137.49
  PROSPECT 5.5\\u20136.99
  SCOUT    3.5\\u20135.49

Uses IDENTICAL hashing logic to FCBase31/32/33 so facet scores are
consistent across page polygon, share card polygon, peer-compare, and
trajectory \\u2014 one fingerprint per player, everywhere.

Single str_replace: injects the module before </body>.

Run from fieldcheck-proxy directory:
  python3 apply_trajectory_path_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-trajectory.bak')

TRAJECTORY_BLOCK = """<!-- FCBase34 · Phase 5 Strike 5 · Trajectory + Path-to-Tier (2026-06-07) -->
<script>
(function(){
  if (window._fcTrajInit) return;
  window._fcTrajInit = true;

  var FACETS = ['Character','Mindset','Mental Strength','Talent','Physical','Mental/IQ','Coachability','Competitiveness'];

  /* Tenet 49 tier ladder */
  var TIERS = [
    { name: 'SCOUT',    min: 3.5,  max: 5.49 },
    { name: 'PROSPECT', min: 5.5,  max: 6.99 },
    { name: 'STAR',     min: 7.0,  max: 7.49 },
    { name: 'ELITE',    min: 7.5,  max: 8.99 },
    { name: 'ELITE+',   min: 9.0,  max: 9.49 },
    { name: 'ICON',     min: 9.5,  max: 10.0 }
  ];

  /* ─── CSS ─── */
  var css = [
    '.fc-traj-section{padding:32px 24px;margin:8px 0 14px;border-radius:18px;background:linear-gradient(180deg,rgba(20,20,26,.6) 0%,rgba(10,10,14,.4) 100%);border:1px solid #2a2a32;position:relative;overflow:hidden}',
    '.fc-traj-section::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(240,198,110,.4),transparent)}',
    '.fc-traj-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:rgba(240,198,110,.85)}',
    '.fc-traj-sub{color:rgba(255,255,255,.45);font-size:10px}',
    /* Progress bar */
    '.fc-traj-progress{margin-bottom:18px}',
    '.fc-traj-progress-bar{position:relative;height:8px;background:rgba(255,255,255,.06);border-radius:999px;overflow:visible;margin:0 8px}',
    '.fc-traj-progress-fill{position:absolute;top:0;left:0;height:100%;background:linear-gradient(90deg,rgba(240,198,110,.4),#f0c66e);border-radius:999px;transition:width .6s ease}',
    '.fc-traj-marker{position:absolute;top:50%;width:16px;height:16px;background:#f0c66e;border:3px solid #0a0a0e;border-radius:50%;transform:translate(-50%,-50%);box-shadow:0 0 0 2px rgba(240,198,110,.4),0 4px 12px rgba(240,198,110,.5);z-index:2}',
    '.fc-traj-progress-labels{display:flex;justify-content:space-between;margin-top:14px;padding:0 4px}',
    '.fc-traj-label{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase}',
    '.fc-traj-label-from{color:rgba(255,255,255,.55)}',
    '.fc-traj-label-to{color:rgba(240,198,110,.85);text-align:right}',
    '.fc-traj-label-tier-name{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:18px;font-weight:700;letter-spacing:-.005em;line-height:1.1;display:block;margin-top:2px;color:#fff}',
    '.fc-traj-label-from .fc-traj-label-tier-name{color:rgba(255,255,255,.7)}',
    '.fc-traj-label-to .fc-traj-label-tier-name{color:#f0c66e}',
    /* Gap callout */
    '.fc-traj-gap-row{display:flex;align-items:center;gap:14px;padding:14px 16px;background:rgba(240,198,110,.06);border:1px solid rgba(240,198,110,.15);border-radius:12px;margin:6px 0 22px}',
    '.fc-traj-gap-value{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:36px;line-height:.9;font-weight:700;color:#f0c66e;letter-spacing:-.02em}',
    '.fc-traj-gap-label{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;line-height:1.4;color:rgba(255,255,255,.7);flex:1}',
    '.fc-traj-gap-label strong{color:rgba(255,255,255,.95);font-weight:600}',
    /* Opportunities list */
    '.fc-traj-opps{padding-top:14px;border-top:1px solid rgba(255,255,255,.08)}',
    '.fc-traj-opps-title{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.55);margin-bottom:12px}',
    '.fc-traj-opp{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;margin-bottom:6px;gap:8px}',
    '.fc-traj-opp:last-child{margin-bottom:0}',
    '.fc-traj-opp-facet{font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;color:rgba(255,255,255,.85);font-weight:500;flex:1;min-width:0}',
    '.fc-traj-opp-arrow{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:rgba(255,255,255,.55);letter-spacing:.02em;white-space:nowrap}',
    '.fc-traj-opp-delta{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:18px;font-weight:700;color:#f0c66e;letter-spacing:-.01em;min-width:42px;text-align:right}',
    /* Top-tier banner (ICON players) */
    '.fc-traj-top-banner{display:flex;align-items:center;gap:10px;padding:18px 20px;background:linear-gradient(135deg,rgba(240,198,110,.18),rgba(240,198,110,.05));border:1px solid rgba(240,198,110,.4);border-radius:14px;margin-bottom:22px;font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:24px;font-weight:700;letter-spacing:-.01em;color:#f0c66e}',
    '.fc-traj-top-banner-star{font-size:28px}',
    '.fc-traj-top-banner-text{font-size:14px;font-family:ui-sans-serif,system-ui,sans-serif;color:rgba(255,255,255,.7);font-weight:400;letter-spacing:0;line-height:1.4;margin-left:auto;text-align:right;max-width:200px}'
  ].join('');
  var sEl = document.createElement('style');
  sEl.id = 'fc-traj-styles';
  sEl.appendChild(document.createTextNode(css));
  document.head.appendChild(sEl);

  /* ─── IDENTICAL hashing to FCBase31/32/33 ─── */
  function _seed(name){
    var s = 0;
    name = String(name || 'athlete').toLowerCase();
    for (var i=0; i<name.length; i++) s = ((s << 5) - s + name.charCodeAt(i)) | 0;
    return Math.abs(s);
  }
  function _facetScores(name, composite){
    var c = parseFloat(composite);
    if (!isFinite(c) || c <= 0) c = 5.0;
    var seed = _seed(name);
    var scores = [];
    for (var i=0; i<8; i++){
      var hash = ((seed * 1103515245) + 12345 + i * 2654435761) & 0x7fffffff;
      var noise = ((hash % 2000) / 1000) - 1.0;
      var sc = c + noise * 1.6;
      scores.push(Math.max(1.5, Math.min(9.8, sc)));
      seed = hash;
    }
    return scores;
  }

  /* ─── Trajectory computation ─── */
  function _computeTrajectory(composite){
    var c = parseFloat(composite);
    if (!isFinite(c)) c = 5.0;
    var currentIdx = 0;
    for (var i=TIERS.length-1; i>=0; i--){
      if (c >= TIERS[i].min) { currentIdx = i; break; }
    }
    var current = TIERS[currentIdx];
    var next = currentIdx < TIERS.length - 1 ? TIERS[currentIdx + 1] : null;
    return {
      current: current,
      next: next,
      composite: c,
      gap: next ? (next.min - c) : 0,
      isTop: !next
    };
  }

  /* ─── Opportunities: lowest 3 facets ─── */
  function _opportunities(name, composite){
    var scores = _facetScores(name, composite);
    var indexed = scores.map(function(s, i){ return { facet: FACETS[i], score: s, idx: i }; });
    indexed.sort(function(a, b){ return a.score - b.score; });
    return indexed.slice(0, 3);
  }

  /* ─── Standouts: highest 3 facets (for ICON tier) ─── */
  function _standouts(name, composite){
    var scores = _facetScores(name, composite);
    var indexed = scores.map(function(s, i){ return { facet: FACETS[i], score: s, idx: i }; });
    indexed.sort(function(a, b){ return b.score - a.score; });
    return indexed.slice(0, 3);
  }

  /* ─── Harvest current player from DOM ─── */
  function _harvest(){
    var urlParams = new URLSearchParams(window.location.search);
    var name = urlParams.get('q') || '';
    var nameEl = document.querySelector('h1');
    if (nameEl && nameEl.textContent && nameEl.textContent.trim().length > 1 && nameEl.textContent.trim().length < 60) {
      name = nameEl.textContent.trim();
    }
    var score = '';
    var all = document.querySelectorAll('*');
    for (var i=0; i<all.length && i<1500; i++){
      var t = (all[i].textContent || '').trim();
      if (/^[0-9]\\.[0-9]$/.test(t) && all[i].children.length === 0) { score = t; break; }
    }
    return { name: name, composite: score };
  }

  /* ─── Render trajectory section ─── */
  function _render(data, traj){
    var html =
      '<div class="fc-traj-header">' +
        '<span>// Trajectory \\u00b7 path to next tier</span>' +
        '<span class="fc-traj-sub">v1.7 framework</span>' +
      '</div>';

    if (traj.isTop) {
      /* ICON-tier players: standout facets */
      var standouts = _standouts(data.name, data.composite);
      html +=
        '<div class="fc-traj-top-banner">' +
          '<span class="fc-traj-top-banner-star">\\u2605</span>' +
          '<span>' + traj.current.name + ' tier</span>' +
          '<span class="fc-traj-top-banner-text">Top of the ladder \\u00b7 maintain elite execution across the framework</span>' +
        '</div>' +
        '<div class="fc-traj-opps">' +
          '<div class="fc-traj-opps-title">Standout facets</div>';
      standouts.forEach(function(o){
        html +=
          '<div class="fc-traj-opp">' +
            '<span class="fc-traj-opp-facet">' + o.facet + '</span>' +
            '<span class="fc-traj-opp-arrow">score</span>' +
            '<span class="fc-traj-opp-delta">' + o.score.toFixed(1) + '</span>' +
          '</div>';
      });
      html += '</div>';
    } else {
      /* Progressing players: path to next tier */
      var range = traj.next.min - traj.current.min;
      var progress = Math.max(0, Math.min(1, (traj.composite - traj.current.min) / range));
      var progressPct = (progress * 100).toFixed(1);

      html +=
        '<div class="fc-traj-progress">' +
          '<div class="fc-traj-progress-bar">' +
            '<div class="fc-traj-progress-fill" style="width:' + progressPct + '%"></div>' +
            '<div class="fc-traj-marker" style="left:' + progressPct + '%" title="' + traj.composite.toFixed(1) + '"></div>' +
          '</div>' +
          '<div class="fc-traj-progress-labels">' +
            '<div class="fc-traj-label fc-traj-label-from">' +
              traj.current.min.toFixed(1) +
              '<span class="fc-traj-label-tier-name">' + traj.current.name + '</span>' +
            '</div>' +
            '<div class="fc-traj-label fc-traj-label-to">' +
              traj.next.min.toFixed(1) +
              '<span class="fc-traj-label-tier-name">' + traj.next.name + '</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div class="fc-traj-gap-row">' +
          '<div class="fc-traj-gap-value">' + traj.gap.toFixed(1) + '</div>' +
          '<div class="fc-traj-gap-label">composite points to <strong>' + traj.next.name + '</strong>. Closest path is below.</div>' +
        '</div>' +
        '<div class="fc-traj-opps">' +
          '<div class="fc-traj-opps-title">Closest path to ' + traj.next.name + '</div>';
      var opps = _opportunities(data.name, data.composite);
      opps.forEach(function(o){
        var target = Math.min(10, Math.max(o.score + 1.0, traj.next.min + 0.3));
        var delta = (target - o.score).toFixed(1);
        html +=
          '<div class="fc-traj-opp">' +
            '<span class="fc-traj-opp-facet">' + o.facet + '</span>' +
            '<span class="fc-traj-opp-arrow">' + o.score.toFixed(1) + ' \\u2192 ' + target.toFixed(1) + '</span>' +
            '<span class="fc-traj-opp-delta">+' + delta + '</span>' +
          '</div>';
      });
      html += '</div>';
    }
    return html;
  }

  /* ─── Mount section ─── */
  function _mount(){
    if (document.querySelector('.fc-traj-section')) return;
    if (!/fieldcheck-verdict\\.html/.test(window.location.pathname)) return;
    var data = _harvest();
    if (!data.name || data.name.length < 2 || !data.composite) return;

    var traj = _computeTrajectory(data.composite);

    /* Insertion: after polygon section if present, else after Hot Reels, else after first .sec */
    var anchor = document.querySelector('.fc-poly-section');
    if (!anchor) {
      var hr = document.querySelector('.fc-hr-row');
      if (hr) anchor = hr.closest('.sec');
    }
    if (!anchor) {
      var secs = document.querySelectorAll('.sec');
      if (secs.length) anchor = secs[0];
    }
    if (!anchor) return;

    var section = document.createElement('section');
    section.className = 'fc-traj-section';
    section.innerHTML = _render(data, traj);

    anchor.insertAdjacentElement('afterend', section);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', _mount);
  else _mount();
  var mo = new MutationObserver(function(){ _mount(); });
  mo.observe(document.body, { childList:true, subtree:true });
})();
</script>
</body>"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if '</body>' not in content:
        print("ERROR: </body> not found.")
        return 1
    if content.count('</body>') > 1:
        print(f"ERROR: </body> appears {content.count('</body>')} times. Ambiguous.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace('</body>', TRAJECTORY_BLOCK, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Trajectory + Path-to-Tier module injected  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh and verify across tiers:")
    print("  JSJ (5.3 SCOUT \\u2192 PROSPECT path):")
    print("    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print("  Boozer (ICON tier banner expected):")
    print("    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Boozer&sport=mens-basketball")
    print("  Williams (~ELITE, gap to ELITE+):")
    print("    https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Cameron+Williams&sport=mens-basketball")
    print()
    print("Expected layout per player:")
    print("  Hot Reels \\u2192 Polygon \\u2192 TRAJECTORY \\u2192 Highlights \\u2192 News")
    print()
    print("Section shows:")
    print("  - Progress bar from current-tier-min \\u2192 next-tier-min with gold marker at composite")
    print("  - Gap callout: '0.2 composite points to PROSPECT'")
    print("  - 3 lowest facets with score \\u2192 target + delta")
    print("  - ICON players: standout-facets banner instead of progress bar")
    print()
    print("Ship to prod:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase34_TRAJECTORY_LIVE")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
