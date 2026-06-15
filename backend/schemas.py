from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from models import CategoryEnum, FabricEnum, WashMethodEnum, DeformationEnum


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


class StatisticsResponse(BaseModel):
    total_garments: int
    total_washes: int
    fabric_stats: List[dict]
    category_stats: List[dict]
    deformation_risk_categories: List[dict]
    idle_garments: List[dict]
    wash_frequency_stats: List[dict]
    monthly_wash_trend: List[dict]
