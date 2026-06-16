import sys
sys.path.insert(0, '/Users/aj/Downloads/AI/0612/309/backend')

import json
import urllib.request
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Get raw API response first
resp = urllib.request.urlopen('http://localhost:8000/api/trip-plans/1')
raw_data = json.loads(resp.read().decode())
print('Raw response keys:', sorted(raw_data.keys()))
print()

# Now test with actual pydantic imports
try:
    import schemas
    print('=== Testing Pydantic TripPlanDetail validation ===')
    
    # Test 1: model_validate
    try:
        validated = schemas.TripPlanDetail.model_validate(raw_data)
        print('✅ model_validate succeeded')
        print('  name:', validated.name)
        print('  items count:', len(validated.items))
        print('  day_outfit_plans count:', len(validated.day_outfit_plans))
        print('  storage_pickup_paths count:', len(validated.storage_pickup_paths))
    except Exception as e:
        print('❌ model_validate FAILED:', e)
        import traceback
        traceback.print_exc()

    print()
    
    # Test 2: check what happens with item.garment fields
    if raw_data.get('items'):
        g = raw_data['items'][0]['garment']
        print('Garment fields (raw):')
        for k in sorted(g.keys()):
            v = g[k]
            t = type(v).__name__
            preview = repr(v)[:60] if not isinstance(v, (dict, list)) else (f'{type(v).__name__}(len={len(v)})')
            print(f'  {k}: {t} = {preview}')
        
        print()
        print('Testing Garment pydantic validation:')
        try:
            g_valid = schemas.Garment.model_validate(g)
            print('✅ Garment pydantic OK')
        except Exception as e:
            print(f'❌ Garment FAILED: {e}')
    
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
