import { Route, Routes } from 'react-router-dom'

import { AiSchedulerPage } from '@/pages/AiSchedulerPage'
import { NamespacePage } from '@/pages/NamespacePage'
import { OverviewPage } from '@/pages/OverviewPage'
import { AppLayout } from './AppLayout'

export function AppRouter() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/namespace" element={<NamespacePage />} />
        <Route path="/ai" element={<AiSchedulerPage />} />
        <Route path="*" element={<OverviewPage />} />
      </Routes>
    </AppLayout>
  )
}
