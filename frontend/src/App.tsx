import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import Dashboard from './pages/Dashboard'
import Matches from './pages/Matches'
import Analysis from './pages/Analysis'
import AnalysisHistory from './pages/AnalysisHistory'
import ProfitLoss from './pages/ProfitLoss'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/matches" element={<Matches />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/analysis/history" element={<AnalysisHistory />} />
        <Route path="/analysis/:id" element={<Analysis />} />
        <Route path="/profit-loss" element={<ProfitLoss />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
