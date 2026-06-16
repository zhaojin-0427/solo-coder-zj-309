import axios from 'axios'
import type {
  StorageZone, Garment, WashRecord, WearRecord,
  ReplacementReminder, Statistics, Enums, CareAdvice,
  WashPlan, GarmentDetail, PlanGroupResponse,
  TripPlanSummary, TripPlanDetail, TripPlan, TripItem
} from './types'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const storageZoneApi = {
  create: (data: Partial<StorageZone>) => api.post<any, StorageZone>('/storage-zones', data),
  list: () => api.get<any, StorageZone[]>('/storage-zones'),
  get: (id: number) => api.get<any, StorageZone>(`/storage-zones/${id}`),
  update: (id: number, data: Partial<StorageZone>) => api.put<any, StorageZone>(`/storage-zones/${id}`, data),
  delete: (id: number) => api.delete(`/storage-zones/${id}`)
}

export const garmentApi = {
  create: (data: any) => api.post<any, Garment>('/garments', data),
  list: (params?: any) => api.get<any, Garment[]>('/garments', { params }),
  get: (id: number) => api.get<any, Garment>(`/garments/${id}`),
  getDetail: (id: number) => api.get<any, GarmentDetail>(`/garments/${id}/detail`),
  update: (id: number, data: any) => api.put<any, Garment>(`/garments/${id}`, data),
  delete: (id: number) => api.delete(`/garments/${id}`)
}

export const washPlanApi = {
  list: (params?: any) => api.get<any, WashPlan[]>('/wash-plans', { params }),
  grouped: () => api.get<any, PlanGroupResponse>('/wash-plans/grouped')
}

export const washRecordApi = {
  create: (data: any) => api.post<any, WashRecord>('/wash-records', data),
  list: (params?: any) => api.get<any, WashRecord[]>('/wash-records', { params })
}

export const wearRecordApi = {
  create: (data: any) => api.post<any, WearRecord>('/wear-records', data),
  list: (params?: any) => api.get<any, WearRecord[]>('/wear-records', { params })
}

export const careAdviceApi = {
  get: (fabric: string) => api.get<any, CareAdvice>(`/care-advice/${fabric}`),
  list: () => api.get<any, CareAdvice[]>('/care-advice')
}

export const reminderApi = {
  list: (params?: any) => api.get<any, ReplacementReminder[]>('/replacement-reminders', { params })
}

export const statisticsApi = {
  get: () => api.get<any, Statistics>('/statistics')
}

export const enumApi = {
  get: () => api.get<any, Enums>('/enums')
}

export const tripPlanApi = {
  create: (data: any) => api.post<any, TripPlan>('/trip-plans', data),
  list: (params?: any) => api.get<any, TripPlanSummary[]>('/trip-plans', { params }),
  get: (id: number) => api.get<any, TripPlanDetail>(`/trip-plans/${id}`),
  update: (id: number, data: any) => api.put<any, TripPlan>(`/trip-plans/${id}`, data),
  delete: (id: number) => api.delete(`/trip-plans/${id}`),
  regenerate: (id: number) => api.post<any, TripPlanDetail>(`/trip-plans/${id}/regenerate`)
}

export const tripItemApi = {
  update: (id: number, data: any) => api.put<any, TripItem>(`/trip-items/${id}`, data),
  togglePack: (id: number) => api.put<any, TripItem>(`/trip-items/${id}/toggle-pack`),
  replace: (id: number, newGarmentId: number) => api.post<any, TripItem>(`/trip-items/${id}/replace?new_garment_id=${newGarmentId}`)
}

export default api
