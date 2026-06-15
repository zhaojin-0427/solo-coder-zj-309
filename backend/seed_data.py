import requests
import random
from datetime import date, timedelta

BASE = "http://localhost:9352/api"

print("开始创建示例数据...")

zone_ids = []
zones = [
    {"name": "抽屉A层", "description": "日常文胸", "capacity": 12},
    {"name": "抽屉B层", "description": "内裤专区", "capacity": 20},
    {"name": "衣柜左格", "description": "睡衣保暖衣", "capacity": 8},
    {"name": "运动收纳袋", "description": "运动内衣", "capacity": 6},
]
for z in zones:
    try:
        r = requests.post(f"{BASE}/storage-zones", json=z, timeout=5)
        if r.status_code == 200:
            zone_ids.append(r.json()["id"])
            print(f"  + 分区: {r.json()['name']}")
        else:
            print(f"  分区错误 {r.status_code}: {r.text[:50]}")
    except Exception as e:
        print(f"  分区异常: {e}")

print(f"创建了 {len(zone_ids)} 个分区")

garment_ids = []
garments = [
    {"name": "粉色蕾丝文胸", "category": "文胸", "size": "75B", "color": "粉色", "fabric": "蕾丝", "offset_days": 200, "zone_idx": 0, "brand": "爱慕", "price": 299.0},
    {"name": "黑色无痕文胸", "category": "文胸", "size": "75B", "color": "黑色", "fabric": "锦纶", "offset_days": 150, "zone_idx": 0, "brand": "优衣库", "price": 149.0},
    {"name": "纯棉白色内裤", "category": "内裤", "size": "M", "color": "白色", "fabric": "纯棉", "offset_days": 90, "zone_idx": 1, "brand": "无印良品", "price": 59.0},
    {"name": "真丝睡裙", "category": "睡衣", "size": "L", "color": "米色", "fabric": "真丝", "offset_days": 365, "zone_idx": 2, "brand": "丝绸博物馆", "price": 599.0},
    {"name": "莫代尔保暖上衣", "category": "保暖内衣", "size": "L", "color": "肤色", "fabric": "莫代尔", "offset_days": 180, "zone_idx": 2, "brand": "蕉内", "price": 199.0},
    {"name": "高强度运动内衣", "category": "运动内衣", "size": "M", "color": "黑色", "fabric": "氨纶", "offset_days": 100, "zone_idx": 3, "brand": "Lululemon", "price": 450.0},
    {"name": "竹纤维三角裤", "category": "内裤", "size": "M", "color": "绿色", "fabric": "竹纤维", "offset_days": 60, "zone_idx": 1, "brand": "蕉内", "price": 79.0},
    {"name": "塑身连体衣", "category": "塑身衣", "size": "M", "color": "肤色", "fabric": "氨纶", "offset_days": 250, "zone_idx": 0, "brand": "婷美", "price": 399.0},
]

for g in garments:
    zone_id = zone_ids[g["zone_idx"]] if g["zone_idx"] < len(zone_ids) else None
    garment_data = {
        "name": g["name"],
        "category": g["category"],
        "size": g["size"],
        "color": g["color"],
        "fabric": g["fabric"],
        "purchase_date": (date.today() - timedelta(days=g["offset_days"])).isoformat(),
        "storage_zone_id": zone_id,
        "brand": g.get("brand", ""),
        "price": g.get("price", 0),
        "notes": ""
    }
    try:
        r = requests.post(f"{BASE}/garments", json=garment_data, timeout=5)
        if r.status_code == 200:
            garment_ids.append(r.json()["id"])
            print(f"  + 衣物: {r.json()['name']}")
        else:
            print(f"  衣物错误 {r.status_code}: {r.text[:80]}")
    except Exception as e:
        print(f"  衣物异常: {e}")

print(f"创建了 {len(garment_ids)} 件衣物，开始添加记录...")

def_levels = ["无", "无", "无", "无", "无", "轻微", "轻微", "中度"]
wash_methods = ["手洗", "手洗", "手洗", "手洗", "机洗", "机洗"]
detergents = ["蓝月亮洗衣液", "中性洗衣液", "专用丝绸洗涤剂", "羊毛专用"]

for gid in garment_ids:
    use_count = random.randint(5, 25)
    for _ in range(use_count):
        wear_date = date.today() - timedelta(days=random.randint(1, 200))
        wear_data = {
            "garment_id": gid,
            "wear_date": wear_date.isoformat(),
            "duration_hours": random.randint(4, 16),
            "deformation_noticed": random.choice(def_levels),
            "notes": ""
        }
        try:
            requests.post(f"{BASE}/wear-records", json=wear_data, timeout=2)
        except:
            pass

    wash_count = random.randint(2, 10)
    for _ in range(wash_count):
        wash_date = date.today() - timedelta(days=random.randint(1, 180))
        wash_data = {
            "garment_id": gid,
            "wash_date": wash_date.isoformat(),
            "wash_method": random.choice(wash_methods),
            "detergent": random.choice(detergents),
            "deformation_after": random.choice(def_levels),
            "notes": ""
        }
        try:
            requests.post(f"{BASE}/wash-records", json=wash_data, timeout=2)
        except:
            pass

print("记录添加完成！正在验证...")

try:
    r = requests.get(f"{BASE}/statistics", timeout=5)
    if r.status_code == 200:
        s = r.json()
        print(f"总衣物: {s['total_garments']}")
        print(f"总洗护: {s['total_washes']}")
        print(f"面料统计: {[f['fabric']+str(f['count']) for f in s['fabric_stats']]}")
        print(f"闲置衣物: {len(s['idle_garments'])} 件")
    else:
        print(f"统计API错误: {r.status_code}")
except Exception as e:
    print(f"统计异常: {e}")

try:
    r = requests.get(f"{BASE}/replacement-reminders", timeout=5)
    if r.status_code == 200:
        print(f"更换提醒: {len(r.json())} 条")
except:
    pass

print("\n✅ 示例数据创建完成！")
