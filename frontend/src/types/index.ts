export interface StorageZone {
  id: number
  name: string
  description: string
  capacity: number
  current_count: number
  created_at: string
}

export interface CareAdvice {
  fabric: string
  wash_method: string
  wash_temp: string
  drying: string
  detergent: string
  iron: string
  notes: string
  recommended_uses: number
  replacement_months: number
}

export interface ReplacementStatus {
  urgency: string
  overall_score: number
  use_ratio: number
  time_ratio: number
  deformation_score: number
  days_remaining: number
  uses_remaining: number
  recommended_uses: number
  replacement_months: number
  reasons: string[]
}

export interface Garment {
  id: number
  name: string
  category: string
  size: string
  color: string
  fabric: string
  purchase_date: string
  storage_zone_id: number | null
  brand: string
  price: number
  notes: string
  use_count: number
  wash_count: number
  created_at: string
  last_worn_date: string | null
  last_wash_date: string | null
  current_deformation: string
  is_active: number
  storage_zone: StorageZone | null
  care_advice: CareAdvice | null
  replacement_status: ReplacementStatus | null
}

export interface WashRecord {
  id: number
  garment_id: number
  garment_name: string
  wash_date: string
  wash_method: string
  detergent: string
  deformation_after: string
  notes: string
  created_at: string
}

export interface WearRecord {
  id: number
  garment_id: number
  garment_name: string
  wear_date: string
  duration_hours: number
  deformation_noticed: string
  notes: string
  created_at: string
}

export interface ReplacementReminder {
  garment: Garment
  reason: string
  days_until_recommended: number
  urgency: string
}

export interface WashPlan {
  garment: Garment
  suggested_wash_date: string
  suggested_wash_method: string
  overdue_days: number
  risk_level: string
  trigger_reason: string
  uses_since_last_wash: number
  days_since_last_wash: number
  last_wash_date: string | null
}

export interface GarmentDetail extends Garment {
  recent_wear_records: WearRecord[]
  recent_wash_records: WashRecord[]
  next_wash_plan: WashPlan | null
}

export interface PlanGroupResponse {
  overdue: WashPlan[]
  today: WashPlan[]
  next_7_days: WashPlan[]
}

export interface Statistics {
  total_garments: number
  total_washes: number
  fabric_stats: Array<{
    fabric: string
    count: number
    avg_use_cycle: number
    avg_wash_count: number
    avg_months_owned: number
  }>
  category_stats: Array<{
    category: string
    count: number
    avg_uses: number
    avg_washes: number
  }>
  deformation_risk_categories: Array<{
    category: string
    total_count: number
    deformation_count: number
    deformation_rate: number
  }>
  idle_garments: Array<{
    id: number
    name: string
    category: string
    idle_days: number
    use_count: number
    last_worn_date: string | null
  }>
  wash_frequency_stats: Array<{
    id: number
    name: string
    category: string
    uses_per_wash: number
    use_count: number
    wash_count: number
  }>
  monthly_wash_trend: Array<{
    month: string
    total_washes: number
    washes_with_deformation: number
  }>
  plan_completion_rate: number
  overdue_wash_count: number
  avg_wash_interval_by_fabric: Array<{
    fabric: string
    avg_days_between_washes: number
    wash_count: number
  }>
}

export interface EnumOption {
  value: string
  name: string
}

export interface Enums {
  categories: EnumOption[]
  fabrics: EnumOption[]
  wash_methods: EnumOption[]
  deformation_levels: EnumOption[]
}
