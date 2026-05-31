import { apiClient } from '../client'
import { REGION_CODE } from '@/shared/constants/carbon.constants'
import type {
  ApiSchedulingRecommendResponse,
  ApiScheduleRecommendRequest,
  ApiScheduleHistoryResponse,
  ApiApplyScheduleRequest,
  ApiApplyScheduleResponse,
  SchedulingRecommendation,
  ScheduleHistoryItem,
  SchedulingSlot,
} from '@/shared/types'

function parseSlot(slot: ApiSchedulingRecommendResponse['recommendations'][number]): SchedulingSlot {
  const start = new Date(slot.start_time)
  const end = new Date(slot.end_time)
  return {
    rank: slot.rank,
    startTime: slot.start_time,
    endTime: slot.end_time,
    durationHours: Math.round((end.getTime() - start.getTime()) / 3_600_000 * 10) / 10,
    carbonIntensity: slot.carbon_intensity,
    savingPercent: slot.saving_percent,
    reason: slot.reason,
    isTopRecommendation: slot.rank === 1,
  }
}

function parseRecommendation(raw: ApiSchedulingRecommendResponse): SchedulingRecommendation {
  return {
    id: raw.id,
    generatedAt: raw.generated_at,
    regionCode: raw.region_code,
    applied: raw.applied,
    slots: raw.recommendations.map(parseSlot).sort((a, b) => a.rank - b.rank),
  }
}

export const aiSchedulerAdapter = {
  async recommend(): Promise<SchedulingRecommendation> {
    const body: ApiScheduleRecommendRequest = { region_code: REGION_CODE }
    const { data } = await apiClient.post<ApiSchedulingRecommendResponse>('/schedule/recommend', body)
    return parseRecommendation(data)
  },

  async getLatest(): Promise<SchedulingRecommendation | null> {
    const { data } = await apiClient.get<ApiSchedulingRecommendResponse>('/schedule/latest')
    return parseRecommendation(data)
  },

  async getHistory(): Promise<ScheduleHistoryItem[]> {
    const { data } = await apiClient.get<ApiScheduleHistoryResponse>('/schedule/history')
    return data.history.map((item) => ({
      id: item.id,
      generatedAt: item.generated_at,
      regionCode: item.region_code,
      applied: item.applied,
      topSlot: parseSlot(
        (item.recommendations.find(r => r.rank === 1) ?? item.recommendations[0])!
      ),
    }))
  },

  async applySchedule(recommendationId: string): Promise<ApiApplyScheduleResponse> {
    const body: ApiApplyScheduleRequest = { recommendation_id: recommendationId }
    const { data } = await apiClient.post<ApiApplyScheduleResponse>('/schedule/apply', body)
    return data
  },
}
