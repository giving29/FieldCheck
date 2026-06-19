#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-evalgrid-polish" "$F"; then echo "Already polished. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.polish.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<'PY'
f="fieldcheck-verdict.html"; s=open(f).read()
block = """<style id="fc-evalgrid-polish">
/* ============ EVAL-GRID POLISH PASS · Apple lens ============ */
/* --- DRIFT: themed hierarchy + horizontal before/after --- */
.driftbox{color:var(--t2)}
.drift-h{font-family:"Anton",sans-serif;font-size:clamp(20px,3vw,28px);line-height:1.12;letter-spacing:-.01em;color:rgba(245,241,232,.96);margin:2px 0 6px}
.drift-sub{color:var(--t3);font-size:13px;line-height:1.55;max-width:640px;margin-bottom:18px}
.drift-trigger{display:flex!important;align-items:center;gap:14px;font-family:inherit!important;font-size:inherit!important;line-height:1.4!important;background:linear-gradient(135deg,rgba(212,162,76,.07),rgba(0,0,0,.18));border:1px solid var(--ge2);border-left:3px solid var(--gold);border-radius:12px;padding:13px 16px;margin-bottom:22px}
.drift-trigger-icon{font-size:22px;flex-shrink:0;filter:drop-shadow(0 0 6px rgba(212,162,76,.45))}
.drift-trigger-lbl{font-family:"JetBrains Mono",monospace;font-size:9px;font-weight:700;letter-spacing:.9px;text-transform:uppercase;color:var(--gold);margin-bottom:3px}
.drift-trigger-text{color:var(--t2);font-size:13px;line-height:1.45}
.drift-grid{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:nowrap;overflow-x:auto;padding:6px 2px 20px;-webkit-overflow-scrolling:touch}
.drift-side{flex:0 0 auto;width:200px;text-align:center;background:rgba(0,0,0,.22);border:1px solid var(--ge2);border-radius:14px;padding:14px 10px 16px}
.drift-side.after{border-color:rgba(107,170,90,.30)}
.drift-side-lbl{font-family:"JetBrains Mono",monospace;font-size:9px;font-weight:700;letter-spacing:.9px;text-transform:uppercase;color:var(--gold)}
.drift-side.after .drift-side-lbl{color:var(--moss)}
.drift-side-year{font-family:"Anton",sans-serif;font-size:20px;color:rgba(245,241,232,.95);line-height:1;margin:5px 0 3px}
.drift-side-ctx{color:var(--t3);font-size:10.5px;line-height:1.35;min-height:28px;margin-bottom:4px}
.drift-side-comp{font-family:"JetBrains Mono",monospace;font-size:18px;font-weight:700;color:rgba(245,241,232,.95);margin-top:6px}
.drift-arrow{font-family:"Anton",sans-serif;font-size:26px;line-height:1;flex:0 0 auto;text-align:center;min-width:62px;color:var(--t2)}
.drift-delta-pos{color:var(--moss)}.drift-delta-neg{color:var(--red)}.drift-delta-zero{color:var(--t4)}
.drift-changes-h{font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--t4);margin:6px 0 10px}
.drift-changes{display:flex;flex-direction:column;gap:8px;margin-bottom:18px}
.drift-change-row{display:flex;align-items:center;gap:12px;padding:10px 14px;background:rgba(0,0,0,.22);border:1px solid var(--ge2);border-radius:10px}
.drift-change-dim{flex:0 0 118px;color:rgba(245,241,232,.92);font-size:13px;font-weight:600}
.drift-change-before{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--t4);min-width:32px;text-align:right}
.drift-change-bar{flex:1;height:6px;background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden;min-width:50px}
.drift-change-fill{height:100%;background:linear-gradient(90deg,var(--gold),rgba(212,162,76,.5));border-radius:3px}
.drift-change-after{font-family:"JetBrains Mono",monospace;font-size:13px;font-weight:700;color:rgba(245,241,232,.95);min-width:32px}
.drift-narrative{background:rgba(0,0,0,.18);border:1px solid var(--ge2);border-left:3px solid var(--gold);border-radius:12px;padding:14px 16px;margin-bottom:14px}
.drift-narrative-lbl{font-family:"JetBrains Mono",monospace;font-size:9px;font-weight:700;letter-spacing:.9px;text-transform:uppercase;color:var(--gold);margin-bottom:6px}
.drift-narrative-text{color:var(--t2);font-size:14px;line-height:1.65;font-family:"Cormorant Garamond",serif;font-style:italic}
.drift-sig{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;justify-content:space-between;padding-top:12px;border-top:1px solid var(--ge2)}
.drift-sig-text{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--t4);letter-spacing:.3px}
.drift-sig-text strong{color:var(--t2)}
.drift-sig-hash{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--gold);opacity:.7;letter-spacing:.3px}
/* --- TRAJECTORY: hardcoded #fff/255s -> palette --- */
.fc-traj-label-tier-name{color:rgba(245,241,232,.92)}
.fc-traj-sub,.fc-traj-label-from,.fc-traj-gap-label,.fc-traj-opps-title,.fc-traj-opp-arrow,.fc-traj-top-banner-text,.fc-traj-strip,.fc-traj-chip-tier{color:var(--t3)}
.fc-traj-opp-facet,.fc-traj-chip{color:var(--t2)}
</style>
</head>"""
assert s.count("</head>")>=1, "no </head>"
s=s.replace("</head>", block, 1)
open(f,"w").write(s); print("inserted fc-evalgrid-polish block")
PY
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
