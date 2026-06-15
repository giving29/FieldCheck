#!/usr/bin/env python3
"""
apply_share_verdict_card_v1.py

FCBase30 · Phase 5 Strike 1 · Shareable Verdict Card.

Adds a floating "Share Card" button on every verdict page that opens a
fullscreen modal containing a 9:16 (Instagram Story aspect) card preview
with the player's FieldCheck verdict — name, school/position, composite
score, tier, top awards, and FieldCheck-verified branding.

Three actions in the modal:
  - DOWNLOAD: html2canvas converts the card to PNG and triggers download
  - SHARE:    Web Share API (mobile native share sheet) with fallback
  - COPY:     Copies the verdict page URL

Reads player data from the DOM after verdict renders (player name, composite,
tier, school text, awards) so it stays in sync with whatever the page shows.

Single str_replace: injects the entire card module before </body>.

Run from fieldcheck-proxy directory:
  python3 apply_share_verdict_card_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-share-card.bak')

SHARE_CARD_BLOCK = """<!-- FCBase30 · Phase 5 Strike 1 · Shareable Verdict Card (2026-06-07) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
(function(){
  if (window._fcShareCardInit) return;
  window._fcShareCardInit = true;

  /* ─── CSS ─── */
  var css = [
    /* Floating share button */
    '.fc-share-fab{position:fixed;bottom:24px;right:24px;z-index:9998;background:linear-gradient(135deg,#f0c66e,#d4a64a);color:#0a0a0e;border:0;width:auto;padding:14px 22px;border-radius:999px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:14px;font-weight:600;letter-spacing:.02em;cursor:pointer;box-shadow:0 12px 32px -8px rgba(240,198,110,.45),0 4px 12px -2px rgba(0,0,0,.4);transition:transform .2s ease,box-shadow .2s ease;display:flex;align-items:center;gap:8px}',
    '.fc-share-fab:hover{transform:translateY(-2px);box-shadow:0 18px 40px -10px rgba(240,198,110,.55),0 6px 16px -4px rgba(0,0,0,.5)}',
    '.fc-share-fab svg{width:18px;height:18px;display:block}',
    '@media(max-width:480px){.fc-share-fab{bottom:18px;right:18px;padding:12px 18px;font-size:13px}}',
    /* Modal overlay */
    '.fc-share-mod-overlay{position:fixed;inset:0;background:rgba(8,8,12,.94);z-index:99999;display:flex;align-items:center;justify-content:center;padding:24px;animation:fcShareModFade .25s ease;overflow-y:auto}',
    '@keyframes fcShareModFade{from{opacity:0}to{opacity:1}}',
    '.fc-share-mod-content{position:relative;max-width:min(420px,95vw);display:flex;flex-direction:column;gap:18px;margin:auto}',
    '.fc-share-mod-close{position:absolute;top:-44px;right:0;background:rgba(255,255,255,.95);color:#111;border:0;width:36px;height:36px;border-radius:50%;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;font-family:system-ui;transition:transform .2s ease}',
    '.fc-share-mod-close:hover{transform:scale(1.08);background:#f0c66e}',
    /* The card itself */
    '.fc-share-card{aspect-ratio:9/16;width:100%;background:radial-gradient(ellipse at top right,#1a1a22 0%,#0a0a0e 60%,#000 100%);border-radius:24px;overflow:hidden;border:1px solid #2a2a32;box-shadow:0 30px 80px -20px rgba(0,0,0,.9);position:relative;padding:34px 28px;display:flex;flex-direction:column;color:#fff;font-family:ui-sans-serif,system-ui,sans-serif}',
    '.fc-share-card::before{content:"";position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#f0c66e 0%,#d4a64a 50%,#f0c66e 100%)}',
    '.fc-share-card::after{content:"";position:absolute;bottom:-40%;left:-20%;width:140%;height:80%;background:radial-gradient(ellipse,rgba(240,198,110,.08) 0%,transparent 60%);pointer-events:none}',
    '.fc-share-brand{display:flex;align-items:center;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:rgba(240,198,110,.85);position:relative;z-index:2}',
    '.fc-share-brand-name{font-weight:600}',
    '.fc-share-brand-verified{color:rgba(255,255,255,.55);font-size:9px}',
    '.fc-share-sport{margin-top:32px;font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.55);position:relative;z-index:2}',
    '.fc-share-name{margin-top:6px;font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:54px;line-height:.95;font-weight:700;letter-spacing:-.01em;color:#fff;position:relative;z-index:2}',
    '.fc-share-meta{margin-top:14px;font-size:12.5px;line-height:1.45;color:rgba(255,255,255,.7);position:relative;z-index:2}',
    '.fc-share-score-wrap{margin-top:auto;margin-bottom:24px;display:flex;align-items:flex-end;justify-content:space-between;gap:14px;position:relative;z-index:2}',
    '.fc-share-score{font-family:"Big Shoulders Display","Bebas Neue",system-ui,sans-serif;font-size:110px;line-height:.9;font-weight:700;color:#f0c66e;letter-spacing:-.02em}',
    '.fc-share-tier-box{display:flex;flex-direction:column;align-items:flex-end;gap:6px;padding-bottom:10px}',
    '.fc-share-tier{background:rgba(240,198,110,.15);color:#f0c66e;border:1px solid rgba(240,198,110,.35);padding:5px 10px;border-radius:6px;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase}',
    '.fc-share-tier-label{font-family:ui-monospace,Menlo,monospace;font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:rgba(255,255,255,.4)}',
    '.fc-share-awards{position:relative;z-index:2;display:flex;flex-direction:column;gap:6px;padding-top:14px;border-top:1px solid rgba(255,255,255,.08);margin-bottom:18px}',
    '.fc-share-award{font-family:ui-monospace,Menlo,monospace;font-size:10px;line-height:1.4;color:rgba(255,255,255,.8);letter-spacing:.02em}',
    '.fc-share-award::before{content:"·\\\\00a0\\\\00a0";color:rgba(240,198,110,.6)}',
    '.fc-share-footer{position:relative;z-index:2;display:flex;align-items:center;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.4)}',
    '.fc-share-footer-url{color:rgba(240,198,110,.7)}',
    /* Action buttons */
    '.fc-share-actions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:4px}',
    '.fc-share-btn{padding:13px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.06);color:#fff;font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:all .2s ease;display:flex;align-items:center;justify-content:center;gap:6px}',
    '.fc-share-btn:hover{background:rgba(240,198,110,.15);border-color:rgba(240,198,110,.4);color:#f0c66e}',
    '.fc-share-btn.is-primary{background:#f0c66e;color:#0a0a0e;border-color:#f0c66e}',
    '.fc-share-btn.is-primary:hover{background:#f5d088;color:#0a0a0e}',
    '.fc-share-btn svg{width:15px;height:15px}',
    '.fc-share-toast{position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:rgba(240,198,110,.95);color:#0a0a0e;padding:10px 18px;border-radius:999px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;font-weight:500;z-index:100000;opacity:0;transition:opacity .3s ease;pointer-events:none}',
    '.fc-share-toast.is-visible{opacity:1}'
  ].join('');
  var sEl = document.createElement('style');
  sEl.id = 'fc-share-card-styles';
  sEl.appendChild(document.createTextNode(css));
  document.head.appendChild(sEl);

  /* ─── Data harvest from the rendered verdict DOM ─── */
  function _harvest(){
    var urlParams = new URLSearchParams(window.location.search);
    var name = urlParams.get('q') || '';
    var sport = urlParams.get('sport') || '';
    // Try to pull from rendered DOM if possible
    var nameEl = document.querySelector('[class*="player-name"], [class*="verdict-name"], h1');
    if (nameEl && nameEl.textContent && nameEl.textContent.trim().length > 1) {
      var t = nameEl.textContent.trim();
      if (t.length < 60) name = t;
    }
    // Composite score - look for a big-font number near the top
    var score = '';
    var scoreCandidates = document.querySelectorAll('*');
    for (var i=0; i<scoreCandidates.length && i<1500; i++){
      var el = scoreCandidates[i];
      var txt = (el.textContent || '').trim();
      if (/^[0-9]\\.[0-9]$/.test(txt) && el.children.length === 0) {
        score = txt; break;
      }
    }
    // Tier - look for SCOUT/PROSPECT/STAR/ELITE/ICON badges
    var tier = '';
    var tierMatch = (document.body.innerText || '').match(/\\b(ICON|ELITE\\+?|STAR|PROSPECT|SCOUT)\\b/);
    if (tierMatch) tier = tierMatch[1];
    // School/position line - usually right under the name
    var school = '';
    var bodyText = document.body.innerText || '';
    var schoolLineMatch = bodyText.match(/([A-Z][^\\n]+(?:Catholic|Prep|HS|High School|Academy)[^\\n]+(?:· |\\u00b7 )[A-Z][^\\n]+)/);
    if (schoolLineMatch) school = schoolLineMatch[1];
    // Awards - look for award lines (year + award name pattern)
    var awards = [];
    var awardMatches = bodyText.match(/(20\\d\\d)[^\\n]{0,80}?(Naismith|McDonald|Gatorade|All-American|MVP|Player of the Year)[^\\n]{0,40}/g);
    if (awardMatches) awards = awardMatches.slice(0, 3);
    return { name: name, sport: sport, score: score, tier: tier, school: school, awards: awards };
  }

  /* ─── Build the card DOM ─── */
  function _buildCard(data){
    var sportLabel = (data.sport || '').replace(/-/g,' ').toUpperCase();
    var cardHTML =
      '<div class="fc-share-brand">' +
        '<span class="fc-share-brand-name">FieldCheck IQ</span>' +
        '<span class="fc-share-brand-verified">// VERIFIED 2026</span>' +
      '</div>' +
      '<div class="fc-share-sport">' + (sportLabel || 'Athlete') + '</div>' +
      '<div class="fc-share-name">' + (data.name || 'Athlete') + '</div>' +
      (data.school ? '<div class="fc-share-meta">' + data.school + '</div>' : '') +
      '<div class="fc-share-score-wrap">' +
        '<div class="fc-share-score">' + (data.score || '—') + '</div>' +
        '<div class="fc-share-tier-box">' +
          '<div class="fc-share-tier-label">// Tier</div>' +
          '<div class="fc-share-tier">' + (data.tier || 'UNVERIFIED') + '</div>' +
        '</div>' +
      '</div>' +
      (data.awards && data.awards.length ?
        '<div class="fc-share-awards">' +
          data.awards.map(function(a){ return '<div class="fc-share-award">' + a + '</div>'; }).join('') +
        '</div>' : '') +
      '<div class="fc-share-footer">' +
        '<span>// scout-class composite</span>' +
        '<span class="fc-share-footer-url">fieldcheck.ai</span>' +
      '</div>';
    return cardHTML;
  }

  /* ─── Toast ─── */
  function _toast(msg){
    var t = document.createElement('div');
    t.className = 'fc-share-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(function(){ t.classList.add('is-visible'); });
    setTimeout(function(){
      t.classList.remove('is-visible');
      setTimeout(function(){ if (t.parentNode) t.parentNode.removeChild(t); }, 400);
    }, 2200);
  }

  /* ─── Open modal ─── */
  function _openShareModal(){
    var data = _harvest();
    var overlay = document.createElement('div');
    overlay.className = 'fc-share-mod-overlay';
    var content = document.createElement('div');
    content.className = 'fc-share-mod-content';
    var closeBtn = document.createElement('button');
    closeBtn.className = 'fc-share-mod-close';
    closeBtn.innerHTML = '\\u2715';
    closeBtn.setAttribute('aria-label','Close');
    var card = document.createElement('div');
    card.className = 'fc-share-card';
    card.id = 'fc-share-card-render';
    card.innerHTML = _buildCard(data);
    var actions = document.createElement('div');
    actions.className = 'fc-share-actions';
    actions.innerHTML =
      '<button class="fc-share-btn is-primary" data-act="download">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' +
        'Download</button>' +
      '<button class="fc-share-btn" data-act="share">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>' +
        'Share</button>' +
      '<button class="fc-share-btn" data-act="copy">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>' +
        'Copy</button>';
    content.appendChild(closeBtn);
    content.appendChild(card);
    content.appendChild(actions);
    overlay.appendChild(content);

    function close(){ if (overlay.parentNode) overlay.parentNode.removeChild(overlay); document.removeEventListener('keydown', escClose); }
    function escClose(e){ if (e.key === 'Escape') close(); }
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', function(e){ if (e.target === overlay) close(); });
    document.addEventListener('keydown', escClose);

    actions.addEventListener('click', function(e){
      var btn = e.target.closest('.fc-share-btn');
      if (!btn) return;
      var act = btn.dataset.act;
      if (act === 'download') _doDownload(card, data);
      else if (act === 'share') _doShare(card, data);
      else if (act === 'copy') _doCopy(data);
    });

    document.body.appendChild(overlay);
  }

  /* ─── Download as PNG ─── */
  function _doDownload(cardEl, data){
    if (typeof html2canvas !== 'function') { _toast('Renderer loading\\u2026 try again'); return; }
    html2canvas(cardEl, { backgroundColor:null, scale:2, useCORS:true, logging:false }).then(function(canvas){
      var link = document.createElement('a');
      link.download = 'fieldcheck-' + (data.name || 'athlete').toLowerCase().replace(/[^a-z0-9]+/g,'-') + '.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      _toast('Card saved');
    }).catch(function(err){ console.error('share download err', err); _toast('Save failed'); });
  }

  /* ─── Share via Web Share API ─── */
  function _doShare(cardEl, data){
    var shareUrl = window.location.href;
    var shareText = (data.name || 'Athlete') + ' \\u00b7 FieldCheck IQ verdict';
    if (typeof html2canvas === 'function' && navigator.canShare) {
      html2canvas(cardEl, { backgroundColor:null, scale:2, useCORS:true, logging:false }).then(function(canvas){
        canvas.toBlob(function(blob){
          var file = new File([blob], 'fieldcheck-verdict.png', { type:'image/png' });
          if (navigator.canShare && navigator.canShare({ files:[file] })) {
            navigator.share({ files:[file], title:shareText, text:shareText, url:shareUrl })
              .catch(function(){ /* user cancelled */ });
          } else if (navigator.share) {
            navigator.share({ title:shareText, text:shareText, url:shareUrl }).catch(function(){});
          } else {
            _doCopy({});
          }
        }, 'image/png');
      });
    } else if (navigator.share) {
      navigator.share({ title:shareText, text:shareText, url:shareUrl }).catch(function(){});
    } else {
      _doCopy({});
    }
  }

  /* ─── Copy link ─── */
  function _doCopy(_data){
    var url = window.location.href;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function(){ _toast('Link copied'); });
    } else {
      var ta = document.createElement('textarea');
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); _toast('Link copied'); } catch(e) {}
      document.body.removeChild(ta);
    }
  }

  /* ─── Mount floating button after verdict renders ─── */
  function _mountFab(){
    if (document.querySelector('.fc-share-fab')) return;
    // Only mount on verdict pages (not home, not gems, etc.)
    if (!/fieldcheck-verdict\\.html/.test(window.location.pathname)) return;
    // Don't mount until we can see a player name (verdict has rendered)
    var data = _harvest();
    if (!data.name || data.name.length < 2) return;
    var fab = document.createElement('button');
    fab.className = 'fc-share-fab';
    fab.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>' +
      '<span>Share Card</span>';
    fab.addEventListener('click', _openShareModal);
    document.body.appendChild(fab);
  }

  /* Mount after DOMContentLoaded + on mutations (verdict renders async) */
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

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace('</body>', SHARE_CARD_BLOCK, 1)
    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Share Card module injected  ({delta:+d} bytes)")
    print()
    print("Deploy:")
    print("  ./fc-deploy-dev.sh")
    print()
    print("Hard refresh any verdict page:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print()
    print("Expected:")
    print("  - Gold 'Share Card' button fixed at bottom-right of viewport")
    print("  - Tap \\u2192 modal with 9:16 portrait card preview")
    print("  - Card shows: FieldCheck IQ logo + player name + school + composite + tier + top awards")
    print("  - Three buttons: Download (PNG via html2canvas), Share (native), Copy (link)")
    print()
    print("If clean across multiple players (JSJ, Boozer, Stokes):")
    print("  ./fc-promote-prod.sh")
    print("  ./fc-freeze.sh FCBase30_SHARE_CARD_LIVE")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
