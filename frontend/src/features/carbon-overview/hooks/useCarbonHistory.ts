import { useState, useEffect, useRef } from 'react'
import { useClusterCarbon } from './useClusterCarbon'

const MAX_POINTS = 40 // 10분치 (15s × 40)

export interface CarbonHistoryPoint {
  time: string    // HH:mm:ss
  co2Gpm: number
}

export function useCarbonHistory(): CarbonHistoryPoint[] {
  const { data } = useClusterCarbon()
  const [history, setHistory] = useState<CarbonHistoryPoint[]>([])
  const seeded = useRef(false)

  useEffect(() => {
    if (!data) return

    setHistory(prev => {
      // 첫 데이터 수신 시 과거 11포인트를 시뮬레이션 (차트 초기 렌더링용)
      if (!seeded.current) {
        seeded.current = true
        const base = data.co2Gpm
        const now = Date.now()
        const seedPoints: CarbonHistoryPoint[] = Array.from({ length: MAX_POINTS - 1 }, (_, i) => {
          const t = new Date(now - (MAX_POINTS - 1 - i) * 15_000)
          const v = Math.round(base * (0.85 + Math.random() * 0.3) * 1000) / 1000
          return {
            time: t.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            co2Gpm: v,
          }
        })
        return [
          ...seedPoints,
          {
            time: new Date(data.timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            co2Gpm: data.co2Gpm,
          },
        ]
      }

      // 이후 폴링 결과 누적
      const newTime = new Date(data.timestamp).toLocaleTimeString('ko-KR', {
        hour: '2-digit', minute: '2-digit', second: '2-digit',
      })
      if (prev.length > 0 && prev.at(-1)?.time === newTime) return prev

      return [
        ...prev.slice(-(MAX_POINTS - 1)),
        { time: newTime, co2Gpm: data.co2Gpm },
      ]
    })
  }, [data])

  return history
}
