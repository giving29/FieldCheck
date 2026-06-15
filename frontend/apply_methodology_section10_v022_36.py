#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
METHODOLOGY · SECTION 10 V5 ALGORITHM UPDATE · V022.36-V5.2
═══════════════════════════════════════════════════════════════════════════
Updates METHODOLOGY_V17_V1.html section 10 with V5 v2.2+v2.3 architecture.

Per Canonical Doctrine: requires Sridhar to upload current methodology file
to ~/Desktop/fieldcheck-proxy/. Script does surgical str_replace.

Run from ~/Desktop/fieldcheck-proxy/.
═══════════════════════════════════════════════════════════════════════════
"""
import sys, shutil, re
from pathlib import Path

print("═══ METHODOLOGY · SECTION 10 V5 ALGORITHM UPDATE ═══\n")

METHOD = Path('METHODOLOGY_V17_V1.html')
if not METHOD.exists():
    print(f"✗ FAIL: {METHOD} not found in cwd")
    print("  Upload current methodology first (Canonical Doctrine)")
    sys.exit(1)

c = METHOD.read_text()
orig_bytes = METHOD.stat().st_size
print(f"▸ {METHOD} · {orig_bytes:,} bytes\n")


# ══════════════════════════════════════════════════════════════════════════
# Idempotency check
# ══════════════════════════════════════════════════════════════════════════
if 'V5 v2.2+v2.3' in c or 'v5_apply_corrections' in c:
    print("✓ V5 v2.2+v2.3 content already present in methodology (idempotent)")
    sys.exit(0)


# ══════════════════════════════════════════════════════════════════════════
# Pre-flight
# ══════════════════════════════════════════════════════════════════════════
print("▸ Pre-flight\n")

# Look for section 10 anchor (multiple strategies)
section_patterns = [
    r'<h2[^>]*>\s*10\.\s*V5\s*Algorithm',
    r'<h2[^>]*>\s*10\.\s*Algorithm',
    r'<section[^>]*id="section-10"',
    r'<section[^>]*id="v5"',
    r'V5 Algorithm</h2>',
]

found_pattern = None
for pat in section_patterns:
    if re.search(pat, c, re.IGNORECASE):
        found_pattern = pat
        print(f"  ✓ section 10 anchor matched: {pat}")
        break

if not found_pattern:
    print("  ✗ FAIL: no section 10 anchor found")
    print("  Methodology may not have section 10 yet, or structure differs.")
    print("  Available <h2> tags:")
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', c, re.IGNORECASE | re.DOTALL)
    for h2 in h2_matches[:15]:
        print(f"    - {h2.strip()[:80]}")
    sys.exit(1)

print("\n▸ Pre-flight passed\n")


# ══════════════════════════════════════════════════════════════════════════
# Backup
# ══════════════════════════════════════════════════════════════════════════
backup = METHOD.with_suffix('.html.pre-section10-v022-36-update.bak')
shutil.copy(METHOD, backup)
print(f"▸ Backup: {backup}\n")


# ══════════════════════════════════════════════════════════════════════════
# Section 10 update content
# ══════════════════════════════════════════════════════════════════════════
new_section_content = '''
<div style="background:#0f2417;border-left:3px solid #4ade80;padding:14px 18px;margin:14px 0;border-radius:0 6px 6px 0;color:#bbf7d0">
<div style="font-size:11px;color:#86efac;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-bottom:6px">V022.36-V5.2 · MAY 27, 2026 · BATTERY VALIDATED 110/110</div>
<p style="margin:0;font-size:14px;line-height:1.65"><b>The V5 algorithm is a two-layer hybrid system:</b> a prompt-driven synthesis layer evaluates evidence; a deterministic post-synthesis correction layer applies bright-line rules where LLM variance is unacceptable. Audit trail in <code style="background:#000;padding:2px 6px;border-radius:3px;color:#a5f3fc">composite_v022_31.v5_corrections[]</code> shows every adjustment with rule, raw value, corrected value, and reason.</p>
</div>

<h3>10.1 · Layer 1 · Synthesis (prompt-driven)</h3>
<p>Sonnet 4.5 evaluates the athlete against 8 facets with cross-sport theoretical 10 anchors, 4 phenom criteria, 8 anti-inflation signals, and default-low principle. The synthesis output includes a raw composite score and per-facet breakdown. <b>10 is the only ceiling.</b> No mathematical caps applied at this layer — Sonnet scores based purely on evidence rigor.</p>

<p>Key prompt sections retained from V5 v2:</p>
<ul>
<li><b>ANTI-CONTAMINATION</b> — reasoning instructions for Jr/Sr/family-lineage cases (named examples like "Kate Harpring → score the HS daughter, NOT Matt Harpring NBA father")</li>
<li><b>CRITICAL 9.7+ RESERVED</b> — imperative upper-bound rules ("NO active player exceeds 9.6")</li>
<li><b>PHENOM CRITERIA</b> — 4 reqs locked (national-best, pro corroboration, multi-year, cross-context)</li>
<li><b>DEFAULT-LOW PRINCIPLE</b> — when uncertain, score lower; V5 inverts V4's hype-default</li>
</ul>

<p><b>Removed in V5 v2.2:</b> HARD NUMERIC ANCHORS section (athletes listed with specific score ranges). This caused peer-association bias — Saniyah Hall scored 9.0 in V5 v2.1 because her anchor entry appeared alongside Caitlin Clark and Steph Curry, leading Sonnet to associate her with their bands.</p>

<h3>10.2 · Layer 2 · Deterministic post-synthesis correction</h3>
<p>After synthesis returns raw composite, a JavaScript function <code>_v5_apply_corrections</code> applies 6 bright-line rules. Each rule is conditional on identity, career stage, and tier signals. Audit metadata records every rule that fires.</p>

<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;background:#0a0a0a;border:1px solid #262626;border-radius:6px;overflow:hidden">
<thead><tr style="background:#1a1a1a">
<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Rule</th>
<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Trigger</th>
<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Action</th>
</tr></thead>
<tbody>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R1</b></td><td style="padding:7px 10px;border-top:1px solid #262626">Jr/Sr/II/III/IV suffix (regex) + amateur tier</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 5.5 (HS) or 7.4 (D1)</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R2</b></td><td style="padding:7px 10px;border-top:1px solid #262626">HS + prep_amateur + no phenom flag</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 5.4</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R3</b></td><td style="padding:7px 10px;border-top:1px solid #262626">D1 + college_amateur + no phenom flag</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 7.4</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R4</b></td><td style="padding:7px 10px;border-top:1px solid #262626">Active career stage (rookie/early/prime/late_pro)</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 9.3</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R5</b></td><td style="padding:7px 10px;border-top:1px solid #262626">Rookie career stage</td><td style="padding:7px 10px;border-top:1px solid #262626">composite ≤ 7.5</td></tr>
<tr><td style="padding:7px 10px;border-top:1px solid #262626"><b>R6</b></td><td style="padding:7px 10px;border-top:1px solid #262626">HS tier + pro stage (classification mismatch)</td><td style="padding:7px 10px;border-top:1px solid #262626">flag identity-review-needed (no correction)</td></tr>
</tbody>
</table>

<p><b>Different from V4 caps:</b> rules are conditional (only fire when identity/stage/tier indicates algorithm error), auditable (every correction has rule + from + to + reason), raw-preserving (synthesis output kept in metadata), and derived from design doc rules — not arbitrary tier numbers.</p>

<h3>10.3 · Audit trail metadata</h3>
<p>Every verdict response includes <code>composite_v022_31</code> with full audit:</p>
<pre style="background:#000;border:1px solid #262626;padding:14px;border-radius:6px;overflow-x:auto;font-size:12.5px;line-height:1.55;color:#a5f3fc">{
  "composite": 5.4,
  "composite_v022_31": {
    "raw": 9.83,
    "capped_legacy": 5.4,
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
<p>Battery validated against 110 athletes across 11 buckets (60 HS / 17 D1 / 13 D2 / 10 D3 / 3 JUCO / 7 pro regression+collision):</p>
<ul>
<li><b>100% rule compliance</b> on the amateur moat case (HS+D1+D2+D3)</li>
<li><b>Jr/Sr suffix athletes</b> deterministically bounded — Jordan Smith Jr 9.83 → 5.4, Carlos Medlock Jr 9.0 → 5.4, Eric Booth Jr 7.5 → 5.4</li>
<li><b>Top D1 amateurs</b> at evidence ceiling — Boozer 9.1 → 7.4, Dybantsa 9.3 → 7.4, JT Toppin 8.7 → 7.4</li>
<li><b>Active pros</b> at active ceiling — Cooper Flagg 9.71 → 9.3</li>
<li><b>Tim Duncan retired</b> passes through unchanged at 9.3 (no rule applies)</li>
<li><b>Under-cap variance preserved</b> — Kate Harpring 4.0, Manuella Fernandez 4.0, Jamarion Vincent 5.3, Anthony Brown Jr 6.2</li>
</ul>

<h3>10.5 · Design lessons from iteration</h3>
<p>Three iterations to reach the architecture. Each iteration informed the next.</p>
<ul>
<li><b>V5 v1</b> (rolled back) — caps off, evidence rigor weak. Every HS scored 9.6-9.8. Pure prompt iteration without evidence rigor is naive.</li>
<li><b>V5 v2</b> — added cross-sport anchors, phenom criteria, anti-inflation. Clean cases worked. Contaminated cases (Jr suffix, family lineage) inflated.</li>
<li><b>V5 v2.1</b> — added HARD NUMERIC ANCHORS list. Backfired: Saniyah Hall 3.5 → 9.0 from peer-association bias. <b>Named-entity lists in prompts amplify variance.</b></li>
<li><b>V5 v2.2 + v2.3</b> — rolled back the anchor list, added deterministic post-processor. 100% compliance on moat case. <b>Hybrid prompt+code is the architecture.</b></li>
</ul>

<p><b>Generalizable insight:</b> For any LLM-scored system requiring bright-line behavior, hybrid architecture wins. Use prompts for evidence reasoning (LLM strength). Use code for identity/pattern detection (deterministic). Preserve raw output in audit metadata for transparency.</p>
'''


# ══════════════════════════════════════════════════════════════════════════
# Find section 10 to update — multiple strategies
# ══════════════════════════════════════════════════════════════════════════
print("▸ Attempting insertion\n")

# Strategy 1: find existing section 10 V5 Algorithm and replace its body
m = re.search(r'(<h2[^>]*>\s*10\.\s*V5\s*Algorithm[^<]*</h2>)([\s\S]*?)(?=<h2|<section|<div\s+class="footer"|</body>)', c, re.IGNORECASE)
if m:
    old_block = m.group(0)
    new_block = m.group(1) + new_section_content
    c = c.replace(old_block, new_block, 1)
    print(f"  ✓ replaced existing section 10 body")
else:
    # Strategy 2: insert section 10 before </body> or before footer
    section_10 = f'\n<section id="section-10-v5"><h2>10. V5 Algorithm</h2>{new_section_content}</section>\n'

    # Try multiple footer-ish anchors
    inserted = False
    for anchor in ['<div class="footer">', '<footer>', '</body>']:
        if anchor in c:
            c = c.replace(anchor, section_10 + anchor, 1)
            print(f"  ✓ inserted new section 10 before {anchor}")
            inserted = True
            break

    if not inserted:
        print("  ✗ FAIL: no insertion anchor found")
        print(f"  Restore: cp {backup} {METHOD}")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════════
METHOD.write_text(c)
new_bytes = METHOD.stat().st_size
delta = new_bytes - orig_bytes
print(f"\n▸ {METHOD} · {new_bytes:,} bytes (delta +{delta:,})\n")


# ══════════════════════════════════════════════════════════════════════════
# VERIFY
# ══════════════════════════════════════════════════════════════════════════
print("▸ Post-patch verification\n")
checks = [
    ('V5 v2.2+v2.3 marker', 'V5 v2.2+v2.3' in c or 'V022.36-V5.2' in c),
    ('Six bright-line rules table', 'suffix-amateur-ceiling' in c),
    ('Audit trail metadata example', 'v5_corrections' in c),
    ('Cooper Flagg in validation', 'Cooper Flagg' in c),
    ('Jordan Smith Jr in validation', 'Jordan Smith Jr' in c),
    ('Architecture narrative', 'Hybrid prompt+code' in c or 'two-layer hybrid' in c),
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
print(f" {METHOD} · {orig_bytes:,} → {new_bytes:,} bytes (+{delta:,})")
print(f" backup: {backup}")
print(f"")
print(f" NEXT: ./fc-deploy-dev.sh")
print(f"       open https://fieldcheck-dev--fieldcheck-app.netlify.app/methodology")
print(f"       (or whatever the methodology URL is)")
