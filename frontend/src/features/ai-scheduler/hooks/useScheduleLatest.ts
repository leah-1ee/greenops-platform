import { useQuery } from '@tanstack/react-query'
import { aiSchedulerAdapter } from '@/shared/api/adapters'
import { SCHEDULER_QUERY_KEYS } from './useScheduleRecommend'

export function useScheduleLatest() {
  return useQuery({
    queryKey: SCHEDULER_QUERY_KEYS.latest(),
    queryFn: aiSchedulerAdapter.getLatest,
    staleTime: 5 * 60_000,
    retry: 1,
  })
}
