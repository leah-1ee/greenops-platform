import { useClusterCarbon } from '../hooks/useClusterCarbon'
import { KpiCard } from './KpiCard'
import styles from './StatWidget.module.css'
import { CARBON_SCORE_BASE, CARBON_SCORE_WORST } from '@/shared/constants/carbon.constants'

function calcScore(co2Gpm: number): number {
  const raw = (1 - (co2Gpm - CARBON_SCORE_BASE) / (CARBON_SCORE_WORST - CARBON_SCORE_BASE)) * 100
  return Math.round(Math.min(100, Math.max(0, raw)))
}

function scoreColor(score: number): string {
  if (score >= 70) return 'var(--color-carbon-low)'
  if (score >= 40) return 'var(--color-carbon-medium)'
  return 'var(--color-carbon-high)'
}

function scoreLabel(score: number): string {
  if (score >= 70) return '좋음'
  if (score >= 40) return '보통'
  return '위험'
}

export function CarbonScoreWidget() {
  const { data, isLoading, isError } = useClusterCarbon()
  const score = data ? calcScore(data.co2Gpm) : null

  return (
    <KpiCard title="탄소 효율 점수" isLoading={isLoading} isError={isError} updatedAt={data?.timestamp}>
      {data && score !== null && (
        <>
          <div className={styles.valueRow}>
            <span className={styles.value} style={{ color: scoreColor(score) }}>
              {score}
            </span>
            <span className={styles.unit}>/ 100</span>
          </div>
          <div className={styles.scoreBar}>
            <div
              className={styles.scoreFill}
              style={{ width: `${score}%`, backgroundColor: scoreColor(score) }}
            />
          </div>
          <div className={styles.meta}>
            <span className={styles.dot} style={{ color: scoreColor(score) }}>
              ● {scoreLabel(score)}
            </span>
            <span className={styles.sub}>
              기준 {CARBON_SCORE_BASE}–{CARBON_SCORE_WORST} gCO₂/min
            </span>
          </div>
        </>
      )}
    </KpiCard>
  )
}
