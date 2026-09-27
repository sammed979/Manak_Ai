import { Link, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, Search, Shield, Settings, LogOut, Network } from 'lucide-react'
import { apiClient } from '../api/client'

export default function DashboardPage() {
  const navigate = useNavigate()

  const handleLogout = () => {
    apiClient.clearToken()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-primary-600">MANAK AI</div>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Welcome, User</span>
            <button onClick={handleLogout} className="text-gray-600 hover:text-primary-600">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        <div className="flex gap-8">
          <aside className="w-64 bg-white rounded-xl shadow-sm p-6 h-fit">
            <nav className="space-y-2">
              <NavLink icon={<LayoutDashboard />} label="Dashboard" active to="/dashboard" />
              <NavLink icon={<Search />} label="Knowledge Search" to="/knowledge" />
              <NavLink icon={<Shield />} label="Compliance Passport" to="/compliance-passport" />
              <NavLink icon={<FileText />} label="Document Analysis" to="/document-analysis" />
              <NavLink icon={<Search />} label="Lab Matcher" to="/lab-matcher" />
              <NavLink icon={<Network />} label="Knowledge Graph" to="/knowledge-graph" />
              <NavLink icon={<Settings />} label="Settings" />
            </nav>
          </aside>

          <main className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
            
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <StatCard title="Total Products" value="0" />
              <StatCard title="Standards Found" value="0" />
              <StatCard title="Compliance Score" value="0%" />
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <Link to="/compliance-passport">
                  <QuickActionCard title="Compliance Passport" description="Track your product's compliance journey" />
                </Link>
                <Link to="/knowledge">
                  <QuickActionCard title="Search Standards" description="Find relevant BIS standards" />
                </Link>
                <Link to="/document-analysis">
                  <QuickActionCard title="Document Analysis" description="Analyze compliance documents with AI" />
                </Link>
                <Link to="/lab-matcher">
                  <QuickActionCard title="Lab Matcher" description="Find verified laboratories" />
                </Link>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

function NavLink({ icon, label, active = false, to }: { icon: React.ReactNode, label: string, active?: boolean, to?: string }) {
  if (to) {
    return (
      <Link to={to} className={`flex items-center gap-3 px-4 py-3 rounded-lg w-full text-left ${
        active ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'
      }`}>
        {icon}
        {label}
      </Link>
    )
  }
  return (
    <button className={`flex items-center gap-3 px-4 py-3 rounded-lg w-full text-left ${
      active ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'
    }`}>
      {icon}
      {label}
    </button>
  )
}

function StatCard({ title, value }: { title: string, value: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h3 className="text-gray-600 text-sm font-medium mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

function QuickActionCard({ title, description }: { title: string, description: string }) {
  return (
    <button className="bg-gray-50 rounded-lg p-4 text-left hover:bg-gray-100 transition-colors">
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  )
}
