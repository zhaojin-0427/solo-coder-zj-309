from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date, datetime, timedelta
from collections import defaultdict

from database import SessionLocal, engine, Base
from models import (
    StorageZone, Garment, WashRecord, WearRecord,
    CategoryEnum, FabricEnum, WashMethodEnum, DeformationEnum,
    FABRIC_CARE_RULES
)
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="内衣收纳与洗护周期管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_care_advice(fabric: FabricEnum) -> dict:
    return FABRIC_CARE_RULES.get(fabric, FABRIC_CARE_RULES[FabricEnum.OTHER])


def calculate_replacement_status(garment: Garment, db: Optional[Session] = None) -> dict:
    care_rules = get_care_advice(garment.fabric)
    recommended_uses = care_rules["recommended_uses"]
    replacement_months = care_rules["replacement_months"]

    today = date.today()
    use_ratio = garment.use_count / recommended_uses if recommended_uses > 0 else 0

    purchase_days = (today - garment.purchase_date).days
    months_owned = purchase_days / 30.44
    time_ratio = months_owned / replacement_months if replacement_months > 0 else 0

    actual_deformation = garment.current_deformation
    if db is not None:
        latest_wear = (
            db.query(WearRecord)
            .filter(WearRecord.garment_id == garment.id)
            .order_by(WearRecord.wear_date.desc(), WearRecord.created_at.desc())
            .first()
        )
        latest_wash = (
            db.query(WashRecord)
            .filter(WashRecord.garment_id == garment.id)
            .order_by(WashRecord.wash_date.desc(), WashRecord.created_at.desc())
            .first()
        )
        candidates = []
        if latest_wear:
            candidates.append((latest_wear.wear_date, latest_wear.deformation_noticed, "wear"))
        if latest_wash:
            candidates.append((latest_wash.wash_date, latest_wash.deformation_after, "wash"))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            actual_deformation = candidates[0][1]

    deformation_score = {
        DeformationEnum.NONE: 0,
        DeformationEnum.SLIGHT: 0.3,
        DeformationEnum.MODERATE: 0.6,
        DeformationEnum.SEVERE: 1.0,
    }.get(actual_deformation, 0)

    overall_score = max(use_ratio, time_ratio) + deformation_score * 0.5

    if overall_score >= 1.2 or actual_deformation == DeformationEnum.SEVERE:
        urgency = "立即更换"
    elif overall_score >= 0.9:
        urgency = "建议更换"
    elif overall_score >= 0.7:
        urgency = "注意观察"
    else:
        urgency = "状态良好"

    days_remaining = max(0, int((replacement_months * 30.44) - purchase_days))
    uses_remaining = max(0, recommended_uses - garment.use_count)

    reasons = []
    if use_ratio >= 0.9:
        reasons.append(f"使用次数已达推荐值的 {int(use_ratio * 100)}%（{garment.use_count}/{recommended_uses}次）")
    if time_ratio >= 0.9:
        reasons.append(f"已使用 {months_owned:.1f} 个月，接近推荐更换周期 {replacement_months} 个月")
    if deformation_score >= 0.3:
        reasons.append(f"存在{actual_deformation.value}变形")
    if not reasons:
        reasons.append("状态正常，继续使用")

    return {
        "urgency": urgency,
        "overall_score": round(overall_score, 2),
        "use_ratio": round(use_ratio, 2),
        "time_ratio": round(time_ratio, 2),
        "deformation_score": deformation_score,
        "days_remaining": days_remaining,
        "uses_remaining": uses_remaining,
        "recommended_uses": recommended_uses,
        "replacement_months": replacement_months,
        "reasons": reasons,
    }


def garment_to_schema(garment: Garment, db: Optional[Session] = None) -> schemas.Garment:
    garment_dict = {c.name: getattr(garment, c.name) for c in garment.__table__.columns}
    garment_dict["storage_zone"] = garment.storage_zone
    garment_dict["care_advice"] = get_care_advice(garment.fabric)
    garment_dict["replacement_status"] = calculate_replacement_status(garment, db)
    return schemas.Garment.model_validate(garment_dict)


@app.get("/")
def root():
    return {"message": "内衣收纳与洗护周期管理平台 API", "version": "1.0.0"}


@app.get("/api/care-advice/{fabric}", response_model=schemas.FabricCareAdvice)
def get_fabric_care_advice(fabric: FabricEnum):
    advice = get_care_advice(fabric)
    return {"fabric": fabric, **advice}


@app.get("/api/care-advice", response_model=List[schemas.FabricCareAdvice])
def get_all_care_advice():
    return [{"fabric": f, **get_care_advice(f)} for f in FabricEnum]


@app.post("/api/storage-zones", response_model=schemas.StorageZone)
def create_storage_zone(zone: schemas.StorageZoneCreate, db: Session = Depends(get_db)):
    existing = db.query(StorageZone).filter(StorageZone.name == zone.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="收纳分区名称已存在")
    db_zone = StorageZone(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    current_count = db.query(Garment).filter(Garment.storage_zone_id == db_zone.id).count()
    zone_dict = {c.name: getattr(db_zone, c.name) for c in db_zone.__table__.columns}
    zone_dict["current_count"] = current_count
    return schemas.StorageZone.model_validate(zone_dict)


@app.get("/api/storage-zones", response_model=List[schemas.StorageZone])
def list_storage_zones(db: Session = Depends(get_db)):
    zones = db.query(StorageZone).order_by(StorageZone.created_at.desc()).all()
    result = []
    for zone in zones:
        current_count = db.query(Garment).filter(Garment.storage_zone_id == zone.id).count()
        zone_dict = {c.name: getattr(zone, c.name) for c in zone.__table__.columns}
        zone_dict["current_count"] = current_count
        result.append(schemas.StorageZone.model_validate(zone_dict))
    return result


@app.get("/api/storage-zones/{zone_id}", response_model=schemas.StorageZone)
def get_storage_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(StorageZone).filter(StorageZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="收纳分区不存在")
    current_count = db.query(Garment).filter(Garment.storage_zone_id == zone.id).count()
    zone_dict = {c.name: getattr(zone, c.name) for c in zone.__table__.columns}
    zone_dict["current_count"] = current_count
    return schemas.StorageZone.model_validate(zone_dict)


@app.put("/api/storage-zones/{zone_id}", response_model=schemas.StorageZone)
def update_storage_zone(zone_id: int, zone_data: schemas.StorageZoneUpdate, db: Session = Depends(get_db)):
    zone = db.query(StorageZone).filter(StorageZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="收纳分区不存在")
    update_data = zone_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(zone, key, value)
    db.commit()
    db.refresh(zone)
    current_count = db.query(Garment).filter(Garment.storage_zone_id == zone.id).count()
    zone_dict = {c.name: getattr(zone, c.name) for c in zone.__table__.columns}
    zone_dict["current_count"] = current_count
    return schemas.StorageZone.model_validate(zone_dict)


@app.delete("/api/storage-zones/{zone_id}")
def delete_storage_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(StorageZone).filter(StorageZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="收纳分区不存在")
    garments = db.query(Garment).filter(Garment.storage_zone_id == zone_id).all()
    for g in garments:
        g.storage_zone_id = None
    db.delete(zone)
    db.commit()
    return {"message": "收纳分区已删除"}


@app.post("/api/garments", response_model=schemas.Garment)
def create_garment(garment: schemas.GarmentCreate, db: Session = Depends(get_db)):
    if garment.storage_zone_id:
        zone = db.query(StorageZone).filter(StorageZone.id == garment.storage_zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail="收纳分区不存在")
    db_garment = Garment(**garment.model_dump())
    db.add(db_garment)
    db.commit()
    db.refresh(db_garment)
    db_garment = db.query(Garment).options(joinedload(Garment.storage_zone)).filter(Garment.id == db_garment.id).first()
    return garment_to_schema(db_garment, db)


@app.get("/api/garments", response_model=List[schemas.Garment])
def list_garments(
    category: Optional[CategoryEnum] = None,
    fabric: Optional[FabricEnum] = None,
    storage_zone_id: Optional[int] = None,
    is_active: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Garment).options(joinedload(Garment.storage_zone))
    if category:
        query = query.filter(Garment.category == category)
    if fabric:
        query = query.filter(Garment.fabric == fabric)
    if storage_zone_id is not None:
        query = query.filter(Garment.storage_zone_id == storage_zone_id)
    if is_active is not None:
        query = query.filter(Garment.is_active == is_active)
    garments = query.order_by(Garment.created_at.desc()).all()
    return [garment_to_schema(g, db) for g in garments]


@app.get("/api/garments/{garment_id}", response_model=schemas.Garment)
def get_garment(garment_id: int, db: Session = Depends(get_db)):
    garment = db.query(Garment).options(joinedload(Garment.storage_zone)).filter(Garment.id == garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")
    return garment_to_schema(garment, db)


@app.put("/api/garments/{garment_id}", response_model=schemas.Garment)
def update_garment(garment_id: int, garment_data: schemas.GarmentUpdate, db: Session = Depends(get_db)):
    garment = db.query(Garment).filter(Garment.id == garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")
    update_data = garment_data.model_dump(exclude_unset=True)
    if "storage_zone_id" in update_data and update_data["storage_zone_id"]:
        zone = db.query(StorageZone).filter(StorageZone.id == update_data["storage_zone_id"]).first()
        if not zone:
            raise HTTPException(status_code=404, detail="收纳分区不存在")
    for key, value in update_data.items():
        setattr(garment, key, value)
    db.commit()
    db.refresh(garment)
    garment = db.query(Garment).options(joinedload(Garment.storage_zone)).filter(Garment.id == garment_id).first()
    return garment_to_schema(garment, db)


@app.delete("/api/garments/{garment_id}")
def delete_garment(garment_id: int, db: Session = Depends(get_db)):
    garment = db.query(Garment).filter(Garment.id == garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")
    garment.is_active = 0
    db.commit()
    return {"message": "衣物已停用"}


@app.post("/api/wash-records", response_model=schemas.WashRecord)
def create_wash_record(record: schemas.WashRecordCreate, db: Session = Depends(get_db)):
    garment = db.query(Garment).filter(Garment.id == record.garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")
    db_record = WashRecord(**record.model_dump())
    db.add(db_record)
    garment.wash_count += 1
    garment.last_wash_date = record.wash_date
    garment.current_deformation = record.deformation_after
    db.commit()
    db.refresh(db_record)
    record_dict = {c.name: getattr(db_record, c.name) for c in db_record.__table__.columns}
    record_dict["garment_name"] = garment.name
    return schemas.WashRecord.model_validate(record_dict)


@app.get("/api/wash-records", response_model=List[schemas.WashRecord])
def list_wash_records(
    garment_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WashRecord).join(Garment)
    if garment_id:
        query = query.filter(WashRecord.garment_id == garment_id)
    if start_date:
        query = query.filter(WashRecord.wash_date >= start_date)
    if end_date:
        query = query.filter(WashRecord.wash_date <= end_date)
    records = query.order_by(WashRecord.wash_date.desc()).all()
    result = []
    for r in records:
        record_dict = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        record_dict["garment_name"] = r.garment.name
        result.append(schemas.WashRecord.model_validate(record_dict))
    return result


@app.post("/api/wear-records", response_model=schemas.WearRecord)
def create_wear_record(record: schemas.WearRecordCreate, db: Session = Depends(get_db)):
    garment = db.query(Garment).filter(Garment.id == record.garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")
    db_record = WearRecord(**record.model_dump())
    db.add(db_record)
    garment.use_count += 1
    garment.last_worn_date = record.wear_date
    garment.current_deformation = record.deformation_noticed
    db.commit()
    db.refresh(db_record)
    record_dict = {c.name: getattr(db_record, c.name) for c in db_record.__table__.columns}
    record_dict["garment_name"] = garment.name
    return schemas.WearRecord.model_validate(record_dict)


@app.get("/api/wear-records", response_model=List[schemas.WearRecord])
def list_wear_records(
    garment_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WearRecord).join(Garment)
    if garment_id:
        query = query.filter(WearRecord.garment_id == garment_id)
    if start_date:
        query = query.filter(WearRecord.wear_date >= start_date)
    if end_date:
        query = query.filter(WearRecord.wear_date <= end_date)
    records = query.order_by(WearRecord.wear_date.desc()).all()
    result = []
    for r in records:
        record_dict = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        record_dict["garment_name"] = r.garment.name
        result.append(schemas.WearRecord.model_validate(record_dict))
    return result


@app.get("/api/replacement-reminders", response_model=List[schemas.ReplacementReminder])
def get_replacement_reminders(
    urgency_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    garments = (
        db.query(Garment)
        .options(joinedload(Garment.storage_zone))
        .filter(Garment.is_active == 1)
        .all()
    )
    reminders = []
    for g in garments:
        status = calculate_replacement_status(g, db)
        if urgency_filter and status["urgency"] != urgency_filter:
            continue
        if status["urgency"] in ["立即更换", "建议更换", "注意观察"]:
            reminders.append({
                "garment": garment_to_schema(g, db),
                "reason": status["reasons"][0],
                "days_until_recommended": status["days_remaining"],
                "urgency": status["urgency"],
            })
    reminders.sort(key=lambda x: {
        "立即更换": 0,
        "建议更换": 1,
        "注意观察": 2,
    }.get(x["urgency"], 99))
    return reminders


@app.get("/api/statistics", response_model=schemas.StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    today = date.today()

    all_garments = db.query(Garment).filter(Garment.is_active == 1).all()
    total_garments = len(all_garments)

    total_washes = db.query(func.sum(Garment.wash_count)).scalar() or 0

    fabric_stats_data = defaultdict(lambda: {"count": 0, "use_counts": [], "wash_counts": [], "purchase_dates": []})
    for g in all_garments:
        fs = fabric_stats_data[g.fabric.value]
        fs["count"] += 1
        fs["use_counts"].append(g.use_count)
        fs["wash_counts"].append(g.wash_count)
        fs["purchase_dates"].append(g.purchase_date)

    fabric_stats = []
    for fabric_name, data in fabric_stats_data.items():
        avg_use_cycle = round(sum(data["use_counts"]) / len(data["use_counts"]), 1) if data["use_counts"] else 0
        avg_wash_count = round(sum(data["wash_counts"]) / len(data["wash_counts"]), 1) if data["wash_counts"] else 0
        avg_months_owned = 0
        if data["purchase_dates"]:
            total_days = sum((today - d).days for d in data["purchase_dates"])
            avg_months_owned = round(total_days / len(data["purchase_dates"]) / 30.44, 1)
        fabric_stats.append({
            "fabric": fabric_name,
            "count": data["count"],
            "avg_use_cycle": avg_use_cycle,
            "avg_wash_count": avg_wash_count,
            "avg_months_owned": avg_months_owned,
        })
    fabric_stats.sort(key=lambda x: x["count"], reverse=True)

    category_stats_data = defaultdict(lambda: {"count": 0, "total_uses": 0, "total_washes": 0, "deformation_count": 0})
    for g in all_garments:
        cs = category_stats_data[g.category.value]
        cs["count"] += 1
        cs["total_uses"] += g.use_count
        cs["total_washes"] += g.wash_count
        if g.current_deformation in [DeformationEnum.SLIGHT, DeformationEnum.MODERATE, DeformationEnum.SEVERE]:
            cs["deformation_count"] += 1

    category_stats = []
    for cat_name, data in category_stats_data.items():
        category_stats.append({
            "category": cat_name,
            "count": data["count"],
            "avg_uses": round(data["total_uses"] / data["count"], 1) if data["count"] else 0,
            "avg_washes": round(data["total_washes"] / data["count"], 1) if data["count"] else 0,
        })
    category_stats.sort(key=lambda x: x["count"], reverse=True)

    deformation_risk = []
    for cat_name, data in category_stats_data.items():
        rate = round(data["deformation_count"] / data["count"] * 100, 1) if data["count"] else 0
        deformation_risk.append({
            "category": cat_name,
            "total_count": data["count"],
            "deformation_count": data["deformation_count"],
            "deformation_rate": rate,
        })
    deformation_risk.sort(key=lambda x: x["deformation_rate"], reverse=True)

    idle_threshold_days = 60
    idle_garments = []
    for g in all_garments:
        latest_wear = (
            db.query(func.max(WearRecord.wear_date))
            .filter(WearRecord.garment_id == g.id)
            .scalar()
        )
        latest_wash = (
            db.query(func.max(WashRecord.wash_date))
            .filter(WashRecord.garment_id == g.id)
            .scalar()
        )
        candidate_dates = [g.purchase_date]
        if latest_wear:
            candidate_dates.append(latest_wear)
        if latest_wash:
            candidate_dates.append(latest_wash)
        last_active = max(candidate_dates)
        idle_days = (today - last_active).days
        if idle_days >= idle_threshold_days:
            idle_garments.append({
                "id": g.id,
                "name": g.name,
                "category": g.category.value,
                "idle_days": idle_days,
                "use_count": g.use_count,
                "last_worn_date": latest_wear.isoformat() if latest_wear else None,
                "last_active_date": last_active.isoformat(),
            })
    idle_garments.sort(key=lambda x: x["idle_days"], reverse=True)

    wash_frequency_stats = []
    for g in all_garments:
        if g.use_count >= 5 and g.wash_count > 0:
            freq = round(g.use_count / g.wash_count, 1)
            wash_frequency_stats.append({
                "id": g.id,
                "name": g.name,
                "category": g.category.value,
                "uses_per_wash": freq,
                "use_count": g.use_count,
                "wash_count": g.wash_count,
            })
    wash_frequency_stats.sort(key=lambda x: x["uses_per_wash"], reverse=True)

    monthly_wash_data = defaultdict(lambda: defaultdict(int))
    all_wash_records = db.query(WashRecord).all()
    for wr in all_wash_records:
        key = wr.wash_date.strftime("%Y-%m")
        monthly_wash_data[key]["total"] += 1
        if wr.deformation_after != DeformationEnum.NONE:
            monthly_wash_data[key]["with_deformation"] += 1

    monthly_wash_trend = []
    for month in sorted(monthly_wash_data.keys()):
        data = monthly_wash_data[month]
        monthly_wash_trend.append({
            "month": month,
            "total_washes": data["total"],
            "washes_with_deformation": data["with_deformation"],
        })
    monthly_wash_trend = monthly_wash_trend[-12:]

    return {
        "total_garments": total_garments,
        "total_washes": total_washes,
        "fabric_stats": fabric_stats,
        "category_stats": category_stats,
        "deformation_risk_categories": deformation_risk,
        "idle_garments": idle_garments,
        "wash_frequency_stats": wash_frequency_stats[:20],
        "monthly_wash_trend": monthly_wash_trend,
    }


@app.get("/api/enums")
def get_enums():
    return {
        "categories": [{"value": e.value, "name": e.name} for e in CategoryEnum],
        "fabrics": [{"value": e.value, "name": e.name} for e in FabricEnum],
        "wash_methods": [{"value": e.value, "name": e.name} for e in WashMethodEnum],
        "deformation_levels": [{"value": e.value, "name": e.name} for e in DeformationEnum],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9352)
