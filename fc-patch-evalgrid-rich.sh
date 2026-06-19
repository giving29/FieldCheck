#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-evalgrid-rich" "$F"; then echo "Already enriched. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.rich.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<'PY'
f="fieldcheck-verdict.html"; s=open(f).read()
block = r"""<style id="fc-evalgrid-rich">
/* ============================================================
   EVAL-GRID RICH DESIGN LAYER · scoped to .eg-subpanel · additive
   Consistent surfaces, hierarchy, accents across every module.
   ============================================================ */
/* module surfaces */
.eg-subpanel .preconbox,.eg-subpanel .analogbox,.eg-subpanel .ledgerbox,
.eg-subpanel .pedigreebox,.eg-subpanel .voicesbox,.eg-subpanel .coachcultbox,
.eg-subpanel .gembox,.eg-subpanel .poolbox,.eg-subpanel .vcbox,.eg-subpanel .calbox,
.eg-subpanel .watchbox,.eg-subpanel .overlaybox,.eg-subpanel .stressbox,
.eg-subpanel .timelinebox,.eg-subpanel .driftbox{
  color:var(--t2);background:linear-gradient(152deg,rgba(28,26,38,.45),rgba(15,14,19,.28));
  border:1px solid var(--ge2);border-radius:16px;padding:22px;margin-bottom:18px}
/* eyebrows + all *-lbl */
.eg-subpanel .ey,.eg-subpanel [class$="-lbl"]{font-family:"JetBrains Mono",monospace;font-size:9.5px;
  font-weight:700;letter-spacing:.9px;text-transform:uppercase;color:var(--gold)}
/* primary headlines */
.eg-subpanel .precon-h,.eg-subpanel .an-h,.eg-subpanel .ledger-h,.eg-subpanel .ped-h,
.eg-subpanel .voices-h,.eg-subpanel .cc-h,.eg-subpanel .gem-h,.eg-subpanel .vf-h,
.eg-subpanel .pool-h,.eg-subpanel .vc-h,.eg-subpanel .cal-h,.eg-subpanel .watch-h,
.eg-subpanel .overlay-h,.eg-subpanel .stress-h,.eg-subpanel .vf-strip-h{
  font-family:"Big Shoulders Display","Anton",sans-serif;font-weight:700;
  font-size:clamp(18px,2.4vw,23px);line-height:1.15;letter-spacing:-.005em;
  color:rgba(245,241,232,.96);margin:2px 0 6px}
/* section sub-headers */
.eg-subpanel .ledger-section-h,.eg-subpanel .voice-section-h,.eg-subpanel .vc-section-h,
.eg-subpanel .cc-athletes-h,.eg-subpanel .pool-table-h,.eg-subpanel .stress-toggles-h,
.eg-subpanel .overlay-divergence-h{font-family:"JetBrains Mono",monospace;font-size:12px;
  font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--t3);margin:14px 0 8px}
/* subtitles */
.eg-subpanel [class$="-sub"]{color:var(--t3);font-size:13px;line-height:1.55;margin-bottom:16px;max-width:680px}
/* read / callout boxes */
.eg-subpanel .precon-read,.eg-subpanel .an-read,.eg-subpanel .overlay-read,
.eg-subpanel .ped-read,.eg-subpanel .cc-read,.eg-subpanel .vc-read,.eg-subpanel .vf-read{
  background:rgba(0,0,0,.18);border:1px solid var(--ge2);border-left:3px solid var(--gold);
  border-radius:12px;padding:14px 16px;margin-top:16px}
.eg-subpanel [class$="-read-lbl"]{color:var(--gold)}
.eg-subpanel [class$="-read-text"]{color:rgba(245,241,232,.9);font-family:"Cormorant Garamond",serif;
  font-style:italic;font-size:15.5px;line-height:1.65}
/* generic body / text */
.eg-subpanel [class$="-body"],.eg-subpanel [class$="-text"]{color:var(--t2);line-height:1.55}
/* numbers / scores -> mono gold (inline-colored deltas still win) */
.eg-subpanel [class$="-num"],.eg-subpanel [class$="-score"],.eg-subpanel [class$="-comp"],
.eg-subpanel [class$="-pct"],.eg-subpanel [class$="-rate"]{font-family:"JetBrains Mono",monospace;
  font-weight:700;color:var(--gold)}
/* tags / chips -> pills */
.eg-subpanel .precon-tag,.eg-subpanel .an-tag,.eg-subpanel .voice-tag,.eg-subpanel .gem-tag,
.eg-subpanel .vf-tag,.eg-subpanel .vf-primary-tag,.eg-subpanel .snap-voice-tag,
.eg-subpanel .cal-chip{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;
  margin:3px 5px 0 0;background:rgba(212,162,76,.08);border:1px solid var(--goldl);
  border-radius:999px;font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:600;
  letter-spacing:.4px;color:var(--gold)}
/* progress bars */
.eg-subpanel .cc-dim-bar,.eg-subpanel .vf-bar,.eg-subpanel .vc-sim-bar{height:6px;
  background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden}
.eg-subpanel .cc-dim-fill,.eg-subpanel .vf-bar-fill,.eg-subpanel .vc-sim-fill{height:100%;
  background:linear-gradient(90deg,var(--gold),rgba(212,162,76,.45));border-radius:3px}
/* sub-cards */
.eg-subpanel .voice-card,.eg-subpanel .cc-coach-card,.eg-subpanel .gem-card,
.eg-subpanel .vf-primary-card,.eg-subpanel .snapcard,.eg-subpanel .ledger-row,
.eg-subpanel .vc-row,.eg-subpanel .vf-row,.eg-subpanel .pool-row,
.eg-subpanel .cc-athlete-row,.eg-subpanel .watch-row,.eg-subpanel .precon-signal{
  background:rgba(0,0,0,.20);border:1px solid var(--ge2);border-radius:12px;
  padding:13px 15px;margin-bottom:10px}
/* names + meta */
.eg-subpanel .voice-name,.eg-subpanel .cc-coach-name,.eg-subpanel .gem-name,
.eg-subpanel .vf-primary-name,.eg-subpanel .vf-name,.eg-subpanel .snap-name,
.eg-subpanel .ped-name,.eg-subpanel .an-side-name,.eg-subpanel .pool-shape-name,
.eg-subpanel .cc-athlete-name{color:rgba(245,241,232,.95);font-weight:700}
.eg-subpanel .voice-role,.eg-subpanel .cc-coach-role,.eg-subpanel .voice-src,
.eg-subpanel .voice-date,.eg-subpanel .voice-meta,.eg-subpanel .gem-position,
.eg-subpanel .gem-program,.eg-subpanel .ledger-date,.eg-subpanel .ped-sport,
.eg-subpanel .vf-meta{color:var(--t3);font-size:11px}
/* quotes */
.eg-subpanel .voice-quote,.eg-subpanel .vc-voice-line{font-family:"Cormorant Garamond",serif;
  font-style:italic;font-size:16px;line-height:1.6;color:rgba(245,241,232,.9)}
/* avatars */
.eg-subpanel .voice-avatar,.eg-subpanel .cc-coach-avatar{border:2px solid var(--goldl);border-radius:50%}
/* layout: open up stacked groups */
.eg-subpanel .precon-cols{display:flex;gap:14px;flex-wrap:wrap}
.eg-subpanel .precon-col{flex:1;min-width:240px;background:rgba(0,0,0,.18);border:1px solid var(--ge2);
  border-radius:12px;padding:14px 16px}
.eg-subpanel .precon-gap{background:linear-gradient(135deg,rgba(212,162,76,.06),rgba(0,0,0,.18));
  border:1px solid var(--goldl);border-radius:12px;padding:14px 16px;margin-top:14px;text-align:center}
.eg-subpanel .precon-gap-num{font-size:30px;color:var(--gold);font-family:"Anton",sans-serif}
.eg-subpanel .an-shapes,.eg-subpanel .an-grid{display:flex;gap:16px;align-items:center;justify-content:center;flex-wrap:wrap}
.eg-subpanel .an-side{text-align:center}
.eg-subpanel .an-mid-sym{font-size:24px;color:var(--gold)}
.eg-subpanel .overlay-grid{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start;justify-content:center}
.eg-subpanel .gem-grid{display:flex;gap:14px;flex-wrap:wrap}
.eg-subpanel .gem-card{flex:1;min-width:230px}
.eg-subpanel .pool-shapes{display:flex;gap:12px;flex-wrap:wrap}
.eg-subpanel .cal-strip{display:flex;gap:10px;overflow-x:auto;padding-bottom:10px;-webkit-overflow-scrolling:touch}
.eg-subpanel .cal-chip{flex:0 0 auto;min-width:96px;flex-direction:column;text-align:center;padding:12px 10px}
.eg-subpanel .cc-dim-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.eg-subpanel .cc-dim-cell{background:rgba(0,0,0,.18);border:1px solid var(--ge2);border-radius:10px;padding:11px 13px}
.eg-subpanel .vf-strip{display:flex;gap:10px;flex-wrap:wrap}
.eg-subpanel .pool-heatmap{overflow-x:auto}
/* ledger status pills */
.eg-subpanel .verified,.eg-subpanel .pending{display:inline-block;padding:2px 9px;border-radius:999px;
  font-family:"JetBrains Mono",monospace;font-size:9.5px;font-weight:700;letter-spacing:.5px}
.eg-subpanel .verified{background:rgba(107,170,90,.12);color:var(--moss);border:1px solid rgba(107,170,90,.3)}
.eg-subpanel .pending{background:rgba(212,162,76,.10);color:var(--gold);border:1px solid var(--goldl)}
/* any leftover hardcoded whites inside eval grid */
.eg-subpanel .fc-peers-chip,.eg-subpanel .fc-watchv2-banner,.eg-subpanel .fc-peers-strip{color:var(--t2)}
</style>
</head>"""
assert s.count("</head>")>=1, "no </head>"
s=s.replace("</head>", block, 1)
open(f,"w").write(s); print("inserted fc-evalgrid-rich design layer (%d chars)"%len(block))
PY
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
