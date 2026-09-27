import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Search, AlertCircle, BookOpen, Tag } from 'lucide-react';
import { apiClient, SearchRequest, SearchResponse, SearchSource } from '../api/client';

const CONFIDENCE_COLORS: Record<string, string> = {
  HIGH: 'bg-green-100 text-green-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-orange-100 text-orange-700',
  INSUFFICIENT_EVIDENCE: 'bg-red-100 text-red-700',
};

export default function KnowledgeSearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    const searchRequest: SearchRequest = {
      query,
      top_k: 5,
      use_hybrid_search: true,
    };

    const response = await apiClient.searchKnowledge(searchRequest);

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setResult(response.data);
    }

    setLoading(false);
  };

  const getSourceMeta = (source: SearchSource) => {
    try {
      return source.metadata_parsed || (source.metadata ? JSON.parse(source.metadata) : {});
    } catch {
      return {};
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/dashboard" className="text-gray-600 hover:text-primary-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base Search</h1>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8 max-w-4xl">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search BIS standards, e.g. 'curd', 'IS 1166', 'helmet certification'..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Search className="w-4 h-4" />
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <span className="text-red-700 text-sm">{error}</span>
          </div>
        )}

        {result && (
          <div className="space-y-5">
            {/* Intent & metadata bar */}
            {(result.intent || result.entities) && (
              <div className="flex flex-wrap gap-2 text-xs">
                {result.intent && result.intent !== 'UNKNOWN' && (
                  <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full flex items-center gap-1">
                    <Tag className="w-3 h-3" />
                    Intent: {result.intent}
                  </span>
                )}
                {result.entities?.is_numbers?.map((isn: string) => (
                  <span key={isn} className="px-2 py-1 bg-purple-50 text-purple-700 rounded-full">
                    IS: {isn}
                  </span>
                ))}
                {result.entities?.product && (
                  <span className="px-2 py-1 bg-green-50 text-green-700 rounded-full">
                    Product: {result.entities.product}
                  </span>
                )}
              </div>
            )}

            {/* Answer */}
            <div className="p-5 bg-white border border-gray-200 rounded-xl shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-primary-600" />
                  Answer
                </h2>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${CONFIDENCE_COLORS[result.confidence] || 'bg-gray-100 text-gray-600'}`}>
                  {result.confidence}
                </span>
              </div>
              <p className="text-gray-700 text-sm whitespace-pre-wrap leading-relaxed">{result.answer}</p>
              <div className="mt-3 text-xs text-gray-400">
                Sources used: {result.context_used}
              </div>
            </div>

            {/* Sources */}
            {result.sources && result.sources.length > 0 && (
              <div>
                <h2 className="text-base font-semibold text-gray-900 mb-3">Evidence Sources</h2>
                <div className="space-y-3">
                  {result.sources.map((source, index) => {
                    const meta = getSourceMeta(source);
                    const score = source.combined_score ?? source.similarity;
                    return (
                      <div key={source.chunk_id} className="p-4 bg-white border border-gray-200 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex flex-wrap gap-2">
                            <span className="text-xs font-medium text-gray-500">Source {index + 1}</span>
                            {meta.standard_number && (
                              <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                                {meta.standard_number}
                              </span>
                            )}
                            {meta.document_type && (
                              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                                {meta.document_type}
                              </span>
                            )}
                            {meta.source_authority && meta.source_authority !== 'UNVERIFIED_DEMO' && (
                              <span className="px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs">
                                {meta.source_authority}
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-gray-400 ml-2 flex-shrink-0">
                            {(score * 100).toFixed(0)}% relevance
                          </span>
                        </div>
                        <p className="text-gray-700 text-sm leading-relaxed">{source.content}</p>
                        {meta.source_authority === 'UNVERIFIED_DEMO' && (
                          <p className="text-xs text-orange-500 mt-2">⚠ Demo data — verify with official BIS sources</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {result.confidence === 'INSUFFICIENT_EVIDENCE' && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg text-sm text-orange-700">
                No sufficiently relevant authoritative information was found for this query in the current knowledge base.
                Please consult <a href="https://www.bis.gov.in" target="_blank" rel="noopener noreferrer" className="underline">bis.gov.in</a> for official guidance.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
