#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
CANONICAL V5.34 → V5.35 v2 · MAY 26 NT · V5 PHILOSOPHY REWRITE
═══════════════════════════════════════════════════════════════════════════
V2 REWRITE per Sridhar V5 philosophy correction:
  - NO CAPS, NO BUCKETS, NO CLAMPS in language or design
  - 10 is the only ceiling (theoretical, unreachable)
  - Algorithm calculates real number from evidence, naturally distributed
  - Phenoms emerge naturally when evidence justifies (Kobe/LeBron/KD/Tiger at 17)
  - Sprint A1 redesigned as POLYGON CONSENSUS-SHADOW OVERLAY (not separate block)
  - Eval tabs broken added as known issue

Captures:
  1. V022.32-YX PROD ship + both UI fixes
  2. NEW MOAT roadmap · Track A · 7 sprints (A1-A7) verdict deepest-read
  3. NEW MOAT roadmap · Track B · Block 10 crawler (the IP unlock)
  4. CORE work · V5 algorithm rewrite (remove cap function, evidence-vs-10 scoring)
  5. Known issue · Eval subtabs not rendering for most players
  6. Version bump V5.34 → V5.35

Single str_replace at <body>. Backup + 18-check grep-verify. Restores on fail.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, hashlib, re
from pathlib import Path

CANON = Path('FC_CANONICAL_STATE_V1.html')
BACKUP = Path('FC_CANONICAL_STATE_V1.html.pre-v535.bak')

print("═══ CANONICAL V5.34 → V5.35 v2 · V5 PHILOSOPHY ═══\n")

if not CANON.exists():
    print("✗ FC_CANONICAL_STATE_V1.html not found · ABORT"); sys.exit(1)

content = CANON.read_text()
size_before = len(content)
sha_before = hashlib.sha256(content.encode()).hexdigest()[:12]
print(f"▸ canonical: {size_before:,} bytes · sha={sha_before}")


# ─── ANCHOR DETECTION ──────────────────────────────────────────────────────
print("\n▸ Anchor detection...")

vstamp_re = re.compile(r'Canonical State · V5\.(\d+)')
m = vstamp_re.search(content)
if not m:
    print("✗ V-stamp not found · ABORT"); sys.exit(1)
current_v = m.group(1)
print(f"  ✓ V-stamp found: V5.{current_v}")

body_open_re = re.compile(r'<body[^>]*>')
bm = body_open_re.search(content)
if not bm:
    print("✗ <body> tag not found · ABORT"); sys.exit(1)
body_tag = bm.group(0)
print(f"  ✓ <body> anchor found")

# Check if v1 of this script already ran (idempotent guard)
if 'session-may26-nt-v535' in content:
    print("\n  ! v1 of capture already in canonical · removing v1 block first")
    # remove the v1 section
    v1_section_re = re.compile(
        r'\n*<!-- ═+\n\s+MAY 26 NT SESSION CAPTURE.*?</section>\n*',
        re.DOTALL
    )
    content = v1_section_re.sub('\n', content)
    new_size_after_strip = len(content)
    print(f"  ✓ v1 section removed (stripped {size_before-new_size_after_strip:+d} bytes)")


# ─── BACKUP ────────────────────────────────────────────────────────────────
shutil.copy(CANON, BACKUP)
print(f"\n▸ Backup: {BACKUP}")


# ─── P1: bump V-stamp → V5.35 ──────────────────────────────────────────────
print(f"\n▸ P1: bump V5.{current_v} → V5.35...")
content_new = vstamp_re.sub('Canonical State · V5.35', content, count=1)
if content_new == content:
    print("✗ P1 no-op · ABORT"); shutil.copy(BACKUP, CANON); sys.exit(1)
print("  ✓ stamp bumped")


# ─── P2: insert V5 philosophy session capture block ────────────────────────
new_section = '''

<!-- ════════════════════════════════════════════════════════════════════════
     MAY 26 NT SESSION CAPTURE · V5.35 · V5 PHILOSOPHY
     Single-block insertion at top of body · move into proper tabs on refactor
     ════════════════════════════════════════════════════════════════════════ -->
<section id="session-may26-nt-v535" style="max-width:1100px;margin:24px auto;padding:24px 28px;background:linear-gradient(135deg,rgba(212,162,76,.04),#16151B);border:1px solid rgba(212,162,76,.32);border-radius:16px;font-family:'Inter',sans-serif;color:#F5F1E8;line-height:1.6">

  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.8px;color:rgba(212,162,76,.65);text-transform:uppercase;margin-bottom:8px">// Session capture · May 26 nt · V5.35 · V5 philosophy</div>
  <h2 style="font-family:'Anton',sans-serif;font-size:32px;letter-spacing:-.005em;line-height:1.1;margin-bottom:10px;color:#F5F1E8">10 is the only ceiling.</h2>
  <p style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:18px;color:rgba(245,241,232,.78);margin-bottom:24px;max-width:780px">No caps. No buckets. No clamps. The algorithm produces a single number 0-10 for every athlete, calculated from evidence, measured against theoretical perfection. Every decimal makes sense. Phenoms emerge naturally when the evidence justifies them. UTR for sports intelligence.</p>

  <!-- ── A · V5 PHILOSOPHY (the gold standard) ── -->
  <div style="margin-bottom:28px;padding:18px 22px;background:rgba(212,162,76,.06);border:1px solid rgba(212,162,76,.32);border-radius:12px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#D4A24C;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:12px">▌ A · V5 algorithm philosophy · the gold standard</div>
    <ul style="list-style:none;padding:0;font-size:14.5px;line-height:1.7">
      <li style="margin-bottom:6px"><b style="font-family:'Anton',sans-serif;color:#D4A24C;letter-spacing:.005em">One number, one ceiling.</b> Single 0-10 score per athlete. 10 = theoretical perfection, unreachable by any human.</li>
      <li style="margin-bottom:6px"><b style="font-family:'Anton',sans-serif;color:#D4A24C;letter-spacing:.005em">Calculated from evidence.</b> Each of the 8 facets scored vs theoretical-perfect-facet performance. No stages, no tiers, no buckets, no clamps.</li>
      <li style="margin-bottom:6px"><b style="font-family:'Anton',sans-serif;color:#D4A24C;letter-spacing:.005em">Evidence rigor is the limiter.</b> An HS top recruit naturally lands ~5 because the evidence is HS-only — not because of a cap. Pro-context facets can't score high without pro-context evidence.</li>
      <li style="margin-bottom:6px"><b style="font-family:'Anton',sans-serif;color:#D4A24C;letter-spacing:.005em">Phenoms emerge naturally.</b> Kobe at 17, LeBron at 17, KD at 18, Tiger at 17 score higher than peers because their evidence already shows pro-tier production, athleticism, competitive context. The algorithm doesn't suppress them — it correctly reads the evidence.</li>
      <li style="margin-bottom:6px"><b style="font-family:'Anton',sans-serif;color:#D4A24C;letter-spacing:.005em">UTR-inspired.</b> Single universal scale, gender/age/sport-blind. UTR doesn't have buckets — Sinner at 16 was already 12+ while normal 16-yo's are 5-7. The math produced that, not categories. We do the same.</li>
      <li><b style="font-family:'Anton',sans-serif;color:#D4A24C;letter-spacing:.005em">Reference distribution, not enforcement.</b> Jordan 9.9 · Duncan 9.3-9.6 · multi-MVPs 9.0-9.3 · top HS ~5 — these describe what evidence-driven scoring naturally produces. They are <i>predicted</i> outputs, not imposed ceilings.</li>
    </ul>
    <div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(212,162,76,.22);font-family:'Cormorant Garamond',serif;font-style:italic;font-size:17px;color:#F5F1E8;line-height:1.55">"Making every number make sense and measured against the highest non-reachable ceiling of 10 — that's all there is."</div>
  </div>

  <!-- ── B · CORE WORK · V5 ALGORITHM REWRITE ── -->
  <div style="margin-bottom:28px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#FF5C3A;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px">▌ B · CORE WORK · V5 algorithm rewrite (worker.js)</div>
    <ul style="list-style:none;padding:0;font-size:14px">
      <li style="padding:10px 14px;background:rgba(255,92,58,.06);border-left:3px solid #FF5C3A;border-radius:0 8px 8px 0;margin-bottom:8px"><b>Remove the cap function.</b> Delete _v22_31_cap clamping in worker.js. The cascade (stage detection → cap clamp) becomes a no-op for output. Stage detection can stay for routing but doesn't influence the composite.</li>
      <li style="padding:10px 14px;background:rgba(255,92,58,.06);border-left:3px solid #FF5C3A;border-radius:0 8px 8px 0;margin-bottom:8px"><b>Rewrite synthesis prompt with theoretical-10 anchors per facet.</b> Each facet (size, athleticism, production, competitive_context, projectability, character, durability, scheme_fit) gets a "perfect 10 = X" reference. HS evidence rated against the perfect 10, not against HS peers. Demands explicit evidence for any score above evidence-justified.</li>
      <li style="padding:10px 14px;background:rgba(255,92,58,.06);border-left:3px solid #FF5C3A;border-radius:0 8px 8px 0;margin-bottom:8px"><b>Per-facet evidence audit in synthesis output.</b> Haiku returns evidence trail per facet so weak evidence → low score is auditable and the polygon shows confidence depth.</li>
      <li style="padding:10px 14px;background:rgba(255,92,58,.06);border-left:3px solid #FF5C3A;border-radius:0 8px 8px 0"><b>Battery is smoke test, not ceiling.</b> The 110-athlete battery proves directional correctness. The real test is the algorithm working for every player in real time across the universe — Caitlin Clark 9.05 (wrong, evidence says lower), Flagg 9.3 (wrong, rookie evidence says lower), Tate Ivanyo 9.3 (wrong, corpus contamination). The algorithm should produce correct numbers for ALL.</li>
    </ul>
  </div>

  <!-- ── C · MOAT ROADMAP · TRACK A · VERDICT DEEPEST-READ ── -->
  <div style="margin-bottom:28px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#D4A24C;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px">▌ C · MOAT roadmap · Track A · Verdict page deepest-read</div>
    <p style="font-size:14px;color:rgba(245,241,232,.78);margin-bottom:14px">Seven aggressive sprints, sequenced by depth-of-read impact. Audit May 26 nt confirmed most bonus moat blocks still 0 refs in verdict page.</p>

    <table style="width:100%;border-collapse:collapse;font-size:13.5px">
      <thead><tr style="border-bottom:1px solid rgba(212,162,76,.22)">
        <th style="text-align:left;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(212,162,76,.65);letter-spacing:1px;text-transform:uppercase">Sprint</th>
        <th style="text-align:left;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(212,162,76,.65);letter-spacing:1px;text-transform:uppercase">Block</th>
        <th style="text-align:left;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(212,162,76,.65);letter-spacing:1px;text-transform:uppercase">What it does</th>
        <th style="text-align:left;padding:10px 12px;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(212,162,76,.65);letter-spacing:1px;text-transform:uppercase">Status</th>
      </tr></thead>
      <tbody>
        <tr style="border-bottom:1px solid rgba(255,252,245,.06)"><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A1</td><td style="padding:12px;font-weight:600">Polygon Consensus-Shadow Overlay</td><td style="padding:12px;color:rgba(245,241,232,.78)">Pre-Consensus Read integrated INTO the polygon. FieldCheck calculated polygon in gold; market consensus polygon as muted shadow underneath. The delta between the two shapes IS the asymmetry — visualized, not narrated. No separate block, no examples needed. The polygon tells the story.</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:#D4A24C;background:rgba(212,162,76,.1);padding:4px 10px;border-radius:9999px;border:1px solid rgba(212,162,76,.32);letter-spacing:.8px">REDESIGN</span></td></tr>
        <tr style="border-bottom:1px solid rgba(255,252,245,.06)"><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A2</td><td style="padding:12px;font-weight:600">16 Voices Deep Dive</td><td style="padding:12px;color:rgba(245,241,232,.78)">Signature page section — PhDs, coaches, scouts, trainers, parents, teammates, opponents, officials, press, fans, recruiters, NIL agents, analytics, tape, video, history. Each voice 2-3 sentences evidence-anchored.</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(245,241,232,.4);background:rgba(255,252,245,.04);padding:4px 10px;border-radius:9999px;letter-spacing:.8px">QUEUED</span></td></tr>
        <tr style="border-bottom:1px solid rgba(255,252,245,.06)"><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A3</td><td style="padding:12px;font-weight:600">Coach Voices + Coach Culture</td><td style="padding:12px;color:rgba(245,241,232,.78)">Coach quotes specific to the athlete + program culture fit score (Saban Discipline Index style).</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(245,241,232,.4);background:rgba(255,252,245,.04);padding:4px 10px;border-radius:9999px;letter-spacing:.8px">QUEUED</span></td></tr>
        <tr style="border-bottom:1px solid rgba(255,252,245,.06)"><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A4</td><td style="padding:12px;font-weight:600">Position Pool Heatmap</td><td style="padding:12px;color:rgba(245,241,232,.78)">Athlete in position cohort cluster. "5.3 combo guard nationally" — visual ranking against peer pool.</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(245,241,232,.4);background:rgba(255,252,245,.04);padding:4px 10px;border-radius:9999px;letter-spacing:.8px">QUEUED</span></td></tr>
        <tr style="border-bottom:1px solid rgba(255,252,245,.06)"><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A5</td><td style="padding:12px;font-weight:600">Hidden Gem on-page section</td><td style="padding:12px;color:rgba(245,241,232,.78)">For Discover-class athletes. Why we found them, what others missed. The Bevo Francis arc.</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(245,241,232,.4);background:rgba(255,252,245,.04);padding:4px 10px;border-radius:9999px;letter-spacing:.8px">QUEUED</span></td></tr>
        <tr style="border-bottom:1px solid rgba(255,252,245,.06)"><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A6</td><td style="padding:12px;font-weight:600">Career Calendar + Eval Grid TOC</td><td style="padding:12px;color:rgba(245,241,232,.78)">Upcoming verdict-moving dates (combine, exhibition, draft) + deep-eval navigation.</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(245,241,232,.4);background:rgba(255,252,245,.04);padding:4px 10px;border-radius:9999px;letter-spacing:.8px">QUEUED</span></td></tr>
        <tr><td style="padding:12px;font-family:'JetBrains Mono',monospace;font-weight:700;color:#D4A24C">A7</td><td style="padding:12px;font-weight:600">Snapshot Card + Trust Delta + Outcome Ledger</td><td style="padding:12px;color:rgba(245,241,232,.78)">Portable verdict (image+text) + public predictions tracking with confidence over time — the receipts.</td><td style="padding:12px"><span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(245,241,232,.4);background:rgba(255,252,245,.04);padding:4px 10px;border-radius:9999px;letter-spacing:.8px">QUEUED</span></td></tr>
      </tbody>
    </table>
  </div>

  <!-- ── D · TRACK B · BLOCK 10 CRAWLER ── -->
  <div style="margin-bottom:28px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#4EC9C0;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px">▌ D · MOAT roadmap · Track B · Block 10 Crawler (parallel)</div>
    <p style="padding:14px 18px;background:rgba(78,201,192,.04);border:1px solid rgba(78,201,192,.18);border-radius:11px;font-size:14px;color:rgba(245,241,232,.85);line-height:1.7"><b>YouTube discovery pipeline · automated HS game film → tagging → never-before-seen data.</b> Per Tenet 40 this is the actual moat: MaxPreps = stats only, Hudl = tape only. FieldCheck triangulates wider via crawl + custom algorithm on data nobody else has structured. 3-5 sprints. Biggest IP unlock. Runs parallel to Track A.</p>
  </div>

  <!-- ── E · KNOWN ISSUES ── -->
  <div style="margin-bottom:28px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#FF5C3A;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px">▌ E · Known issues to fix</div>
    <ul style="list-style:none;padding:0;font-size:14px">
      <li style="padding:10px 14px;background:rgba(255,92,58,.04);border-left:3px solid rgba(255,92,58,.5);border-radius:0 8px 8px 0;margin-bottom:8px"><b>Eval tabs broken for most players.</b> Subtabs (eg-timeline, eg-drift, eg-overlay) and downstream blocks not rendering for non-FC17 players. May 26 nt polygon-gate fix stopped the unconditional hiding, but the subtab content itself may not be wired per-player. Diagnose: per-tab data binding, per-player render conditions.</li>
      <li style="padding:10px 14px;background:rgba(255,92,58,.04);border-left:3px solid rgba(255,92,58,.5);border-radius:0 8px 8px 0;margin-bottom:8px"><b>Caitlin Clark = 9.05 (algorithm wrong).</b> Year-2 WNBA evidence doesn't justify 9.05 vs theoretical 10. V5 rewrite should drop this naturally.</li>
      <li style="padding:10px 14px;background:rgba(255,92,58,.04);border-left:3px solid rgba(255,92,58,.5);border-radius:0 8px 8px 0;margin-bottom:8px"><b>Cooper Flagg = 9.3 (algorithm wrong).</b> Rookie evidence doesn't justify 9.3. V5 rewrite should drop this naturally.</li>
      <li style="padding:10px 14px;background:rgba(255,92,58,.04);border-left:3px solid rgba(255,92,58,.5);border-radius:0 8px 8px 0"><b>Tate Ivanyo = 9.3 (corpus contamination).</b> Persists across all patches. Identity validation at corpus boundary needed.</li>
    </ul>
  </div>

  <!-- ── F · SHIPPED TONIGHT ── -->
  <div style="margin-bottom:8px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:#6BAA5A;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px">▌ F · Shipped tonight (PROD)</div>
    <ul style="list-style:none;padding:0;font-size:14px">
      <li style="padding:10px 14px;background:rgba(107,170,90,.06);border-left:3px solid #6BAA5A;border-radius:0 8px 8px 0;margin-bottom:8px"><b>V022.32-YX worker</b> · Tim Duncan legend_pro fix · D1 spread emerging · D2 +7pp compliance · partial decimal moat proof (transitional release; V5 rewrite is the real fix)</li>
      <li style="padding:10px 14px;background:rgba(107,170,90,.06);border-left:3px solid #6BAA5A;border-radius:0 8px 8px 0;margin-bottom:8px"><b>UI fix · FC17 polygon gate</b> · fieldcheck-verdict.html +666B · only Flagg/Caleb/Caitlin/Skinner get new FC17 polygon, all others get legacy polygon back (was rendering blank)</li>
      <li style="padding:10px 14px;background:rgba(107,170,90,.06);border-left:3px solid #6BAA5A;border-radius:0 8px 8px 0"><b>UI fix · composite display</b> · fieldcheck-verdict.html line 3589 reordered to read top-level composite first · Tim Duncan correctly shows 9.3 ELITE+</li>
    </ul>
  </div>

  <div style="margin-top:24px;padding-top:14px;border-top:1px solid rgba(255,252,245,.06);font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(245,241,232,.4);letter-spacing:.4px">Captured by apply_canonical_v535_v2.py · V5 philosophy · Tenet 22 + Tenet 48 · May 26 nt</div>
</section>

'''

print("\n▸ P2: insert V5 philosophy session capture after <body>...")
content_new2 = content_new.replace(body_tag, body_tag + new_section, 1)
if content_new2 == content_new:
    print("✗ P2 no-op · ABORT"); shutil.copy(BACKUP, CANON); sys.exit(1)
print(f"  ✓ inserted (delta +{len(content_new2)-len(content_new)} bytes)")


# ─── WRITE ─────────────────────────────────────────────────────────────────
CANON.write_text(content_new2)
size_after = len(content_new2)
sha_after = hashlib.sha256(content_new2.encode()).hexdigest()[:12]
print(f"\n▸ canonical · {size_after:,} bytes · sha={sha_after}\n")


# ─── GREP-VERIFY ───────────────────────────────────────────────────────────
print("▸ Grep-verify (Tenet 47.1)...")
checks = [
    ("V5.35 stamp present", "Canonical State · V5.35" in content_new2),
    ("session capture inserted", "session-may26-nt-v535" in content_new2),
    ("V5 philosophy heading", "10 is the only ceiling" in content_new2),
    ("no caps no buckets phrase", "No caps. No buckets. No clamps" in content_new2),
    ("theoretical perfection language", "theoretical perfection, unreachable" in content_new2),
    ("phenoms emerge naturally", "Phenoms emerge naturally" in content_new2),
    ("UTR-inspired", "UTR-inspired" in content_new2),
    ("V5 core work · remove cap function", "Remove the cap function" in content_new2),
    ("Sprint A1 polygon overlay", "Polygon Consensus-Shadow Overlay" in content_new2),
    ("Sprint A2 16 Voices", "16 Voices Deep Dive" in content_new2),
    ("Sprint A7 Snapshot Card", "Snapshot Card + Trust Delta" in content_new2),
    ("Track B Block 10", "Block 10 Crawler" in content_new2),
    ("Eval tabs broken issue", "Eval tabs broken for most players" in content_new2),
    ("Caitlin 9.05 known issue", "Caitlin Clark = 9.05" in content_new2),
    ("Flagg 9.3 known issue", "Cooper Flagg = 9.3" in content_new2),
    ("V022.32-YX shipped", "V022.32-YX worker" in content_new2),
    ("FC17 polygon gate shipped", "FC17 polygon gate" in content_new2),
    ("Sridhar V5 quote captured", "highest non-reachable ceiling of 10" in content_new2),
]
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False

if not all_ok:
    print("\n✗ GREP-VERIFY FAILED · restoring"); shutil.copy(BACKUP, CANON); sys.exit(1)


# ─── DONE ──────────────────────────────────────────────────────────────────
print()
print("═══════════════════════════════════════════════════════════════════════")
print(" CANONICAL V5.35 v2 APPLIED · V5 PHILOSOPHY")
print("═══════════════════════════════════════════════════════════════════════")
print(f" canonical · V5.{current_v} → V5.35 · {size_after:,} bytes")
print(f"")
print(f" Captured:")
print(f"   ✓ V5 algorithm philosophy (10 only ceiling, no caps/buckets/clamps)")
print(f"   ✓ V5 core work (remove _v22_31_cap, rewrite synthesis prompt)")
print(f"   ✓ Track A · Sprint A1-A7 verdict deepest-read (A1 = polygon overlay)")
print(f"   ✓ Track B · Block 10 crawler (the IP unlock)")
print(f"   ✓ Known issues · Eval tabs broken, Caitlin/Flagg/Ivanyo algorithm wrong")
print(f"   ✓ Tonight's ships (V022.32-YX + both UI fixes)")
print(f"")
print(f" Backup: {BACKUP}")
print(f" NEXT: ./fc-deploy-dev.sh")
