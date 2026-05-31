import {
  ClusterRateWidget,
  DailyTotalWidget,
  CarbonScoreWidget,
  NamespaceRankWidget,
  TrendChartWidget,
} from '@/features/carbon-overview'
import { GrafanaPanel, PANEL_IDS } from '@/features/grafana-embed'

import styles from './OverviewPage.module.css'

export function OverviewPage() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <section className={styles.kpiRow}>
          <ClusterRateWidget />
          <DailyTotalWidget />
          <CarbonScoreWidget />
        </section>

        <section className={styles.chartRow}>
          <NamespaceRankWidget />
          <TrendChartWidget />
        </section>

        <section className={styles.heatmapRow}>
          <GrafanaPanel
            panelId={PANEL_IDS.HEATMAP}
            height={260}
            title="시간대별 탄소강도 히트맵 (7일)"
            variables={{ datasource: 'prometheus' }}
          />
        </section>
      </main>

      <footer className={styles.footer}>
        <span>GreenOps v{import.meta.env.VITE_APP_VERSION ?? '0.1.0'}</span>
        <span>·</span>
        <span>PUE 1.15 · 탄소강도 415 gCO₂/kWh (IEA 2024)</span>
        <span>·</span>
        <span>EU CSRD · K-ESG 기준</span>
      </footer>
    </div>
  )
}
