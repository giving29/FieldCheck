import json
d = json.load(open('marquee_recuration_report.json'))

print("="*80)
print("ICON → SCOUT (HS athletes inflated to ICON):")
print("="*80)
for u in [x for x in d['updated'] if x['before']['tier']=='ICON' and x['after']['tier']=='SCOUT']:
    print(f"  {u['name']:30} {u['school']:40} {u['class_year']:12} {u['before']['composite']} → {u['after']['composite']} [{u['classification']}]")

print()
print("="*80)
print("ELITE → SCOUT (single big drop):")
print("="*80)
for u in [x for x in d['updated'] if x['before']['tier']=='ELITE' and x['after']['tier']=='SCOUT']:
    print(f"  {u['name']:30} {u['school']:40} {u['class_year']:12} {u['before']['composite']} → {u['after']['composite']} [{u['classification']}]")

print()
print("="*80)
print("UNCHANGED (38 · first 15 — retired GOATs should be here):")
print("="*80)
for u in d['unchanged'][:15]:
    print(f"  {u['name']:30} {u['composite']} {u['tier']:10} [{u['classification']}]")

print()
print("="*80)
print("FIRST 25 UPDATES:")
print("="*80)
for u in d['updated'][:25]:
    print(f"  {u['name']:30} {u['before']['composite']} {u['before']['tier']:10} → {u['after']['composite']} {u['after']['tier']:10} [{u['classification']}]")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"  Updated:   {len(d['updated'])}")
print(f"  Unchanged: {len(d['unchanged'])}")
print(f"  Transitions: {d['tier_changes']}")
