#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"; F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-modules-batch2" "$F"; then echo "Already applied. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.batch2.$(date +%Y%m%d_%H%M)"; echo "backed up $F"
cat > /tmp/__b2.css <<'CSSE'
/* ===== BATCH 2 · Position Pool (heatmap) / Voice Cluster ===== */
/* --- Position Pool: shape strip + real heatmap grid --- */
[data-vtab="evalgrid"] .pool-h{font-family:"Big Shoulders Display",sans-serif;font-weight:700;font-size:clamp(17px,2.3vw,22px);color:rgba(245,241,232,.96);margin-bottom:14px}
[data-vtab="evalgrid"] .pool-shapes{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:22px}
[data-vtab="evalgrid"] .pool-shape{flex:1;min-width:120px;background:rgba(0,0,0,.2);border:1px solid var(--ge2);border-radius:12px;padding:12px 10px;text-align:center;margin:0}
[data-vtab="evalgrid"] .pool-shape.self{border-color:var(--gold);background:rgba(212,162,76,.07)}
[data-vtab="evalgrid"] .pool-shape-rank{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--gold);font-weight:700}
[data-vtab="evalgrid"] .pool-shape-name{color:rgba(245,241,232,.95);font-weight:700;font-size:12.5px;margin-top:4px}
[data-vtab="evalgrid"] .pool-shape-prog{color:var(--t3);font-size:10px;margin-top:2px;line-height:1.3}
[data-vtab="evalgrid"] .pool-shape-tag{display:inline-block;margin-top:6px;font-family:"JetBrains Mono",monospace;font-size:8px;color:var(--gold);border:1px solid var(--goldl);border-radius:5px;padding:2px 6px}
[data-vtab="evalgrid"] .pool-table-h{font-family:"JetBrains Mono",monospace;font-size:10.5px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--t3);margin:6px 0 10px}
[data-vtab="evalgrid"] .pool-heatmap{overflow-x:auto;border:1px solid var(--ge2);border-radius:12px;-webkit-overflow-scrolling:touch}
[data-vtab="evalgrid"] .pool-row{display:grid;grid-template-columns:190px repeat(11,minmax(32px,1fr));align-items:stretch;background:transparent !important;border:0 !important;border-radius:0 !important;padding:0 !important;margin:0 !important;min-width:540px}
[data-vtab="evalgrid"] .pool-row.head .pool-cell{position:sticky;top:0;background:rgba(0,0,0,.4);color:var(--t3);font-size:8px;text-transform:uppercase;letter-spacing:.2px}
[data-vtab="evalgrid"] .pool-row.self{outline:1.5px solid var(--gold);outline-offset:-1.5px;border-radius:6px;z-index:1}
[data-vtab="evalgrid"] .pool-row-label{display:flex;align-items:center;gap:6px;padding:7px 8px;font-size:11.5px;font-weight:600;color:rgba(245,241,232,.9);border-bottom:1px solid rgba(0,0,0,.3)}
[data-vtab="evalgrid"] .pool-cell{font-family:"JetBrains Mono",monospace;font-size:10.5px;text-align:center;display:flex;align-items:center;justify-content:center;padding:7px 2px;border-bottom:1px solid rgba(0,0,0,.25);border-right:1px solid rgba(0,0,0,.2)}
/* --- Voice Cluster: ranked cosine-similarity rows --- */
[data-vtab="evalgrid"] .vc-h{font-family:"Big Shoulders Display",sans-serif;font-weight:700;font-size:clamp(17px,2.3vw,22px);color:rgba(245,241,232,.96);margin-bottom:14px}
[data-vtab="evalgrid"] .vc-section{margin-bottom:18px}
[data-vtab="evalgrid"] .vc-section-h{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--gold);margin-bottom:12px}
[data-vtab="evalgrid"] .vc-section.anti .vc-section-h{color:var(--t3)}
[data-vtab="evalgrid"] .vc-row{display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:rgba(0,0,0,.2) !important;border:1px solid var(--ge2) !important;border-radius:12px !important;padding:12px 14px !important;margin-bottom:9px !important}
[data-vtab="evalgrid"] .vc-row.anti{border-style:dashed !important;opacity:.75}
[data-vtab="evalgrid"] .vc-rank{font-family:"Anton",sans-serif;font-size:22px;color:var(--gold);flex:0 0 auto;min-width:26px;line-height:1}
[data-vtab="evalgrid"] .vc-row.anti .vc-rank{color:var(--t4)}
[data-vtab="evalgrid"] .vc-info{flex:1 1 200px;min-width:0}
[data-vtab="evalgrid"] .vc-name{color:rgba(245,241,232,.95);font-weight:700;font-size:14px}
[data-vtab="evalgrid"] .vc-voice-line{color:var(--t3);font-size:11.5px;margin-top:2px;font-family:inherit;font-style:normal}
[data-vtab="evalgrid"] .vc-voice-line strong{color:var(--t2);font-weight:600}
[data-vtab="evalgrid"] .vc-overlap{color:var(--t4);font-size:10.5px;margin-top:3px}
[data-vtab="evalgrid"] .vc-sim{display:flex;align-items:center;gap:9px;flex:1 1 200px;min-width:160px}
[data-vtab="evalgrid"] .vc-sim-bar{flex:1;height:7px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;min-width:50px}
[data-vtab="evalgrid"] .vc-sim-fill{height:100%;background:linear-gradient(90deg,var(--gold),rgba(212,162,76,.4));border-radius:4px}
[data-vtab="evalgrid"] .vc-row.anti .vc-sim-fill{background:var(--t4)}
[data-vtab="evalgrid"] .vc-sim-num{font-family:"JetBrains Mono",monospace;font-weight:700;color:var(--gold);font-size:13px}
[data-vtab="evalgrid"] .vc-sim-lbl{font-family:"JetBrains Mono",monospace;font-size:9px;color:var(--t4);text-transform:uppercase}
[data-vtab="evalgrid"] .vc-go{flex:0 0 auto;font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--gold);text-decoration:none;border:1px solid var(--goldl);border-radius:6px;padding:5px 9px}
CSSE
python3 - <<'PYEOF'
f="fieldcheck-verdict.html"; s=open(f).read()
css=open("/tmp/__b2.css").read()
block='<style id="fc-modules-batch2">\n'+css+'\n</style>\n</head>'
assert s.count("</head>")>=1
s=s.replace("</head>",block,1)
open(f,"w").write(s); print("batch2 modules styled: Position Pool heatmap, Voice Cluster")
PYEOF
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
