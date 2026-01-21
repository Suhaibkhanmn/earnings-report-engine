'use client'

import { useState } from 'react'

interface ReportViewerProps {
  report: any
}

export default function ReportViewer({ report }: ReportViewerProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['summary']))

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const SectionHeader = ({ title, count }: { title: string; count?: number }) => (
    <button
      onClick={() => toggleSection(title)}
      style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 0',
        backgroundColor: 'transparent',
        border: 'none',
        borderBottom: '1px solid #e0e0e0',
        cursor: 'pointer',
        fontSize: '1rem',
        fontWeight: 600,
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
        textAlign: 'left',
        color: '#1a1a1a',
        transition: 'color 0.2s'
      }}
      onMouseEnter={(e) => e.currentTarget.style.color = '#000'}
      onMouseLeave={(e) => e.currentTarget.style.color = '#1a1a1a'}
    >
      <span>{title}</span>
      {count !== undefined && <span style={{ fontSize: '0.6875rem', color: '#999', fontWeight: 400 }}>{count}</span>}
    </button>
  )

  return (
    <div style={{ marginTop: '4rem' }}>
      <div style={{
        backgroundColor: 'transparent',
        border: 'none',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '0 0 1.5rem 0', borderBottom: '1px solid #e0e0e0', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.25rem', color: '#1a1a1a' }}>
            {report.ticker} — {report.quarter}
          </h2>
          {report.prev_quarter && (
            <p style={{ fontSize: '0.9375rem', color: '#666', fontWeight: 400 }}>
              Comparison with {report.prev_quarter}
            </p>
          )}
        </div>

        {report.summary && (
          <div>
            <SectionHeader title="Summary" />
            {expandedSections.has('summary') && (
              <div style={{ padding: '1.75rem 0', backgroundColor: '#ffffff' }}>
                {report.summary?.high_level ? (
                  <p style={{ marginBottom: '1.75rem', lineHeight: 1.8, fontSize: '1.125rem', color: '#1a1a1a', fontWeight: 400 }}>
                    {report.summary.high_level}
                  </p>
                ) : (
                  <p style={{ marginBottom: '1.75rem', lineHeight: 1.8, color: '#777', fontStyle: 'italic', fontSize: '1.125rem' }}>
                    Summary not available
                  </p>
                )}
                {report.summary?.tone && (
                  <div style={{ display: 'inline-block', padding: '0.4rem 0.9rem', backgroundColor: '#111', borderRadius: 999, fontSize: '0.75rem', letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 500, color: '#fff' }}>
                    Tone: {report.summary.tone}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {report.guidance && report.guidance.length > 0 && (
          <div>
            <SectionHeader title="Guidance" count={report.guidance.length} />
            {expandedSections.has('Guidance') && (
              <div style={{ padding: '1.75rem 0', backgroundColor: '#fcfcfc' }}>
                {report.guidance.map((item: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '2rem', paddingBottom: '2rem', borderBottom: idx < report.guidance.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                      <h4 style={{ fontSize: '1.125rem', fontWeight: 500, lineHeight: 1.7, color: '#1a1a1a' }}>{item.claim}</h4>
                      <span style={{ padding: '0.25rem 0.6rem', backgroundColor: '#f2f2f2', borderRadius: 999, fontSize: '0.75rem', letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 500, color: '#555' }}>
                        {item.direction_vs_prev}
                      </span>
                    </div>
                    {item.evidence_current && (
                      <div style={{ marginTop: '0.75rem', padding: '1rem 1.25rem', backgroundColor: '#f5f5f5', borderRadius: 4, fontSize: '1.0625rem', fontStyle: 'italic', color: '#1a1a1a', lineHeight: 1.8 }}>
                        <span style={{ fontWeight: 600, fontStyle: 'normal', color: '#666', fontSize: '0.875rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Current:</span> {item.evidence_current}
                      </div>
                    )}
                    {item.evidence_prev && item.evidence_prev !== 'unknown' && (
                      <div style={{ marginTop: '0.75rem', padding: '1rem 1.25rem', backgroundColor: '#f5f5f5', borderRadius: 4, fontSize: '1.0625rem', fontStyle: 'italic', color: '#1a1a1a', lineHeight: 1.8 }}>
                        <span style={{ fontWeight: 600, fontStyle: 'normal', color: '#666', fontSize: '0.875rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Previous:</span> {item.evidence_prev}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {report.growth_drivers && report.growth_drivers.length > 0 && (
          <div>
            <SectionHeader title="Growth Drivers" count={report.growth_drivers.length} />
            {expandedSections.has('Growth Drivers') && (
              <div style={{ padding: '1.75rem 0', backgroundColor: '#fcfcfc' }}>
                {report.growth_drivers.map((item: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: idx < report.growth_drivers.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '0.75rem', color: '#111' }}>{item.claim}</h4>
                    {item.evidence && (
                      <div style={{ padding: '0.85rem 1rem', backgroundColor: '#f5f5f5', borderRadius: 4, fontSize: '0.95rem', fontStyle: 'italic', color: '#333', lineHeight: 1.8 }}>
                        {item.evidence}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {report.risks && report.risks.length > 0 && (
          <div>
            <SectionHeader title="Risks" count={report.risks.length} />
            {expandedSections.has('Risks') && (
              <div style={{ padding: '1.75rem 0', backgroundColor: '#fcfcfc' }}>
                {report.risks.map((item: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: idx < report.risks.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                      <h4 style={{ fontSize: '1.125rem', fontWeight: 500, lineHeight: 1.7, color: '#1a1a1a' }}>{item.claim}</h4>
                      {item.is_new && (
                        <span style={{ padding: '0.25rem 0.6rem', backgroundColor: '#fff7e0', borderRadius: 999, fontSize: '0.75rem', letterSpacing: '0.05em', textTransform: 'uppercase', fontWeight: 500, color: '#8a5a00' }}>
                          New
                        </span>
                      )}
                    </div>
                    {item.evidence_current && (
                      <div style={{ padding: '0.85rem 1rem', backgroundColor: '#f5f5f5', borderRadius: 4, fontSize: '0.95rem', fontStyle: 'italic', color: '#333', lineHeight: 1.8 }}>
                        {item.evidence_current}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {report.margin_dynamics && report.margin_dynamics.length > 0 && (
          <div>
            <SectionHeader title="Margin Dynamics" count={report.margin_dynamics.length} />
            {expandedSections.has('Margin Dynamics') && (
              <div style={{ padding: '1.75rem 0', backgroundColor: '#fcfcfc' }}>
                {report.margin_dynamics.map((item: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: idx < report.margin_dynamics.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '0.75rem', color: '#111' }}>{item.claim}</h4>
                    {item.evidence && (
                      <div style={{ padding: '0.85rem 1rem', backgroundColor: '#f5f5f5', borderRadius: 4, fontSize: '0.95rem', fontStyle: 'italic', color: '#333', lineHeight: 1.8 }}>
                        {item.evidence}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {report.qa_pressure_points && report.qa_pressure_points.length > 0 && (
          <div>
            <SectionHeader title="Q&A Pressure Points" count={report.qa_pressure_points.length} />
            {expandedSections.has('Q&A Pressure Points') && (
              <div style={{ padding: '1.75rem 0', backgroundColor: '#fcfcfc' }}>
                {report.qa_pressure_points.map((item: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '2rem', paddingBottom: '2rem', borderBottom: idx < report.qa_pressure_points.length - 1 ? '1px solid #e0e0e0' : 'none' }}>
                    <div style={{ marginBottom: '1rem' }}>
                      <span style={{ fontSize: '1rem', fontWeight: 500, color: '#1a1a1a', letterSpacing: '0.05em', textTransform: 'uppercase' }}>{item.theme}</span>
                      {item.analyst_name && (
                        <span style={{ fontSize: '1rem', color: '#666', marginLeft: '0.75rem', fontWeight: 400 }}>
                          — {item.analyst_name}
                        </span>
                      )}
                    </div>
                    {item.evidence_question && (
                      <div style={{ marginBottom: '0.75rem', padding: '1rem 1.25rem', backgroundColor: '#f5f8ff', borderRadius: 4, fontSize: '1.0625rem', color: '#1a1a1a', lineHeight: 1.8 }}>
                        <span style={{ fontWeight: 600, color: '#6174b6', fontSize: '0.875rem', letterSpacing: '0.06em', textTransform: 'uppercase' }}>Q:</span> {item.evidence_question}
                      </div>
                    )}
                    {item.evidence_answer && (
                      <div style={{ padding: '1rem 1.25rem', backgroundColor: '#f5f5f5', borderRadius: 4, fontSize: '1.0625rem', fontStyle: 'italic', color: '#1a1a1a', lineHeight: 1.8 }}>
                        <span style={{ fontWeight: 600, fontStyle: 'normal', color: '#666', fontSize: '0.875rem', letterSpacing: '0.06em', textTransform: 'uppercase' }}>A:</span> {item.evidence_answer}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
