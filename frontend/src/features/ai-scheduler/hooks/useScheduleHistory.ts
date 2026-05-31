import { useQuery } from '@tanstack/react-query'
import { aiSchedulerAdapter } from '@/shared/api/adapters'
import { SCHEDULER_QUERY_KEYS } from './useScheduleRecommend'

export function useScheduleHistory() {
  return useQuery({
    queryKey: SCHEDULER_QUERY_KEYS.history(),
    queryFn: aiSchedulerAdapter.getHistory,
    staleTime: 60_000,
    retry: 1,
  })
}
