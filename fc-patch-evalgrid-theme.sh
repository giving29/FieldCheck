#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"
F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-evalgrid-retheme" "$F"; then echo "Already themed. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.theme.$(date +%Y%m%d_%H%M)"
echo "backed up $F"

python3 - <<'PY'
f="fieldcheck-verdict.html"; s=open(f).read()
block = """<style id="fc-evalgrid-retheme">
/* eval-grid computed modules: theme + horizontal layout (additive, scoped) */
.eg-subpanel{color:var(--t2)}
.eg-subpanel h2,.eg-subpanel h3,.eg-subpanel .ey,.eg-subpanel .eyebrow{color:var(--gold)}
.timeline-h{color:rgba(245,241,232,.92);font-weight:700}
.timeline-sub{color:var(--t3)}
.timeline-row{display:flex;flex-wrap:nowrap;gap:14px;overflow-x:auto;padding:6px 2px 14px;-webkit-overflow-scrolling:touch;scrollbar-width:thin}
.timeline-row::-webkit-scrollbar{height:6px}
.timeline-row::-webkit-scrollbar-thumb{background:var(--ge2);border-radius:3px}
.timeline-card{flex:0 0 auto;width:152px;background:rgba(0,0,0,.28);border:1px solid var(--ge2);border-radius:12px;padding:12px 10px 14px;text-align:center;transition:border-color .15s,box-shadow .15s}
.timeline-card:hover{border-color:rgba(212,162,76,.45)}
.timeline-card.active{border-color:var(--gold);box-shadow:0 0 0 1px rgba(212,162,76,.22)}
.timeline-year{color:var(--gold);font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;letter-spacing:.5px}
.timeline-ctx{color:var(--t3);font-size:11px;line-height:1.4;margin:4px 0 8px;min-height:30px}
.timeline-comp{color:rgba(245,241,232,.92);font-family:"JetBrains Mono",monospace;font-size:13px;font-weight:700;margin-top:6px}
.drift-dim{color:rgba(245,241,232,.92);font-weight:600}
.drift-delta{color:var(--t3)}
</style>
</head>"""
assert s.count("</head>")>=1, "no </head>"
s=s.replace("</head>", block, 1)
open(f,"w").write(s); print("inserted scoped re-theme style block before </head>")
PY
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
