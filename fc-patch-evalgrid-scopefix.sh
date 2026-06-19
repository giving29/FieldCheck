#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"; F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-evalgrid-scopefix" "$F"; then echo "Already scope-fixed. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.scopefix.$(date +%Y%m%d_%H%M)"; echo "backed up $F"
cat > /tmp/__sf.css <<'CSSEOF'
[data-vtab="evalgrid"]{color:var(--t2);background:linear-gradient(152deg,rgba(28,26,38,.45),rgba(15,14,19,.28));border:1px solid var(--ge2);border-radius:16px;padding:22px;margin-bottom:18px}
.calbox,.stressbox{color:var(--t2);background:linear-gradient(152deg,rgba(28,26,38,.45),rgba(15,14,19,.28));border:1px solid var(--ge2);border-radius:16px;padding:22px;margin-bottom:18px}

/* ============================================================
   EVAL-GRID RICH DESIGN LAYER · scoped to [data-vtab="evalgrid"] · additive
   Consistent surfaces, hierarchy, accents across every module.
   ============================================================ */
/* module surfaces */
[data-vtab="evalgrid"] .preconbox,[data-vtab="evalgrid"] .analogbox,[data-vtab="evalgrid"] .ledgerbox,
[data-vtab="evalgrid"] .pedigreebox,[data-vtab="evalgrid"] .voicesbox,[data-vtab="evalgrid"] .coachcultbox,
[data-vtab="evalgrid"] .gembox,[data-vtab="evalgrid"] .poolbox,[data-vtab="evalgrid"] .vcbox,[data-vtab="evalgrid"] .calbox,
[data-vtab="evalgrid"] .watchbox,[data-vtab="evalgrid"] .overlaybox,[data-vtab="evalgrid"] .stressbox,
[data-vtab="evalgrid"] .timelinebox,[data-vtab="evalgrid"] .driftbox{
  color:var(--t2);background:linear-gradient(152deg,rgba(28,26,38,.45),rgba(15,14,19,.28));
  border:1px solid var(--ge2);border-radius:16px;padding:22px;margin-bottom:18px}
/* eyebrows + all *-lbl */
[data-vtab="evalgrid"] .ey,[data-vtab="evalgrid"] [class$="-lbl"]{font-family:"JetBrains Mono",monospace;font-size:9.5px;
  font-weight:700;letter-spacing:.9px;text-transform:uppercase;color:var(--gold)}
/* primary headlines */
[data-vtab="evalgrid"] .precon-h,[data-vtab="evalgrid"] .an-h,[data-vtab="evalgrid"] .ledger-h,[data-vtab="evalgrid"] .ped-h,
[data-vtab="evalgrid"] .voices-h,[data-vtab="evalgrid"] .cc-h,[data-vtab="evalgrid"] .gem-h,[data-vtab="evalgrid"] .vf-h,
[data-vtab="evalgrid"] .pool-h,[data-vtab="evalgrid"] .vc-h,[data-vtab="evalgrid"] .cal-h,[data-vtab="evalgrid"] .watch-h,
[data-vtab="evalgrid"] .overlay-h,[data-vtab="evalgrid"] .stress-h,[data-vtab="evalgrid"] .vf-strip-h{
  font-family:"Big Shoulders Display","Anton",sans-serif;font-weight:700;
  font-size:clamp(18px,2.4vw,23px);line-height:1.15;letter-spacing:-.005em;
  color:rgba(245,241,232,.96);margin:2px 0 6px}
/* section sub-headers */
[data-vtab="evalgrid"] .ledger-section-h,[data-vtab="evalgrid"] .voice-section-h,[data-vtab="evalgrid"] .vc-section-h,
[data-vtab="evalgrid"] .cc-athletes-h,[data-vtab="evalgrid"] .pool-table-h,[data-vtab="evalgrid"] .stress-toggles-h,
[data-vtab="evalgrid"] .overlay-divergence-h{font-family:"JetBrains Mono",monospace;font-size:12px;
  font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--t3);margin:14px 0 8px}
/* subtitles */
[data-vtab="evalgrid"] [class$="-sub"]{color:var(--t3);font-size:13px;line-height:1.55;margin-bottom:16px;max-width:680px}
/* read / callout boxes */
[data-vtab="evalgrid"] .precon-read,[data-vtab="evalgrid"] .an-read,[data-vtab="evalgrid"] .overlay-read,
[data-vtab="evalgrid"] .ped-read,[data-vtab="evalgrid"] .cc-read,[data-vtab="evalgrid"] .vc-read,[data-vtab="evalgrid"] .vf-read{
  background:rgba(0,0,0,.18);border:1px solid var(--ge2);border-left:3px solid var(--gold);
  border-radius:12px;padding:14px 16px;margin-top:16px}
[data-vtab="evalgrid"] [class$="-read-lbl"]{color:var(--gold)}
[data-vtab="evalgrid"] [class$="-read-text"]{color:rgba(245,241,232,.9);font-family:"Cormorant Garamond",serif;
  font-style:italic;font-size:15.5px;line-height:1.65}
/* generic body / text */
[data-vtab="evalgrid"] [class$="-body"],[data-vtab="evalgrid"] [class$="-text"]{color:var(--t2);line-height:1.55}
/* numbers / scores -> mono gold (inline-colored deltas still win) */
[data-vtab="evalgrid"] [class$="-num"],[data-vtab="evalgrid"] [class$="-score"],[data-vtab="evalgrid"] [class$="-comp"],
[data-vtab="evalgrid"] [class$="-pct"],[data-vtab="evalgrid"] [class$="-rate"]{font-family:"JetBrains Mono",monospace;
  font-weight:700;color:var(--gold)}
/* tags / chips -> pills */
[data-vtab="evalgrid"] .precon-tag,[data-vtab="evalgrid"] .an-tag,[data-vtab="evalgrid"] .voice-tag,[data-vtab="evalgrid"] .gem-tag,
[data-vtab="evalgrid"] .vf-tag,[data-vtab="evalgrid"] .vf-primary-tag,[data-vtab="evalgrid"] .snap-voice-tag,
[data-vtab="evalgrid"] .cal-chip{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;
  margin:3px 5px 0 0;background:rgba(212,162,76,.08);border:1px solid var(--goldl);
  border-radius:999px;font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:600;
  letter-spacing:.4px;color:var(--gold)}
/* progress bars */
[data-vtab="evalgrid"] .cc-dim-bar,[data-vtab="evalgrid"] .vf-bar,[data-vtab="evalgrid"] .vc-sim-bar{height:6px;
  background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden}
[data-vtab="evalgrid"] .cc-dim-fill,[data-vtab="evalgrid"] .vf-bar-fill,[data-vtab="evalgrid"] .vc-sim-fill{height:100%;
  background:linear-gradient(90deg,var(--gold),rgba(212,162,76,.45));border-radius:3px}
/* sub-cards */
[data-vtab="evalgrid"] .voice-card,[data-vtab="evalgrid"] .cc-coach-card,[data-vtab="evalgrid"] .gem-card,
[data-vtab="evalgrid"] .vf-primary-card,[data-vtab="evalgrid"] .snapcard,[data-vtab="evalgrid"] .ledger-row,
[data-vtab="evalgrid"] .vc-row,[data-vtab="evalgrid"] .vf-row,[data-vtab="evalgrid"] .pool-row,
[data-vtab="evalgrid"] .cc-athlete-row,[data-vtab="evalgrid"] .watch-row,[data-vtab="evalgrid"] .precon-signal{
  background:rgba(0,0,0,.20);border:1px solid var(--ge2);border-radius:12px;
  padding:13px 15px;margin-bottom:10px}
/* names + meta */
[data-vtab="evalgrid"] .voice-name,[data-vtab="evalgrid"] .cc-coach-name,[data-vtab="evalgrid"] .gem-name,
[data-vtab="evalgrid"] .vf-primary-name,[data-vtab="evalgrid"] .vf-name,[data-vtab="evalgrid"] .snap-name,
[data-vtab="evalgrid"] .ped-name,[data-vtab="evalgrid"] .an-side-name,[data-vtab="evalgrid"] .pool-shape-name,
[data-vtab="evalgrid"] .cc-athlete-name{color:rgba(245,241,232,.95);font-weight:700}
[data-vtab="evalgrid"] .voice-role,[data-vtab="evalgrid"] .cc-coach-role,[data-vtab="evalgrid"] .voice-src,
[data-vtab="evalgrid"] .voice-date,[data-vtab="evalgrid"] .voice-meta,[data-vtab="evalgrid"] .gem-position,
[data-vtab="evalgrid"] .gem-program,[data-vtab="evalgrid"] .ledger-date,[data-vtab="evalgrid"] .ped-sport,
[data-vtab="evalgrid"] .vf-meta{color:var(--t3);font-size:11px}
/* quotes */
[data-vtab="evalgrid"] .voice-quote,[data-vtab="evalgrid"] .vc-voice-line{font-family:"Cormorant Garamond",serif;
  font-style:italic;font-size:16px;line-height:1.6;color:rgba(245,241,232,.9)}
/* avatars */
[data-vtab="evalgrid"] .voice-avatar,[data-vtab="evalgrid"] .cc-coach-avatar{border:2px solid var(--goldl);border-radius:50%}
/* layout: open up stacked groups */
[data-vtab="evalgrid"] .precon-cols{display:flex;gap:14px;flex-wrap:wrap}
[data-vtab="evalgrid"] .precon-col{flex:1;min-width:240px;background:rgba(0,0,0,.18);border:1px solid var(--ge2);
  border-radius:12px;padding:14px 16px}
[data-vtab="evalgrid"] .precon-gap{background:linear-gradient(135deg,rgba(212,162,76,.06),rgba(0,0,0,.18));
  border:1px solid var(--goldl);border-radius:12px;padding:14px 16px;margin-top:14px;text-align:center}
[data-vtab="evalgrid"] .precon-gap-num{font-size:30px;color:var(--gold);font-family:"Anton",sans-serif}
[data-vtab="evalgrid"] .an-shapes,[data-vtab="evalgrid"] .an-grid{display:flex;gap:16px;align-items:center;justify-content:center;flex-wrap:wrap}
[data-vtab="evalgrid"] .an-side{text-align:center}
[data-vtab="evalgrid"] .an-mid-sym{font-size:24px;color:var(--gold)}
[data-vtab="evalgrid"] .overlay-grid{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start;justify-content:center}
[data-vtab="evalgrid"] .gem-grid{display:flex;gap:14px;flex-wrap:wrap}
[data-vtab="evalgrid"] .gem-card{flex:1;min-width:230px}
[data-vtab="evalgrid"] .pool-shapes{display:flex;gap:12px;flex-wrap:wrap}
[data-vtab="evalgrid"] .cal-strip{display:flex;gap:10px;overflow-x:auto;padding-bottom:10px;-webkit-overflow-scrolling:touch}
[data-vtab="evalgrid"] .cal-chip{flex:0 0 auto;min-width:96px;flex-direction:column;text-align:center;padding:12px 10px}
[data-vtab="evalgrid"] .cc-dim-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
[data-vtab="evalgrid"] .cc-dim-cell{background:rgba(0,0,0,.18);border:1px solid var(--ge2);border-radius:10px;padding:11px 13px}
[data-vtab="evalgrid"] .vf-strip{display:flex;gap:10px;flex-wrap:wrap}
[data-vtab="evalgrid"] .pool-heatmap{overflow-x:auto}
/* ledger status pills */
[data-vtab="evalgrid"] .verified,[data-vtab="evalgrid"] .pending{display:inline-block;padding:2px 9px;border-radius:999px;
  font-family:"JetBrains Mono",monospace;font-size:9.5px;font-weight:700;letter-spacing:.5px}
[data-vtab="evalgrid"] .verified{background:rgba(107,170,90,.12);color:var(--moss);border:1px solid rgba(107,170,90,.3)}
[data-vtab="evalgrid"] .pending{background:rgba(212,162,76,.10);color:var(--gold);border:1px solid var(--goldl)}
/* any leftover hardcoded whites inside eval grid */
[data-vtab="evalgrid"] .fc-peers-chip,[data-vtab="evalgrid"] .fc-watchv2-banner,[data-vtab="evalgrid"] .fc-peers-strip{color:var(--t2)}


/* OUTCOME LEDGER -> signed verdict timeline (scoped, additive) */
[data-vtab="evalgrid"] .ledgerbox{color:var(--t2)}
[data-vtab="evalgrid"] .ledger-stats{display:flex;gap:12px;flex-wrap:wrap;margin:6px 0 36px}
[data-vtab="evalgrid"] .ledger-stat{flex:1;min-width:150px;position:relative;overflow:hidden;background:linear-gradient(155deg,rgba(28,26,38,.7),rgba(15,14,19,.4));border:1px solid var(--ge2);border-radius:16px;padding:18px}
[data-vtab="evalgrid"] .ledger-stat::after{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--moss)}
[data-vtab="evalgrid"] .ledger-stat.pending::after{background:var(--t4)}
[data-vtab="evalgrid"] .ledger-stat:not(.verified):not(.pending)::after{background:var(--gold)}
[data-vtab="evalgrid"] .ledger-stat-num{font-family:"Anton",sans-serif;font-size:42px;line-height:1;color:rgba(245,241,232,.96)}
[data-vtab="evalgrid"] .ledger-stat.verified .ledger-stat-num{color:var(--moss)}
[data-vtab="evalgrid"] .ledger-stat-lbl{font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--t3);margin-top:6px}
[data-vtab="evalgrid"] .ledger-section-h{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--t3);margin:8px 0 22px}
[data-vtab="evalgrid"] .ledger-section{position:relative;padding-left:40px;margin-bottom:10px}
[data-vtab="evalgrid"] .ledger-section::before{content:"";position:absolute;left:13px;top:34px;bottom:18px;width:2px;background:var(--moss)}
[data-vtab="evalgrid"] .ledger-section.pending::before{background:var(--gold);opacity:.55}
[data-vtab="evalgrid"] .ledger-row{position:relative;display:block;margin-bottom:20px;padding:0}
[data-vtab="evalgrid"] .ledger-icon{position:absolute;left:-33px;top:2px;width:16px;height:16px;border-radius:50%;background:var(--bg1,#0F0E13);border:2px solid var(--moss);box-shadow:0 0 0 4px var(--bg,#07060A);font-size:0;z-index:2}
[data-vtab="evalgrid"] .ledger-section.pending .ledger-icon{border-color:var(--gold);border-style:dashed;background:transparent}
[data-vtab="evalgrid"] .ledger-row.live .ledger-icon{border-color:var(--gold);box-shadow:0 0 0 4px var(--bg,#07060A),0 0 16px rgba(212,162,76,.6)}
[data-vtab="evalgrid"] .ledger-section.pending .ledger-row:last-child .ledger-icon{width:20px;height:20px;left:-35px;border-style:solid;background:radial-gradient(circle,rgba(212,162,76,.35),transparent 70%);box-shadow:0 0 0 4px var(--bg,#07060A),0 0 22px rgba(212,162,76,.7)}
[data-vtab="evalgrid"] .ledger-body{background:linear-gradient(155deg,rgba(28,26,38,.55),rgba(15,14,19,.32));border:1px solid var(--ge2);border-radius:14px;padding:14px 16px}
[data-vtab="evalgrid"] .ledger-row.live .ledger-body{border-color:var(--goldl);background:linear-gradient(155deg,rgba(212,162,76,.10),rgba(15,14,19,.4))}
[data-vtab="evalgrid"] .ledger-section.pending .ledger-row:last-child .ledger-body{border-color:rgba(212,162,76,.45);background:linear-gradient(155deg,rgba(212,162,76,.14),rgba(15,14,19,.45))}
[data-vtab="evalgrid"] .ledger-date{font-family:"JetBrains Mono",monospace;font-size:10.5px;font-weight:700;letter-spacing:.5px;color:var(--gold);margin-bottom:5px}
[data-vtab="evalgrid"] .ledger-event{font-family:"Big Shoulders Display",sans-serif;font-weight:700;font-size:17px;line-height:1.2;color:rgba(245,241,232,.96);margin-bottom:9px}
[data-vtab="evalgrid"] .ledger-call{display:block;padding-top:9px;border-top:1px solid var(--ge2);color:var(--t2);font-size:12.5px;line-height:1.55}
[data-vtab="evalgrid"] .ledger-call strong{display:inline-block;font-family:"JetBrains Mono",monospace;font-size:8.5px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--moss);background:rgba(107,170,90,.12);border:1px solid rgba(107,170,90,.3);border-radius:6px;padding:3px 7px;margin:0 8px 4px 0;vertical-align:middle}
[data-vtab="evalgrid"] .ledger-section.pending .ledger-call strong,[data-vtab="evalgrid"] .ledger-row.live .ledger-call strong{color:var(--gold);background:rgba(212,162,76,.10);border-color:var(--goldl)}

CSSEOF
python3 - <<'PYEOF'
f="fieldcheck-verdict.html"; s=open(f).read()
css=open("/tmp/__sf.css").read()
block='<style id="fc-evalgrid-scopefix">\n'+css+'\n</style>\n</head>'
assert s.count("</head>")>=1
s=s.replace("</head>",block,1)
open(f,"w").write(s); print("scope-fixed eval-grid CSS applied (now matches edge-served marquees)")
PYEOF
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
