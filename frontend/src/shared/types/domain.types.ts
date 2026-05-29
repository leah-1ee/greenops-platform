// ── Carbon 도메인 타입 ────────────────────────────────────────────────────────

export type CarbonLevel = 'low' | 'medium' | 'high'
export type DataSource = 'live'

export interface RegionConfig {
  code: string
  name: string
  pue: number
  carbonIntensity: number // gCO₂/kWh
}

export interface ClusterCarbonRate {
  co2Gpm: number          // gCO₂/min
  powerWatt: number
  region: RegionConfig
  level: CarbonLevel      // adapter가 threshold 기준으로 계산
  timestamp: string
  source: DataSource
}

export interface PodCarbon {
  podName: string
  namespace: string
  co2Gpm: number
  powerWatt: number
  sharePercent: number
  level: CarbonLevel
}

export interface NamespaceCarbon {
  namespace: string
  co2Gpm: number
  podCount: number
  topPod: string
  level: CarbonLevel
}

export interface DailyCarbonSummary {
  totalCo2Grams: number
  totalCo2Kg: number       // totalCo2Grams / 1000
  periodHours: number
  avgCo2Gpm: number
  peakCo2Gpm: number
  timestamp: string
}

export interface CarbonScore {
  score: number            // 0–100
  level: CarbonLevel
  label: string            // "좋음" | "주의" | "위험"
}

// ── AI Scheduler 도메인 타입 ─────────────────────────────────────────────────

export interface SchedulingSlot {
  rank: number
  startTime: string        // ISO 8601
  endTime: string
  durationHours: number    // adapter 계산
  carbonIntensity: number
  savingPercent: number
  reason: string
  isTopRecommendation: boolean  // rank === 1
}

export interface SchedulingRecommendation {
  id: string
  generatedAt: string
  regionCode: string
  applied: boolean
  slots: SchedulingSlot[]
}

export interface ScheduleHistoryItem {
  id: string
  generatedAt: string
  regionCode: string
  applied: boolean
  topSlot: SchedulingSlot
}

// ── UI 상태 타입 ────────────────────────────────────────────────────────────

export interface WidgetState<T> {
  data: T | null
  isLoading: boolean
  isError: boolean
  lastUpdated: string | null
}

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface DrillDownTarget {
  type: 'namespace' | 'pod'
  name: string
}
