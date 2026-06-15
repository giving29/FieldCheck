#!/usr/bin/env python3
"""FCBase65 inline patcher . trust page cross-linking (3 files)"""
import gzip, base64, os, subprocess, sys, tempfile

PATCH_B64 = """
H4sIAH2MKGoC/91WUU/bMBB+z684wkNbrU2ACqZ1tBJjQ2ObBBOgPUAVGefSWCR2ZDstFWJ/a+/7
ZbPTNE3WbgNpe1keGvvy3Xfn7852t7f8XEn/lnEf+RSyuY4F7zuu654cvyEKD/bBg4t5mqKWjIKW
udKQkQkClUKpXsL4HeMTg3dYmgmpQSgnkiI1IB0n7BZK87mZOs7Z1eX51eUFDIt5WyjPwjy8zwgP
c4Wy3frqvxUznggSqlan4zjnR5fH799Zl2sHzLMNux6YBLjuaUm4yohETucDIGEI/iwmWvU4zuAF
+CLXVKSo4BYjIRF0jFAuaweUJmlWMD4Uv/ZpRSzB1sC+MQlpjPSutx7Ki3WatLorL5GE1umQQCwx
Grq+QppLpufu6KIcHfpkdMMt+tDQcBN9nuDQTYmcMN5LMNJmAbkWr+u8ZhnP4K1QlQbu6IsZ3rQU
mMkm5FIgd3RWjp6eZ5HmY7esyZ4HVdiyFL9Rv/9k9SvSP4u+Xih3dGRtULf9nUI8O9Y/kLzvgdmV
sQhFIiZl//drO1SBFhAJoVFCeyH8/kEPJVkai0CdJxShFuZXZTix6GOLhtPP8P1bPTWY7novrS3P
QqIxhA85R3gFezt7B9a8EscdxUYRK0jTPsVE0KLvl6N1TCYxZFQzwY22tQkkGE5QrjtQMTViTNAd
LUeQksziNpT+v1pfE7fqSFHryCamdqTMmkdKE7dpX5CN+6Jq5rHjOCFGJjfG251BYTbnhb0/aAyM
Q3kBDKqaZOYuWF4k/gJ3vWjbcYWhBpN5EkkYaLzX7U71hUVLF1vasY1AV9wFv2RctyMXQN2xDB4a
ER6hTRLLO1/QYNhxOw13KrhmPMd6ROpRkRvSkspumnEHtoaw2wwtCVNo7lulMX13z2wWJ0enn37O
YQCGAQinsRGqYIaHjSEea7lZSaiRJEsIxQas21CkC7srp8ybmWsGFyLSmr3S6OwjrKe3OIXsnwNl
zyUMTR6OY4QIAk5SDAIYDqEVBLboQdBaiLDoAOcHCmaMWZMIAAA=
"""

def check():
    home = os.path.expanduser('~/Downloads')
    files = ['fieldcheck-agent-transparency.html', 'fieldcheck-whats-new.html', 'fieldcheck-methodology.html']
    missing = [f for f in files if not os.path.exists(os.path.join(home, f))]
    if missing:
        print('FAIL: missing in ~/Downloads/: ' + ', '.join(missing))
        for f in missing:
            print(f'  cp ~/Desktop/fieldcheck-proxy/frontend/{f} ~/Downloads/')
        sys.exit(1)
    print('  All 3 files in ~/Downloads/')

def apply():
    code = gzip.decompress(base64.b64decode(PATCH_B64.strip())).decode()
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
        f.write(code); tmp = f.name
    try:
        r = subprocess.run([sys.executable, tmp], capture_output=True, text=True)
        if r.stdout: print(r.stdout, end='')
        if r.stderr: print(r.stderr, end='', file=sys.stderr)
        if r.returncode != 0: sys.exit(1)
    finally:
        os.unlink(tmp)

print('=== FCBase65 trust page cross-linking ===')
check()
print()
apply()
print('\n=== Done. Run: cd ~/Desktop/fieldcheck-proxy && ./fc-ship-FCBase65.sh ===')
