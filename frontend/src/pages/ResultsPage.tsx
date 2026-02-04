import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText, Loader2, AlertCircle, Plus, CheckCircle2, Download } from 'lucide-react'
import { marked } from 'marked'
import ResultsContent from '../components/ResultsContent'
import { GujRAMLogo, GujaratPoliceLogo } from '../components/Logo'

const AVAILABLE_SECTIONS = [
  { id: 'ndps', label: 'NDPS Act', description: 'Narcotic Drugs and Psychotropic Substances Act' },
  { id: 'bns', label: 'BNS', description: 'Bharatiya Nyaya Sanhita' },
  { id: 'bnss', label: 'BNSS', description: 'Bharatiya Nagarik Suraksha Sanhita' },
  { id: 'bsa', label: 'BSA', description: 'Bharatiya Sakshya Adhiniyam' },
  { id: 'investigation_plan', label: 'Investigation Plan', description: 'Detailed investigation roadmap' },
  { id: 'historical_cases', label: 'Historical Cases', description: 'Similar past legal cases' },
  { id: 'timeline', label: 'Timeline', description: 'Investigation & legal timeline' },
  { id: 'evidence', label: 'Evidence Checklist', description: 'Evidence collection requirements' },
  { id: 'dos_and_donts', label: "Do's & Don'ts", description: 'Guidelines for law enforcement' },
  { id: 'weaknesses', label: 'Prosecution Weaknesses', description: 'Potential case weaknesses' },
  { id: 'defence_rebuttal', label: 'Defence & Rebuttal', description: 'Defence perspective and prosecution rebuttal' },
  { id: 'court_summary', label: 'Summary for Court', description: 'Comprehensive court summary for prosecution' },
  { id: 'chargesheet', label: 'Chargesheet', description: 'Formal chargesheet with relevant sections' },
]

interface WorkflowState {
  workflow_id?: string
  pdf_filename?: string
  fir_facts?: Record<string, string>
  ndps_sections?: Array<{
    section_number: string
    section_description: string
    why_section_is_relevant: string
    source?: string
  }>
  bns_sections?: Array<{
    section_number: string
    section_description: string
    why_section_is_relevant: string
    source?: string
  }>
  bnss_sections?: Array<{
    section_number: string
    section_description: string
    why_section_is_relevant: string
    source?: string
  }>
  bsa_sections?: Array<{
    section_number: string
    section_description: string
    why_section_is_relevant: string
    source?: string
  }>
  investigation_plan?: Array<{
    title: string
    date_range?: string
    description: string
  }>
  investigation_and_legal_timeline?: {
    date_string: string
    timeline: string
  }
  evidence_checklist?: string
  dos?: string[]
  donts?: string[]
  potential_prosecution_weaknesses?: Record<string, string>
  next_steps?: string[]
  historical_cases?: Array<{
    title: string
    url?: string
    summary: string
  }>
  defence_perspective_rebuttal?: Array<{
    defence_perspective: string[]
    rebuttal: string[]
  }>
  summary_for_the_court?: {
    case_title: string
    ndps_sections: string[]
    core_issue: string
    date_and_place: string
    recovery: string
    quantity: string
    safeguards: string[]
    conscious_possession_proven: string[]
    procedural_compliance: string[]
    legal_position: string[]
    judicial_balance: string
    prosecution_prayer: string[]
  }
  chargesheet?: {
    case_title: string
    ndps_sections: string[]
    bns_sections: string[]
    bnss_sections: string[]
    bsa_sections: string[]
    core_issue: string
    date_and_place: string
    recovery: string
    quantity: string
    safeguards: string[]
    conscious_possession_proven: string[]
    procedural_compliance: string[]
    legal_position: string[]
    judicial_balance: string
    prosecution_prayer: string[]
  }
  sections?: string[]  // Selected sections
  stats?: {
    ndps_count: number
    bns_count: number
    bnss_count: number
    bsa_count: number
    next_steps_count: number
  }
}

export default function ResultsPage() {
  const { workflowId } = useParams<{ workflowId: string }>()
  const navigate = useNavigate()
  const [state, setState] = useState<WorkflowState | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddSections, setShowAddSections] = useState(false)
  const [selectedNewSections, setSelectedNewSections] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`/api/results/${workflowId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch results')
        }
        const data = await response.json()
        setState(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    if (workflowId) {
      fetchResults()
    }
  }, [workflowId])

  const handleAddSections = async () => {
    if (!workflowId || selectedNewSections.length === 0) {
      setError('Please select at least one section to generate')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('sections', JSON.stringify(selectedNewSections))
      formData.append('workflow_id', workflowId)

      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (response.ok && data.success) {
        // Refresh results
        const resultsResponse = await fetch(`/api/results/${workflowId}`)
        if (resultsResponse.ok) {
          const updatedData = await resultsResponse.json()
          setState(updatedData)
          setShowAddSections(false)
          setSelectedNewSections([])
        }
      } else {
        setError(data.detail || 'Error generating additional sections')
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const getAvailableSections = () => {
    const existingSections = state?.sections || []
    return AVAILABLE_SECTIONS.filter(section => !existingSections.includes(section.id))
  }

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-[#CECAB1]">
        <div className="bg-white rounded-xl shadow-lg p-4 mb-6 flex items-center justify-between w-full max-w-4xl">
          <GujRAMLogo size="md" />
          <div className="text-center flex-1 mx-4">
            <div className="text-[#1e3a8a] px-6 py-3 text-base font-bold">
              AI-Powered Legal Investigation Assistant
            </div>
            <div className="text-xs text-gray-600 mt-2 font-medium">
              Gujarat Narcotics RAG-based LLM Module
            </div>
          </div>
          <GujaratPoliceLogo size="md" />
        </div>
        <div className="text-center bg-white rounded-xl shadow-lg p-8">
          <Loader2 className="w-12 h-12 animate-spin text-[#5F4C24] mx-auto mb-4" />
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    )
  }

  if (error || !state) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-6">{error || 'Results not found'}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-[#5F4C24] text-white px-6 py-2 rounded-lg hover:bg-[#4A3B1C] transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#CECAB1] p-4 md:p-8 flex flex-col">
      {/* Header with Logos */}
      <div className="max-w-7xl mx-auto w-full mb-6">
        <div className="bg-white rounded-xl shadow-lg p-4 flex items-center justify-between">
          <GujRAMLogo size="md" />
          <div className="text-center flex-1 mx-4">
            <div className="text-[#1e3a8a] px-6 py-3 text-base font-bold">
              AI-Powered Legal Investigation Assistant
            </div>
            <div className="text-xs text-gray-600 mt-2 font-medium">
              Gujarat Narcotics RAG-based LLM Module
            </div>
          </div>
          <GujaratPoliceLogo size="md" />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1">
        <div className="max-w-7xl mx-auto bg-white rounded-2xl shadow-2xl p-6 md:p-8 animate-fade-in">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-[#5F4C24] hover:text-[#4A3B1C] transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-semibold">Upload New FIR</span>
            </button>
            <button
              onClick={async () => {
                if (!workflowId || isDownloading) return
                setIsDownloading(true)
                try {
                  const response = await fetch(`/api/document/${workflowId}`)
                  if (!response.ok) {
                    throw new Error('Failed to generate document')
                  }
                  const blob = await response.blob()
                  const url = window.URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `FIR_Report_${workflowId}.docx`
                  document.body.appendChild(a)
                  a.click()
                  window.URL.revokeObjectURL(url)
                  document.body.removeChild(a)
                } catch (err) {
                  console.error('Error downloading document:', err)
                  alert('Failed to generate document. Please try again.')
                } finally {
                  setIsDownloading(false)
                }
              }}
              disabled={isDownloading}
              className="flex items-center gap-2 bg-[#5F4C24] text-white px-4 py-2 rounded-lg hover:bg-[#4A3B1C] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  <span>Generate Document</span>
                </>
              )}
            </button>
          </div>

        <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-8 pb-6 border-b border-gray-200">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Legal Analysis Results</h1>
            {state.pdf_filename && (
              <div className="flex items-center gap-2 text-gray-600">
                <FileText className="w-4 h-4" />
                <span className="text-sm">{state.pdf_filename}</span>
              </div>
            )}
          </div>
          {state.workflow_id && (
            <div className="mt-4 md:mt-0 bg-gray-100 px-4 py-2 rounded-lg">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Workflow ID</div>
              <div className="text-sm font-mono text-gray-900">{state.workflow_id.slice(0, 8)}...</div>
            </div>
          )}
        </div>

        {state.stats && (() => {
          const selectedSections = state.sections || []
          const statsToShow = []
          
          if (selectedSections.includes('ndps') && state.stats.ndps_count > 0) {
            statsToShow.push({ label: 'NDPS', value: state.stats.ndps_count })
          }
          if (selectedSections.includes('bns') && state.stats.bns_count > 0) {
            statsToShow.push({ label: 'BNS', value: state.stats.bns_count })
          }
          if (selectedSections.includes('bnss') && state.stats.bnss_count > 0) {
            statsToShow.push({ label: 'BNSS', value: state.stats.bnss_count })
          }
          if (selectedSections.includes('bsa') && state.stats.bsa_count > 0) {
            statsToShow.push({ label: 'BSA', value: state.stats.bsa_count })
          }
          if (state.stats.next_steps_count > 0) {
            statsToShow.push({ label: 'Next Steps', value: state.stats.next_steps_count })
          }
          
          return statsToShow.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
              {statsToShow.map((stat) => (
                <StatCard key={stat.label} label={stat.label} value={stat.value} />
              ))}
            </div>
          ) : null
        })()}

        {/* Add More Sections Section */}
        {getAvailableSections().length > 0 && (
          <div className="mb-8 p-4 bg-[#CECAB1]/20 border border-[#5F4C24]/20 rounded-lg">
            {!showAddSections ? (
              <button
                onClick={() => setShowAddSections(true)}
                className="flex items-center gap-2 text-[#5F4C24] hover:text-[#4A3B1C] font-semibold"
              >
                <Plus className="w-5 h-5" />
                <span>Generate Additional Sections</span>
              </button>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Select Additional Sections</h3>
                  <button
                    onClick={() => {
                      setShowAddSections(false)
                      setSelectedNewSections([])
                    }}
                    className="text-gray-600 hover:text-gray-800 text-sm"
                  >
                    Cancel
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {getAvailableSections().map((section) => (
                    <label
                      key={section.id}
                      className={`flex items-center gap-2 p-3 bg-white rounded-lg border-2 cursor-pointer transition-all ${
                        selectedNewSections.includes(section.id)
                          ? 'border-[#5F4C24] bg-[#CECAB1]/40'
                          : 'border-gray-200 hover:border-[#5F4C24] hover:bg-[#CECAB1]/20'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedNewSections.includes(section.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedNewSections([...selectedNewSections, section.id])
                          } else {
                            setSelectedNewSections(selectedNewSections.filter(id => id !== section.id))
                          }
                        }}
                        className="w-4 h-4 text-[#5F4C24] border-gray-300 rounded focus:ring-[#5F4C24]"
                      />
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">{section.label}</div>
                        <div className="text-xs text-gray-500">{section.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={() => setSelectedNewSections(getAvailableSections().map(s => s.id))}
                    className="text-[#5F4C24] hover:text-[#4A3B1C] font-medium text-sm"
                  >
                    Select All
                  </button>
                  <button
                    onClick={handleAddSections}
                    disabled={selectedNewSections.length === 0 || isGenerating}
                    className="bg-[#5F4C24] text-white px-6 py-2 rounded-lg font-semibold text-sm shadow-lg hover:bg-[#4A3B1C] hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        Generate Sections
                      </>
                    )}
                  </button>
                </div>
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2 text-red-700 text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{error}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <ResultsContent state={state} selectedSections={state.sections} />
        </div>
      </div>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto w-full mt-6">
        <div className="bg-white rounded-xl shadow-lg p-4 flex items-center justify-center gap-8">
          <GujRAMLogo size="sm" />
          <div className="h-12 w-px bg-gray-300"></div>
          <GujaratPoliceLogo size="sm" />
        </div>
      </footer>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-[#CECAB1]/40 border border-[#5F4C24]/30 rounded-xl p-4 text-center">
      <div className="text-3xl font-bold text-[#5F4C24] mb-1">{value}</div>
      <div className="text-xs font-semibold text-gray-600 uppercase tracking-wider">{label}</div>
    </div>
  )
}
