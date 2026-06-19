#!/usr/bin/env bash
set -e
WS="${WS:-$HOME/Desktop/fieldcheck-proxy}"
cd "$WS"; F="fieldcheck-verdict.html"
[ -f "$F" ] || { echo "ABORT :: $F not found"; exit 1; }
if grep -q "fc-modules-batch1" "$F"; then echo "Already applied. Nothing to do."; exit 0; fi
cp "$F" "$F.bak.batch1.$(date +%Y%m%d_%H%M)"; echo "backed up $F"
cat > /tmp/__b1.css <<'CSSEOF'
/* ===== BATCH 1 · Coach Voices / Coach Culture / 16 Voices ===== */
/* --- Coach Voices: editorial pull-quotes --- */
[data-vtab="evalgrid"] .voice-card{position:relative;background:linear-gradient(155deg,rgba(28,26,38,.55),rgba(15,14,19,.32));border:1px solid var(--ge2);border-radius:14px;padding:16px 20px 16px 20px;margin-bottom:12px;overflow:hidden}
[data-vtab="evalgrid"] .voice-card.elite{border-color:var(--goldl);background:linear-gradient(155deg,rgba(212,162,76,.08),rgba(15,14,19,.4))}
[data-vtab="evalgrid"] .voice-card::before{content:"\201C";position:absolute;top:4px;left:14px;font-family:"Cormorant Garamond",serif;font-size:52px;line-height:1;color:var(--goldl);pointer-events:none}
[data-vtab="evalgrid"] .voice-avatar{width:34px;height:34px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:rgba(212,162,76,.12);border:1.5px solid var(--goldl);color:var(--gold);font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;float:left;margin:0 11px 4px 0}
[data-vtab="evalgrid"] .voice-quote{font-family:"Cormorant Garamond",serif;font-style:italic;font-size:17px;line-height:1.55;color:rgba(245,241,232,.92);margin:2px 0 12px;padding-left:30px}
[data-vtab="evalgrid"] .voice-name{color:rgba(245,241,232,.95);font-weight:700;font-size:13px}
[data-vtab="evalgrid"] .voice-role{color:var(--t3);font-size:12px}
[data-vtab="evalgrid"] .voice-src{color:var(--gold);font-size:11px;text-decoration:none}
[data-vtab="evalgrid"] .voice-tag{display:inline-block;margin-left:6px;padding:2px 8px;border-radius:999px;background:rgba(212,162,76,.08);border:1px solid var(--goldl);color:var(--gold);font-family:"JetBrains Mono",monospace;font-size:9px;font-weight:700;letter-spacing:.4px}
/* --- Coach Culture: coach hero + heatmap + delta rows --- */
[data-vtab="evalgrid"] .cc-coach-card{display:flex;gap:14px;align-items:center;background:linear-gradient(135deg,rgba(212,162,76,.07),rgba(0,0,0,.2));border:1px solid var(--goldl);border-radius:14px;padding:16px;margin-bottom:18px}
[data-vtab="evalgrid"] .cc-coach-avatar{width:48px;height:48px;flex:0 0 auto;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(212,162,76,.14);border:2px solid var(--goldl);color:var(--gold);font-family:"JetBrains Mono",monospace;font-weight:700;font-size:15px}
[data-vtab="evalgrid"] .cc-coach-body{flex:1}
[data-vtab="evalgrid"] .cc-coach-name{color:rgba(245,241,232,.96);font-weight:700;font-size:16px}
[data-vtab="evalgrid"] .cc-coach-role{color:var(--t3);font-size:11.5px;margin:2px 0 4px}
[data-vtab="evalgrid"] .cc-coach-snap{color:var(--t2);font-size:12.5px;line-height:1.45}
[data-vtab="evalgrid"] .cc-coach-comp{text-align:center;flex:0 0 auto;padding-left:8px}
[data-vtab="evalgrid"] .cc-coach-comp-num{font-family:"Anton",sans-serif;font-size:30px;color:var(--gold);line-height:1}
[data-vtab="evalgrid"] .cc-coach-comp-lbl{font-family:"JetBrains Mono",monospace;font-size:8.5px;letter-spacing:.5px;text-transform:uppercase;color:var(--t3);margin-top:2px}
[data-vtab="evalgrid"] .cc-dim-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:18px}
[data-vtab="evalgrid"] .cc-dim-cell{background:rgba(0,0,0,.2);border:1px solid var(--ge2);border-radius:10px;padding:11px 13px}
[data-vtab="evalgrid"] .cc-dim-lbl{display:flex;justify-content:space-between;align-items:center;color:var(--t2);font-size:12px;font-weight:600;margin-bottom:7px}
[data-vtab="evalgrid"] .cc-dim-score{font-family:"JetBrains Mono",monospace;color:var(--gold);font-weight:700}
[data-vtab="evalgrid"] .cc-dim-bar{height:6px;background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden}
[data-vtab="evalgrid"] .cc-dim-fill{height:100%;background:linear-gradient(90deg,var(--gold),rgba(212,162,76,.45));border-radius:3px}
[data-vtab="evalgrid"] .cc-dim-note{color:var(--t3);font-size:10.5px;line-height:1.4;margin-top:6px}
[data-vtab="evalgrid"] .cc-athletes-h{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--t3);margin:6px 0 10px}
[data-vtab="evalgrid"] .cc-athlete-row{display:flex;gap:12px;align-items:center;flex-wrap:wrap;background:rgba(0,0,0,.18);border:1px solid var(--ge2);border-radius:10px;padding:10px 14px;margin-bottom:8px}
[data-vtab="evalgrid"] .cc-athlete-row.self{border-color:var(--goldl);background:rgba(212,162,76,.06)}
[data-vtab="evalgrid"] .cc-athlete-name{color:rgba(245,241,232,.95);font-weight:700;font-size:13px}
[data-vtab="evalgrid"] .cc-self-marker{margin-left:7px;font-family:"JetBrains Mono",monospace;font-size:8.5px;letter-spacing:.4px;text-transform:uppercase;color:var(--gold);border:1px solid var(--goldl);border-radius:5px;padding:2px 6px}
[data-vtab="evalgrid"] .cc-athlete-span{color:var(--t3);font-size:11px}
[data-vtab="evalgrid"] .cc-athlete-delta{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:12px;color:var(--t2)}
[data-vtab="evalgrid"] .cc-athlete-delta.up,[data-vtab="evalgrid"] .cc-athlete-delta.pos{color:var(--moss)}
[data-vtab="evalgrid"] .cc-athlete-delta.down,[data-vtab="evalgrid"] .cc-athlete-delta.neg{color:var(--red)}
[data-vtab="evalgrid"] .cc-athlete-note{color:var(--t3);font-size:11px;flex:1 1 100%;line-height:1.4}
/* --- 16 Voices: primary hero + ranked affinity meters --- */
[data-vtab="evalgrid"] .vf-h{font-family:"Big Shoulders Display",sans-serif;font-weight:700;font-size:clamp(18px,2.4vw,23px);color:rgba(245,241,232,.96);margin:2px 0 6px}
[data-vtab="evalgrid"] .vf-sub{color:var(--t3);font-size:13px;line-height:1.55;margin-bottom:12px;max-width:660px}
[data-vtab="evalgrid"] .vf-meta{color:var(--t4);font-family:"JetBrains Mono",monospace;font-size:10px;margin-bottom:18px}
[data-vtab="evalgrid"] .vf-primary-card{display:flex;gap:16px;align-items:center;background:linear-gradient(135deg,rgba(212,162,76,.09),rgba(0,0,0,.22));border:1px solid var(--goldl);border-radius:16px;padding:18px 20px;margin-bottom:20px}
[data-vtab="evalgrid"] .vf-primary-num{font-family:"Anton",sans-serif;font-size:46px;line-height:1;color:var(--gold);flex:0 0 auto}
[data-vtab="evalgrid"] .vf-primary-body{flex:1}
[data-vtab="evalgrid"] .vf-primary-tag{font-family:"JetBrains Mono",monospace;font-size:9px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--gold)}
[data-vtab="evalgrid"] .vf-primary-name{font-family:"Big Shoulders Display",sans-serif;font-weight:700;font-size:20px;color:rgba(245,241,232,.96);margin:3px 0}
[data-vtab="evalgrid"] .vf-primary-brief{color:var(--t2);font-size:13px;line-height:1.5}
[data-vtab="evalgrid"] .vf-strip-h{font-family:"JetBrains Mono",monospace;font-size:10px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;color:var(--t4);margin:8px 0 10px}
[data-vtab="evalgrid"] .vf-strip{display:flex;flex-direction:column;gap:5px}
[data-vtab="evalgrid"] .vf-row{display:flex;align-items:center;gap:10px;padding:5px 4px}
[data-vtab="evalgrid"] .vf-row.anti{opacity:.45}
[data-vtab="evalgrid"] .vf-rank{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--t4);flex:0 0 22px}
[data-vtab="evalgrid"] .vf-name{font-weight:700;font-size:12.5px;color:rgba(245,241,232,.92);flex:0 0 108px}
[data-vtab="evalgrid"] .vf-tag{color:var(--t3);font-size:10.5px;flex:0 0 104px}
[data-vtab="evalgrid"] .vf-bar{flex:1;height:7px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;min-width:60px}
[data-vtab="evalgrid"] .vf-bar-fill{height:100%;background:linear-gradient(90deg,var(--gold),rgba(212,162,76,.4));border-radius:4px}
[data-vtab="evalgrid"] .vf-row.anti .vf-bar-fill{background:var(--t4)}
[data-vtab="evalgrid"] .vf-pct{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:700;color:var(--gold);flex:0 0 28px;text-align:right}
CSSEOF
python3 - <<'PYEOF'
f="fieldcheck-verdict.html"; s=open(f).read()
css=open("/tmp/__b1.css").read()
block='<style id="fc-modules-batch1">\n'+css+'\n</style>\n</head>'
assert s.count("</head>")>=1
s=s.replace("</head>",block,1)
open(f,"w").write(s); print("batch1 modules styled: Coach Voices, Coach Culture, 16 Voices")
PYEOF
echo ""; echo "Ship to DEV:  bash fc-dev.sh"
