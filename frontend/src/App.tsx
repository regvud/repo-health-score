import {useCallback, useEffect, useState} from 'react'
import SearchBar from './components/SearchBar'
import {analyzeRepo} from './api'
import {HealthReport} from "./interfaces/responses.ts";
import ReportComponent from "./components/ReportComponent.tsx";

const ROUTE = '/score'

function getUrlParam(): string {
  return new URLSearchParams(window.location.search).get('url') ?? ''
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<HealthReport | null>(null)

  const handleSearch = useCallback(async (url: string) => {
    history.replaceState(null, '', `${ROUTE}?url=${encodeURIComponent(url)}`)
    setLoading(true)
    setError(null)
    setReport(null)
    try {
      setReport(await analyzeRepo(url))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (window.location.pathname !== ROUTE) {
      history.replaceState(null, '', ROUTE + window.location.search)
    }
    const url = getUrlParam()
    if (url) handleSearch(url)
  }, [handleSearch])

  return (
    <div className="app">
      <header className="header">
        <h1>Repository Health Score</h1>
      </header>

      <main className="main">
        <SearchBar onSearch={handleSearch} loading={loading} defaultValue={getUrlParam()}/>
        {error && <div className="error-msg">{error}</div>}
        {report && <ReportComponent report={report}/>}
      </main>
    </div>
  )
}
