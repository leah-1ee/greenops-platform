import { useQuery } from '@tanstack/react-query'
import { carbonAdapter } from '@/shared/api/adapters'

export const CARBON_QUERY_KEYS = {
  all: ['carbon'] as const,
  clusterRate: () => [...CARBON_QUERY_KEYS.all, 'cluster', 'rate'] as const,
  podList: () => [...CARBON_QUERY_KEYS.all, 'pod', 'list'] as const,
  dailySummary: () => [...CARBON_QUERY_KEYS.all, 'daily', 'summary'] as const,
  namespace: (ns: string) => [...CARBON_QUERY_KEYS.all, 'namespace', ns] as const,
} as const

const POLL_INTERVAL = Number(import.meta.env.VITE_POLLING_INTERVAL_MS ?? 15_000)

export function useClusterCarbon() {
  return useQuery({
    queryKey: CARBON_QUERY_KEYS.clusterRate(),
    queryFn: carbonAdapter.getClusterRate,
    staleTime: POLL_INTERVAL,
    refetchInterval: POLL_INTERVAL,
    // 탭 비활성화 시에도 계속 fetch (모니터링 대시보드 특성)
    refetchIntervalInBackground: true,
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10_000),
  })
}

export function usePodCarbonList() {
  return useQuery({
    queryKey: CARBON_QUERY_KEYS.podList(),
    queryFn: carbonAdapter.getPodList,
    staleTime: POLL_INTERVAL,
    refetchInterval: POLL_INTERVAL,
    refetchIntervalInBackground: true,
  })
}

export function useDailyCarbonSummary() {
  return useQuery({
    queryKey: CARBON_QUERY_KEYS.dailySummary(),
    queryFn: carbonAdapter.getDailySummary,
    staleTime: 60_000,        // 일일 요약은 1분 캐시 (자주 안 바뀜)
    refetchInterval: 60_000,
  })
}
