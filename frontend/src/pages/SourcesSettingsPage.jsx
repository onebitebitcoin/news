import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  RefreshCw,
  Sparkles,
  Save,
  Trash2,
  Pencil,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Settings2,
  Power,
  PowerOff,
  RotateCcw,
} from 'lucide-react'
import ErrorAlert from '../components/common/ErrorAlert'
import { adminApi } from '../api/feed'
import { extractApiError } from '../api/client'

function formatKST(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function SourcesSettingsPage() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const [name, setName] = useState('')
  const [listUrl, setListUrl] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [editingId, setEditingId] = useState(null)

  const [analyzing, setAnalyzing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [analysis, setAnalysis] = useState(null)

  const [rowLoadingId, setRowLoadingId] = useState(null)

  const fetchSources = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await adminApi.getCustomSources()
      setSources(data.sources || [])
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSources()
  }, [fetchSources])

  const resetForm = () => {
    setName('')
    setListUrl('')
    setIsActive(true)
    setEditingId(null)
    setAnalysis(null)
  }

  const isDraftMatchingForm = useMemo(() => {
    if (!analysis?.draft) return false
    return (
      analysis.draft.name?.trim() === name.trim()
      && analysis.draft.list_url?.trim() === listUrl.trim()
    )
  }, [analysis, name, listUrl])

  const handleAnalyze = async () => {
    if (!name.trim() || !listUrl.trim()) {
      setError('소스 이름과 목록 URL을 입력해주세요.')
      return
    }

    try {
      setAnalyzing(true)
      setError(null)
      setSuccess(null)
      const data = await adminApi.analyzeCustomSource({
        name: name.trim(),
        list_url: listUrl.trim(),
      })
      setAnalysis(data)
      if (!data.is_valid) {
        setError({
          message: '분석은 완료되었지만 저장 가능한 상태가 아닙니다.',
          detail: (data.validation_errors || []).join(' / ') || null,
          type: 'ValidationError',
          status: null,
        })
      }
    } catch (err) {
      setAnalysis(null)
      setError(extractApiError(err))
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSave = async () => {
    if (!analysis?.draft || !isDraftMatchingForm) {
      setError('저장 전에 현재 입력값 기준으로 Analyze를 다시 실행해주세요.')
      return
    }
    if (!analysis.is_valid) {
      setError('분석 결과가 유효하지 않아 저장할 수 없습니다.')
      return
    }

    const payload = {
      name: name.trim(),
      slug: analysis.draft.slug_suggestion,
      list_url: listUrl.trim(),
      extraction_rules: analysis.draft.extraction_rules,
      normalization_rules: analysis.draft.normalization_rules || {},
      ai_model: analysis.draft.ai_model || null,
      is_active: isActive,
    }

    try {
      setSaving(true)
      setError(null)
      setSuccess(null)
      if (editingId) {
        await adminApi.updateCustomSource(editingId, payload)
        setSuccess('커스텀 소스를 수정했습니다.')
      } else {
        await adminApi.createCustomSource(payload)
        setSuccess('커스텀 소스를 추가했습니다.')
      }
      await fetchSources()
      resetForm()
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = (source) => {
    setEditingId(source.id)
    setName(source.name)
    setListUrl(source.list_url)
    setIsActive(source.is_active)
    setAnalysis(null)
    setError(null)
    setSuccess(null)
  }

  const handleToggleActive = async (source) => {
    try {
      setRowLoadingId(source.id)
      setError(null)
      setSuccess(null)
      await adminApi.updateCustomSource(source.id, { is_active: !source.is_active })
      setSuccess(source.is_active ? '소스를 비활성화했습니다.' : '소스를 활성화했습니다.')
      await fetchSources()
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setRowLoadingId(null)
    }
  }

  const handleDelete = async (source) => {
    if (!window.confirm(`삭제할까요?\n${source.name}`)) return
    try {
      setRowLoadingId(source.id)
      setError(null)
      setSuccess(null)
      await adminApi.deleteCustomSource(source.id)
      setSuccess('커스텀 소스를 삭제했습니다.')
      if (editingId === source.id) resetForm()
      await fetchSources()
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setRowLoadingId(null)
    }
  }

  const handleReanalyze = async (source) => {
    try {
      setRowLoadingId(source.id)
      setError(null)
      setSuccess(null)
      const data = await adminApi.reanalyzeCustomSource(source.id)
      setEditingId(source.id)
      setName(source.name)
      setListUrl(source.list_url)
      setIsActive(source.is_active)
      setAnalysis(data)
      setSuccess('재분석을 완료했습니다. 검토 후 저장하세요.')
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setRowLoadingId(null)
    }
  }

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
      <div className="flex items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2 min-w-0">
          <Link to="/settings/api-keys" className="p-2 rounded-lg hover:bg-zinc-800 transition-colors">
            <ArrowLeft className="w-5 h-5 text-zinc-400" />
          </Link>
          <Settings2 className="w-5 h-5 text-orange-500" />
          <h1 className="text-xl font-bold truncate">Sources</h1>
        </div>
        <button
          onClick={fetchSources}
          disabled={loading}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-zinc-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="mb-4 flex items-center gap-2 text-xs text-zinc-500">
        <Link to="/settings/api-keys" className="hover:text-zinc-300 transition-colors">API Keys</Link>
        <span>/</span>
        <span className="text-zinc-300">Custom Sources</span>
      </div>

      <ErrorAlert message={error} onRetry={fetchSources} />

      {success && (
        <div className="mb-4 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
          {success}
        </div>
      )}

      <section className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/60 mb-4">
        <div className="flex items-center justify-between mb-3 gap-2">
          <div>
            <h2 className="font-semibold text-sm">{editingId ? '소스 수정' : '소스 추가'}</h2>
            <p className="text-xs text-zinc-500 mt-1">스크래핑 목록 URL을 분석해서 규칙을 생성합니다.</p>
          </div>
          {editingId && (
            <button
              onClick={resetForm}
              className="text-xs px-2.5 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
            >
              취소
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr_auto] gap-2 mb-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Source name"
            className="bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-orange-500"
          />
          <input
            value={listUrl}
            onChange={(e) => setListUrl(e.target.value)}
            placeholder="https://example.com/news"
            className="bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-orange-500"
          />
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !name.trim() || !listUrl.trim()}
            className="px-3 py-2.5 rounded-lg bg-orange-600 hover:bg-orange-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-sm font-medium transition-colors flex items-center justify-center gap-2"
          >
            {analyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Analyze
          </button>
        </div>

        <div className="flex items-center gap-3 mb-3">
          <label className="inline-flex items-center gap-2 text-sm text-zinc-300">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="rounded border-zinc-600 bg-zinc-800"
            />
            저장 후 즉시 활성화
          </label>
          {analysis?.draft?.slug_suggestion && (
            <span className="text-xs text-zinc-500">slug: {analysis.draft.slug_suggestion}</span>
          )}
        </div>

        <button
          onClick={handleSave}
          disabled={saving || analyzing || !analysis || !analysis.is_valid || !isDraftMatchingForm}
          className="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-zinc-100 text-zinc-950 font-medium hover:bg-white disabled:bg-zinc-700 disabled:text-zinc-400 transition-colors flex items-center justify-center gap-2"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {editingId ? '수정 저장' : '소스 저장'}
        </button>
      </section>

      {analysis && (
        <section className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/40 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-orange-400" />
            <h2 className="font-semibold text-sm">분석 결과 미리보기</h2>
          </div>

          {analysis.warnings?.length > 0 && (
            <div className="mb-3 space-y-2">
              {analysis.warnings.map((warning, idx) => (
                <div key={`${warning}-${idx}`} className="text-xs text-amber-300 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2">
                  {warning}
                </div>
              ))}
            </div>
          )}

          {analysis.validation_errors?.length > 0 && (
            <div className="mb-3 space-y-2">
              {analysis.validation_errors.map((msg, idx) => (
                <div key={`${msg}-${idx}`} className="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 flex items-start gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                  <span>{msg}</span>
                </div>
              ))}
            </div>
          )}

          <div className="space-y-2">
            {(analysis.preview_items || []).length === 0 ? (
              <div className="text-sm text-zinc-500 py-6 text-center">미리보기 결과가 없습니다.</div>
            ) : (
              analysis.preview_items.map((item, idx) => (
                <a
                  key={`${item.url}-${idx}`}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-lg border border-zinc-800 hover:border-zinc-700 bg-zinc-950/50 px-3 py-3 transition-colors"
                >
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm text-zinc-100 line-clamp-2">{item.title}</p>
                      <p className="text-xs text-zinc-500 mt-1">{formatKST(item.published_at)}</p>
                      {item.summary && (
                        <p className="text-xs text-zinc-400 mt-1 line-clamp-2">{item.summary}</p>
                      )}
                    </div>
                  </div>
                </a>
              ))
            )}
          </div>
        </section>
      )}

      <section className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/30">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h2 className="font-semibold text-sm">등록된 커스텀 소스</h2>
          <span className="text-xs text-zinc-500">{sources.length}개</span>
        </div>

        {loading && sources.length === 0 ? (
          <div className="py-8 text-sm text-zinc-500 flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            불러오는 중...
          </div>
        ) : sources.length === 0 ? (
          <div className="py-10 text-center text-sm text-zinc-500">등록된 커스텀 소스가 없습니다.</div>
        ) : (
          <div className="space-y-2">
            {sources.map((source) => {
              const busy = rowLoadingId === source.id
              return (
                <div key={source.id} className="rounded-lg border border-zinc-800 bg-zinc-950/50 px-3 py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center flex-wrap gap-2">
                        <p className="text-sm font-medium text-zinc-100">{source.name}</p>
                        <span className={`text-[11px] px-1.5 py-0.5 rounded ${source.is_active ? 'bg-emerald-500/10 text-emerald-300' : 'bg-zinc-700 text-zinc-300'}`}>
                          {source.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-500 mt-1 break-all">{source.slug}</p>
                      <p className="text-xs text-zinc-500 break-all">{source.list_url}</p>
                      <p className="text-xs text-zinc-600 mt-1">
                        마지막 분석: {formatKST(source.last_analyzed_at)}
                      </p>
                      {source.last_validation_error && (
                        <p className="text-xs text-red-400 mt-1 break-all">{source.last_validation_error}</p>
                      )}
                    </div>

                    <div className="shrink-0 flex items-center gap-1">
                      <button
                        onClick={() => handleToggleActive(source)}
                        disabled={busy}
                        className="p-2 rounded-lg hover:bg-zinc-800 disabled:opacity-50 transition-colors"
                        title={source.is_active ? '비활성화' : '활성화'}
                      >
                        {source.is_active ? (
                          <Power className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <PowerOff className="w-4 h-4 text-zinc-500" />
                        )}
                      </button>
                      <button
                        onClick={() => handleEdit(source)}
                        disabled={busy}
                        className="p-2 rounded-lg hover:bg-zinc-800 disabled:opacity-50 transition-colors"
                        title="수정"
                      >
                        <Pencil className="w-4 h-4 text-zinc-400" />
                      </button>
                      <button
                        onClick={() => handleReanalyze(source)}
                        disabled={busy}
                        className="p-2 rounded-lg hover:bg-zinc-800 disabled:opacity-50 transition-colors"
                        title="재분석"
                      >
                        {busy ? (
                          <Loader2 className="w-4 h-4 animate-spin text-zinc-400" />
                        ) : (
                          <RotateCcw className="w-4 h-4 text-zinc-400" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(source)}
                        disabled={busy}
                        className="p-2 rounded-lg hover:bg-zinc-800 disabled:opacity-50 transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="w-4 h-4 text-zinc-500 hover:text-red-400" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
