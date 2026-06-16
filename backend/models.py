from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class CategoryEnum(str, enum.Enum):
    BRA = "文胸"
    PANTY = "内裤"
    PAJAMAS = "睡衣"
    SPORTS = "运动内衣"
    SHAPEWEAR = "塑身衣"
    THERMAL = "保暖内衣"
    OTHER = "其他"


class FabricEnum(str, enum.Enum):
    COTTON = "纯棉"
    SILK = "真丝"
    LACE = "蕾丝"
    MODAL = "莫代尔"
    NYLON = "锦纶"
    SPANDEX = "氨纶"
    POLYESTER = "聚酯纤维"
    BAMBOO = "竹纤维"
    WOOL = "羊毛"
    OTHER = "其他"


class WashMethodEnum(str, enum.Enum):
    MACHINE = "机洗"
    HAND = "手洗"
    DRY_CLEAN = "干洗"


class DeformationEnum(str, enum.Enum):
    NONE = "无"
    SLIGHT = "轻微"
    MODERATE = "中度"
    SEVERE = "严重"


FABRIC_CARE_RULES = {
    FabricEnum.COTTON: {
        "wash_method": "机洗/手洗均可",
        "wash_temp": "最高40°C",
        "drying": "可机洗脱水，阴凉处平铺晾干",
        "detergent": "中性或弱碱性洗涤剂",
        "iron": "可中温熨烫",
        "notes": "避免长时间暴晒，防止褪色",
        "recommended_uses": 30,
        "replacement_months": 12,
    },
    FabricEnum.SILK: {
        "wash_method": "手洗或干洗",
        "wash_temp": "最高30°C冷水",
        "drying": "不可拧干，阴凉处悬挂晾干",
        "detergent": "专用丝绸洗涤剂或中性洗发水",
        "iron": "低温垫布熨烫",
        "notes": "避免与粗糙物品摩擦，不可漂白",
        "recommended_uses": 25,
        "replacement_months": 18,
    },
    FabricEnum.LACE: {
        "wash_method": "手洗或洗衣袋机洗",
        "wash_temp": "最高30°C",
        "drying": "平铺阴干，不可悬挂",
        "detergent": "中性洗涤剂",
        "iron": "不可熨烫或低温蒸汽",
        "notes": "轻柔揉搓，避免勾丝",
        "recommended_uses": 20,
        "replacement_months": 9,
    },
    FabricEnum.MODAL: {
        "wash_method": "机洗/手洗均可",
        "wash_temp": "最高40°C",
        "drying": "可机洗脱水，悬挂晾干",
        "detergent": "中性洗涤剂",
        "iron": "低温熨烫",
        "notes": "首次洗涤可能轻微缩水",
        "recommended_uses": 40,
        "replacement_months": 12,
    },
    FabricEnum.NYLON: {
        "wash_method": "机洗/手洗均可",
        "wash_temp": "最高40°C",
        "drying": "中低温烘干或阴干",
        "detergent": "中性洗涤剂",
        "iron": "低温熨烫",
        "notes": "避免高温，防止弹性损失",
        "recommended_uses": 50,
        "replacement_months": 18,
    },
    FabricEnum.SPANDEX: {
        "wash_method": "手洗或洗衣袋机洗",
        "wash_temp": "最高30°C",
        "drying": "平铺阴干，不可高温烘干",
        "detergent": "中性洗涤剂，避免柔顺剂",
        "iron": "不可熨烫",
        "notes": "柔顺剂会破坏弹性纤维",
        "recommended_uses": 35,
        "replacement_months": 12,
    },
    FabricEnum.POLYESTER: {
        "wash_method": "机洗/手洗均可",
        "wash_temp": "最高40°C",
        "drying": "可烘干，避免高温",
        "detergent": "普通洗涤剂即可",
        "iron": "中温熨烫",
        "notes": "易产生静电，可用柔顺剂",
        "recommended_uses": 60,
        "replacement_months": 24,
    },
    FabricEnum.BAMBOO: {
        "wash_method": "机洗/手洗均可",
        "wash_temp": "最高40°C",
        "drying": "阴干，避免暴晒",
        "detergent": "中性洗涤剂",
        "iron": "低温熨烫",
        "notes": "天然抗菌，无需频繁洗涤",
        "recommended_uses": 45,
        "replacement_months": 15,
    },
    FabricEnum.WOOL: {
        "wash_method": "手洗或干洗",
        "wash_temp": "最高30°C冷水",
        "drying": "平铺阴干，不可悬挂",
        "detergent": "羊毛专用洗涤剂",
        "iron": "低温垫布熨烫",
        "notes": "避免热水和揉搓，防缩",
        "recommended_uses": 25,
        "replacement_months": 24,
    },
    FabricEnum.OTHER: {
        "wash_method": "请参考洗水标",
        "wash_temp": "建议30°C以下",
        "drying": "建议阴干",
        "detergent": "中性洗涤剂",
        "iron": "请参考洗水标",
        "notes": "请仔细阅读衣物洗水说明",
        "recommended_uses": 30,
        "replacement_months": 12,
    },
}


class StorageZone(Base):
    __tablename__ = "storage_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), default="")
    capacity = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    garments = relationship("Garment", back_populates="storage_zone")


class Garment(Base):
    __tablename__ = "garments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    size = Column(String(50), nullable=False)
    color = Column(String(50), nullable=False)
    fabric = Column(Enum(FabricEnum), nullable=False)
    purchase_date = Column(Date, nullable=False)
    storage_zone_id = Column(Integer, ForeignKey("storage_zones.id"), nullable=True)
    brand = Column(String(100), default="")
    price = Column(Float, default=0.0)
    notes = Column(Text, default="")
    use_count = Column(Integer, default=0)
    wash_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_worn_date = Column(Date, nullable=True)
    last_wash_date = Column(Date, nullable=True)
    current_deformation = Column(Enum(DeformationEnum), default=DeformationEnum.NONE)
    is_active = Column(Integer, default=1)

    storage_zone = relationship("StorageZone", back_populates="garments")
    wash_records = relationship("WashRecord", back_populates="garment", cascade="all, delete-orphan")
    wear_records = relationship("WearRecord", back_populates="garment", cascade="all, delete-orphan")


class WashRecord(Base):
    __tablename__ = "wash_records"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id"), nullable=False)
    wash_date = Column(Date, nullable=False)
    wash_method = Column(Enum(WashMethodEnum), nullable=False)
    detergent = Column(String(200), default="")
    deformation_after = Column(Enum(DeformationEnum), default=DeformationEnum.NONE)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    garment = relationship("Garment", back_populates="wash_records")


class WearRecord(Base):
    __tablename__ = "wear_records"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id"), nullable=False)
    wear_date = Column(Date, nullable=False)
    duration_hours = Column(Integer, default=8)
    deformation_noticed = Column(Enum(DeformationEnum), default=DeformationEnum.NONE)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    garment = relationship("Garment", back_populates="wear_records")


class ActivitySceneEnum(str, enum.Enum):
    DAILY = "日常出行"
    BUSINESS = "商务出差"
    VACATION = "度假休闲"
    SPORTS = "运动健身"
    PARTY = "聚会派对"
    OTHER = "其他"


class ChangePreferenceEnum(str, enum.Enum):
    DAILY = "每天更换"
    EVERY_OTHER = "隔天更换"
    MINIMAL = "尽量精简"
    PLENTY = "多备几套"


class TripStatusEnum(str, enum.Enum):
    PLANNING = "规划中"
    PACKING = "打包中"
    IN_PROGRESS = "出行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class PackStatusEnum(str, enum.Enum):
    UNPACKED = "未打包"
    PACKED = "已打包"
    USED = "已使用"
    RETURNED = "已归位"


class RecommendLevelEnum(str, enum.Enum):
    MUST = "必带"
    OPTIONAL = "备选"
    NOT_RECOMMENDED = "不建议携带"


class TripPlan(Base):
    __tablename__ = "trip_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=False)
    weather_min = Column(Integer, nullable=True)
    weather_max = Column(Integer, nullable=True)
    weather_description = Column(String(500), default="")
    activity_scenes = Column(String(500), default="")
    change_preference = Column(Enum(ChangePreferenceEnum), default=ChangePreferenceEnum.DAILY)
    status = Column(Enum(TripStatusEnum), default=TripStatusEnum.PLANNING)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("TripItem", back_populates="trip_plan", cascade="all, delete-orphan")


class TripItem(Base):
    __tablename__ = "trip_items"

    id = Column(Integer, primary_key=True, index=True)
    trip_plan_id = Column(Integer, ForeignKey("trip_plans.id"), nullable=False)
    garment_id = Column(Integer, ForeignKey("garments.id"), nullable=False)
    recommend_level = Column(Enum(RecommendLevelEnum), default=RecommendLevelEnum.OPTIONAL)
    recommend_reasons = Column(String(1000), default="")
    is_user_adjusted = Column(Integer, default=0)
    planned_quantity = Column(Integer, default=1)
    pack_status = Column(Enum(PackStatusEnum), default=PackStatusEnum.UNPACKED)
    packed_quantity = Column(Integer, default=0)
    actual_used = Column(Integer, default=0)
    need_wash_after = Column(Integer, default=1)
    replaced_from_garment_id = Column(Integer, ForeignKey("garments.id"), nullable=True)
    day_assignments = Column(String(500), default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trip_plan = relationship("TripPlan", back_populates="items")
    garment = relationship("Garment", foreign_keys=[garment_id])
    replaced_from_garment = relationship("Garment", foreign_keys=[replaced_from_garment_id])
