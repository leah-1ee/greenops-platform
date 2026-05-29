import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { useCarbonHistory } from '../hooks/useCarbonHistory'
import { KpiCard } from './KpiCard'
import styles from './TrendChartWidget.module.css'
import { CARBON_THRESHOLDS } from '@/shared/constants/carbon.constants'

export function TrendChartWidget() {
  const history = useCarbonHistory()

  return (
    <KpiCard title="CO₂ 배출 추세 (실시간)" isLoading={history.length === 0}>
      {history.length > 0 && (
        <div className={styles.wrap}>
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={history} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="co2Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#73BF69" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#73BF69" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2c2f36" vertical={false} />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 10, fill: '#5c6370' }}
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 10, fill: '#5c6370' }}
                tickLine={false}
                axisLine={false}
                domain={[0, 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#181b1f',
                  border: '1px solid #2c2f36',
                  borderRadius: 4,
                  fontSize: 12,
                }}
                labelStyle={{ color: '#8e8e8e' }}
                itemStyle={{ color: '#73BF69' }}
                formatter={(val: number) => [`${val} gCO₂/min`, 'CO₂']}
              />
              <ReferenceLine y={CARBON_THRESHOLDS.LOW_MAX}    stroke="#FADE2A" strokeDasharray="4 3" strokeWidth={1} />
              <ReferenceLine y={CARBON_THRESHOLDS.MEDIUM_MAX} stroke="#F2495C" strokeDasharray="4 3" strokeWidth={1} />
              <Area
                type="monotone"
                dataKey="co2Gpm"
                stroke="#73BF69"
                strokeWidth={2}
                fill="url(#co2Grad)"
                dot={false}
                activeDot={{ r: 4, strokeWidth: 0 }}
              />
            </AreaChart>
          </ResponsiveContainer>
          <div className={styles.legend}>
            <span style={{ color: '#FADE2A' }}>── {CARBON_THRESHOLDS.LOW_MAX} 주의</span>
            <span style={{ color: '#F2495C' }}>── {CARBON_THRESHOLDS.MEDIUM_MAX} 위험</span>
          </div>
        </div>
      )}
    </KpiCard>
  )
}
