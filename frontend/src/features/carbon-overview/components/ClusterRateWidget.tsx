import { useState, useEffect, useRef } from 'react'
import { useClusterCarbon } from '../hooks/useClusterCarbon'
import { KpiCard } from './KpiCard'
import styles from './StatWidget.module.css'
import type { CarbonLevel } from '@/shared/types'

const LEVEL_COLOR: Record<CarbonLevel, string> = {
  low:    'var(--color-carbon-low)',
  medium: 'var(--color-carbon-medium)',
  high:   'var(--color-carbon-high)',
}

const LEVEL_LABEL: Record<CarbonLevel, string> = {
  low: '정상', medium: '주의', high: '위험',
}

export function ClusterRateWidget() {
  const { data, isLoading, isError } = useClusterCarbon()
  const [delta, setDelta] = useState<number | null>(null)
  const prevCo2 = useRef<number | null>(null)

  useEffect(() => {
    if (!data) return
    if (prevCo2.current !== null) {
      setDelta(Math.round((data.co2Gpm - prevCo2.current) * 1000) / 1000)
    }
    prevCo2.current = data.co2Gpm
  }, [data])

  const deltaSign = delta !== null && Math.abs(delta) > 0.0001 ? (delta > 0 ? '+' : '') : null

  return (
    <KpiCard title="클러스터 탄소 배출률" isLoading={isLoading} isError={isError} updatedAt={data?.timestamp}>
      {data && (
        <>
          <div className={styles.valueRow}>
            <span className={styles.value} style={{ color: LEVEL_COLOR[data.level] }}>
              {data.co2Gpm}
            </span>
            <span className={styles.unit}>gCO₂/min</span>
            {deltaSign !== null && (
              <span
                className={styles.delta}
                style={{ color: delta! > 0 ? 'var(--color-carbon-high)' : 'var(--color-carbon-low)' }}
              >
                {deltaSign}{delta}
              </span>
            )}
          </div>
          <div className={styles.meta}>
            <span className={styles.dot} style={{ color: LEVEL_COLOR[data.level] }}>
              ● {LEVEL_LABEL[data.level]}
            </span>
            <span className={styles.sub}>{data.powerWatt.toFixed(2)}W · {data.region.name}</span>
          </div>
        </>
      )}
    </KpiCard>
  )
}
