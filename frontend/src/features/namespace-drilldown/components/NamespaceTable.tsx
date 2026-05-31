import { usePodCarbonList } from '@/features/carbon-overview'
import styles from './NamespaceTable.module.css'
import type { CarbonLevel } from '@/shared/types'

const LEVEL_COLOR: Record<CarbonLevel, string> = {
  low:    'var(--color-carbon-low)',
  medium: 'var(--color-carbon-medium)',
  high:   'var(--color-carbon-high)',
}

interface Props {
  namespace?: string  // undefined = 전체 표시
}

export function NamespaceTable({ namespace }: Props) {
  const { data, isLoading, isError } = usePodCarbonList()

  const pods = data
    ? namespace
      ? data.filter(p => p.namespace === namespace)
      : data
    : []

  if (isLoading) return <div className={styles.state}>로딩 중...</div>
  if (isError)   return <div className={`${styles.state} ${styles.error}`}>Pod 데이터 조회 실패</div>
  if (pods.length === 0) return <div className={styles.state}>표시할 Pod가 없습니다.</div>

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Pod</th>
          <th>Namespace</th>
          <th>CO₂/min</th>
          <th>Power</th>
          <th>점유율</th>
          <th>레벨</th>
        </tr>
      </thead>
      <tbody>
        {pods.map(pod => (
          <tr key={pod.podName}>
            <td className={styles.mono}>{pod.podName}</td>
            <td className={styles.mono}>{pod.namespace.replace('greenops-', '')}</td>
            <td className={styles.mono}>{pod.co2Gpm}</td>
            <td className={styles.mono}>{pod.powerWatt.toFixed(3)}W</td>
            <td className={styles.mono}>{pod.sharePercent}%</td>
            <td>
              <span
                className={styles.badge}
                style={{ color: LEVEL_COLOR[pod.level], borderColor: LEVEL_COLOR[pod.level] }}
              >
                {pod.level}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
