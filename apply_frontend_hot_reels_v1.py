#!/usr/bin/env python3
"""
apply_frontend_hot_reels_v1.py

FCBase27 · Integrates Hot Reels + Follow sections into fieldcheck-verdict.html.

CONDITIONAL RENDER — only fires when data has short_form/socials. The 104
non-curated athletes render IDENTICALLY to today. Zero disruption.

Two surgical insertions (anchored on existing markup):
  1. Before line 4212 (Highlights section header): inject Hot Reels block + CSS
  2. Before line 4267 (Public record fallback header): inject Follow chips block

Both anchored on the EXACT existing markup string — fails clean if anchors
have shifted.

Run from fieldcheck-proxy directory:
  python3 apply_frontend_hot_reels_v1.py
"""

import shutil
import sys
from pathlib import Path

HTML = Path('fieldcheck-verdict.html')
BACKUP = Path('fieldcheck-verdict.html.pre-hot-reels.bak')

# ─── ANCHOR 1: Hot Reels section + CSS injection (before Highlights header) ───

ANCHOR_HIGHLIGHTS = "    h+='<div class=\"sec\"><div class=\"ey\">// Highlights &amp; video</div>';"

# CSS uses unique fc-hr- prefix to avoid any class collision with existing page CSS.
# Injected once per render via window._fcHrCssInjected guard.
HOT_REELS_BLOCK = """    // FCBase27 · Hot Reels (short-form from CURATED_MEDIA.short_form)
    // Renders ONLY when data has short_form array. Non-curated athletes unchanged.
    var shortFormArr = data.short_form || (data.encyclopedia && data.encyclopedia.short_form) || [];
    if (Array.isArray(shortFormArr) && shortFormArr.length) {
      if (!window._fcHrCssInjected) {
        h += '<style id=\"fc-hr-styles\">'
          + '.fc-hr-row{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding:14px 0 4px;margin-bottom:6px;scrollbar-width:thin}'
          + '.fc-hr-row::-webkit-scrollbar{height:6px}'
          + '.fc-hr-row::-webkit-scrollbar-thumb{background:#2a2a32;border-radius:3px}'
          + '.fc-hr-card{flex:0 0 168px;aspect-ratio:9/16;border-radius:14px;overflow:hidden;position:relative;scroll-snap-align:start;cursor:pointer;transition:transform .25s ease,box-shadow .25s ease;border:1px solid #2a2a32;text-decoration:none;color:#fff;display:block}'
          + '.fc-hr-card:hover{transform:translateY(-4px);box-shadow:0 18px 40px -16px rgba(0,0,0,.7)}'
          + '.fc-hr-yt{background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,.85) 100%),linear-gradient(135deg,#2a1010 0%,#5a1a1a 100%)}'
          + '.fc-hr-ig{background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,.85) 100%),linear-gradient(135deg,#401040 0%,#6a2050 60%,#d04030 100%)}'
          + '.fc-hr-tt{background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,.85) 100%),linear-gradient(135deg,#0a2030 0%,#1a4060 100%)}'
          + '.fc-hr-plat{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);color:#fff;padding:3px 8px;border-radius:999px;font-family:ui-monospace,Menlo,monospace;font-size:9.5px;font-weight:500;letter-spacing:.1em;text-transform:uppercase}'
          + '.fc-hr-dur{position:absolute;top:10px;right:10px;background:rgba(0,0,0,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);color:#fff;padding:3px 7px;border-radius:999px;font-family:ui-monospace,Menlo,monospace;font-size:10px}'
          + '.fc-hr-play{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.95);color:#111;display:flex;align-items:center;justify-content:center;transition:transform .2s ease,background .2s ease}'
          + '.fc-hr-card:hover .fc-hr-play{transform:translate(-50%,-50%) scale(1.08);background:#f0c66e}'
          + '.fc-hr-play svg{width:18px;height:18px;margin-left:2px}'
          + '.fc-hr-meta{position:absolute;bottom:0;left:0;right:0;padding:12px 12px 14px;color:#fff}'
          + '.fc-hr-cap{font-size:12.5px;font-weight:500;line-height:1.32;margin:0 0 6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}'
          + '.fc-hr-creator{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:rgba(255,255,255,.7)}'
          + '.fc-hr-follow{background:linear-gradient(135deg,rgba(201,169,107,.05) 0%,rgba(201,169,107,.01) 100%);border:1px solid rgba(201,169,107,.15);border-radius:14px;padding:24px;margin-top:8px}'
          + '.fc-hr-follow-prompt{font-weight:700;font-size:22px;margin:0 0 4px;letter-spacing:-.005em}'
          + '.fc-hr-gold{color:#c9a96b}'
          + '.fc-hr-follow-sub{color:#9a9690;font-size:13px;margin-bottom:14px}'
          + '.fc-hr-chips{display:flex;gap:10px;flex-wrap:wrap}'
          + '.fc-hr-chip{display:inline-flex;align-items:center;gap:10px;padding:10px 16px 10px 12px;background:#15151a;border:1px solid #1f1f26;border-radius:999px;color:#ece9e1;text-decoration:none;font-weight:500;font-size:13.5px;transition:transform .15s ease,border-color .15s ease}'
          + '.fc-hr-chip:hover{transform:translateY(-1px);border-color:#c9a96b}'
          + '.fc-hr-logo{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0}'
          + '.fc-hr-logo svg{width:14px;height:14px}'
          + '.fc-hr-logo-ig{background:linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%)}'
          + '.fc-hr-logo-tt{background:#000;border:1px solid #2a2a32}'
          + '.fc-hr-logo-x{background:#000;border:1px solid #2a2a32}'
          + '.fc-hr-handle{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:#9a9690}'
          + '</style>';
        window._fcHrCssInjected = true;
      }
      h += '<div class=\"sec\"><div class=\"ey\">// Hot Reels \\u00b7 short-form</div>';
      h += '<div class=\"fc-hr-row\">';
      shortFormArr.forEach(function(s) {
        var plat = String(s.platform || 'youtube_shorts').toLowerCase();
        var platCls = plat.indexOf('insta') >= 0 ? 'ig' : (plat.indexOf('tiktok') >= 0 ? 'tt' : 'yt');
        var platLbl = plat.indexOf('insta') >= 0 ? 'IG Reel' : (plat.indexOf('tiktok') >= 0 ? 'TikTok' : 'YT Shorts');
        var dur = Number(s.duration_seconds) || 0;
        var durStr = dur > 0 ? (Math.floor(dur/60) + ':' + String(dur%60).padStart(2,'0')) : '';
        h += '<a class=\"fc-hr-card fc-hr-' + platCls + '\" href=\"' + esc(s.url || '#') + '\" target=\"_blank\" rel=\"noopener\">';
        h += '<div class=\"fc-hr-plat\">' + platLbl + '</div>';
        if (durStr) h += '<div class=\"fc-hr-dur\">' + esc(durStr) + '</div>';
        h += '<div class=\"fc-hr-play\"><svg viewBox=\"0 0 24 24\" fill=\"currentColor\"><path d=\"M8 5v14l11-7z\"/></svg></div>';
        h += '<div class=\"fc-hr-meta\"><p class=\"fc-hr-cap\">' + esc(s.title || '') + '</p>';
        if (s.creator) h += '<div class=\"fc-hr-creator\">' + esc(s.creator) + '</div>';
        h += '</div></a>';
      });
      h += '</div></div>';
    }
    h+='<div class=\"sec\"><div class=\"ey\">// Highlights &amp; video</div>';"""

# ─── ANCHOR 2: Follow section (before public record fallback) ─────────────────

ANCHOR_PUBREC = "  h+='<div class=\"sec\"><div class=\"ey\">// More \\u00b7 search the public record</div>';"

FOLLOW_BLOCK = """  // FCBase27 · Follow handles (from CURATED_MEDIA.socials)
  // Renders ONLY when data has socials object with at least one handle.
  var socialsObj = data.socials || (data.encyclopedia && data.encyclopedia.socials) || null;
  if (socialsObj && (socialsObj.instagram || socialsObj.tiktok || socialsObj.x)) {
    var firstName = ((name || '').split(' ')[0] || 'them');
    h += '<div class=\"sec\"><div class=\"fc-hr-follow\">';
    h += '<div class=\"fc-hr-follow-prompt\">Follow <span class=\"fc-hr-gold\">' + esc(firstName) + '</span> for what\\u2019s next</div>';
    h += '<div class=\"fc-hr-follow-sub\">Highlights drop in real time. Tap a handle to follow.</div>';
    h += '<div class=\"fc-hr-chips\">';
    if (socialsObj.instagram) {
      var igH = String(socialsObj.instagram).replace(/^@/, '');
      h += '<a class=\"fc-hr-chip\" href=\"https://instagram.com/' + esc(igH) + '\" target=\"_blank\" rel=\"noopener\">';
      h += '<span class=\"fc-hr-logo fc-hr-logo-ig\"><svg viewBox=\"0 0 24 24\" fill=\"white\"><path d=\"M12 2.2c3.2 0 3.6 0 4.8.07 1.2.05 1.8.25 2.2.42.6.22 1 .5 1.5 1s.78.9 1 1.5c.17.4.37 1 .42 2.2.06 1.2.07 1.6.07 4.8s0 3.6-.07 4.8c-.05 1.2-.25 1.8-.42 2.2-.22.6-.5 1-1 1.5s-.9.78-1.5 1c-.4.17-1 .37-2.2.42-1.2.06-1.6.07-4.8.07s-3.6 0-4.8-.07c-1.2-.05-1.8-.25-2.2-.42-.6-.22-1-.5-1.5-1s-.78-.9-1-1.5c-.17-.4-.37-1-.42-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.8c.05-1.2.25-1.8.42-2.2.22-.6.5-1 1-1.5s.9-.78 1.5-1c.4-.17 1-.37 2.2-.42C8.4 2.2 8.8 2.2 12 2.2zm0 3.06A5.06 5.06 0 1 1 12 17.12 5.06 5.06 0 0 1 12 7.06zm0 8.34a3.28 3.28 0 1 0 0-6.56 3.28 3.28 0 0 0 0 6.56zm6.43-8.55a1.18 1.18 0 1 1-2.37 0 1.18 1.18 0 0 1 2.37 0z\"/></svg></span>';
      h += '<span>Instagram</span><span class=\"fc-hr-handle\">@' + esc(igH) + '</span></a>';
    }
    if (socialsObj.tiktok) {
      var ttH = String(socialsObj.tiktok).replace(/^@/, '');
      h += '<a class=\"fc-hr-chip\" href=\"https://tiktok.com/@' + esc(ttH) + '\" target=\"_blank\" rel=\"noopener\">';
      h += '<span class=\"fc-hr-logo fc-hr-logo-tt\"><svg viewBox=\"0 0 24 24\" fill=\"white\"><path d=\"M19.6 7.7a6.2 6.2 0 0 1-4.4-2v8.5a5.7 5.7 0 1 1-5-5.6v2.8a2.9 2.9 0 1 0 2.2 2.8V2h2.8a4.2 4.2 0 0 0 4.4 4.2v2.5z\"/></svg></span>';
      h += '<span>TikTok</span><span class=\"fc-hr-handle\">@' + esc(ttH) + '</span></a>';
    }
    if (socialsObj.x) {
      var xH = String(socialsObj.x).replace(/^@/, '');
      h += '<a class=\"fc-hr-chip\" href=\"https://x.com/' + esc(xH) + '\" target=\"_blank\" rel=\"noopener\">';
      h += '<span class=\"fc-hr-logo fc-hr-logo-x\"><svg viewBox=\"0 0 24 24\" fill=\"white\"><path d=\"M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z\"/></svg></span>';
      h += '<span>X</span><span class=\"fc-hr-handle\">@' + esc(xH) + '</span></a>';
    }
    h += '</div></div></div>';
  }

  h+='<div class=\"sec\"><div class=\"ey\">// More \\u00b7 search the public record</div>';"""


def apply():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found in {Path.cwd()}")
        return 1

    content = HTML.read_text()
    original_size = len(content)

    if ANCHOR_HIGHLIGHTS not in content:
        print("ERROR: Highlights anchor not found.")
        print(f"  Looking for: {ANCHOR_HIGHLIGHTS[:80]}...")
        return 1
    if content.count(ANCHOR_HIGHLIGHTS) > 1:
        print(f"ERROR: Highlights anchor appears {content.count(ANCHOR_HIGHLIGHTS)} times. Ambiguous.")
        return 1

    if ANCHOR_PUBREC not in content:
        print("ERROR: Public record anchor not found.")
        print(f"  Looking for: {ANCHOR_PUBREC[:80]}...")
        return 1
    if content.count(ANCHOR_PUBREC) > 1:
        print(f"ERROR: Public record anchor appears {content.count(ANCHOR_PUBREC)} times.")
        return 1

    shutil.copy(HTML, BACKUP)
    print(f"OK   Backup: {BACKUP} ({original_size} B)")

    new_content = content.replace(ANCHOR_HIGHLIGHTS, HOT_REELS_BLOCK, 1)
    new_content = new_content.replace(ANCHOR_PUBREC, FOLLOW_BLOCK, 1)

    HTML.write_text(new_content)
    delta = len(new_content) - original_size
    print(f"OK   Inserted Hot Reels + Follow sections  ({delta:+d} bytes)")

    # Sanity checks
    new_markers = [
      ("FCBase27 . Hot Reels", "Hot Reels block"),
      ("FCBase27 . Follow handles", "Follow block"),
      ("fc-hr-row", "Hot Reels CSS"),
      ("fc-hr-follow", "Follow CSS"),
    ]
    for marker, label in new_markers:
        # marker uses '.' as wildcard for the middot
        import re
        if not re.search(marker, new_content):
            print(f"WARN: {label} marker missing — patch may not have fully applied")

    print()
    print("Next: ./fc-deploy-dev.sh")
    print("Then verify on dev:")
    print("  https://fieldcheck-dev--fieldcheck-app.netlify.app/fieldcheck-verdict.html?q=Jordan+Smith+Jr&sport=mens-basketball")
    print("  (sections will not appear yet — needs Patch 1+2 worker.js for short_form/socials data)")
    return 0


if __name__ == '__main__':
    sys.exit(apply())
