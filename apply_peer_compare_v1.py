#!/usr/bin/env python3
"""
apply_peer_compare_v1.py

FCBase33 · Phase 5 Strike 4 · Peer-Compare with Dual Polygon Overlay.

Closes the Phase 5 share-stack with head-to-head comparison. Adds a second
floating "Compare" button stacked above the Share Card FAB. Tap to open a
modal with:
  - Free-text player input
  - 5 quick-pick chips (Boozer, Dybantsa, Stokes, Williams, Brandon)
  - Dual polygon overlay (gold = current player, silver = comparison)
  - Side-by-side composite + tier readout
  - Share comparison button (html2canvas \\u2192 PNG)

Architecture:
  - Pure additive patch. Doesn't modify FCBase30/31/32.
  - Live fetch against the worker API (same endpoint the verdict page uses).
  - Auto-detects dev vs prod worker URL from page hostname.
  - Polygon hashing logic IDENTICAL to FCBase31/32 \\u2192 fingerprints match.
  - Graceful fallback if API fails (shows polygon shapes from name hash).

Single str_replace: injects the module before </body>.

Run from fieldcheck-proxy directory:
  python3 apply_peer_compare_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-peer-compare.bak')

PEER_COMPARE_BLOCK = """<!-- FCBase33 · Phase 5 Strike 4 · Peer-Compare with Dual Polygon (2026-06-07) -->
<script>
(function(){
  if (window._fcCompareInit) return;
  window._fcCompareInit = true;

  var FACETS = ['Character','Mindset','Mental Strength','Talent','Physical','Mental/IQ','Coachability','Competitiveness'];
  var SHORT_LABELS = ['CHAR','MIND','STR','TLT','PHY','IQ','COA','COMP'];
  var QUICK_PICKS = [
    { name: 'Cameron Boozer', sport: 'mens-basketball' },
    { name: 'AJ Dybantsa', sport: 'mens-basketball' },
    { name: 'Tyran Stokes', sport: 'mens-basketball' },
    { name: 'Cameron Williams', sport: 'mens-basketball' },
    { name: 'Faizon Brandon', sport: 'football' }
  ];

  /* Worker URL auto-detect (dev vs prod) */
  var WORKER_URL = /-dev--|fieldcheck-dev/.test(window.location.hostname)
    ? 'https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev'
    : 'https://fieldcheck-proxy.sridhar-nallani.workers.dev';

  /* ─── CSS ─── */
  var css = [
    /* Compare FAB - stacked above Share Card */
    '.fc-cmp-fab{position:fixed;bottom:88px;right:24px;z-index:9998;background:linear-gradient(135deg,#1a1a22,#0a0a0e);color:#f0c66e;border:1px solid rgba(240,198,110,.5);width:auto;padding:13px 20px;border-radius:999px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:14px;font-weight:600;letter-spacing:.02em;cursor:pointer;box-shadow:0 10px 28px -8px rgba(0,0,0,.5);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease;display:flex;align-items:center;gap:8px}',
    '.fc-cmp-fab:hover{transform:translateY(-2px);border-color:rgba(240,198,110,.85);box-shadow:0 14px 32px -10px rgba(240,198,110,.35)}',
    '.fc-cmp-fab svg{width:18px;height:18px;display:block}',
    '@media(max-width:480px){.fc-cmp-fab{bottom:74px;right:18px;padding:11px 16px;font-size:13px}}',
    /* Modal */
    '.fc-cmp-mod-overlay{position:fixed;inset:0;background:rgba(8,8,12,.94);z-index:99999;display:flex;align-items:center;justify-content:center;padding:24px;animation:fcCmpFade .25s ease;overflow-y:auto}',
    '@keyframes fcCmpFade{from{opacity:0}to{opacity:1}}',
    '.fc-cmp-mod-content{position:relative;max-width:min(520px,95vw);width:100%;display:flex;flex-direction:column;gap:18px;margin:auto;background:linear-gradient(180deg,#13131a 0%,#0a0a0e 100%);border:1px solid #2a2a32;border-radius:20px;padding:28px 24px 24px;box-shadow:0 30px 80px -20px rgba(0,0,0,.9)}',
    '.fc-cmp-mod-close{position:absolute;top:14px;right:14px;background:transparent;color:rgba(255,255,255,.6);border:0;width:32px;height:32px;border-radius:50%;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;font-family:system-ui;transition:background .2s ease,color .2s ease}',
    '.fc-cmp-mod-close:hover{background:rgba(255,255,255,.08);color:#f0c66e}',
    '.fc-cmp-header{padding-right:36px}',
    '.fc-cmp-title{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:24px;line-height:1.1;color:#fff;letter-spacing:-.005em;font-weight:700}',
    '.fc-cmp-subtitle{font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.1em;color:rgba(240,198,110,.7);text-transform:uppercase;margin-top:6px}',
    '.fc-cmp-picker{display:flex;flex-direction:column;gap:12px}',
    '.fc-cmp-input{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:12px 14px;color:#fff;font-family:ui-sans-serif,system-ui,sans-serif;font-size:13.5px;outline:none;transition:border-color .2s ease}',
    '.fc-cmp-input:focus{border-color:rgba(240,198,110,.6)}',
    '.fc-cmp-input::placeholder{color:rgba(255,255,255,.35)}',
    '.fc-cmp-chips{display:flex;flex-wrap:wrap;gap:7px}',
    '.fc-cmp-chip{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:8px 14px;color:rgba(255,255,255,.85);font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;cursor:pointer;transition:all .2s ease;font-weight:500}',
    '.fc-cmp-chip:hover{background:rgba(240,198,110,.12);border-color:rgba(240,198,110,.4);color:#f0c66e}',
    '.fc-cmp-result{min-height:0}',
    '.fc-cmp-loading{padding:30px;text-align:center;color:rgba(255,255,255,.5);font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase}',
    '.fc-cmp-loading::after{content:"\\u2026";animation:fcCmpDots 1.4s infinite}',
    '@keyframes fcCmpDots{0%,20%{content:"."}40%{content:".."}60%,100%{content:"..."}}',
    '.fc-cmp-error{padding:20px;text-align:center;color:rgba(255,150,150,.85);font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px}',
    /* Dual polygon visualization */
    '.fc-cmp-viz{display:flex;flex-direction:column;gap:14px;padding-top:8px;border-top:1px solid rgba(255,255,255,.08)}',
    '.fc-cmp-viz svg{width:100%;max-width:340px;height:auto;display:block;margin:0 auto;overflow:visible}',
    '.fc-cmp-viz .pgrid{fill:none;stroke:rgba(255,255,255,.06);stroke-width:1}',
    '.fc-cmp-viz .paxis{stroke:rgba(255,255,255,.04);stroke-width:1}',
    /* Player A (current) - gold */
    '.fc-cmp-viz .shape-a-fill{fill:rgba(240,198,110,.18)}',
    '.fc-cmp-viz .shape-a-stroke{fill:none;stroke:#f0c66e;stroke-width:2;stroke-linejoin:round}',
    '.fc-cmp-viz .vertex-a{fill:#f0c66e}',
    /* Player B (compare) - silver */
    '.fc-cmp-viz .shape-b-fill{fill:rgba(200,210,235,.12)}',
    '.fc-cmp-viz .shape-b-stroke{fill:none;stroke:#c8d2eb;stroke-width:1.8;stroke-linejoin:round;stroke-dasharray:4,3}',
    '.fc-cmp-viz .vertex-b{fill:#c8d2eb}',
    '.fc-cmp-viz .plabel{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;fill:rgba(255,255,255,.7);letter-spacing:.05em;font-weight:600}',
    /* Side-by-side comparison */
    '.fc-cmp-stats{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center;padding:14px;background:rgba(255,255,255,.03);border-radius:12px;border:1px solid rgba(255,255,255,.08)}',
    '.fc-cmp-stat-col{display:flex;flex-direction:column;gap:4px;min-width:0}',
    '.fc-cmp-stat-col.col-a{text-align:left}',
    '.fc-cmp-stat-col.col-b{text-align:right}',
    '.fc-cmp-stat-name{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.5);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '.fc-cmp-stat-name.is-a{color:rgba(240,198,110,.85)}',
    '.fc-cmp-stat-name.is-b{color:rgba(200,210,235,.85)}',
    '.fc-cmp-stat-score{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:38px;line-height:.95;font-weight:700;letter-spacing:-.02em}',
    '.fc-cmp-stat-score.is-a{color:#f0c66e}',
    '.fc-cmp-stat-score.is-b{color:#c8d2eb}',
    '.fc-cmp-stat-tier{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.55)}',
    '.fc-cmp-stat-vs{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:18px;color:rgba(255,255,255,.4);font-weight:700;padding:0 4px}',
    /* Actions */
    '.fc-cmp-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:6px}',
    '.fc-cmp-btn{padding:12px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.06);color:#fff;font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:all .2s ease;display:flex;align-items:center;justify-content:center;gap:6px}',
    '.fc-cmp-btn:hover{background:rgba(240,198,110,.15);border-color:rgba(240,198,110,.4);color:#f0c66e}',
    '.fc-cmp-btn.is-primary{background:#f0c66e;color:#0a0a0e;border-color:#f0c66e}',
    '.fc-cmp-btn.is-primary:hover{background:#f5d088;color:#0a0a0e}',
    '.fc-cmp-btn svg{width:14px;height:14px}'
  ].join('');
  var sEl = document.createElement('style');
  sEl.id = 'fc-cmp-styles';
  sEl.appendChild(document.createTextNode(css));
  document.head.appendChild(sEl);

  /* ─── IDENTICAL hashing to FCBase31/32 ─── */
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

  /* ─── Dual polygon SVG builder ─── */
  function _polyPts(scores, R, cx, cy){
    var pts = [];
    for (var i=0; i<8; i++){
      var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
      var r = (scores[i] / 10) * R;
      pts.push([cx + Math.cos(ang) * r, cy + Math.sin(ang) * r]);
    }
    return pts;
  }
  function _ptsToPath(pts){
    return 'M ' + pts.map(function(p){ return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' L ') + ' Z';
  }
  function _buildDualSvg(pA, pB){
    var sA = _facetScores(pA.name, pA.composite);
    var sB = _facetScores(pB.name, pB.composite);
    var W = 340, H = 340, cx = W/2, cy = H/2, R = 115;

    var ptsA = _polyPts(sA, R, cx, cy);
    var ptsB = _polyPts(sB, R, cx, cy);
    var pathA = _ptsToPath(ptsA);
    var pathB = _ptsToPath(ptsB);

    var grid = '';
    [0.25, 0.5, 0.75, 1.0].forEach(function(p){
      var gpts = [];
      for (var i=0; i<8; i++){
        var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
        gpts.push([cx + Math.cos(ang) * p * R, cy + Math.sin(ang) * p * R]);
      }
      grid += '<path class="pgrid" d="' + _ptsToPath(gpts) + '"/>';
    });

    var axes = '';
    for (var i=0; i<8; i++){
      var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
      var ex = cx + Math.cos(ang) * R;
      var ey = cy + Math.sin(ang) * R;
      axes += '<line class="paxis" x1="' + cx + '" y1="' + cy + '" x2="' + ex.toFixed(1) + '" y2="' + ey.toFixed(1) + '"/>';
    }

    var vertsA = ptsA.map(function(p){ return '<circle class="vertex-a" cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3"/>'; }).join('');
    var vertsB = ptsB.map(function(p){ return '<circle class="vertex-b" cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3"/>'; }).join('');

    var labels = '';
    for (var i=0; i<8; i++){
      var ang = -Math.PI/2 + (i * 2 * Math.PI / 8);
      var lx = cx + Math.cos(ang) * (R + 18);
      var ly = cy + Math.sin(ang) * (R + 18);
      var anchor = 'middle';
      if (Math.cos(ang) > 0.4) anchor = 'start';
      else if (Math.cos(ang) < -0.4) anchor = 'end';
      var dy = Math.sin(ang) > 0.4 ? '0.8em' : Math.sin(ang) < -0.4 ? '0em' : '0.32em';
      labels += '<text class="plabel" x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" text-anchor="' + anchor + '" dy="' + dy + '">' + SHORT_LABELS[i] + '</text>';
    }

    /* Draw B first (silver, dashed) so A (gold, solid) sits on top */
    return '<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg">' +
      grid + axes +
      '<path class="shape-b-fill" d="' + pathB + '"/>' +
      '<path class="shape-b-stroke" d="' + pathB + '"/>' +
      '<path class="shape-a-fill" d="' + pathA + '"/>' +
      '<path class="shape-a-stroke" d="' + pathA + '"/>' +
      vertsB + vertsA + labels +
    '</svg>';
  }

  /* ─── Harvest current player from page ─── */
  function _harvestCurrent(){
    var urlParams = new URLSearchParams(window.location.search);
    var name = urlParams.get('q') || '';
    var sport = urlParams.get('sport') || 'mens-basketball';
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
    var tier = '';
    var tierMatch = (document.body.innerText || '').match(/\\b(ICON|ELITE\\+?|STAR|PROSPECT|SCOUT)\\b/);
    if (tierMatch) tier = tierMatch[1];
    return { name: name, composite: score, tier: tier, sport: sport };
  }

  /* ─── Fetch comparison player from worker ─── */
  function _fetchPlayer(name, sport){
    return fetch(WORKER_URL + '/verdict/player', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name, sport: sport })
    }).then(function(r){
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function(json){
      /* Try multiple response shapes */
      var composite = json.composite || (json.fieldcheck_iq && json.fieldcheck_iq.score) || json.score || (json.verdict && json.verdict.composite) || '';
      var tier = json.tier || (json.fieldcheck_iq && json.fieldcheck_iq.tier) || (json.verdict && json.verdict.tier) || '';
      return {
        name: json.name || name,
        composite: composite ? String(composite) : '',
        tier: tier || '',
        sport: sport
      };
    });
  }

  /* ─── Build comparison result UI ─── */
  function _renderResult(pA, pB, resultEl){
    resultEl.innerHTML = '';
    var viz = document.createElement('div');
    viz.className = 'fc-cmp-viz';
    viz.id = 'fc-cmp-viz-capture';

    var stats = document.createElement('div');
    stats.className = 'fc-cmp-stats';
    stats.innerHTML =
      '<div class="fc-cmp-stat-col col-a">' +
        '<div class="fc-cmp-stat-name is-a">' + (pA.name || 'Player A') + '</div>' +
        '<div class="fc-cmp-stat-score is-a">' + (pA.composite || '\\u2014') + '</div>' +
        '<div class="fc-cmp-stat-tier">' + (pA.tier || 'UNVERIFIED') + '</div>' +
      '</div>' +
      '<div class="fc-cmp-stat-vs">VS</div>' +
      '<div class="fc-cmp-stat-col col-b">' +
        '<div class="fc-cmp-stat-name is-b">' + (pB.name || 'Player B') + '</div>' +
        '<div class="fc-cmp-stat-score is-b">' + (pB.composite || '\\u2014') + '</div>' +
        '<div class="fc-cmp-stat-tier">' + (pB.tier || 'UNVERIFIED') + '</div>' +
      '</div>';

    var svgWrap = document.createElement('div');
    svgWrap.innerHTML = _buildDualSvg(pA, pB);

    viz.appendChild(stats);
    viz.appendChild(svgWrap);
    resultEl.appendChild(viz);

    var actions = document.createElement('div');
    actions.className = 'fc-cmp-actions';
    actions.innerHTML =
      '<button class="fc-cmp-btn is-primary" data-act="cmp-download">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' +
        'Download</button>' +
      '<button class="fc-cmp-btn" data-act="cmp-share">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>' +
        'Share</button>';
    resultEl.appendChild(actions);

    actions.addEventListener('click', function(e){
      var btn = e.target.closest('.fc-cmp-btn');
      if (!btn) return;
      var act = btn.dataset.act;
      if (act === 'cmp-download') _captureCompare(viz, pA, pB, 'download');
      else if (act === 'cmp-share') _captureCompare(viz, pA, pB, 'share');
    });
  }

  /* ─── Capture comparison as PNG ─── */
  function _captureCompare(vizEl, pA, pB, mode){
    if (typeof html2canvas !== 'function') { alert('Renderer loading\\u2026 try again'); return; }
    html2canvas(vizEl, { backgroundColor:'#0a0a0e', scale:2, useCORS:true, logging:false }).then(function(canvas){
      var filename = 'fieldcheck-' +
        (pA.name || 'a').toLowerCase().replace(/[^a-z0-9]+/g,'-') + '-vs-' +
        (pB.name || 'b').toLowerCase().replace(/[^a-z0-9]+/g,'-') + '.png';
      if (mode === 'download') {
        var link = document.createElement('a');
        link.download = filename;
        link.href = canvas.toDataURL('image/png');
        link.click();
      } else {
        canvas.toBlob(function(blob){
          var file = new File([blob], filename, { type:'image/png' });
          if (navigator.canShare && navigator.canShare({ files:[file] })) {
            navigator.share({ files:[file], title:pA.name + ' vs ' + pB.name + ' \\u00b7 FieldCheck IQ', text:pA.name + ' vs ' + pB.name + ' \\u00b7 FieldCheck IQ' }).catch(function(){});
          } else if (navigator.share) {
            navigator.share({ title:pA.name + ' vs ' + pB.name, url:window.location.href }).catch(function(){});
          }
        }, 'image/png');
      }
    });
  }

  /* ─── Open compare modal ─── */
  function _openCompareModal(){
    var pA = _harvestCurrent();
    if (!pA.name || !pA.composite) { alert('Open a verdict page first'); return; }

    var overlay = document.createElement('div');
    overlay.className = 'fc-cmp-mod-overlay';
    var content = document.createElement('div');
    content.className = 'fc-cmp-mod-content';

    var chips = QUICK_PICKS
      .filter(function(p){ return p.name.toLowerCase() !== pA.name.toLowerCase(); })
      .map(function(p){
        return '<button class="fc-cmp-chip" data-name="' + p.name + '" data-sport="' + p.sport + '">' + p.name + '</button>';
      }).join('');

    content.innerHTML =
      '<button class="fc-cmp-mod-close" aria-label="Close">\\u2715</button>' +
      '<div class="fc-cmp-header">' +
        '<div class="fc-cmp-title">Compare ' + pA.name + ' with\\u2026</div>' +
        '<div class="fc-cmp-subtitle">// Pick a marquee or type any player</div>' +
      '</div>' +
      '<div class="fc-cmp-picker">' +
        '<input class="fc-cmp-input" type="text" placeholder="Player name\\u2026 (then press Enter)" />' +
        '<div class="fc-cmp-chips">' + chips + '</div>' +
      '</div>' +
      '<div class="fc-cmp-result" id="fc-cmp-result"></div>';
    overlay.appendChild(content);

    function close(){ if (overlay.parentNode) overlay.parentNode.removeChild(overlay); document.removeEventListener('keydown', escClose); }
    function escClose(e){ if (e.key === 'Escape') close(); }
    content.querySelector('.fc-cmp-mod-close').addEventListener('click', close);
    overlay.addEventListener('click', function(e){ if (e.target === overlay) close(); });
    document.addEventListener('keydown', escClose);

    var resultEl = content.querySelector('#fc-cmp-result');

    function pickPlayer(name, sport){
      resultEl.innerHTML = '<div class="fc-cmp-loading">loading verdict</div>';
      _fetchPlayer(name, sport).then(function(pB){
        if (!pB.composite) {
          /* Fallback: use placeholder composite so polygon shape still renders */
          pB.composite = '—';
        }
        _renderResult(pA, pB, resultEl);
      }).catch(function(err){
        /* Graceful degradation: render polygon shape only */
        console.warn('compare fetch failed', err);
        _renderResult(pA, { name: name, composite: '—', tier: 'UNVERIFIED', sport: sport }, resultEl);
      });
    }

    content.querySelectorAll('.fc-cmp-chip').forEach(function(chip){
      chip.addEventListener('click', function(){
        pickPlayer(chip.dataset.name, chip.dataset.sport);
      });
    });

    var input = content.querySelector('.fc-cmp-input');
    input.addEventListener('keydown', function(e){
      if (e.key === 'Enter') {
        var val = input.value.trim();
        if (val) pickPlayer(val, pA.sport || 'mens-basketball');
      }
    });

    document.body.appendChild(overlay);
    setTimeout(function(){ input.focus(); }, 50);
  }

  /* ─── Mount Compare FAB ─── */
  function _mountFab(){
    if (document.querySelector('.fc-cmp-fab')) return;
    if (!/fieldcheck-verdict\\.html/.test(window.location.pathname)) return;
    var data = _harvestCurrent();
    if (!data.name || data.name.length < 2) return;
    var fab = document.createElement('button');
    fab.className = 'fc-cmp-fab';
    fab.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M4 20L21 3"/><path d="M21 16v5h-5"/><path d="M15 15l6 6"/><path d="M4 4l5 5"/></svg>' +
      '<span>Compare</span>';
    fab.addEventListener('click', _openCompareModal);
    document.body.appendChild(fab);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', _mountFab);
  else _mountFab();
  var mo = new MutationObserver(function(){ _mountFab(); });
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

    if '_fcShareCardInit' not in content:
        print("WARN: FCBase30 share card module not detected (Compare FAB will still mount).")
    if '_fcPolyInit' not in content:
        print("WARN: FCBase31 polygon module not detected (hash logic self-contained, OK).")

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace('</body>', PEER_COMPARE_BLOCK, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Peer-Compare module injected  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh any verdict page:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Expected:")
    print("  - SECOND floating button 'Compare' stacked above the Share Card button (bottom-right)")
    print("  - Tap \\u2192 modal with input + 5 quick-pick chips (excluding current player)")
    print("  - Pick Boozer / Dybantsa / Stokes / Williams / Brandon")
    print("  - Loading state \\u2192 dual polygon (GOLD = current, SILVER dashed = comparison)")
    print("  - Side-by-side composite + tier readout with VS divider")
    print("  - Download (PNG) / Share (native sheet with PNG attached)")
    print()
    print("Worker auto-detect:")
    print("  - dev host \\u2192 https://fieldcheck-proxy-dev.sridhar-nallani.workers.dev")
    print("  - prod host \\u2192 https://fieldcheck-proxy.sridhar-nallani.workers.dev")
    print()
    print("Graceful degradation: if API fails or composite missing, polygon still renders")
    print("from name-hash (shape comparison still works, just '\\u2014' for composite).")
    print()
    print("Ship to prod:")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase33_PEER_COMPARE_LIVE")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
