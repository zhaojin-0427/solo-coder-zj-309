import json
import urllib.request

resp = urllib.request.urlopen('http://localhost:8000/api/trip-plans/1')
data = json.loads(resp.read().decode())

print('=== available_replacements 类型 ===')
print('Type:', type(data['available_replacements']))
print('Value:', json.dumps(data['available_replacements'], ensure_ascii=False)[:500])
print()

print('=== day_outfit_plans[0] 类型 ===')
dop0 = data['day_outfit_plans'][0]
print('Type:', type(dop0))
if isinstance(dop0, str):
    print('String value (first 500):', repr(dop0)[:500])
    try:
        parsed = json.loads(dop0)
        print('Parsed type:', type(parsed))
        if isinstance(parsed, dict):
            print('Parsed keys:', list(parsed.keys()))
        elif isinstance(parsed, list):
            print('Parsed len:', len(parsed))
    except Exception as e:
        print('Parse error:', e)
elif isinstance(dop0, dict):
    print('Keys:', list(dop0.keys()))
print()

print('=== storage_pickup_paths[0] 类型 ===')
spp0 = data['storage_pickup_paths'][0]
print('Type:', type(spp0))
if isinstance(spp0, str):
    print('String value (first 500):', repr(spp0)[:500])
    try:
        parsed = json.loads(spp0)
        print('Parsed type:', type(parsed))
        if isinstance(parsed, dict):
            print('Parsed keys:', list(parsed.keys()))
        elif isinstance(parsed, list):
            print('Parsed len:', len(parsed))
    except Exception as e:
        print('Parse error:', e)
elif isinstance(spp0, dict):
    print('Keys:', list(spp0.keys()))
print()

# Check list API for status
resp2 = urllib.request.urlopen('http://localhost:8000/api/trip-plans')
list_data = json.loads(resp2.read().decode())
print('=== trip list statuses ===')
for p in list_data:
    print(f"  id={p['id']} name={p['name']} status={p['status']} start={p['start_date']} end={p['end_date']}")
