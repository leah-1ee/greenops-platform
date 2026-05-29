import { Link, useSearchParams } from 'react-router-dom'

import { NamespaceRankWidget } from '@/features/carbon-overview'
import { NamespaceTable } from '@/features/namespace-drilldown'

import styles from './PlaceholderPage.module.css'

export function NamespacePage() {
  const [params] = useSearchParams()
  const ns = params.get('ns') ?? undefined

  return (
    <div className={styles.page}>
      {ns && (
        <div className={styles.subHeader}>
          <nav className={styles.breadcrumb}>
            <Link to="/namespace">Namespace</Link>
            <span>/</span>
            <span>{ns.replace('greenops-', '')}</span>
          </nav>
          <Link to="/namespace" className={styles.weekBadge} style={{ textDecoration: 'none' }}>
            ← 전체 보기
          </Link>
        </div>
      )}

      <main className={styles.main}>
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Namespace CO₂ 순위</h2>
          <NamespaceRankWidget />
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Pod 상세
            {ns
              ? <small className={styles.sectionNote}> — {ns.replace('greenops-', '')} · 15s 갱신</small>
              : <small className={styles.sectionNote}> — 전체 · 15s 갱신</small>
            }
          </h2>
          <NamespaceTable namespace={ns} />
        </section>
      </main>
    </div>
  )
}
