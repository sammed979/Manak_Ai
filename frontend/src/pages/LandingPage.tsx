import { Link } from 'react-router-dom'
import { Bot, Shield, FileText, Search, Network, Globe } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-2xl font-bold text-primary-600">MANAK AI</div>
        <div className="space-x-4">
          <Link to="/login" className="text-gray-600 hover:text-primary-600">Login</Link>
          <Link to="/register" className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
            Register
          </Link>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            MANAK AI
          </h1>
          <p className="text-2xl text-primary-600 font-semibold mb-4">
            From Product to Compliance
          </p>
          <p className="text-lg text-gray-600 mb-8">
            An AI-powered assistant that helps industries and consumers understand Indian Standards, 
            BIS services, testing, certification, and compliance requirements.
          </p>
          <div className="space-x-4">
            <Link to="/dashboard" className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 inline-block">
              Ask MANAK AI
            </Link>
            <Link to="/dashboard" className="border-2 border-primary-600 text-primary-600 px-8 py-3 rounded-lg hover:bg-primary-50 inline-block">
              Explore Standards
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <Link to="/knowledge">
            <FeatureCard icon={<Bot />} title="AI Standards Search" description="Natural language search for BIS standards and requirements" />
          </Link>
          <Link to="/compliance-passport">
            <FeatureCard icon={<Shield />} title="Compliance Passport" description="Track your product's compliance journey in one place" />
          </Link>
          <Link to="/document-analysis">
            <FeatureCard icon={<FileText />} title="Document Analysis" description="Upload and analyze compliance documents with AI" />
          </Link>
          <Link to="/lab-matcher">
            <FeatureCard icon={<Search />} title="Smart Lab Matcher" description="Find verified laboratories for your testing needs" />
          </Link>
          <Link to="/knowledge-graph">
            <FeatureCard icon={<Network />} title="Knowledge Graph" description="Visualize relationships between standards and requirements" />
          </Link>
          <Link to="/knowledge">
            <FeatureCard icon={<Globe />} title="Multilingual AI" description="Interact in English, Hindi, and Kannada" />
          </Link>
        </div>

        <div className="mt-20 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Disclaimer</h2>
          <p className="text-gray-600">
            MANAK AI provides informational and decision-support guidance based on its indexed knowledge sources. 
            It is not an official BIS certification authority, legal advisor, or substitute for official BIS processes. 
            Users should verify critical compliance decisions with authoritative sources and appropriate professionals.
          </p>
        </div>
      </main>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
