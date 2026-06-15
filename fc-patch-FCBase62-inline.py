#!/usr/bin/env python3
"""FCBase62 inline patcher . footer link backfill (5 pages)"""
import gzip, base64, os, subprocess, sys, tempfile

PATCH_B64 = """
H4sIAFd/KGoC/+VVwW7TQBC9+ysG92BbcuymtBUKdaRSWoEANVLbs7XZHcerOLvu7qaJVZUjH8DP
cOdT+BLGTpumKgLEAQT45tnZ9+a9sWe2nqRza9KxVCmqK6gbV2r11PN9/+ToBbO4vwMJnGjt0EAl
1RTGjE8LWVXQAyaEhZRNULmeM0zZmhlUvAFutLW9Lt1p2ANkppIEUFOuJWhPzmptHGjrFUbPKO7K
So7hNjyiV887vTgfXZyfQda9h9ombVqCy5opMbdowuB9+lIvVKWZsEEUed4WHDNedjRQMgsMhCwK
pKIcFCsN1hmpJgm8YzXoSsCXDx9B4QJwybirmsQbHZ4fvTpuaa89oCcoJFaCl8invSs0QnKXlG5W
BQMIu4QuaaQXRCNg3MBRxeYC4fMnOCBDFPCKWZv5l3PtmA9SZH7BeyvTVrFhfxsu52id1MqmgjVQ
U6FX0kqnzUHaggyD+PdxdXAMSoNF5n+jvT6Z2FSY+VxX2gzMZMzCnd29uP9sN96Ok/3oucOl6wnk
2rCWaKC0Qn9oEcGVCDW1vHYHKRsGnagofmT0DOkzFAQ/aX7W7O8J+6F7jy7/eQtqKpK+tbaiX7Xg
b5TNNf1kxPw/aSbFdv5Pd/nG8zyBBcyYVGE06MKFNlAoNsMYQprEcTuGI5AKbidwIh3O7F12+9Q0
lO+2Qrq6uz7jdFYnBpnI2+rCaH0ii27AEzC/h+rgaBO4sAgA7FTWcN0B3kDIqhamabcS9UdEQfTg
GtfKSTXHTQKecD0nMNIRwZMM+g+ZDJMW4ayxpOh4KVvSk8PXb+8oB90mul1QHRBcbyJSTbT1kDvq
bH+znFY0J9F1xTiuTYwp6d6zZGHIyJUpfCO+Fn/6Bu4LKTY2Pa13FMTmeaQwz9uMPIcsgyDP20bm
ebCSueqq9xWkx1ZGSwgAAA==
"""

def check_files():
    home = os.path.expanduser('~/Downloads')
    files = ['fieldcheck-verdict.html', 'fieldcheck-methodology.html',
             'fieldcheck-predictions.html', 'fieldcheck-coverage.html',
             'fieldcheck-versus.html']
    missing = [f for f in files if not os.path.exists(os.path.join(home, f))]
    if missing:
        print('FAIL: missing files in ~/Downloads/: ' + ', '.join(missing))
        for f in missing:
            print(f'  cp ~/Desktop/fieldcheck-proxy/frontend/{f} ~/Downloads/')
        sys.exit(1)
    print('  All 5 files present in ~/Downloads/')

def apply(b64):
    code = gzip.decompress(base64.b64decode(b64.strip())).decode()
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
        f.write(code); tmp = f.name
    try:
        result = subprocess.run([sys.executable, tmp], capture_output=True, text=True)
        if result.stdout: print(result.stdout, end='')
        if result.stderr: print(result.stderr, end='', file=sys.stderr)
        if result.returncode != 0:
            print(f'FAIL: returned {result.returncode}'); sys.exit(1)
    finally:
        os.unlink(tmp)

def verify():
    home = os.path.expanduser('~/Downloads')
    print()
    for f in ['fieldcheck-verdict.html', 'fieldcheck-methodology.html',
              'fieldcheck-predictions.html', 'fieldcheck-coverage.html',
              'fieldcheck-versus.html']:
        c = open(os.path.join(home, f)).read()
        ok = '/agent-transparency' in c
        print(f'  {("OK" if ok else "FAIL"):<6} {f} → /agent-transparency link')

print('=== FCBase62 footer backfill ===')
check_files()
print('\n>>> Applying footer patch')
apply(PATCH_B64)
verify()
print('\n=== Done. Now run: cd ~/Desktop/fieldcheck-proxy && ./fc-ship-FCBase62.sh ===')
