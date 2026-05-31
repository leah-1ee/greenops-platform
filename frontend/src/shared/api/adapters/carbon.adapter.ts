import { apiClient } from '../client'
import type {
  ApiNodeCarbonResponse,
  ApiPodCarbonResponse,
  ClusterCarbonRate,
  PodCarbon,
  DailyCarbonSummary,
  CarbonLevel,
  RegionConfig,
} from '@/shared/types'

function toCarbonLevel(co2Gpm: number): CarbonLevel {
  if (co2Gpm < 50) return 'low'
  if (co2Gpm < 100) return 'medium'
  return 'high'
}

function toRegionConfig(raw: ApiNodeCarbonResponse): RegionConfig {
  return {
    code: raw.region_code,
    name: raw.region_name,
    pue: raw.pue,
    carbonIntensity: raw.carbon_intensity,
  }
}

// co2_grams(15s) → gCO₂/min 환산
// duration_sec이 바뀌어도 이 함수만 수정
function toGpm(co2Grams: number, durationSec: number): number {
  return (co2Grams / durationSec) * 60
}

export const carbonAdapter = {
  async getClusterRate(): Promise<ClusterCarbonRate> {
    const { data } = await apiClient.get<ApiNodeCarbonResponse>('/carbon/node')
    const co2Gpm = toGpm(data.co2_grams, data.duration_sec)

    return {
      co2Gpm: Math.round(co2Gpm * 1000) / 1000,
      powerWatt: data.power_watt,
      region: toRegionConfig(data),
      level: toCarbonLevel(co2Gpm),
      timestamp: data.timestamp,
      source: 'live' as const,
    }
  },

  async getPodList(): Promise<PodCarbon[]> {
    const { data } = await apiClient.get<ApiPodCarbonResponse>('/carbon/pods')

    return data.pods.map((pod) => {
      const co2Gpm = toGpm(pod.co2_grams, pod.duration_sec)
      const namespace = pod.namespace ?? pod.pod_name.split('-').slice(0, 2).join('-')

      return {
        podName: pod.pod_name,
        namespace,
        co2Gpm: Math.round(co2Gpm * 1000) / 1000,
        powerWatt: pod.power_watt,
        sharePercent: pod.share_percent,
        level: toCarbonLevel(co2Gpm),
      }
    })
  },

  async getDailySummary(): Promise<DailyCarbonSummary> {
    const { data } = await apiClient.get<ApiNodeCarbonResponse>('/carbon/node')
    const co2Gpm = toGpm(data.co2_grams, data.duration_sec)
    const estimatedDailyGrams = co2Gpm * 60 * 24 // 현재 rate 기준 추정

    return {
      totalCo2Grams: Math.round(estimatedDailyGrams),
      totalCo2Kg: Math.round(estimatedDailyGrams / 1000 * 100) / 100,
      periodHours: 24,
      avgCo2Gpm: Math.round(co2Gpm * 10) / 10,
      peakCo2Gpm: Math.round(co2Gpm * 1.3 * 10) / 10, // 추정 피크 (MVP)
      timestamp: data.timestamp,
    }
  },
}
