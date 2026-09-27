import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Upload, ArrowLeft, AlertCircle, BookOpen } from 'lucide-react'
import { apiClient, DocumentAnalysisResponse } from '../api/client'

export default function DocumentAnalysis() {
  const [file, setFile] = useState<File | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [results, setResults] = useState<DocumentAnalysisResponse | null>(null)
  const [error, setError] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResults(null)
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    if (!apiClient.isAuthenticated()) {
      setError('Please log in to analyze documents.')
      return
    }

    setAnalyzing(true)
    setError('')
    setResults(null)

    const response = await apiClient.analyzeDocument(file)

    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setResults(response.data)
    }

    setAnalyzing(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/dashboard" className="text-gray-600 hover:text-primary-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Document Analysis</h1>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h2>
            <p className="text-sm text-gray-500 mb-4">
              Supported formats: PDF, DOCX, TXT. Maximum size: 10 MB.
            </p>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4 text-sm">
                Drag and drop your compliance document here, or click to browse
              </p>
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                accept=".pdf,.docx,.txt,.csv"
              />
              <label
                htmlFor="file-upload"
                className="inline-block bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 cursor-pointer text-sm"
              >
                Select File
              </label>
              {file && (
                <div className="mt-4 text-sm text-gray-600">
                  Selected: <span className="font-medium">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2 text-sm text-red-700">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                {error}
              </div>
            )}

            {file && (
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="mt-4 w-full bg-primary-600 text-white py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {analyzing ? 'Analyzing...' : (
                  <>
                    <FileText className="w-5 h-5" />
                    Analyze Document
                  </>
                )}
              </button>
            )}
          </div>

          {results && (
            <div className="bg-white rounded-xl shadow-sm p-6 space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">File:</span>{' '}
                  <span className="font-medium">{results.filename}</span>
                </div>
                <div>
                  <span className="text-gray-500">Size:</span>{' '}
                  <span className="font-medium">{(results.file_size / 1024).toFixed(1)} KB</span>
                </div>
                <div>
                  <span className="text-gray-500">Text extracted:</span>{' '}
                  <span className={`font-medium ${results.text_extracted ? 'text-green-600' : 'text-red-600'}`}>
                    {results.text_extracted ? `Yes (${results.text_length?.toLocaleString()} chars)` : 'No'}
                  </span>
                </div>
              </div>

              {!results.text_extracted && results.error && (
                <div className="p-3 bg-orange-50 border border-orange-200 rounded text-sm text-orange-700">
                  {results.error}
                </div>
              )}

              {results.is_numbers_found && results.is_numbers_found.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2 text-sm">IS Numbers Found in Document</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.is_numbers_found.map((isn, i) => (
                      <span key={i} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                        {isn}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {results.standards_found && results.standards_found.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2 text-sm">Matched Standards in Knowledge Base</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.standards_found.map((std, i) => (
                      <span key={i} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        {std}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {results.analysis && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2 text-sm">
                    <BookOpen className="w-4 h-4 text-primary-600" />
                    AI Analysis
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      results.analysis.confidence === 'HIGH' ? 'bg-green-100 text-green-700' :
                      results.analysis.confidence === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                      results.analysis.confidence === 'INSUFFICIENT_EVIDENCE' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {results.analysis.confidence}
                    </span>
                  </h3>
                  <p className="text-gray-700 text-sm whitespace-pre-wrap leading-relaxed bg-gray-50 p-4 rounded-lg">
                    {results.analysis.answer}
                  </p>
                </div>
              )}

              {results.disclaimer && (
                <p className="text-xs text-gray-400 border-t pt-4">{results.disclaimer}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
