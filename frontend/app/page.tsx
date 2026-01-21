'use client'

import { useState } from 'react'
import ReportViewer from '@/components/ReportViewer'
import ReportForm from '@/components/ReportForm'

export default function Home() {
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async (ticker: string, quarter: string, prevQuarter: string | null) => {
    setLoading(true)
    setError(null)
    setReport(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker,
          quarter,
          prev_quarter: prevQuarter || undefined,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Report generation failed')
      }

      const data = await response.json()
      console.log('Report data received:', data)
      if (data && data.data) {
        setReport(data.data)
      } else {
        throw new Error('Invalid response format from API')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ 
          fontSize: '1.4rem', 
          fontWeight: 700, 
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          color: '#1a1a1a', 
          marginBottom: 0,
          letterSpacing: '-0.02em',
          lineHeight: 1.2
        }}>
          the report
        </h1>
      </header>

      <ReportForm onGenerate={handleGenerate} loading={loading} />

      {error && (
        <div style={{
          marginTop: '2rem',
          padding: '1rem 0',
          borderLeft: '2px solid #c33',
          paddingLeft: '1rem',
          color: '#c33',
          fontSize: '0.875rem'
        }}>
          Error: {error}
        </div>
      )}

      {report && <ReportViewer report={report} />}
    </div>
  )
}
