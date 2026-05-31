export const REGION_CODE = import.meta.env.VITE_REGION_CODE ?? 'ap-northeast-2'
export const CARBON_INTENSITY = Number(import.meta.env.VITE_CARBON_INTENSITY ?? 415) // gCO₂/kWh
export const PUE = Number(import.meta.env.VITE_PUE ?? 1.15)

// Grafana threshold와 동일하게 유지
export const CARBON_THRESHOLDS = {
  LOW_MAX: 50,     // < 50 → low (green)
  MEDIUM_MAX: 100, // 50–100 → medium (yellow)
                   // ≥ 100 → high (red)
} as const

export const CARBON_SCORE_BASE = 30
export const CARBON_SCORE_WORST = 100
export const KEPLER_SCRAPE_INTERVAL_MS = 15_000
export const DAILY_CARBON_BUDGET_G = 1_000
