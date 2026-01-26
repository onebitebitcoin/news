export default function SourceSelect({ sources, selected, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-xs text-zinc-500">소스</label>
      <select
        value={selected || ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="bg-zinc-900 border border-zinc-800 text-sm text-zinc-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-orange-500/30"
      >
        <option value="">전체</option>
        {sources.map((source) => (
          <option key={source} value={source}>
            {source}
          </option>
        ))}
      </select>
    </div>
  )
}
