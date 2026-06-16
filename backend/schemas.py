from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from models import (
    CategoryEnum, FabricEnum, WashMethodEnum, DeformationEnum,
    ActivitySceneEnum, ChangePreferenceEnum, TripStatusEnum,
    PackStatusEnum, RecommendLevelEnum
)


class StorageZoneBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = ""
    capacity: Optional[int] = 10


class StorageZoneCreate(StorageZoneBase):
    pass


class StorageZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None


class StorageZone(StorageZoneBase):
    id: int
    created_at: datetime
    current_count: int = 0

    class Config:
        from_attributes = True


class GarmentBase(BaseModel):
    name: str = Field(..., max_length=200)
    category: CategoryEnum
    size: str = Field(..., max_length=50)
    color: str = Field(..., max_length=50)
    fabric: FabricEnum
    purchase_date: date
    storage_zone_id: Optional[int] = None
    brand: Optional[str] = ""
    price: Optional[float] = 0.0
    notes: Optional[str] = ""


class GarmentCreate(GarmentBase):
    pass


class GarmentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[CategoryEnum] = None
    size: Optional[str] = None
    color: Optional[str] = None
    fabric: Optional[FabricEnum] = None
    purchase_date: Optional[date] = None
    storage_zone_id: Optional[int] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    notes: Optional[str] = None
    current_deformation: Optional[DeformationEnum] = None
    is_active: Optional[int] = None


class Garment(GarmentBase):
    id: int
    use_count: int = 0
    wash_count: int = 0
    created_at: datetime
    last_worn_date: Optional[date] = None
    last_wash_date: Optional[date] = None
    current_deformation: DeformationEnum = DeformationEnum.NONE
    is_active: int = 1
    storage_zone: Optional[StorageZone] = None
    care_advice: Optional[dict] = None
    replacement_status: Optional[dict] = None

    class Config:
        from_attributes = True


class WashRecordBase(BaseModel):
    garment_id: int
    wash_date: date
    wash_method: WashMethodEnum
    detergent: Optional[str] = ""
    deformation_after: DeformationEnum = DeformationEnum.NONE
    notes: Optional[str] = ""


class WashRecordCreate(WashRecordBase):
    pass


class WashRecord(WashRecordBase):
    id: int
    created_at: datetime
    garment_name: Optional[str] = None

    class Config:
        from_attributes = True


class WearRecordBase(BaseModel):
    garment_id: int
    wear_date: date
    duration_hours: Optional[int] = 8
    deformation_noticed: DeformationEnum = DeformationEnum.NONE
    notes: Optional[str] = ""


class WearRecordCreate(WearRecordBase):
    pass


class WearRecord(WearRecordBase):
    id: int
    created_at: datetime
    garment_name: Optional[str] = None

    class Config:
        from_attributes = True


class FabricCareAdvice(BaseModel):
    fabric: FabricEnum
    wash_method: str
    wash_temp: str
    drying: str
    detergent: str
    iron: str
    notes: str
    recommended_uses: int
    replacement_months: int


class ReplacementReminder(BaseModel):
    garment: Garment
    reason: str
    days_until_recommended: int
    urgency: str


class WashPlan(BaseModel):
    garment: Garment
    suggested_wash_date: date
    suggested_wash_method: str
    overdue_days: int
    risk_level: str
    trigger_reason: str
    uses_since_last_wash: int
    days_since_last_wash: int
    last_wash_date: Optional[date] = None


class GarmentDetail(Garment):
    recent_wear_records: List[WearRecord] = []
    recent_wash_records: List[WashRecord] = []
    next_wash_plan: Optional[WashPlan] = None


class PlanGroupResponse(BaseModel):
    overdue: List[WashPlan]
    today: List[WashPlan]
    next_7_days: List[WashPlan]


class StatisticsResponse(BaseModel):
    total_garments: int
    total_washes: int
    fabric_stats: List[dict]
    category_stats: List[dict]
    deformation_risk_categories: List[dict]
    idle_garments: List[dict]
    wash_frequency_stats: List[dict]
    monthly_wash_trend: List[dict]
    plan_completion_rate: float
    overdue_wash_count: int
    avg_wash_interval_by_fabric: List[dict]
    trip_stats: Optional[dict] = None


class TripPlanBase(BaseModel):
    name: str = Field(..., max_length=200)
    destination: str = Field(..., max_length=200)
    start_date: date
    end_date: date
    duration_days: int
    weather_min: Optional[int] = None
    weather_max: Optional[int] = None
    weather_description: Optional[str] = ""
    activity_scenes: Optional[str] = ""
    change_preference: ChangePreferenceEnum = ChangePreferenceEnum.DAILY
    status: TripStatusEnum = TripStatusEnum.PLANNING
    notes: Optional[str] = ""


class TripPlanCreate(TripPlanBase):
    pass


class TripPlanUpdate(BaseModel):
    name: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_days: Optional[int] = None
    weather_min: Optional[int] = None
    weather_max: Optional[int] = None
    weather_description: Optional[str] = None
    activity_scenes: Optional[str] = None
    change_preference: Optional[ChangePreferenceEnum] = None
    status: Optional[TripStatusEnum] = None
    notes: Optional[str] = None


class TripItemBase(BaseModel):
    garment_id: int
    recommend_level: RecommendLevelEnum = RecommendLevelEnum.OPTIONAL
    recommend_reasons: Optional[str] = ""
    planned_quantity: int = 1
    pack_status: PackStatusEnum = PackStatusEnum.UNPACKED
    packed_quantity: int = 0
    day_assignments: Optional[str] = ""
    notes: Optional[str] = ""


class TripItemCreate(TripItemBase):
    pass


class TripItemUpdate(BaseModel):
    recommend_level: Optional[RecommendLevelEnum] = None
    planned_quantity: Optional[int] = None
    pack_status: Optional[PackStatusEnum] = None
    packed_quantity: Optional[int] = None
    actual_used: Optional[int] = None
    need_wash_after: Optional[int] = None
    replaced_from_garment_id: Optional[int] = None
    day_assignments: Optional[str] = None
    notes: Optional[str] = None
    is_user_adjusted: Optional[int] = None


class TripItem(TripItemBase):
    id: int
    trip_plan_id: int
    garment: Optional[Garment] = None
    is_user_adjusted: int = 0
    actual_used: int = 0
    need_wash_after: int = 1
    replaced_from_garment_id: Optional[int] = None
    replaced_from_garment: Optional[Garment] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TripPlan(TripPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[TripItem] = []

    class Config:
        from_attributes = True


class TripPlanSummary(BaseModel):
    id: int
    name: str
    destination: str
    start_date: date
    end_date: date
    duration_days: int
    status: TripStatusEnum
    items_count: int = 0
    packed_count: int = 0
    must_count: int = 0
    created_at: datetime


class DayOutfitPlan(BaseModel):
    day_index: int
    date: date
    garments: List[Garment] = []


class StoragePickupPath(BaseModel):
    storage_zone_id: Optional[int]
    storage_zone_name: str
    garments: List[dict] = []
    total_items: int = 0


class RecommendationSummary(BaseModel):
    must_carry: List[TripItem] = []
    optional: List[TripItem] = []
    not_recommended: List[TripItem] = []
    total_estimated_wears: int = 0
    estimated_wash_after_return: int = 0
    change_gap_analysis: dict = {}


class TripPlanDetail(TripPlan):
    recommendation_summary: RecommendationSummary
    day_outfit_plans: List[DayOutfitPlan] = []
    storage_pickup_paths: List[StoragePickupPath] = []
    available_replacements: dict = {}
