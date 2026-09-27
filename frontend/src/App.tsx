import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import KnowledgeSearch from './pages/KnowledgeSearch'
import CompliancePassport from './pages/CompliancePassport'
import DocumentAnalysis from './pages/DocumentAnalysis'
import LabMatcher from './pages/LabMatcher'
import KnowledgeGraph from './pages/KnowledgeGraph'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/knowledge" element={<KnowledgeSearch />} />
        <Route path="/compliance-passport" element={<CompliancePassport />} />
        <Route path="/document-analysis" element={<DocumentAnalysis />} />
        <Route path="/lab-matcher" element={<LabMatcher />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
