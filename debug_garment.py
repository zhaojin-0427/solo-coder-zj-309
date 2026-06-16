import json
import urllib.request

# Find garment id for 黑色无痕文胸
resp = urllib.request.urlopen('http://localhost:8000/api/garments')
garments = json.loads(resp.read().decode())
for g in garments:
    print(f"id={g['id']} name={g['name']} cat={g['category']}")
target_id = next((g['id'] for g in garments if '黑色' in g['name'] or '无痕' in g['name']), None)

if target_id:
    print(f"\n=== /api/garments/{target_id} ===")
    resp1 = urllib.request.urlopen(f'http://localhost:8000/api/garments/{target_id}')
    d1 = json.loads(resp1.read().decode())
    for k in sorted(d1.keys()):
        print(f"  {k}: {type(d1[k]).__name__}" + (f" = {repr(d1[k])[:60]}" if not isinstance(d1[k], (list, dict)) else ""))
    print(f"  has trip_occupancy: {'trip_occupancy' in d1}")

    print(f"\n=== /api/garments/{target_id}/detail ===")
    resp2 = urllib.request.urlopen(f'http://localhost:8000/api/garments/{target_id}/detail')
    d2 = json.loads(resp2.read().decode())
    for k in sorted(d2.keys()):
        v = d2[k]
        if isinstance(v, list):
            print(f"  {k}: list(len={len(v)})")
        elif isinstance(v, dict):
            print(f"  {k}: dict(keys={sorted(v.keys())[:5]})")
        else:
            print(f"  {k}: {type(v).__name__} = {repr(v)[:60]}")
    print(f"\n  trip_occupancy = {json.dumps(d2.get('trip_occupancy'), ensure_ascii=False)}")
