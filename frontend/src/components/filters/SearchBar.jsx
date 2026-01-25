import { useState, useCallback } from 'react'
import { Search, X } from 'lucide-react'

export default function SearchBar({ value, onChange, placeholder = '뉴스 검색...' }) {
  const [localValue, setLocalValue] = useState(value || '')

  const handleSubmit = useCallback((e) => {
    e.preventDefault()
    onChange?.(localValue)
  }, [localValue, onChange])

  const handleClear = useCallback(() => {
    setLocalValue('')
    onChange?.('')
  }, [onChange])

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-10 py-2.5 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
      />
      {localValue && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </form>
  )
}
