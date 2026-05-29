// ── /api/v1/carbon/node 응답 ────────────────────────────────────────────────
export interface ApiNodeCarbonResponse {
  power_watt: number
  energy_kwh: number
  co2_grams: number
  duration_sec: number
  region_code: string
  region_name: string
  pue: number
  carbon_intensity: number
  timestamp: string
  source: string
  cpu_percent?: number
  memory_gb?: number
  instance_type?: string
  tdp_watt?: number
}

// ── /api/v1/carbon/pods 응답 ───────────────────────────────────────────────
export interface ApiPodCarbonItem extends ApiNodeCarbonResponse {
  pod_name: string
  namespace?: string  // Prometheus 실측 시 실제 k8s namespace
  share_percent: number
}

export interface ApiPodCarbonResponse {
  timestamp: string
  source: string
  pods: ApiPodCarbonItem[]
}

// ── /api/v1/carbon/regions 응답 ────────────────────────────────────────────
export interface ApiRegionInfo {
  name: string
  pue: number
  sdk_location: string
  carbon_intensity: number
}

export interface ApiRegionsResponse {
  regions: Record<string, ApiRegionInfo>
}

// ── /api/v1/schedule/* 요청/응답 ────────────────────────────────────────────
export interface ApiSchedulingSlot {
  rank: number
  start_time: string
  end_time: string
  carbon_intensity: number
  saving_percent: number
  reason: string
}

export interface ApiSchedulingRecommendResponse {
  id: string
  generated_at: string
  region_code: string
  applied: boolean
  recommendations: ApiSchedulingSlot[]
}

export interface ApiScheduleRecommendRequest {
  region_code: string
}

export interface ApiScheduleHistoryItem {
  id: string
  generated_at: string
  region_code: string
  applied: boolean
  recommendations: ApiSchedulingSlot[]
}

export interface ApiScheduleHistoryResponse {
  history: ApiScheduleHistoryItem[]
  total: number
}

export interface ApiApplyScheduleRequest {
  recommendation_id: string
}

export interface ApiApplyScheduleResponse {
  success: boolean
  message: string
  applied_at: string
}
