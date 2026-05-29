import { Link } from 'react-router-dom'
import { usePodCarbonList } from '../hooks/useClusterCarbon'
import { KpiCard } from './KpiCard'
import styles from './NamespaceRankWidget.module.css'
import type { CarbonLevel, PodCarbon } from '@/shared/types'

const LEVEL_COLOR: Record<CarbonLevel, string> = {
  low:    'var(--color-carbon-low)',
  medium: 'var(--color-carbon-medium)',
  high:   'var(--color-carbon-high)',
}

interface NsEntry {
  namespace: string
  co2Gpm: number
  podCount: number
  level: CarbonLevel
}

function groupByNamespace(pods: PodCarbon[]): NsEntry[] {
  const map = new Map<string, NsEntry>()
  for (const pod of pods) {
    const existing = map.get(pod.namespace)
    if (existing) {
      existing.co2Gpm = Math.round((existing.co2Gpm + pod.co2Gpm) * 1000) / 1000
      existing.podCount++
      if (pod.level === 'high') existing.level = 'high'
      else if (pod.level === 'medium' && existing.level === 'low') existing.level = 'medium'
    } else {
      map.set(pod.namespace, { namespace: pod.namespace, co2Gpm: pod.co2Gpm, podCount: 1, level: pod.level })
    }
  }
  return [...map.values()].sort((a, b) => b.co2Gpm - a.co2Gpm)
}

function fmtCo2(v: number): string {
  if (v >= 10)  return v.toFixed(1)
  if (v >= 1)   return v.toFixed(2)
  if (v >= 0.1) return v.toFixed(3)
  return v.toFixed(4)
}

export function NamespaceRankWidget() {
  const { data, isLoading, isError } = usePodCarbonList()
  const namespaces = data ? groupByNamespace(data) : []
  const maxCo2 = namespaces[0]?.co2Gpm ?? 1

  return (
    <KpiCard title="Namespace CO₂ 순위" isLoading={isLoading} isError={isError}>
      {namespaces.length > 0 && (
        <ul className={styles.list}>
          {namespaces.map((ns, i) => (
            <li key={ns.namespace} className={styles.row}>
              <span className={styles.rank}>{i + 1}</span>
              <div className={styles.body}>
                <div className={styles.nameRow}>
                  <Link
                    to={`/namespace?ns=${encodeURIComponent(ns.namespace)}`}
                    className={styles.nameLink}
                  >
                    {ns.namespace.replace('greenops-', '')}
                  </Link>
                  <span className={styles.value}>{fmtCo2(ns.co2Gpm)} gCO₂/min</span>
                </div>
                <div className={styles.bar}>
                  <div
                    className={styles.fill}
                    style={{
                      width: `${(ns.co2Gpm / maxCo2) * 100}%`,
                      backgroundColor: LEVEL_COLOR[ns.level],
                    }}
                  />
                </div>
                <span className={styles.podCount}>{ns.podCount} pod{ns.podCount > 1 ? 's' : ''}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </KpiCard>
  )
}
