import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'
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

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [selectedSections, setSelectedSections] = useState<string[]>(AVAILABLE_SECTIONS.map(s => s.id))
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a PDF file')
        return
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit')
        return
      }
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Please drop a PDF file')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a PDF file')
      return
    }

    setIsUploading(true)
    setError(null)

    if (selectedSections.length === 0) {
      setError('Please select at least one section to analyze')
      return
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('sections', JSON.stringify(selectedSections))

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (response.ok && data.success) {
        navigate(`/results/${data.workflow_id}`)
      } else {
        setError(data.detail || 'Error processing PDF. Please try again.')
        setIsUploading(false)
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.')
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col p-4 bg-[#CECAB1]">
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
      <div className="flex-1 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-5xl w-full animate-fade-in">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">FIR Legal Analysis</h1>
            <p className="text-gray-600 text-sm">
              Upload your FIR PDF document to automatically extract facts, map relevant legal sections, and generate an investigation plan.
            </p>
          </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Side - File Upload */}
            <div className="lg:col-span-1">
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center ${
                  file
                    ? 'border-green-500 bg-green-50'
                    : 'border-[#CECAB1] hover:border-[#5F4C24] hover:bg-[#CECAB1]/30'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                {file ? (
                  <div className="space-y-2">
                    <CheckCircle2 className="w-10 h-10 text-green-500 mx-auto" />
                    <div className="text-sm font-semibold text-gray-900 break-words">{file.name}</div>
                    <div className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="w-10 h-10 text-gray-400 mx-auto" />
                    <div>
                      <div className="text-sm font-semibold text-gray-700 mb-1">
                        Click to upload
                      </div>
                      <div className="text-xs text-gray-500">PDF (max 10MB)</div>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-4 flex items-center gap-2 text-red-700 text-sm">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!file || isUploading || selectedSections.length === 0}
                className="w-full bg-[#5F4C24] text-white py-3 rounded-lg font-semibold text-base shadow-lg hover:bg-[#4A3B1C] hover:shadow-xl transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 mt-4"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing FIR document...
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    Analyze Document
                  </>
                )}
              </button>
            </div>

            {/* Right Side - Section Selection */}
            <div className="lg:col-span-2 border border-[#5F4C24]/20 rounded-lg p-4 bg-[#CECAB1]/20">
              <div className="mb-3">
                <h3 className="text-base font-semibold text-gray-900 mb-1">Select Analysis Sections</h3>
                <p className="text-xs text-gray-600">Choose which sections to generate</p>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {AVAILABLE_SECTIONS.map((section) => (
                  <label
                    key={section.id}
                    className={`flex flex-col items-center justify-center gap-1.5 p-3 bg-white rounded-lg border-2 cursor-pointer transition-all text-center ${
                      selectedSections.includes(section.id)
                        ? 'border-[#5F4C24] bg-[#CECAB1]/40'
                        : 'border-gray-200 hover:border-[#5F4C24] hover:bg-[#CECAB1]/20'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSections.includes(section.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSections([...selectedSections, section.id])
                        } else {
                          setSelectedSections(selectedSections.filter(id => id !== section.id))
                        }
                      }}
                      className="w-3.5 h-3.5 text-[#5F4C24] border-gray-300 rounded focus:ring-[#5F4C24]"
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900 text-xs">{section.label}</div>
                      <div className="text-[10px] text-gray-500 mt-0.5 leading-tight">{section.description}</div>
                    </div>
                  </label>
                ))}
              </div>
              <div className="mt-3 flex items-center justify-between text-xs pt-3 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setSelectedSections(AVAILABLE_SECTIONS.map(s => s.id))}
                  className="text-[#5F4C24] hover:text-[#4A3B1C] font-medium"
                >
                  Select All
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedSections([])}
                  className="text-gray-600 hover:text-gray-700 font-medium"
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>
        </form>
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
