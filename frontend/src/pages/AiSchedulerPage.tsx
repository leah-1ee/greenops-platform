import { useState } from 'react'

import { useClusterCarbon } from '@/features/carbon-overview'
import { useScheduleLatest, useScheduleHistory, useScheduleRecommend } from '@/features/ai-scheduler'
import type { SchedulingRecommendation, SchedulingSlot } from '@/shared/types'

import styles from './AiSchedulerPage.module.css'

const LEVEL_COLOR = { low: 'var(--color-carbon-low)', medium: 'var(--color-carbon-medium)', high: 'var(--color-carbon-high)' }
const RANK_ICON = ['🥇', '🥈', '🥉']

function fmt(iso: string, opts: Intl.DateTimeFormatOptions) {
  return new Date(iso).toLocaleString('ko-KR', opts)
}

function SlotList({ recommendation, onApply, applying }: {
  recommendation: SchedulingRecommendation
  onApply?: (id: string) => void
  applying?: boolean
}) {
  return (
    <ul className={styles.slotList}>
      {recommendation.slots.map((slot: SchedulingSlot) => (
        <li key={slot.rank} className={styles.slotItem} data-top={slot.isTopRecommendation}>
          <div className={styles.slotRank}>{RANK_ICON[slot.rank - 1] ?? slot.rank}</div>
          <div className={styles.slotBody}>
            <div className={styles.slotTime}>
              {fmt(slot.startTime, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              {' — '}
              {fmt(slot.endTime, { hour: '2-digit', minute: '2-digit' })}
              <span className={styles.slotDuration}> ({slot.durationHours}h)</span>
            </div>
            <div className={styles.slotReason}>{slot.reason}</div>
            {slot.isTopRecommendation && onApply && (
              recommendation.applied
                ? <div className={styles.appliedBadge}>✓ 적용됨</div>
                : (
                  <button
                    className={styles.applyBtn}
                    onClick={() => onApply(recommendation.id)}
                    disabled={applying}
                  >
                    스케줄 적용
                  </button>
                )
            )}
          </div>
          <div className={styles.slotStats}>
            <div className={styles.slotIntensity}>
              {slot.carbonIntensity} <small>gCO₂/kWh</small>
            </div>
            <div className={styles.slotSaving}>-{slot.savingPercent}% CO₂</div>
          </div>
        </li>
      ))}
    </ul>
  )
}

export function AiSchedulerPage() {
  const { data: clusterData } = useClusterCarbon()
  const { data: latest, isLoading: latestLoading, isError: latestError } = useScheduleLatest()
  const { data: history, isLoading: histLoading } = useScheduleHistory()
  const { mutate: recommend, data: newResult, isPending, isError: recommendError } = useScheduleRecommend()
  const [applying, setApplying] = useState(false)

  function handleApply(recommendationId: string) {
    setApplying(true)
    setTimeout(() => setApplying(false), 1000) // MSW mock 응답 후 상태 초기화
  }

  const displayRecommendation = newResult ?? latest

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        {/* 현재 탄소 배출 현황 */}
        <div className={styles.statusBanner}>
          <div className={styles.statusCard}>
            <div className={styles.statusLabel}>현재 탄소 배출률</div>
            <div
              className={styles.statusValue}
              style={{ color: clusterData ? LEVEL_COLOR[clusterData.level] : 'var(--color-text)' }}
            >
              {clusterData ? `${clusterData.co2Gpm} gCO₂/min` : '—'}
            </div>
            <div className={styles.statusMeta}>
              {clusterData ? `${clusterData.powerWatt.toFixed(2)}W · ${clusterData.region.name}` : '데이터 조회 중'}
            </div>
          </div>
          <div className={styles.statusCard}>
            <div className={styles.statusLabel}>탄소강도 (리전)</div>
            <div className={styles.statusValue} style={{ color: 'var(--color-carbon-medium)' }}>
              {clusterData ? `${clusterData.region.carbonIntensity}` : '—'}
            </div>
            <div className={styles.statusMeta}>
              gCO₂/kWh · PUE {clusterData?.region.pue ?? '—'} · IEA 2024
            </div>
          </div>
          <div className={styles.statusCard}>
            <div className={styles.statusLabel}>최적화 가능 절감</div>
            <div className={styles.statusValue} style={{ color: 'var(--color-carbon-low)' }}>
              {displayRecommendation?.slots[0] ? `${displayRecommendation.slots[0].savingPercent}%` : '—'}
            </div>
            <div className={styles.statusMeta}>
              {displayRecommendation?.slots[0]
                ? `최적 구간: ${fmt(displayRecommendation.slots[0].startTime, { hour: '2-digit', minute: '2-digit' })}`
                : 'AI 분석 후 확인 가능'}
            </div>
          </div>
        </div>

        {/* AI 추천 섹션 */}
        <section className={styles.section}>
          <div className={styles.sectionHead}>
            <h2 className={styles.sectionTitle}>
              최적 CronJob 실행 구간 Top 3
              <span className={styles.sectionNote}> — Carbon Aware SDK · 서울 리전</span>
            </h2>
            <button
              className={styles.recommendBtn}
              onClick={() => recommend()}
              disabled={isPending}
            >
              {isPending && <span className={styles.spinner} />}
              {isPending ? '분석 중...' : '새 AI 추천 받기'}
            </button>
          </div>

          {recommendError && (
            <div className={styles.errMsg}>AI 추천 API 연결 실패</div>
          )}

          {newResult && (
            <div className={styles.newResult}>
              <div className={styles.newResultLabel}>
                새 분석 결과 · {fmt(newResult.generatedAt, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </div>
              <SlotList recommendation={newResult} onApply={handleApply} applying={applying} />
            </div>
          )}

          {!newResult && latestLoading && (
            <div className={styles.loadingMsg}>최근 추천 불러오는 중...</div>
          )}

          {!newResult && latestError && (
            <div className={styles.empty}>
              <p>아직 AI 추천 내역이 없습니다.</p>
              <small>위 버튼을 눌러 첫 분석을 실행하세요.</small>
            </div>
          )}

          {!newResult && latest && (
            <>
              <div className={styles.sectionNote} style={{ marginBottom: 10 }}>
                최근 분석: {fmt(latest.generatedAt, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </div>
              <SlotList recommendation={latest} onApply={handleApply} applying={applying} />
            </>
          )}
        </section>

        {/* 히스토리 섹션 */}
        <section className={styles.section}>
          <div className={styles.sectionHead}>
            <h2 className={styles.sectionTitle}>추천 히스토리</h2>
          </div>

          {histLoading && <div className={styles.loadingMsg}>히스토리 불러오는 중...</div>}

          {!histLoading && (!history || history.length === 0) && (
            <div className={styles.empty}>히스토리가 없습니다.</div>
          )}

          {history && history.length > 0 && (
            <table className={styles.histTable}>
              <thead>
                <tr>
                  <th>분석 시각</th>
                  <th>최적 구간</th>
                  <th>절감율</th>
                  <th>탄소강도</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {history.map(item => (
                  <tr key={item.id}>
                    <td>{fmt(item.generatedAt, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</td>
                    <td>
                      {fmt(item.topSlot.startTime, { hour: '2-digit', minute: '2-digit' })}
                      {' — '}
                      {fmt(item.topSlot.endTime, { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ color: 'var(--color-carbon-low)' }}>-{item.topSlot.savingPercent}%</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{item.topSlot.carbonIntensity}</td>
                    <td>
                      <span className={styles.applied} data-applied={item.applied}>
                        {item.applied ? '적용됨' : '미적용'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  )
}
