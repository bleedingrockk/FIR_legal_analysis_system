import { useState } from 'react'
import { marked } from 'marked'
import { 
  FileText, Scale, BookOpen, Shield, ClipboardList, 
  CheckCircle, XCircle, AlertTriangle, Clock, History, Gavel, ScrollText
} from 'lucide-react'

interface WorkflowState {
  fir_facts?: Record<string, string>
  ndps_sections?: Array<any>
  bns_sections?: Array<any>
  bnss_sections?: Array<any>
  bsa_sections?: Array<any>
  investigation_plan?: Array<any>
  investigation_and_legal_timeline?: { date_string: string; timeline: string }
  evidence_checklist?: string
  dos?: string[]
  donts?: string[]
  potential_prosecution_weaknesses?: Record<string, string>
  next_steps?: string[]
  historical_cases?: Array<any>
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
}

interface ResultsContentProps {
  state: WorkflowState
  selectedSections?: string[]
}

// Map section IDs to tab IDs
const SECTION_TO_TAB_MAP: Record<string, string> = {
  'ndps': 'ndps',
  'bns': 'bns',
  'bnss': 'bnss',
  'bsa': 'bsa',
  'investigation_plan': 'investigation',
  'timeline': 'timeline',
  'historical_cases': 'historical',
  'evidence': 'evidence',
  'dos_and_donts': 'dos-donts',
  'weaknesses': 'weaknesses',
  'defence_rebuttal': 'defence-rebuttal',
  'court_summary': 'court-summary',
  'chargesheet': 'chargesheet',
}

export default function ResultsContent({ state, selectedSections }: ResultsContentProps) {
  const allTabs = [
    { id: 'fir-facts', label: 'FIR Facts', icon: FileText, condition: state.fir_facts, sectionId: null },
    { id: 'ndps', label: 'NDPS Act', icon: Scale, condition: state.ndps_sections?.length, sectionId: 'ndps' },
    { id: 'bns', label: 'BNS', icon: BookOpen, condition: state.bns_sections?.length, sectionId: 'bns' },
    { id: 'bnss', label: 'BNSS', icon: Shield, condition: state.bnss_sections?.length, sectionId: 'bnss' },
    { id: 'bsa', label: 'BSA', icon: BookOpen, condition: state.bsa_sections?.length, sectionId: 'bsa' },
    { id: 'investigation', label: 'Investigation Plan', icon: ClipboardList, condition: state.investigation_plan?.length, sectionId: 'investigation_plan' },
    { id: 'timeline', label: 'Timeline', icon: Clock, condition: state.investigation_and_legal_timeline, sectionId: 'timeline' },
    { id: 'evidence', label: 'Evidence', icon: FileText, condition: state.evidence_checklist, sectionId: 'evidence' },
    { id: 'dos-donts', label: "Do's & Don'ts", icon: CheckCircle, condition: state.dos && state.donts, sectionId: 'dos_and_donts' },
    { id: 'weaknesses', label: 'Weaknesses', icon: AlertTriangle, condition: state.potential_prosecution_weaknesses, sectionId: 'weaknesses' },
    { id: 'defence-rebuttal', label: 'Defence & Rebuttal', icon: Gavel, condition: state.defence_perspective_rebuttal?.length, sectionId: 'defence_rebuttal' },
    { id: 'court-summary', label: 'Summary for Court', icon: ScrollText, condition: state.summary_for_the_court, sectionId: 'court_summary' },
    { id: 'chargesheet', label: 'Chargesheet', icon: FileText, condition: state.chargesheet, sectionId: 'chargesheet' },
    { id: 'next-steps', label: 'Recommendations', icon: CheckCircle, condition: state.next_steps?.length, sectionId: null },
    { id: 'historical', label: 'Historical Cases', icon: History, condition: state.historical_cases?.length, sectionId: 'historical_cases' },
  ]
  
  // Filter tabs: show FIR Facts always, show others only if selected and have data
  const tabs = allTabs.filter(tab => {
    if (tab.id === 'fir-facts') return tab.condition // Always show FIR Facts if available
    if (!tab.condition) return false // Don't show if no data
    if (!selectedSections || selectedSections.length === 0) return true // Show all if no selection (backward compatibility)
    if (!tab.sectionId) return true // Show tabs without section mapping
    return selectedSections.includes(tab.sectionId) // Only show if section was selected
  })

  const [activeTab, setActiveTab] = useState(tabs[0]?.id || '')

  const renderMarkdown = (content: string) => {
    return { __html: marked.parse(content) }
  }

  return (
    <div>
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6 p-4 bg-[#CECAB1]/20 rounded-xl border border-[#5F4C24]/20">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                activeTab === tab.id
                  ? 'bg-[#5F4C24] text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-[#CECAB1]/20'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'fir-facts' && state.fir_facts && (
          <FirFactsSection facts={state.fir_facts} />
        )}

        {activeTab === 'ndps' && state.ndps_sections && (
          <SectionsSection title="NDPS Act" sections={state.ndps_sections} />
        )}

        {activeTab === 'bns' && state.bns_sections && (
          <SectionsSection title="Bharatiya Nyaya Sanhita (BNS)" sections={state.bns_sections} />
        )}

        {activeTab === 'bnss' && state.bnss_sections && (
          <SectionsSection title="Bharatiya Nagarik Suraksha Sanhita (BNSS)" sections={state.bnss_sections} />
        )}

        {activeTab === 'bsa' && state.bsa_sections && (
          <SectionsSection title="Bharatiya Sakshya Adhiniyam (BSA)" sections={state.bsa_sections} />
        )}

        {activeTab === 'investigation' && state.investigation_plan && (
          <InvestigationPlanSection plan={state.investigation_plan} />
        )}

        {activeTab === 'timeline' && state.investigation_and_legal_timeline && (
          <TimelineSection timeline={state.investigation_and_legal_timeline} />
        )}

        {activeTab === 'evidence' && state.evidence_checklist && (
          <EvidenceSection checklist={state.evidence_checklist} />
        )}

        {activeTab === 'dos-donts' && state.dos && state.donts && (
          <DosDontsSection dos={state.dos} donts={state.donts} />
        )}

        {activeTab === 'weaknesses' && state.potential_prosecution_weaknesses && (
          <WeaknessesSection weaknesses={state.potential_prosecution_weaknesses} />
        )}

        {activeTab === 'defence-rebuttal' && state.defence_perspective_rebuttal && (
          <DefenceRebuttalSection data={state.defence_perspective_rebuttal} />
        )}

        {activeTab === 'court-summary' && state.summary_for_the_court && (
          <CourtSummarySection summary={state.summary_for_the_court} />
        )}

        {activeTab === 'chargesheet' && state.chargesheet && (
          <ChargesheetSection chargesheet={state.chargesheet} />
        )}

        {activeTab === 'next-steps' && state.next_steps && (
          <NextStepsSection steps={state.next_steps} />
        )}

        {activeTab === 'historical' && state.historical_cases && (
          <HistoricalCasesSection cases={state.historical_cases} />
        )}
      </div>
    </div>
  )
}

function FirFactsSection({ facts }: { facts: Record<string, string> }) {
  const entries = Object.entries(facts)
  const leftColumn = entries.filter((_, idx) => idx % 2 === 0)
  const rightColumn = entries.filter((_, idx) => idx % 2 === 1)

  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <FileText className="w-7 h-7" />
        FIR Facts Summary
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          {leftColumn.map(([key, value]) => (
            <div key={key} className="bg-white rounded-lg p-5 border border-[#CECAB1]">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                {key.replace(/_/g, ' ')}
              </div>
              <div 
                className="text-base text-gray-700 prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: marked.parse(value) }}
              />
            </div>
          ))}
        </div>
        <div className="space-y-4">
          {rightColumn.map(([key, value]) => (
            <div key={key} className="bg-white rounded-lg p-5 border border-[#CECAB1]">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                {key.replace(/_/g, ' ')}
              </div>
              <div 
                className="text-base text-gray-700 prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: marked.parse(value) }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SectionsSection({ title, sections }: { title: string; sections: Array<any> }) {
  const leftColumn = sections.filter((_, idx) => idx % 2 === 0)
  const rightColumn = sections.filter((_, idx) => idx % 2 === 1)

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          {leftColumn.map((section, idx) => {
            const originalIdx = sections.indexOf(section)
            return (
              <div key={originalIdx} className="bg-white border-l-4 border-[#5F4C24] rounded-lg p-5 shadow-sm">
                <div className="text-lg font-bold text-[#5F4C24] mb-3">
                  Section {section.section_number}
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Description</div>
                    <div 
                      className="text-base text-gray-700 prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(section.section_description) }}
                    />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Relevance</div>
                    <div 
                      className="text-base text-gray-700 prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(section.why_section_is_relevant) }}
                    />
                  </div>
                  {section.source && (
                    <div className="pt-3 border-t border-gray-200">
                      <a 
                        href={section.source} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm text-[#5F4C24] hover:text-[#4A3B1C]"
                      >
                        {section.source}
                      </a>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
        <div className="space-y-4">
          {rightColumn.map((section, idx) => {
            const originalIdx = sections.indexOf(section)
            return (
              <div key={originalIdx} className="bg-white border-l-4 border-[#5F4C24] rounded-lg p-5 shadow-sm">
                <div className="text-lg font-bold text-[#5F4C24] mb-3">
                  Section {section.section_number}
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Description</div>
                    <div 
                      className="text-base text-gray-700 prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(section.section_description) }}
                    />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Relevance</div>
                    <div 
                      className="text-base text-gray-700 prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(section.why_section_is_relevant) }}
                    />
                  </div>
                  {section.source && (
                    <div className="pt-3 border-t border-gray-200">
                      <a 
                        href={section.source} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm text-[#5F4C24] hover:text-[#4A3B1C]"
                      >
                        {section.source}
                      </a>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function InvestigationPlanSection({ plan }: { plan: Array<any> }) {
  const leftColumn = plan.filter((_, idx) => idx % 2 === 0)
  const rightColumn = plan.filter((_, idx) => idx % 2 === 1)

  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <ClipboardList className="w-7 h-7" />
        Detailed Investigation Plan
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          {leftColumn.map((point, idx) => {
            const originalIdx = plan.indexOf(point)
            return (
              <div key={originalIdx} className="bg-white rounded-lg p-5 shadow-sm">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-10 h-10 bg-[#5F4C24] text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                    {originalIdx + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{point.title}</h3>
                    {point.date_range && (
                      <span className="inline-block text-xs font-semibold text-[#5F4C24] bg-[#CECAB1]/40 px-3 py-1 rounded-full">
                        {point.date_range}
                      </span>
                    )}
                  </div>
                </div>
                <div 
                  className="text-base text-gray-700 prose prose-sm max-w-none ml-13"
                  dangerouslySetInnerHTML={{ __html: marked.parse(point.description) }}
                />
              </div>
            )
          })}
        </div>
        <div className="space-y-4">
          {rightColumn.map((point, idx) => {
            const originalIdx = plan.indexOf(point)
            return (
              <div key={originalIdx} className="bg-white rounded-lg p-5 shadow-sm">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-10 h-10 bg-[#5F4C24] text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                    {originalIdx + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{point.title}</h3>
                    {point.date_range && (
                      <span className="inline-block text-xs font-semibold text-[#5F4C24] bg-[#CECAB1]/40 px-3 py-1 rounded-full">
                        {point.date_range}
                      </span>
                    )}
                  </div>
                </div>
                <div 
                  className="text-base text-gray-700 prose prose-sm max-w-none ml-13"
                  dangerouslySetInnerHTML={{ __html: marked.parse(point.description) }}
                />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function TimelineSection({ timeline }: { timeline: { date_string: string; timeline: string } }) {
  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Clock className="w-7 h-7" />
        Investigation & Legal Timeline
      </h2>
      {timeline.date_string && (
        <div className="bg-white rounded-lg p-4 mb-6 border border-[#CECAB1]">
          <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Date</div>
          <div className="text-lg font-bold text-[#5F4C24]">{timeline.date_string}</div>
        </div>
      )}
      <div 
        className="bg-white rounded-lg p-6 prose prose-base max-w-none text-base"
        dangerouslySetInnerHTML={{ __html: marked.parse(timeline.timeline) }}
      />
    </div>
  )
}

function EvidenceSection({ checklist }: { checklist: string }) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <FileText className="w-7 h-7" />
        Evidence Checklist & Compliance
      </h2>
      <div 
        className="bg-white rounded-lg p-6 prose prose-base max-w-none text-base"
        dangerouslySetInnerHTML={{ __html: marked.parse(checklist) }}
      />
    </div>
  )
}

function DosDontsSection({ dos, donts }: { dos: string[]; donts: string[] }) {
  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <CheckCircle className="w-7 h-7" />
        Do's & Don'ts for Law Enforcement
      </h2>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <h3 className="text-xl font-bold text-green-700 mb-4 flex items-center gap-2">
            <CheckCircle className="w-6 h-6" />
            Do's
          </h3>
          <ul className="space-y-3">
            {dos.map((item, idx) => (
              <li key={idx} className="flex items-start gap-3 text-base text-gray-700">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <h3 className="text-xl font-bold text-red-700 mb-4 flex items-center gap-2">
            <XCircle className="w-6 h-6" />
            Don'ts
          </h3>
          <ul className="space-y-3">
            {donts.map((item, idx) => (
              <li key={idx} className="flex items-start gap-3 text-base text-gray-700">
                <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

function WeaknessesSection({ weaknesses }: { weaknesses: Record<string, string> }) {
  const entries = Object.entries(weaknesses)
  const leftColumn = entries.filter((_, idx) => idx % 2 === 0)
  const rightColumn = entries.filter((_, idx) => idx % 2 === 1)

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <AlertTriangle className="w-7 h-7" />
        Potential Prosecution Weaknesses
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          {leftColumn.map(([heading, details], idx) => (
            <div key={idx} className="bg-white rounded-lg p-5 border border-yellow-200">
              <h3 className="text-lg font-bold text-yellow-800 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                {heading}
              </h3>
              <div className="text-base text-gray-700">{details}</div>
            </div>
          ))}
        </div>
        <div className="space-y-4">
          {rightColumn.map(([heading, details], idx) => (
            <div key={idx} className="bg-white rounded-lg p-5 border border-yellow-200">
              <h3 className="text-lg font-bold text-yellow-800 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                {heading}
              </h3>
              <div className="text-base text-gray-700">{details}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function NextStepsSection({ steps }: { steps: string[] }) {
  const leftColumn = steps.filter((_, idx) => idx % 2 === 0)
  const rightColumn = steps.filter((_, idx) => idx % 2 === 1)

  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <CheckCircle className="w-7 h-7" />
        Other Recommendations
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3">
          {leftColumn.map((step, idx) => {
            const originalIdx = steps.indexOf(step)
            return (
              <div key={originalIdx} className="flex items-start gap-3 bg-white rounded-lg p-4 border border-green-200">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div 
                  className="text-base text-gray-700 prose prose-sm max-w-none flex-1"
                  dangerouslySetInnerHTML={{ __html: marked.parse(step) }}
                />
              </div>
            )
          })}
        </div>
        <div className="space-y-3">
          {rightColumn.map((step, idx) => {
            const originalIdx = steps.indexOf(step)
            return (
              <div key={originalIdx} className="flex items-start gap-3 bg-white rounded-lg p-4 border border-green-200">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div 
                  className="text-base text-gray-700 prose prose-sm max-w-none flex-1"
                  dangerouslySetInnerHTML={{ __html: marked.parse(step) }}
                />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function HistoricalCasesSection({ cases }: { cases: Array<any> }) {
  const leftColumn = cases.filter((_, idx) => idx % 2 === 0)
  const rightColumn = cases.filter((_, idx) => idx % 2 === 1)

  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <History className="w-7 h-7" />
        Historical Cases
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          {leftColumn.map((caseItem, idx) => {
            const originalIdx = cases.indexOf(caseItem)
            return (
              <div key={originalIdx} className="bg-white rounded-lg p-5 border border-[#CECAB1] shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-3">{caseItem.title}</h3>
                <div 
                  className="text-base text-gray-700 prose prose-sm max-w-none mb-4"
                  dangerouslySetInnerHTML={{ __html: marked.parse(caseItem.summary) }}
                />
                {caseItem.url && (
                  <a 
                    href={caseItem.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-[#5F4C24] hover:text-[#4A3B1C] font-semibold text-sm"
                  >
                    View Source →
                  </a>
                )}
              </div>
            )
          })}
        </div>
        <div className="space-y-4">
          {rightColumn.map((caseItem, idx) => {
            const originalIdx = cases.indexOf(caseItem)
            return (
              <div key={originalIdx} className="bg-white rounded-lg p-5 border border-[#CECAB1] shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-3">{caseItem.title}</h3>
                <div 
                  className="text-base text-gray-700 prose prose-sm max-w-none mb-4"
                  dangerouslySetInnerHTML={{ __html: marked.parse(caseItem.summary) }}
                />
                {caseItem.url && (
                  <a 
                    href={caseItem.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-[#5F4C24] hover:text-[#4A3B1C] font-semibold text-sm"
                  >
                    View Source →
                  </a>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function DefenceRebuttalSection({ data }: { data: Array<{ defence_perspective: string[]; rebuttal: string[] }> }) {
  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Gavel className="w-7 h-7" />
        Defence Perspective & Prosecution Rebuttal
      </h2>
      <div className="space-y-6">
        {data.map((item, idx) => (
          <div key={idx} className="bg-white rounded-lg p-6 border border-[#CECAB1] shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Defence Perspective */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
                <h3 className="text-xl font-bold text-blue-700 mb-4 flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  Defence Perspective
                </h3>
                <ul className="space-y-3">
                  {item.defence_perspective.map((point, pointIdx) => (
                    <li key={pointIdx} className="flex items-start gap-3 text-base text-gray-700">
                      <XCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <span 
                        className="prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                      />
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Prosecution Rebuttal */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-5">
                <h3 className="text-xl font-bold text-green-700 mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  Prosecution Rebuttal
                </h3>
                <ul className="space-y-3">
                  {item.rebuttal.map((point, pointIdx) => (
                    <li key={pointIdx} className="flex items-start gap-3 text-base text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span 
                        className="prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function CourtSummarySection({ summary }: { 
  summary: {
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
}) {
  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <ScrollText className="w-7 h-7" />
        Summary for the Court
      </h2>

      {/* Case Title */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-2xl font-bold text-[#1e3a8a] mb-2">{summary.case_title}</h3>
        {summary.ndps_sections && summary.ndps_sections.length > 0 && (
          <div className="text-lg text-gray-700">
            <span className="font-semibold">NDPS Act – Sections </span>
            {summary.ndps_sections.join(', ')}
          </div>
        )}
      </div>

      {/* Core Issue */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-3">Core Issue</h3>
        <div 
          className="text-base text-gray-700 prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: marked.parse(summary.core_issue) }}
        />
      </div>

      {/* Prosecution Snapshot */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Prosecution Snapshot</h3>
        <div className="space-y-3">
          <div>
            <span className="font-semibold text-gray-700">Date & Place: </span>
            <span className="text-gray-700">{summary.date_and_place}</span>
          </div>
          <div>
            <span className="font-semibold text-gray-700">Recovery: </span>
            <span 
              className="text-gray-700 prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: marked.parse(summary.recovery) }}
            />
          </div>
          <div>
            <span className="font-semibold text-gray-700">Quantity: </span>
            <span 
              className="text-gray-700 prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: marked.parse(summary.quantity) }}
            />
          </div>
          {summary.safeguards && summary.safeguards.length > 0 && (
            <div>
              <span className="font-semibold text-gray-700">Safeguards: </span>
              <ul className="list-disc list-inside mt-2 space-y-1">
                {summary.safeguards.map((safeguard, idx) => (
                  <li key={idx} className="text-gray-700">
                    <span className="text-green-600">✔</span> {safeguard}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Why the Case is Strong */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Why the Case is Strong</h3>
        <div className="space-y-4">
          {summary.conscious_possession_proven && summary.conscious_possession_proven.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-800 mb-2">Conscious Possession Proven</h4>
              <ul className="space-y-2">
                {summary.conscious_possession_proven.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-green-600 mt-1">•</span>
                    <span 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          )}
          {summary.procedural_compliance && summary.procedural_compliance.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-800 mb-2">Procedural Compliance</h4>
              <ul className="space-y-2">
                {summary.procedural_compliance.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-green-600 mt-1">•</span>
                    <span 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          )}
          {summary.legal_position && summary.legal_position.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-800 mb-2">Legal Position</h4>
              <ul className="space-y-2">
                {summary.legal_position.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-green-600 mt-1">•</span>
                    <span 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Judicial Balance */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-3">Judicial Balance</h3>
        <div 
          className="text-base text-gray-700 prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: marked.parse(summary.judicial_balance) }}
        />
      </div>

      {/* Prosecution Prayer */}
      <div className="bg-white rounded-lg p-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Prosecution Prayer</h3>
        <ul className="space-y-2">
          {summary.prosecution_prayer.map((prayer, idx) => (
            <li key={idx} className="flex items-start gap-3 text-base text-gray-700">
              <CheckCircle className="w-5 h-5 text-[#5F4C24] flex-shrink-0 mt-0.5" />
              <span 
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: marked.parse(prayer) }}
              />
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function ChargesheetSection({ chargesheet }: { 
  chargesheet: {
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
}) {
  // Combine all sections for display
  const allSections = [
    ...(chargesheet.ndps_sections.length > 0 ? [`NDPS Act – ${chargesheet.ndps_sections.join(', ')}`] : []),
    ...(chargesheet.bns_sections.length > 0 ? [`BNS – ${chargesheet.bns_sections.join(', ')}`] : []),
    ...(chargesheet.bnss_sections.length > 0 ? [`BNSS – ${chargesheet.bnss_sections.join(', ')}`] : []),
    ...(chargesheet.bsa_sections.length > 0 ? [`BSA – ${chargesheet.bsa_sections.join(', ')}`] : []),
  ]

  return (
    <div className="bg-[#CECAB1]/30 border border-[#5F4C24]/20 rounded-xl p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <FileText className="w-7 h-7" />
        Chargesheet
      </h2>

      {/* Case Title */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-2xl font-bold text-[#1e3a8a] mb-2">{chargesheet.case_title}</h3>
        {allSections.length > 0 && (
          <div className="text-lg text-gray-700 space-y-1">
            {allSections.map((section, idx) => (
              <div key={idx}>{section}</div>
            ))}
          </div>
        )}
      </div>

      {/* Core Issue */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-3">Core Issue</h3>
        <div 
          className="text-base text-gray-700 prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: marked.parse(chargesheet.core_issue) }}
        />
      </div>

      {/* Prosecution Snapshot */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Prosecution Snapshot</h3>
        <div className="space-y-3">
          <div>
            <span className="font-semibold text-gray-700">Date & Place: </span>
            <span className="text-gray-700">{chargesheet.date_and_place}</span>
          </div>
          <div>
            <span className="font-semibold text-gray-700">Recovery: </span>
            <span 
              className="text-gray-700 prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: marked.parse(chargesheet.recovery) }}
            />
          </div>
          <div>
            <span className="font-semibold text-gray-700">Quantity: </span>
            <span 
              className="text-gray-700 prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: marked.parse(chargesheet.quantity) }}
            />
          </div>
          {chargesheet.safeguards && chargesheet.safeguards.length > 0 && (
            <div>
              <span className="font-semibold text-gray-700">Safeguards: </span>
              <ul className="list-disc list-inside mt-2 space-y-1">
                {chargesheet.safeguards.map((safeguard, idx) => (
                  <li key={idx} className="text-gray-700">
                    <span className="text-green-600">✔</span> {safeguard}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Why the Case is Strong */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Why the Case is Strong</h3>
        <div className="space-y-4">
          {chargesheet.conscious_possession_proven && chargesheet.conscious_possession_proven.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-800 mb-2">Conscious Possession Proven</h4>
              <ul className="space-y-2">
                {chargesheet.conscious_possession_proven.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-green-600 mt-1">•</span>
                    <span 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          )}
          {chargesheet.procedural_compliance && chargesheet.procedural_compliance.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-800 mb-2">Procedural Compliance</h4>
              <ul className="space-y-2">
                {chargesheet.procedural_compliance.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-green-600 mt-1">•</span>
                    <span 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          )}
          {chargesheet.legal_position && chargesheet.legal_position.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-800 mb-2">Legal Position</h4>
              <ul className="space-y-2">
                {chargesheet.legal_position.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-green-600 mt-1">•</span>
                    <span 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: marked.parse(point) }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Judicial Balance */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-3">Judicial Balance</h3>
        <div 
          className="text-base text-gray-700 prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: marked.parse(chargesheet.judicial_balance) }}
        />
      </div>

      {/* Prosecution Prayer */}
      <div className="bg-white rounded-lg p-6 border border-[#CECAB1] shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Prosecution Prayer</h3>
        <ul className="space-y-2">
          {chargesheet.prosecution_prayer.map((prayer, idx) => (
            <li key={idx} className="flex items-start gap-3 text-base text-gray-700">
              <CheckCircle className="w-5 h-5 text-[#5F4C24] flex-shrink-0 mt-0.5" />
              <span 
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: marked.parse(prayer) }}
              />
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
