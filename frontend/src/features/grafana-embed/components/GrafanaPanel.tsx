import { Suspense } from 'react'

interface GrafanaPanelProps {
  panelId: number
  height?: number
  /** Grafana 대시보드 변수 (var-xxx 쿼리스트링으로 전달) */
  variables?: Record<string, string>
  title?: string
  className?: string
}

function buildGrafanaUrl(panelId: number, variables: Record<string, string>): string {
  const baseUrl = import.meta.env.VITE_GRAFANA_URL ?? 'http://localhost:30300'
  const dashUid = import.meta.env.VITE_GRAFANA_DASHBOARD_UID ?? 'greenops-overview'
  const orgId = import.meta.env.VITE_GRAFANA_ORG_ID ?? '1'

  const varParams = Object.entries(variables)
    .map(([k, v]) => `var-${k}=${encodeURIComponent(v)}`)
    .join('&')

  // kiosk: 헤더/네비 숨김, theme=dark: 다크모드, 기본 7일 범위
  const base = `${baseUrl}/d-solo/${dashUid}?orgId=${orgId}&panelId=${panelId}&theme=dark&kiosk&from=now-7d&to=now`
  return varParams ? `${base}&${varParams}` : base
}

export function GrafanaPanel({
  panelId,
  height = 300,
  variables = {},
  title,
  className = '',
}: GrafanaPanelProps) {
  const src = buildGrafanaUrl(panelId, variables)

  return (
    <div className={`grafana-panel-wrapper ${className}`} style={{ width: '100%' }}>
      {title && (
        <p style={{ fontSize: 12, color: '#8e8e8e', marginBottom: 4 }}>
          {title}
        </p>
      )}
      <iframe
        src={src}
        width="100%"
        height={height}
        frameBorder="0"
        title={title ?? `Grafana Panel ${panelId}`}
      />
    </div>
  )
}

/** Grafana 전체 대시보드 embed (단일 iframe) */
export function GrafanaDashboard({
  height = 900,
  variables = {},
}: Pick<GrafanaPanelProps, 'height' | 'variables'>) {
  const baseUrl = import.meta.env.VITE_GRAFANA_URL ?? 'http://localhost:30300'
  const dashUid = import.meta.env.VITE_GRAFANA_DASHBOARD_UID ?? 'greenops-overview'
  const orgId = import.meta.env.VITE_GRAFANA_ORG_ID ?? '1'

  const varParams = Object.entries(variables)
    .map(([k, v]) => `var-${k}=${encodeURIComponent(v)}`)
    .join('&')

  const src = `${baseUrl}/d/${dashUid}?orgId=${orgId}&theme=dark&kiosk${varParams ? `&${varParams}` : ''}`

  return (
    <iframe
      src={src}
      width="100%"
      height={height}
      frameBorder="0"
      title="GreenOps Carbon Dashboard"
    />
  )
}

export const PANEL_IDS = {
  CLUSTER_CO2_RATE: 1,
  DAILY_TOTAL: 2,
  CARBON_SCORE: 3,
  NAMESPACE_RANK: 4,
  CO2_TREND: 5,
  HEATMAP: 6,
} as const
