import {type FormEvent, useState} from 'react'
const GITHUB_REPO_URL = /^https?:\/\/github\.com\/([^/]+)\/([^/\s?#]+)/

interface SearchBarProps {
  onSearch: (url: string) => void
  loading: boolean
  defaultValue?: string
}

export default function SearchBar({onSearch, loading, defaultValue = ''}: SearchBarProps) {
  const [value, setValue] = useState(defaultValue)
  const [validationError, setValidationError] = useState<string | null>(null)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!GITHUB_REPO_URL.test(trimmed)) {
      setValidationError('Please enter a valid GitHub repository URL (e.g. https://github.com/owner/repo)')
      return
    }
    setValidationError(null)
    onSearch(trimmed)
  }

  return (
    <div className="search-wrapper">
      <form className="search-form" onSubmit={handleSubmit}>
        <input
          className="search-input"
          type="text"
          placeholder="https://github.com/owner/repo"
          value={value}
          onChange={e => {
            setValue(e.target.value);
            setValidationError(null)
          }}
          disabled={loading}
          autoFocus
        />
        <button className="search-btn" type="submit" disabled={loading || !value.trim()}>
          {loading ? 'Checking…' : 'Check'}
        </button>
      </form>
      {validationError && <p className="validation-error">{validationError}</p>}
    </div>
  )
}
