import { useState } from 'react'
import { AlertTriangle, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react'

export default function ErrorAlert({ message, onRetry }) {
  const [expanded, setExpanded] = useState(false)

  if (!message) return null

  // 문자열/객체 모두 지원 (하위 호환)
  const isObject = typeof message === 'object'
  const displayMessage = isObject ? message.message : message
  const status = isObject ? message.status : null
  const detail = isObject ? message.detail : null
  const errorType = isObject ? message.type : null
  const hasDetail = detail || errorType || status

  return (
    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-red-400 text-sm">{displayMessage}</p>

          {isObject && hasDetail && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 mt-2 text-xs text-red-400/60 hover:text-red-400 transition-colors"
            >
              {expanded ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
              {expanded ? '접기' : '상세 정보'}
            </button>
          )}

          {expanded && (
            <div className="mt-2 text-xs text-red-400/70 space-y-1 bg-red-500/5 rounded p-2">
              {status && <p>HTTP {status}</p>}
              {errorType && <p>{errorType}</p>}
              {detail && <p className="break-all">{detail}</p>}
            </div>
          )}
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="shrink-0 p-1.5 rounded hover:bg-red-500/10 transition-colors"
            title="재시도"
          >
            <RotateCcw className="w-4 h-4 text-red-400" />
          </button>
        )}
      </div>
    </div>
  )
}
