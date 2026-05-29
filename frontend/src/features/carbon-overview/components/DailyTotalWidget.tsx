import { useDailyCarbonSummary } from '../hooks/useClusterCarbon'
import { KpiCard } from './KpiCard'
import styles from './StatWidget.module.css'
import { DAILY_CARBON_BUDGET_G } from '@/shared/constants/carbon.constants'

export function DailyTotalWidget() {
  const { data, isLoading, isError } = useDailyCarbonSummary()

  const budgetPct  = data ? Math.min((data.totalCo2Grams / DAILY_CARBON_BUDGET_G) * 100, 100) : 0
  const isOverBudget = data ? data.totalCo2Grams >= DAILY_CARBON_BUDGET_G : false
  const displayValue = data
    ? data.totalCo2Grams >= 1000
      ? `${data.totalCo2Kg}`
      : `${data.totalCo2Grams}`
    : '—'
  const displayUnit = data && data.totalCo2Grams >= 1000 ? 'kgCO₂' : 'gCO₂'

  return (
    <KpiCard title="금일 누적 탄소" isLoading={isLoading} isError={isError} updatedAt={data?.timestamp}>
      {data && (
        <>
          <div className={styles.valueRow}>
            <span
              className={styles.value}
              style={{ color: isOverBudget ? 'var(--color-carbon-high)' : 'var(--color-text)' }}
            >
              {displayValue}
            </span>
            <span className={styles.unit}>{displayUnit}</span>
          </div>
          <div className={styles.budgetBar}>
            <div
              className={styles.budgetFill}
              style={{
                width: `${budgetPct}%`,
                backgroundColor: isOverBudget ? 'var(--color-carbon-high)' : 'var(--color-carbon-low)',
              }}
            />
          </div>
          <div className={styles.meta}>
            <span className={styles.sub}>
              일일 예산 {DAILY_CARBON_BUDGET_G}g 대비 {Math.round(budgetPct)}%
            </span>
          </div>
        </>
      )}
    </KpiCard>
  )
}
