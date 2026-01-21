'use client'

import { useState, useEffect } from 'react'

interface ReportFormProps {
  onGenerate: (ticker: string, quarter: string, prevQuarter: string | null) => void
  loading: boolean
}

export default function ReportForm({ onGenerate, loading }: ReportFormProps) {
  const [ticker, setTicker] = useState('GOOG')
  const [quarter, setQuarter] = useState('2025_Q3')
  const [prevQuarter, setPrevQuarter] = useState<string>('2025_Q2')
  const [availableQuarters, setAvailableQuarters] = useState<string[]>([])

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
        const response = await fetch(`${apiUrl}/documents`)
        if (response.ok) {
          const data = await response.json()
          const quarters = Array.isArray(data) 
            ? [...new Set(data.map((d: any) => d.quarter).filter(Boolean))].sort()
            : []
          setAvailableQuarters(quarters)
        }
      } catch (err) {
        console.error('Failed to fetch documents:', err)
      }
    }
    fetchDocuments()
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onGenerate(ticker, quarter, prevQuarter || null)
  }

  return (
    <form onSubmit={handleSubmit} style={{
      backgroundColor: 'transparent',
      padding: 0,
      border: 'none'
    }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500, marginBottom: '0.5rem', color: '#666', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            Ticker
          </label>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            style={{
              width: '100%',
              padding: '0.5rem 0',
              border: 'none',
              borderBottom: '1px solid #e0e0e0',
              borderRadius: 0,
              fontSize: '0.9375rem',
              fontFamily: 'inherit',
              backgroundColor: 'transparent',
              transition: 'border-color 0.2s'
            }}
            onFocus={(e) => e.target.style.borderBottomColor = '#1a1a1a'}
            onBlur={(e) => e.target.style.borderBottomColor = '#e0e0e0'}
            required
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500, marginBottom: '0.5rem', color: '#666', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            Current Quarter
          </label>
          {availableQuarters.length > 0 ? (
            <select
              value={quarter}
              onChange={(e) => setQuarter(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem 0',
                border: 'none',
                borderBottom: '1px solid #e0e0e0',
                borderRadius: 0,
                fontSize: '0.9375rem',
                fontFamily: 'inherit',
                backgroundColor: 'transparent',
                cursor: 'pointer',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderBottomColor = '#1a1a1a'}
              onBlur={(e) => e.target.style.borderBottomColor = '#e0e0e0'}
              required
            >
              {availableQuarters.map((q) => (
                <option key={q} value={q}>{q}</option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={quarter}
              onChange={(e) => setQuarter(e.target.value)}
              placeholder="2025_Q3"
              style={{
                width: '100%',
                padding: '0.5rem 0',
                border: 'none',
                borderBottom: '1px solid #e0e0e0',
                borderRadius: 0,
                fontSize: '0.9375rem',
                fontFamily: 'inherit',
                backgroundColor: 'transparent',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderBottomColor = '#1a1a1a'}
              onBlur={(e) => e.target.style.borderBottomColor = '#e0e0e0'}
              required
            />
          )}
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500, marginBottom: '0.5rem', color: '#666', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            Previous Quarter (optional)
          </label>
          {availableQuarters.length > 0 ? (
            <select
              value={prevQuarter}
              onChange={(e) => setPrevQuarter(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem 0',
                border: 'none',
                borderBottom: '1px solid #e0e0e0',
                borderRadius: 0,
                fontSize: '0.9375rem',
                fontFamily: 'inherit',
                backgroundColor: 'transparent',
                cursor: 'pointer',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderBottomColor = '#1a1a1a'}
              onBlur={(e) => e.target.style.borderBottomColor = '#e0e0e0'}
            >
              <option value="">None</option>
              {availableQuarters.filter(q => q !== quarter).map((q) => (
                <option key={q} value={q}>{q}</option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={prevQuarter}
              onChange={(e) => setPrevQuarter(e.target.value)}
              placeholder="2025_Q2 (optional)"
              style={{
                width: '100%',
                padding: '0.5rem 0',
                border: 'none',
                borderBottom: '1px solid #e0e0e0',
                borderRadius: 0,
                fontSize: '0.9375rem',
                fontFamily: 'inherit',
                backgroundColor: 'transparent',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderBottomColor = '#1a1a1a'}
              onBlur={(e) => e.target.style.borderBottomColor = '#e0e0e0'}
            />
          )}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          padding: '1.25rem 2rem',
          backgroundColor: loading ? '#999' : '#000000',
          color: '#ffffff',
          border: 'none',
          borderRadius: 0,
          fontSize: '1rem',
          fontWeight: 600,
          letterSpacing: '0.02em',
          textTransform: 'uppercase',
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'background-color 0.2s',
          marginTop: '2rem',
          width: '100%',
          textAlign: 'center',
          fontFamily: 'Inter, sans-serif'
        }}
      >
        {loading ? 'Generating...' : 'Generate Report'}
      </button>
    </form>
  )
}
