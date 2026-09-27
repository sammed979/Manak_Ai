import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Shield, Plus, Search, ArrowLeft, AlertCircle, HelpCircle } from 'lucide-react'
import { apiClient, Product, ProductStandardMatch, ProductCreate } from '../api/client'

const CATEGORIES = [
  'FOOD', 'ELECTRICAL', 'METALS', 'PLASTICS', 'CONSTRUCTION',
  'AUTOMOTIVE', 'CHEMICALS', 'PRECIOUS_METALS', 'TEXTILES', 'OTHER',
]

export default function CompliancePassport() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [matches, setMatches] = useState<ProductStandardMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [matchLoading, setMatchLoading] = useState(false)
  const [error, setError] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [creating, setCreating] = useState(false)
  const [newProduct, setNewProduct] = useState<ProductCreate>({
    name: '', description: '', category: 'OTHER',
  })

  const isLoggedIn = apiClient.isAuthenticated()

  const loadProducts = async () => {
    if (!isLoggedIn) {
      setError('Please log in to view your products.')
      return
    }
    setLoading(true)
    setError('')
    const response = await apiClient.listProducts()
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setProducts(response.data)
    }
    setLoading(false)
  }

  const loadMatches = async (productId: string) => {
    setMatchLoading(true)
    const response = await apiClient.getProductMatches(productId)
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setMatches(response.data)
    }
    setMatchLoading(false)
  }

  const handleProductSelect = (product: Product) => {
    setSelectedProduct(product)
    setMatches([])
    loadMatches(product.id)
  }

  const handleMatchStandards = async () => {
    if (!selectedProduct) return
    setMatchLoading(true)
    setError('')
    const response = await apiClient.matchStandards(selectedProduct.id)
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setMatches(response.data)
    }
    setMatchLoading(false)
  }

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newProduct.name.trim()) return
    setCreating(true)
    setError('')
    const response = await apiClient.createProduct(newProduct)
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setProducts(prev => [...prev, response.data!])
      setShowCreateForm(false)
      setNewProduct({ name: '', description: '', category: 'OTHER' })
    }
    setCreating(false)
  }

  useEffect(() => {
    loadProducts()
  }, [])

  const getMandatoryBadge = (is_mandatory: string) => {
    if (is_mandatory === 'YES') return <span className="px-2 py-1 rounded text-xs bg-red-100 text-red-700">Mandatory</span>
    if (is_mandatory === 'NO') return <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-700">Voluntary</span>
    return <span className="px-2 py-1 rounded text-xs bg-gray-100 text-gray-600">Not Determined</span>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/dashboard" className="text-gray-600 hover:text-primary-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Compliance Passport</h1>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        {!isLoggedIn && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-300 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
            <span className="text-yellow-800">
              You need to <Link to="/login" className="underline font-medium">log in</Link> to use the Compliance Passport.
            </span>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6">
          {/* Left panel — product list */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl shadow-sm p-6 mb-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Your Products</h2>
                <button
                  onClick={() => setShowCreateForm(!showCreateForm)}
                  className="text-primary-600 hover:text-primary-700"
                  title="Add product"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              <button
                onClick={loadProducts}
                disabled={loading || !isLoggedIn}
                className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 mb-4 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Search className="w-4 h-4" />
                {loading ? 'Loading...' : 'Load Products'}
              </button>

              {error && (
                <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  {error}
                </div>
              )}

              {/* Create product form */}
              {showCreateForm && (
                <form onSubmit={handleCreateProduct} className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
                  <h3 className="font-medium text-gray-900 text-sm">New Product</h3>
                  <input
                    type="text"
                    placeholder="Product name *"
                    value={newProduct.name}
                    onChange={e => setNewProduct(p => ({ ...p, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-primary-500"
                    required
                  />
                  <textarea
                    placeholder="Description"
                    value={newProduct.description || ''}
                    onChange={e => setNewProduct(p => ({ ...p, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-primary-500"
                    rows={2}
                  />
                  <select
                    value={newProduct.category}
                    onChange={e => setNewProduct(p => ({ ...p, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-primary-500"
                  >
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      disabled={creating}
                      className="flex-1 bg-primary-600 text-white py-2 rounded text-sm hover:bg-primary-700 disabled:opacity-50"
                    >
                      {creating ? 'Creating...' : 'Create'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateForm(false)}
                      className="flex-1 bg-gray-200 text-gray-700 py-2 rounded text-sm hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}

              {/* Product list */}
              <div className="space-y-2">
                {loading ? (
                  <div className="text-center py-4 text-gray-500 text-sm">Loading products...</div>
                ) : products.length === 0 ? (
                  <div className="text-center py-6 text-gray-500">
                    <Shield className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm">No products found.</p>
                    <button
                      onClick={() => setShowCreateForm(true)}
                      className="mt-2 text-primary-600 text-sm hover:underline"
                    >
                      Create your first product
                    </button>
                  </div>
                ) : (
                  products.map((product) => (
                    <button
                      key={product.id}
                      onClick={() => handleProductSelect(product)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedProduct?.id === product.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium text-gray-900 text-sm">{product.name}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{product.category}</div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right panel — compliance details */}
          <div className="md:col-span-2">
            {selectedProduct ? (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-1">{selectedProduct.name}</h2>
                <div className="text-sm text-gray-500 mb-4">
                  Category: {selectedProduct.category}
                  {selectedProduct.brand && ` | Brand: ${selectedProduct.brand}`}
                </div>
                {selectedProduct.description && (
                  <p className="text-gray-600 text-sm mb-6">{selectedProduct.description}</p>
                )}

                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Applicable Standards</h3>
                  <button
                    onClick={handleMatchStandards}
                    disabled={matchLoading}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50"
                  >
                    {matchLoading ? 'Matching...' : 'Find Standards'}
                  </button>
                </div>

                {matchLoading ? (
                  <div className="text-center py-8 text-gray-500">Matching standards...</div>
                ) : matches.length > 0 ? (
                  <div className="space-y-3">
                    {matches.map((match) => (
                      <div key={match.id} className="p-4 border border-gray-200 rounded-lg hover:border-primary-200">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="font-medium text-gray-900 text-sm">
                              Match Score: {((match.match_score ?? 0) * 100).toFixed(1)}%
                            </div>
                            {match.match_reason && (
                              <div className="text-xs text-gray-500 mt-1">{match.match_reason}</div>
                            )}
                          </div>
                          {getMandatoryBadge(match.is_mandatory)}
                        </div>
                        {match.applicability_notes && (
                          <div className="text-xs text-gray-600 mt-2 p-2 bg-gray-50 rounded">
                            {match.applicability_notes}
                          </div>
                        )}
                      </div>
                    ))}
                    <p className="text-xs text-gray-400 mt-4">
                      Compliance status is based on indexed knowledge. Verify mandatory requirements with official BIS sources.
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <HelpCircle className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm">No standards matched yet.</p>
                    <p className="text-xs text-gray-400 mt-1">Click "Find Standards" to match applicable BIS standards.</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-6 text-center">
                <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a Product</h3>
                <p className="text-gray-500 text-sm">
                  Choose a product from the left panel to view its compliance passport.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
