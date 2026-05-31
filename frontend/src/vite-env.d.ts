/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_ENABLE_MOCK: string
  readonly VITE_GRAFANA_URL: string
  readonly VITE_GRAFANA_CARBON_PANEL_ID: string
  readonly VITE_GRAFANA_NAMESPACE_PANEL_ID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
