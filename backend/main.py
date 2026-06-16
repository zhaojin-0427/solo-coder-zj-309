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


def calculate_wash_plan(garment: Garment, db: Session) -> Optional[dict]:
    if not garment.is_active:
        return None

    care_rules = get_care_advice(garment.fabric)
    today = date.today()

    wears_since_last_wash = 0
    days_since_last_wash = 0

    all_wears = (
        db.query(WearRecord)
        .filter(WearRecord.garment_id == garment.id)
        .order_by(WearRecord.wear_date.desc())
        .all()
    )

    all_washes = (
        db.query(WashRecord)
        .filter(WashRecord.garment_id == garment.id)
        .order_by(WashRecord.wash_date.desc())
        .all()
    )

    last_wash_date = all_washes[0].wash_date if all_washes else garment.last_wash_date

    if last_wash_date:
        wears_after_wash = [w for w in all_wears if w.wear_date > last_wash_date]
        wears_since_last_wash = len(wears_after_wash)
        days_since_last_wash = (today - last_wash_date).days
    else:
        wears_since_last_wash = len(all_wears)
        if garment.purchase_date:
            days_since_last_wash = (today - garment.purchase_date).days
        else:
            days_since_last_wash = 0

    uses_between_wash_map = {
        CategoryEnum.BRA: 3,
        CategoryEnum.PANTY: 1,
        CategoryEnum.PAJAMAS: 7,
        CategoryEnum.SPORTS: 1,
        CategoryEnum.SHAPEWEAR: 3,
        CategoryEnum.THERMAL: 5,
        CategoryEnum.OTHER: 3,
    }
    recommended_uses_between_wash = uses_between_wash_map.get(garment.category, 3)

    deformation_factor = {
        DeformationEnum.NONE: 1.0,
        DeformationEnum.SLIGHT: 0.85,
        DeformationEnum.MODERATE: 0.7,
        DeformationEnum.SEVERE: 0.5,
    }.get(garment.current_deformation, 1.0)

    adjusted_max_uses = max(1, int(recommended_uses_between_wash * deformation_factor))
    max_days_between_wash = max(3, int(14 * deformation_factor))

    triggers = []
    suggested_dates = []
    overdue_accumulated = 0

    if wears_since_last_wash >= adjusted_max_uses:
        overdue_by_uses = wears_since_last_wash - adjusted_max_uses + 1
        triggers.append(f"已穿着 {wears_since_last_wash} 次，超过建议的 {adjusted_max_uses} 次（+{overdue_by_uses}）")
        projected_last_wear_date = all_wears[0].wear_date if all_wears else (last_wash_date or garment.purchase_date or today)
        overdue_accumulated = max(overdue_accumulated, overdue_by_uses * 2, (today - projected_last_wear_date).days)
        suggested_date = today - timedelta(days=max(1, overdue_by_uses * 2))
        suggested_dates.append(suggested_date)

    if days_since_last_wash >= max_days_between_wash:
        overdue_by_days = days_since_last_wash - max_days_between_wash + 1
        triggers.append(f"距上次洗护已 {days_since_last_wash} 天，超过建议的 {max_days_between_wash} 天（+{overdue_by_days}）")
        overdue_accumulated = max(overdue_accumulated, overdue_by_days)
        date_from_rule = today - timedelta(days=overdue_by_days)
        if not suggested_dates or date_from_rule < suggested_dates[0]:
            suggested_dates.insert(0, date_from_rule)

    if garment.current_deformation in [DeformationEnum.MODERATE, DeformationEnum.SEVERE]:
        triggers.append(f"存在{garment.current_deformation.value}变形，需要更频繁洗护")

    if not suggested_dates:
        uses_remaining = adjusted_max_uses - wears_since_last_wash
        days_remaining = max_days_between_wash - days_since_last_wash

        if last_wash_date:
            suggested_by_days = last_wash_date + timedelta(days=max_days_between_wash)
        else:
            suggested_by_days = garment.purchase_date + timedelta(days=max_days_between_wash)

        if all_wears and last_wash_date:
            recent_wears_after = [w for w in all_wears if w.wear_date > last_wash_date]
            if len(recent_wears_after) >= 2:
                recent_wears_after_sorted = sorted(recent_wears_after, key=lambda w: w.wear_date)
                days_between_wears = (recent_wears_after_sorted[-1].wear_date - recent_wears_after_sorted[0].wear_date).days
                if days_between_wears > 0 and wears_since_last_wash > 0:
                    avg_days_per_use = days_between_wears / max(1, len(recent_wears_after) - 1)
                    projected_days = max(0, uses_remaining) * max(1, avg_days_per_use)
                    suggested_by_uses = today + timedelta(days=projected_days)
                    suggested_date = min(suggested_by_days, suggested_by_uses)
                    triggers.append(f"按当前穿着频率，预计还可穿 {uses_remaining} 次")
                else:
                    suggested_date = suggested_by_days
                    triggers.append(f"还可穿 {uses_remaining} 次或 {days_remaining} 天后需要洗护")
            else:
                suggested_date = suggested_by_days
                triggers.append(f"还可穿 {uses_remaining} 次或 {days_remaining} 天后需要洗护")
        else:
            suggested_date = suggested_by_days
            triggers.append(f"建议 {max_days_between_wash} 天内洗护（还可穿 {uses_remaining} 次）")

        suggested_dates.append(suggested_date)

    final_suggested_date = min(suggested_dates) if suggested_dates else today
    raw_overdue = (today - final_suggested_date).days
    overdue_days = max(0, overdue_accumulated, raw_overdue)

    if overdue_days > 0 and (today - final_suggested_date).days <= 0:
        final_suggested_date = today - timedelta(days=overdue_days)

    actual_suggested_date = final_suggested_date

    if overdue_days > 7:
        risk_level = "高风险"
    elif overdue_days > 2:
        risk_level = "中风险"
    elif overdue_days > 0:
        risk_level = "低风险"
    elif (final_suggested_date - today).days <= 1:
        risk_level = "待处理"
    else:
        risk_level = "正常"

    wash_method_map = {
        "机洗/手洗均可": "机洗或手洗",
        "手洗或干洗": "建议手洗或干洗",
        "手洗或洗衣袋机洗": "手洗或洗衣袋机洗",
        "请参考洗水标": "按洗水标说明",
    }
    suggested_wash_method = wash_method_map.get(
        care_rules["wash_method"],
        care_rules["wash_method"]
    )

    trigger_reason = "；".join(triggers) if triggers else "状态良好"

    return {
        "garment": garment_to_schema(garment, db),
        "suggested_wash_date": actual_suggested_date,
        "suggested_wash_method": suggested_wash_method,
        "overdue_days": overdue_days,
        "risk_level": risk_level,
        "trigger_reason": trigger_reason,
        "uses_since_last_wash": wears_since_last_wash,
        "days_since_last_wash": days_since_last_wash,
        "last_wash_date": last_wash_date,
    }


def garment_to_schema(garment: Garment, db: Optional[Session] = None) -> schemas.Garment:
    garment_dict = {c.name: getattr(garment, c.name) for c in garment.__table__.columns}
    garment_dict["storage_zone"] = garment.storage_zone
    garment_dict["care_advice"] = get_care_advice(garment.fabric)
    garment_dict["replacement_status"] = calculate_replacement_status(garment, db)

    if db is not None:
        latest_wash = (
            db.query(WashRecord)
            .filter(WashRecord.garment_id == garment.id)
            .order_by(WashRecord.wash_date.desc())
            .first()
        )
        if latest_wash:
            garment_dict["last_wash_date"] = latest_wash.wash_date
            total_washes = db.query(WashRecord).filter(WashRecord.garment_id == garment.id).count()
            garment_dict["wash_count"] = total_washes

        total_wears = db.query(WearRecord).filter(WearRecord.garment_id == garment.id).count()
        garment_dict["use_count"] = total_wears

        latest_wear = (
            db.query(WearRecord)
            .filter(WearRecord.garment_id == garment.id)
            .order_by(WearRecord.wear_date.desc())
            .first()
        )
        if latest_wear:
            garment_dict["last_worn_date"] = latest_wear.wear_date

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


@app.get("/api/wash-plans", response_model=List[schemas.WashPlan])
def get_wash_plans(
    risk_level: Optional[str] = None,
    storage_zone_id: Optional[int] = None,
    fabric: Optional[FabricEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Garment).options(joinedload(Garment.storage_zone)).filter(Garment.is_active == 1)
    if storage_zone_id is not None:
        query = query.filter(Garment.storage_zone_id == storage_zone_id)
    if fabric:
        query = query.filter(Garment.fabric == fabric)
    garments = query.order_by(Garment.last_wash_date.is_(None).desc(), Garment.last_wash_date.asc()).all()

    plans = []
    for g in garments:
        plan = calculate_wash_plan(g, db)
        if not plan:
            continue
        if risk_level and plan["risk_level"] != risk_level:
            continue
        if start_date and plan["suggested_wash_date"] < start_date:
            continue
        if end_date and plan["suggested_wash_date"] > end_date:
            continue
        plans.append(plan)

    plans.sort(key=lambda x: (
        {"高风险": 0, "中风险": 1, "低风险": 2, "待处理": 3, "正常": 4}.get(x["risk_level"], 99),
        x["suggested_wash_date"]
    ))
    return plans


@app.get("/api/wash-plans/grouped", response_model=schemas.PlanGroupResponse)
def get_wash_plans_grouped(
    db: Session = Depends(get_db)
):
    today = date.today()
    seven_days_later = today + timedelta(days=7)

    garments = (
        db.query(Garment)
        .options(joinedload(Garment.storage_zone))
        .filter(Garment.is_active == 1)
        .all()
    )

    overdue = []
    today_list = []
    next_7_days = []

    for g in garments:
        plan = calculate_wash_plan(g, db)
        if not plan:
            continue
        if plan["overdue_days"] > 0:
            overdue.append(plan)
        elif plan["suggested_wash_date"] == today:
            today_list.append(plan)
        elif plan["suggested_wash_date"] <= seven_days_later:
            next_7_days.append(plan)

    sort_key = lambda x: (x["overdue_days"], x["suggested_wash_date"])
    overdue.sort(key=sort_key, reverse=True)
    today_list.sort(key=sort_key)
    next_7_days.sort(key=sort_key)

    return {
        "overdue": overdue,
        "today": today_list,
        "next_7_days": next_7_days,
    }


@app.get("/api/garments/{garment_id}/detail", response_model=schemas.GarmentDetail)
def get_garment_detail(garment_id: int, db: Session = Depends(get_db)):
    garment = (
        db.query(Garment)
        .options(joinedload(Garment.storage_zone))
        .filter(Garment.id == garment_id)
        .first()
    )
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")

    recent_wears = (
        db.query(WearRecord)
        .filter(WearRecord.garment_id == garment_id)
        .order_by(WearRecord.wear_date.desc())
        .limit(5)
        .all()
    )
    recent_washes = (
        db.query(WashRecord)
        .filter(WashRecord.garment_id == garment_id)
        .order_by(WashRecord.wash_date.desc())
        .limit(5)
        .all()
    )

    wear_records = []
    for r in recent_wears:
        rd = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        rd["garment_name"] = garment.name
        wear_records.append(schemas.WearRecord.model_validate(rd))

    wash_records = []
    for r in recent_washes:
        rd = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        rd["garment_name"] = garment.name
        wash_records.append(schemas.WashRecord.model_validate(rd))

    next_plan = calculate_wash_plan(garment, db)

    return {
        **garment_to_schema(garment, db).model_dump(),
        "recent_wear_records": wear_records,
        "recent_wash_records": wash_records,
        "next_wash_plan": next_plan,
    }


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

    all_plans = []
    for g in all_garments:
        plan = calculate_wash_plan(g, db)
        if plan:
            all_plans.append(plan)

    total_planned = len(all_plans)
    overdue_wash_count = sum(1 for p in all_plans if p["overdue_days"] > 0)
    plan_completion_rate = round(
        (total_planned - overdue_wash_count) / total_planned * 100, 1
    ) if total_planned > 0 else 100.0

    fabric_wash_intervals = defaultdict(list)
    all_wash_records_sorted = sorted(all_wash_records, key=lambda x: x.wash_date)
    for wr in all_wash_records_sorted:
        fabric_wash_intervals[wr.garment.fabric.value].append(wr.wash_date)

    avg_wash_interval_by_fabric = []
    for fabric_name, dates in fabric_wash_intervals.items():
        if len(dates) >= 2:
            total_interval = 0
            for i in range(1, len(dates)):
                total_interval += (dates[i] - dates[i-1]).days
            avg_interval = round(total_interval / (len(dates) - 1), 1)
            avg_wash_interval_by_fabric.append({
                "fabric": fabric_name,
                "avg_days_between_washes": avg_interval,
                "wash_count": len(dates),
            })
    avg_wash_interval_by_fabric.sort(key=lambda x: x["avg_days_between_washes"])

    return {
        "total_garments": total_garments,
        "total_washes": total_washes,
        "fabric_stats": fabric_stats,
        "category_stats": category_stats,
        "deformation_risk_categories": deformation_risk,
        "idle_garments": idle_garments,
        "wash_frequency_stats": wash_frequency_stats[:20],
        "monthly_wash_trend": monthly_wash_trend,
        "plan_completion_rate": plan_completion_rate,
        "overdue_wash_count": overdue_wash_count,
        "avg_wash_interval_by_fabric": avg_wash_interval_by_fabric,
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
