#!/usr/bin/env python3
# FCBase89 battery gates - compares baseline (prod) vs candidate (dev finepass) battery outputs.
# Usage: python3 fc-gate-FCBase89.py baseline.json candidate.json
# Schema-tolerant: accepts list of objects or dict; finds name via name/player/athlete, composite via composite/score/fc_pred.
import json, sys

def load(path):
    d = json.load(open(path))
    items = d if isinstance(d, list) else d.get('results') or d.get('athletes') or d.get('battery') or list(d.values())
    out = {}
    for it in items:
        if not isinstance(it, dict): continue
        nm = it.get('name') or it.get('player') or it.get('athlete')
        cp = it.get('composite', it.get('score', it.get('fc_pred')))
        try: cp = float(cp)
        except: continue
        if nm and cp > 0: out[str(nm).strip().lower()] = cp
    return out

def tier(c):
    if c >= 9.5: return 'ICON'
    if c >= 9.0: return 'ELITE+'
    if c >= 7.5: return 'ELITE'
    if c >= 7.0: return 'STAR'
    if c >= 5.5: return 'PROSPECT'
    if c >= 3.5: return 'SCOUT'
    return 'DEV'

KNEES = [5.2, 5.3, 6.6, 7.2, 7.3, 9.1]   # band knees across rules (R2,R1hs,R3b,R3,R5,R4)
LOWEST_KNEE = 5.2

def main():
    base, cand = load(sys.argv[1]), load(sys.argv[2])
    common = sorted(set(base) & set(cand))
    print('athletes compared:', len(common), '(baseline %d / candidate %d)' % (len(base), len(cand)))
    if len(common) < min(len(base), len(cand)) * 0.9:
        print('WARN: >10% name mismatch between files - check runs cover same roster')
    movers, fails = [], []

    for n in common:
        b, c = base[n], cand[n]
        if abs(b - c) >= 0.005:
            movers.append((n, b, c, round(c - b, 2)))
            if b < LOWEST_KNEE - 1e-9:
                fails.append('G1 FAIL: %s moved (%.2f -> %.2f) but baseline below lowest knee %.1f' % (n, b, c, LOWEST_KNEE))

    # G2: global monotonicity - candidate ordering must respect baseline ordering
    pairs_checked = inversions = 0
    arr = sorted([(base[n], cand[n], n) for n in common])
    for i in range(len(arr) - 1):
        b1, c1, n1 = arr[i]; b2, c2, n2 = arr[i + 1]
        if b2 - b1 > 0.005:
            pairs_checked += 1
            if c1 - c2 > 0.005:
                inversions += 1
                fails.append('G2 FAIL: ordering inversion %s(%.2f->%.2f) vs %s(%.2f->%.2f)' % (n1, b1, c1, n2, b2, c2))

    # G3: tier crossings
    crossings = [(n, base[n], cand[n], tier(base[n]), tier(cand[n])) for n in common if tier(base[n]) != tier(cand[n])]
    for n, b, c, tb, tc in crossings:
        near = any(abs(b - k) <= 0.25 or abs(b - (k + 0.2)) <= 0.25 for k in KNEES)
        line = 'G3 %s: %s %.2f(%s) -> %.2f(%s)' % ('REVIEW' if near else 'FAIL', n, b, tb, c, tc)
        if not near: fails.append(line)
        else: print('  ' + line)

    print('')
    print('movers: %d | ordering pairs checked: %d | inversions: %d | tier crossings: %d' % (len(movers), pairs_checked, inversions, len(crossings)))
    for m in sorted(movers, key=lambda x: x[3])[:30]:
        print('  MOVE  %-28s %.2f -> %.2f (%+.2f)' % m)
    print('')
    if fails:
        print('===== GATE RESULT: FAIL (%d) =====' % len(fails))
        for f in fails: print('  ' + f)
        sys.exit(1)
    print('===== GATE RESULT: ALL GATES PASS - cleared for prod =====')

main()
