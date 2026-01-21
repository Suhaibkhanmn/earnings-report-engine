import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Earnings Call Intelligence Engine',
  description: 'Structured earnings call analysis with evidence-backed insights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
