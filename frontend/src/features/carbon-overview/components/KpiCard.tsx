import type { ReactNode } from 'react'
import styles from './KpiCard.module.css'

interface KpiCardProps {
  title: string
  children: ReactNode
  isLoading?: boolean
  isError?: boolean
  updatedAt?: string | null
}

export function KpiCard({ title, children, isLoading, isError, updatedAt }: KpiCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.title}>{title}</span>
        {updatedAt && !isLoading && (
          <span className={styles.updated}>
            {new Date(updatedAt).toLocaleTimeString('ko-KR')}
          </span>
        )}
      </div>
      <div className={styles.body}>
        {isLoading && <div className={styles.skeleton} />}
        {!isLoading && isError && <div className={styles.error}>데이터 조회 실패</div>}
        {!isLoading && !isError && children}
      </div>
    </div>
  )
}
