import { NavLink } from 'react-router-dom'
import styles from './AppLayout.module.css'

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.titleRow}>
          <span className={styles.logo}>🌿</span>
          <div>
            <h1 className={styles.title}>GreenOps Platform</h1>
            <p className={styles.subtitle}>
              Kubernetes 탄소 배출 실시간 모니터링 · 서울 리전 · Kepler eBPF 15s
            </p>
          </div>
        </div>

        <nav className={styles.nav}>
          <NavLink
            to="/"
            end
            className={({ isActive }) => `${styles.navLink}${isActive ? ` ${styles.navActive}` : ''}`}
          >
            Overview
          </NavLink>
          <NavLink
            to="/namespace"
            className={({ isActive }) => `${styles.navLink}${isActive ? ` ${styles.navActive}` : ''}`}
          >
            Namespace
          </NavLink>
          <NavLink
            to="/ai"
            className={({ isActive }) => `${styles.navLink}${isActive ? ` ${styles.navActive}` : ''}`}
          >
            AI 스케줄러
          </NavLink>
        </nav>

        <div className={styles.statusBadge}>
          ● LIVE
        </div>
      </header>

      <div className={styles.content}>
        {children}
      </div>
    </div>
  )
}
