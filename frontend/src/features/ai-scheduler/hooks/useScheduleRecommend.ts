import { useMutation, useQueryClient } from '@tanstack/react-query'
import { aiSchedulerAdapter } from '@/shared/api/adapters'

export const SCHEDULER_QUERY_KEYS = {
  all:     ['ai-scheduler'] as const,
  latest:  () => [...SCHEDULER_QUERY_KEYS.all, 'latest'] as const,
  history: () => [...SCHEDULER_QUERY_KEYS.all, 'history'] as const,
} as const

export function useScheduleRecommend() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: aiSchedulerAdapter.recommend,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SCHEDULER_QUERY_KEYS.latest() })
      queryClient.invalidateQueries({ queryKey: SCHEDULER_QUERY_KEYS.history() })
    },
  })
}
