import { BrowserRouter } from 'react-router-dom'

import { AppRouter } from './Router'
import { QueryProvider } from './providers/QueryProvider'

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </QueryProvider>
  )
}
