import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, MapPin, Phone, Mail, ArrowLeft, AlertCircle, ExternalLink } from 'lucide-react'
import { apiClient, Lab } from '../api/client'

export default function LabMatcher() {
  const [searchTerm, setSearchTerm] = useState('')
  const [city, setCity] = useState('')
  const [labType, setLabType] = useState('')
  const [labs, setLabs] = useState<Lab[]>([])
  const [total, setTotal] = useState(0)
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const fetchLabs = async (q?: string, cityVal?: string, typeVal?: string) => {
    setLoading(true)
    setError('')
    const response = await apiClient.searchLabs({
      q: q || undefined,
      city: cityVal || undefined,
      lab_type: typeVal || undefined,
    })
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setLabs(response.data.labs)
      setTotal(response.data.total)
      setNote(response.data.note)
    }
    setLoading(false)
    setSearched(true)
  }

  const handleSearch = () => {
    fetchLabs(searchTerm, city, labType)
  }

  // Load all labs on mount
  useEffect(() => {
    fetchLabs()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/dashboard" className="text-gray-600 hover:text-primary-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Smart Lab Matcher</h1>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Find Laboratories</h2>
            <div className="grid md:grid-cols-4 gap-4 mb-4">
              <input
                type="text"
                placeholder="Search by name or specialty..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
              />
              <select
                value={labType}
                onChange={(e) => setLabType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
              >
                <option value="">All Types</option>
                <option value="BIS_RECOGNIZED">BIS Recognized</option>
                <option value="NABL">NABL Accredited</option>
                <option value="GOVERNMENT">Government</option>
                <option value="PRIVATE">Private</option>
              </select>
              <input
                type="text"
                placeholder="City..."
                value={city}
                onChange={(e) => setCity(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm"
              />
              <button
                onClick={handleSearch}
                disabled={loading}
                className="bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 flex items-center justify-center gap-2 disabled:opacity-50 text-sm"
              >
                <Search className="w-4 h-4" />
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {note && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                {note}
              </div>
            )}
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {error}
            </div>
          )}

          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading laboratories...</div>
          ) : searched && labs.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl shadow-sm">
              <Search className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-600 font-medium">No laboratories found</p>
              <p className="text-gray-400 text-sm mt-1">
                Try a different search term or check{' '}
                <a href="https://www.nabl-india.org" target="_blank" rel="noopener noreferrer" className="text-primary-600 underline">
                  NABL
                </a>{' '}
                or{' '}
                <a href="https://www.bis.gov.in" target="_blank" rel="noopener noreferrer" className="text-primary-600 underline">
                  BIS
                </a>{' '}
                directly.
              </p>
            </div>
          ) : (
            <>
              {total > 0 && (
                <p className="text-sm text-gray-500 mb-4">{total} laborator{total === 1 ? 'y' : 'ies'} found</p>
              )}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {labs.map((lab) => (
                  <div key={lab.id} className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 text-sm">{lab.name}</h3>
                        {(lab.city || lab.state) && (
                          <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
                            <MapPin className="w-3 h-3" />
                            {[lab.city, lab.state].filter(Boolean).join(', ')}
                          </div>
                        )}
                      </div>
                      {lab.lab_type && (
                        <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs ml-2 flex-shrink-0">
                          {lab.lab_type.replace('_', ' ')}
                        </span>
                      )}
                    </div>

                    {lab.scope_of_testing && (
                      <div className="mb-3">
                        <div className="text-xs font-medium text-gray-600 mb-1">Scope</div>
                        <div className="text-xs text-gray-500">{lab.scope_of_testing}</div>
                      </div>
                    )}

                    {lab.capabilities && lab.capabilities.length > 0 && (
                      <div className="mb-3">
                        <div className="text-xs font-medium text-gray-600 mb-1">Capabilities</div>
                        <div className="flex flex-wrap gap-1">
                          {lab.capabilities.slice(0, 4).map((cap, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                              {cap}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="space-y-1 text-xs text-gray-500">
                      {lab.contact_phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="w-3 h-3" />
                          {lab.contact_phone}
                        </div>
                      )}
                      {lab.contact_email && (
                        <div className="flex items-center gap-2">
                          <Mail className="w-3 h-3" />
                          {lab.contact_email}
                        </div>
                      )}
                      {lab.nabl_accreditation_number && (
                        <div className="text-xs text-green-600">
                          NABL: {lab.nabl_accreditation_number}
                        </div>
                      )}
                    </div>

                    {lab.verification_status === 'DEMO' && (
                      <p className="text-xs text-orange-500 mt-3">⚠ Demo data — verify with NABL/BIS</p>
                    )}

                    {lab.website && (
                      <a
                        href={lab.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-3 w-full flex items-center justify-center gap-2 border border-primary-600 text-primary-600 py-2 rounded-lg hover:bg-primary-50 text-sm"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Visit Website
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
