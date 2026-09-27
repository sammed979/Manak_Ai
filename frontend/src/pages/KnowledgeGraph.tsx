import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Network, ArrowLeft, RefreshCw, AlertCircle } from 'lucide-react'
import { apiClient } from '../api/client'

interface GraphNode {
  id: string
  label: string
  type: string
  category?: string
}

interface GraphEdge {
  from: string
  to: string
  label?: string
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  stats: Record<string, number>
}

const NODE_COLORS: Record<string, string> = {
  standard: 'bg-blue-500',
  clause: 'bg-green-500',
  requirement: 'bg-yellow-500',
  scheme: 'bg-purple-500',
}

export default function KnowledgeGraph() {
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadGraph = async () => {
    setLoading(true)
    setError('')
    const response = await apiClient.request<GraphData>('/graph/')
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setGraphData(response.data)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadGraph()
  }, [])

  const getNodeEdges = (nodeId: string) => {
    if (!graphData) return []
    return graphData.edges.filter(e => e.from === nodeId || e.to === nodeId)
  }

  const getConnectedNodes = (nodeId: string) => {
    if (!graphData) return []
    const edges = getNodeEdges(nodeId)
    const connectedIds = edges.map(e => e.from === nodeId ? e.to : e.from)
    return graphData.nodes.filter(n => connectedIds.includes(n.id))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/dashboard" className="text-gray-600 hover:text-primary-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Graph</h1>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        <div className="grid md:grid-cols-4 gap-6">
          <div className="md:col-span-3">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Standards & Requirements Graph</h2>
                <button
                  onClick={loadGraph}
                  disabled={loading}
                  className="p-2 hover:bg-gray-100 rounded disabled:opacity-50"
                  title="Refresh"
                >
                  <RefreshCw className={`w-5 h-5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  {error}
                </div>
              )}

              {loading ? (
                <div className="h-96 flex items-center justify-center text-gray-500">
                  Loading graph from database...
                </div>
              ) : graphData && graphData.nodes.length > 0 ? (
                <div className="relative h-96 bg-gray-50 rounded-lg border border-gray-200 p-4 overflow-auto">
                  <div className="flex flex-wrap gap-4 justify-center">
                    {graphData.nodes.map((node) => (
                      <div
                        key={node.id}
                        onClick={() => setSelectedNode(node)}
                        className={`cursor-pointer transform hover:scale-105 transition-transform ${
                          selectedNode?.id === node.id ? 'ring-4 ring-primary-500 rounded-full' : ''
                        }`}
                      >
                        <div className={`w-14 h-14 rounded-full ${NODE_COLORS[node.type] || 'bg-gray-500'} flex items-center justify-center text-white font-bold text-xs mx-auto`}>
                          {node.type.charAt(0).toUpperCase()}
                        </div>
                        <div className="text-center mt-1 text-xs font-medium text-gray-800 max-w-20 truncate">
                          {node.label}
                        </div>
                        {node.category && (
                          <div className="text-center text-xs text-gray-400 max-w-20 truncate">
                            {node.category}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-96 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <Network className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p>No graph data available.</p>
                    <p className="text-sm text-gray-400 mt-1">Run the database seeder to populate standards data.</p>
                  </div>
                </div>
              )}

              <div className="mt-4 flex flex-wrap gap-4 text-sm">
                {Object.entries(NODE_COLORS).map(([type, color]) => (
                  <div key={type} className="flex items-center gap-2">
                    <div className={`w-4 h-4 ${color} rounded-full`} />
                    <span className="text-gray-600 capitalize">{type}s</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="md:col-span-1 space-y-4">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Node Details</h3>
              {selectedNode ? (
                <div className="space-y-3 text-sm">
                  <div>
                    <div className="text-gray-500 text-xs">Label</div>
                    <div className="font-medium text-gray-900">{selectedNode.label}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Type</div>
                    <div className="font-medium text-gray-900 capitalize">{selectedNode.type}</div>
                  </div>
                  {selectedNode.category && (
                    <div>
                      <div className="text-gray-500 text-xs">Category</div>
                      <div className="font-medium text-gray-900">{selectedNode.category}</div>
                    </div>
                  )}
                  <div>
                    <div className="text-gray-500 text-xs mb-1">Connected to</div>
                    <div className="space-y-1">
                      {getConnectedNodes(selectedNode.id).slice(0, 5).map(n => (
                        <div key={n.id} className="text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded">
                          {n.label}
                        </div>
                      ))}
                      {getConnectedNodes(selectedNode.id).length === 0 && (
                        <div className="text-xs text-gray-400">No connections</div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6 text-gray-500">
                  <Network className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm">Click a node to view details</p>
                </div>
              )}
            </div>

            {graphData && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Graph Statistics</h3>
                <div className="space-y-2 text-sm">
                  {Object.entries(graphData.stats).map(([key, val]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="font-medium text-gray-900">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
