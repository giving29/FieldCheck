#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
METHODOLOGY · SECTION 10 V5 ALGORITHM UPDATE · V2
═══════════════════════════════════════════════════════════════════════════
Fixed pattern: matches actual h2 format <h2><span class="num">10</span>...
Replaces section 10 body content with V5 v2.2+v2.3 architecture content
while preserving the section header.

Run from ~/Desktop/fieldcheck-proxy/.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, re
from pathlib import Path

print("═══ METHODOLOGY · SECTION 10 V5 UPDATE · V2 ═══\n")

METHOD = Path('METHODOLOGY_V17_V1.html')
if not METHOD.exists():
    print(f"✗ FAIL: {METHOD} not found in cwd")
    sys.exit(1)

c = METHOD.read_text()
orig_bytes = METHOD.stat().st_size
print(f"▸ {METHOD} · {orig_bytes:,} bytes\n")


# Idempotency
if 'V5 v2.2+v2.3 architecture' in c or 'suffix-amateur-ceiling' in c:
    print("✓ V5 v2.2+v2.3 content already present (idempotent)")
    sys.exit(0)


# Pre-flight · find section 10 h2 with the actual format
section10_h2_pattern = re.compile(
    r'<h2[^>]*>\s*<span class="num">10</span>[^<]*<b>V5 algorithm</b>[^<]*</h2>',
    re.IGNORECASE
)
m_h2 = section10_h2_pattern.search(c)
if not m_h2:
    print("✗ FAIL: section 10 h2 not found with expected pattern")
    print("  Looking for: <h2><span class=\"num\">10</span>The <b>V5 algorithm</b>...")
    sys.exit(1)

# Find section 11 h2 (next section) — to know where section 10 ends
section11_h2_pattern = re.compile(
    r'<h2[^>]*>\s*<span class="num">11</span>',
    re.IGNORECASE
)
m_next = section11_h2_pattern.search(c, pos=m_h2.end())

# If no section 11, find the next h2 of any number, or footer
if not m_next:
    next_h2 = re.compile(r'<h2[^>]*>', re.IGNORECASE)
    m_next = next_h2.search(c, pos=m_h2.end())

# If still nothing, find footer/end markers
if not m_next:
    for end_marker in ['<footer', '<div class="footer"', '<div class="cta"', '</main>', '</body>']:
        idx = c.find(end_marker, m_h2.end())
        if idx > 0:
            print(f"  Section 10 ends at: {end_marker}")
            class FakeMatch:
                def __init__(self, start): self._start = start
                def start(self): return self._start
            m_next = FakeMatch(idx)
            break

if not m_next:
    print("✗ FAIL: cannot determine end of section 10")
    sys.exit(1)

section_start = m_h2.start()
section_end = m_next.start()
print(f"  ✓ Section 10 found · spans bytes {section_start:,} → {section_end:,}")
print(f"  ✓ Current section 10 content: {section_end - section_start:,} bytes\n")


# Backup
backup = METHOD.with_suffix('.html.pre-section10-v022-36-v2.bak')
shutil.copy(METHOD, backup)
print(f"▸ Backup: {backup}\n")


# New section 10 content (h2 + body)
new_section = '''<h2><span class="num">10</span>The <b>V5 algorithm</b> · prompt + deterministic post-processing</h2>

<div style="background:#0f2417;border-left:3px solid #4ade80;padding:14px 18px;margin:14px 0;border-radius:0 6px 6px 0;color:#bbf7d0;font-family:ui-monospace,SFMono-Regular,monospace">
<div style="font-size:11px;color:#86efac;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-bottom:6px">V022.36-V5.2 · MAY 27, 2026 · BATTERY VALIDATED 110/110</div>
<p style="margin:0;font-size:14px;line-height:1.65">The V5 algorithm is a two-layer hybrid system: a prompt-driven synthesis layer evaluates evidence, and a deterministic post-synthesis correction layer applies bright-line rules where LLM variance is unacceptable. Audit trail in <code style="background:#000;padding:2px 6px;border-radius:3px;color:#a5f3fc">composite_v022_31.v5_corrections[]</code> shows every adjustment with rule, raw value, corrected value, and reason.</p>
</div>

<h3>10.1 · Layer 1 · Synthesis (prompt-driven)</h3>
<p>Sonnet 4.5 evaluates the athlete against 8 facets with cross-sport theoretical 10 anchors, 4 phenom criteria, 8 anti-inflation signals, and the default-low principle. Synthesis output includes raw composite and per-facet scores. <b>10 is the only ceiling.</b> No mathematical caps applied at this layer — Sonnet scores based purely on evidence rigor.</p>

<p>Prompt sections that drive the rigor:</p>
<ul>
<li><b>Cross-sport theoretical 10 anchors</b> — Duncan / Brady / Tiger / Federer per facet calibrate upper bounds across sport contexts</li>
<li><b>Phenom criteria</b> — 4 reqs locked: national-best evidence, pro coach corroboration, multi-year sustained signal, cross-context consistency. All 4 must be true for phenom_qualified.</li>
<li><b>Anti-inflation</b> — 8 explicit signals that do NOT justify higher scores (recruiting rank, summer camp, hype articles, etc.)</li>
<li><b>Default-low principle</b> — when evidence is uncertain, score lower; V5 inverts V4's hype-default-up</li>
<li><b>Anti-contamination</b> — reasoning instructions for Jr/Sr/family-lineage cases with named examples (Kate Harpring → score the daughter, not Matt Harpring NBA father)</li>
<li><b>Critical 9.7+ reserved</b> — imperative upper-bound rules: NO active player exceeds 9.6 except retired-singular Jordan at 9.9</li>
</ul>

<p><b>What was removed:</b> The V5 v2.1 iteration tried adding HARD NUMERIC ANCHORS — a list of named athletes with specific score ranges. This backfired. Saniyah Hall was anchored at 5.0-5.4 with the list present, yet Sonnet returned her at 9.0. The reason: listing Saniyah alongside Caitlin Clark, Steph Curry, and Tim Duncan caused peer-association bias — the model associated her with their tier, overriding the numeric bound. <b>This is a generalizable LLM lesson: reasoning instructions ("if X, then Y") beat anchor lookup tables for deterministic behavior.</b> We removed the list and moved enforcement to Layer 2.</p>

<h3>10.2 · Layer 2 · Deterministic post-synthesis correction</h3>
<p>After synthesis returns raw composite, a JavaScript function <code>_v5_apply_corrections</code> applies 6 bright-line rules. Each rule is conditional on identity, career stage, and tier signals — derived from the design doc, not arbitrary tier numbers.</p>

<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;background:#0a0a0a;border:1px solid #262626;border-radius:6px;overflow:hidden;font-family:ui-monospace,SFMono-Regular,monospace">
<thead><tr style="background:#1a1a1a">
<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Rule</th>
<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Trigger</th>
<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Action</th>
</tr></thead>
<tbody>
<tr><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8"><b>R1</b></td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">Jr/Sr/II/III/IV suffix (regex) + amateur tier</td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">composite ≤ 5.5 (HS) or 7.4 (D1)</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8"><b>R2</b></td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">HS + prep_amateur + no phenom flag</td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">composite ≤ 5.4</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8"><b>R3</b></td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">D1 + college_amateur + no phenom flag</td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">composite ≤ 7.4</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8"><b>R4</b></td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">Active career stage (rookie/early/prime/late_pro)</td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">composite ≤ 9.3</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8"><b>R5</b></td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">Rookie career stage</td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">composite ≤ 7.5</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8"><b>R6</b></td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">HS tier + pro stage (classification mismatch)</td><td style="padding:7px 10px;border-top:1px solid #262626;color:#e8e8e8">flag identity-review-needed (no correction)</td></tr>
</tbody>
</table>

<p><b>Why this is not V4 caps.</b> V4 had unconditional tier-based ceilings with no transparency. V5 corrections are conditional on identity+stage+tier signals; every correction logs <code>rule</code>, <code>from</code>, <code>to</code>, and a <code>reason</code> in the audit trail; raw synthesis is preserved in metadata; and phenom-qualified athletes bypass R2 and R3 entirely.</p>

<h3>10.3 · Audit trail metadata</h3>
<p>Every verdict response includes <code>composite_v022_31</code> with the full audit chain:</p>
<pre style="background:#000;border:1px solid #262626;padding:14px;border-radius:6px;overflow-x:auto;font-size:12.5px;line-height:1.55;color:#a5f3fc;font-family:ui-monospace,SFMono-Regular,monospace">{
  "composite": 5.4,
  "composite_v022_31": {
    "raw": 9.83,
    "v5_corrected": 5.4,
    "v5_corrections": [
      {"rule": "suffix-amateur-ceiling", "from": 9.83, "to": 5.5, "reason": "..."},
      {"rule": "hs-evidence-ceiling-non-phenom", "from": 5.5, "to": 5.4, "reason": "..."}
    ],
    "v5_corrections_applied": true,
    "tier": "hs",
    "stage": "prep_amateur"
  }
}</pre>

<h3>10.4 · Validation · 110-athlete battery</h3>
<p>The architecture validated against 110 athletes across 11 buckets (60 HS / 17 D1 / 13 D2 / 10 D3 / 3 JUCO / 7 pro regression+collision). Cold cache against DEV endpoint. Results:</p>
<ul>
<li><b>100% rule compliance</b> on the amateur moat case (HS + D1 + D2 + D3)</li>
<li>Jr/Sr suffix athletes deterministically bounded — Jordan Smith Jr 9.83 → 5.4, Carlos Medlock Jr 9.0 → 5.4, Eric Booth Jr 7.5 → 5.4</li>
<li>Top D1 amateurs at evidence ceiling — Cameron Boozer 9.1 → 7.4, AJ Dybantsa 9.3 → 7.4, JT Toppin 8.7 → 7.4</li>
<li>Active pros at active ceiling — Cooper Flagg 9.71 → 9.3 (active rule), Tim Duncan retired passes through unchanged at 9.3</li>
<li>Under-cap variance preserved — Kate Harpring 4.0, Manuella Fernandez 4.0, Jamarion Vincent 5.3 (D1 hidden gem), Anthony Brown Jr 6.2</li>
</ul>

<h3>10.5 · Design lessons from 3 iterations</h3>
<ul>
<li><b>V5 v1 rolled back</b> — caps off, evidence rigor weak. Every HS scored 9.6-9.8. Pure prompt iteration without rigor is naive.</li>
<li><b>V5 v2</b> — added cross-sport anchors, phenom criteria, anti-inflation. Clean cases worked. Contamination cases inflated.</li>
<li><b>V5 v2.1</b> — added HARD NUMERIC ANCHORS list. Backfired: Saniyah Hall 3.5 → 9.0 via peer-association. Named-entity lists amplify variance.</li>
<li><b>V5 v2.2 + v2.3</b> — rolled back the list, added deterministic post-processor + audit. 100% compliance. <b>Hybrid prompt+code is the architecture.</b></li>
</ul>

<p><b>Generalizable insight:</b> for any LLM-scored system that requires bright-line behavior, hybrid wins. Use prompts for evidence reasoning (LLM strength). Use code for identity/pattern detection (deterministic). Preserve raw output in audit metadata for transparency.</p>

'''


# Apply replacement
c_new = c[:section_start] + new_section + c[section_end:]
METHOD.write_text(c_new)

new_bytes = METHOD.stat().st_size
delta = new_bytes - orig_bytes
print(f"▸ {METHOD} · {new_bytes:,} bytes (delta {delta:+,})\n")


# Verify
print("▸ Post-patch verification\n")
checks = [
    ('Section 10 new h2', 'prompt + deterministic post-processing' in c_new),
    ('V022.36-V5.2 marker', 'V022.36-V5.2' in c_new),
    ('R1 suffix rule', 'suffix-amateur-ceiling' in c_new),
    ('R6 mismatch flag', 'identity-review-needed' in c_new),
    ('Audit trail metadata sample', 'v5_corrections' in c_new),
    ('Battery validation', 'Jordan Smith Jr' in c_new and 'Cooper Flagg' in c_new),
    ('3 iterations lessons', 'V5 v2.1' in c_new and 'V5 v2.2 + v2.3' in c_new),
    ('Sections 01-09 preserved', '<span class="num">01</span>' in c_new and '<span class="num">09</span>' in c_new),
]
ok = True
for label, found in checks:
    print(f"  {'✓' if found else '✗'} {label}")
    if not found:
        ok = False

if not ok:
    print(f"\n✗ POST-PATCH VERIFICATION FAILED")
    print(f"  Restore: cp {backup} {METHOD}")
    sys.exit(1)


print(f"\n═══════════════════════════════════════════════════════════════════════")
print(f" METHODOLOGY SECTION 10 V5 · UPDATED")
print(f"═══════════════════════════════════════════════════════════════════════")
print(f" {METHOD} · {orig_bytes:,} → {new_bytes:,} bytes ({delta:+,})")
print(f" backup: {backup}")
print(f"")
print(f" NEXT: ./fc-deploy-dev.sh")
