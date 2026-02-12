import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Search,
  Plus,
  Loader2,
  ExternalLink,
  CheckSquare,
  Square,
  MinusSquare,
  AlertCircle,
} from 'lucide-react'
import { feedApi } from '../api/feed'
import { extractApiError } from '../api/client'
import { getTimeAgo } from '../utils/dateUtils'

function isUrlInput(value) {
  const trimmed = value.trim().toLowerCase()
  return trimmed.startsWith('http://') || trimmed.startsWith('https://')
}

export default function AddArticlePage() {
  const navigate = useNavigate()
  const [input, setInput] = useState('')

  // URL 모드 state
  const [preview, setPreview] = useState(null)
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [previewLoading, setPreviewLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)

  // 검색 모드 state
  const [searchResults, setSearchResults] = useState(null)
  const [selectedUrls, setSelectedUrls] = useState(new Set())
  const [searchLoading, setSearchLoading] = useState(false)
  const [batchLoading, setBatchLoading] = useState(false)

  // 공통
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const isUrl = isUrlInput(input)

  // --- URL 모드 ---
  const handlePreview = async () => {
    if (!input.trim()) return
    setError(null)
    setPreview(null)
    setSearchResults(null)
    setPreviewLoading(true)
    try {
      const data = await feedApi.previewUrl(input.trim())
      setPreview(data)
      setTitle(data.title || '')
      setSummary(data.summary || '')
      setImageUrl(data.image_url || '')
    } catch (err) {
      const apiErr = extractApiError(err)
      setError(apiErr.message)
    } finally {
      setPreviewLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('제목을 입력해주세요')
      return
    }
    setError(null)
    setSubmitLoading(true)
    try {
      await feedApi.createManual({
        url: input.trim(),
        title: title.trim(),
        summary: summary.trim() || null,
        image_url: imageUrl.trim() || null,
      })
      setSuccess('기사가 추가되었습니다')
      setTimeout(() => navigate('/'), 1500)
    } catch (err) {
      const apiErr = extractApiError(err)
      setError(apiErr.message)
    } finally {
      setSubmitLoading(false)
    }
  }

  // --- 검색 모드 ---
  const handleSearch = async () => {
    if (!input.trim()) return
    setError(null)
    setPreview(null)
    setSearchResults(null)
    setSelectedUrls(new Set())
    setSearchLoading(true)
    try {
      const data = await feedApi.searchArticles(input.trim())
      setSearchResults(data)
    } catch (err) {
      const apiErr = extractApiError(err)
      setError(apiErr.message)
    } finally {
      setSearchLoading(false)
    }
  }

  const toggleSelect = (url) => {
    setSelectedUrls((prev) => {
      const next = new Set(prev)
      if (next.has(url)) {
        next.delete(url)
      } else {
        next.add(url)
      }
      return next
    })
  }

  const selectableItems = searchResults?.items?.filter((item) => !item.is_duplicate) || []

  const toggleSelectAll = () => {
    if (selectedUrls.size === selectableItems.length) {
      setSelectedUrls(new Set())
    } else {
      setSelectedUrls(new Set(selectableItems.map((item) => item.url)))
    }
  }

  const handleBatchAdd = async () => {
    if (selectedUrls.size === 0) return
    setError(null)
    setBatchLoading(true)
    try {
      const articles = searchResults.items
        .filter((item) => selectedUrls.has(item.url))
        .map((item) => ({
          url: item.url,
          title: item.title,
          summary: item.summary || null,
          image_url: null,
        }))
      const data = await feedApi.createManualBatch(articles)
      setSuccess(`${data.added}개 추가, ${data.skipped}개 건너뜀`)
      setTimeout(() => navigate('/'), 1500)
    } catch (err) {
      const apiErr = extractApiError(err)
      setError(apiErr.message)
    } finally {
      setBatchLoading(false)
    }
  }

  // --- 공통 ---
  const handleAction = () => {
    if (isUrl) {
      handlePreview()
    } else {
      handleSearch()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAction()
    }
  }

  const loading = previewLoading || searchLoading

  const allSelected = selectableItems.length > 0 && selectedUrls.size === selectableItems.length
  const someSelected = selectedUrls.size > 0 && selectedUrls.size < selectableItems.length

  return (
    <div className="max-w-screen-md mx-auto px-4 sm:px-6 py-4">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-6">
        <Link
          to="/"
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-zinc-400" />
        </Link>
        <h1 className="font-bold text-lg">기사 추가</h1>
      </div>

      {/* 입력 */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="키워드 또는 URL을 입력하세요"
          className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
        />
        <button
          onClick={handleAction}
          disabled={!input.trim() || loading}
          className="px-4 py-3 bg-zinc-800 text-zinc-300 rounded-lg hover:bg-zinc-700 transition-colors disabled:opacity-50 flex items-center gap-2 shrink-0"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          <span className="hidden sm:inline">{isUrl ? '미리보기' : '검색'}</span>
        </button>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* 성공 메시지 */}
      {success && (
        <div className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
          {success}
        </div>
      )}

      {/* URL 모드: 미리보기 결과 */}
      {preview && (
        <div className="space-y-4">
          {imageUrl && (
            <div className="rounded-lg overflow-hidden bg-zinc-900">
              <img
                src={imageUrl}
                alt=""
                className="w-full aspect-video object-cover"
              />
            </div>
          )}

          <div className="space-y-3">
            <div>
              <label className="block text-sm text-zinc-400 mb-1">제목</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-1">요약</label>
              <textarea
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                rows={3}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-colors resize-none"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-1">이미지 URL</label>
              <input
                type="url"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
                placeholder="https://..."
              />
            </div>
          </div>

          <a
            href={input}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span className="truncate">{input}</span>
          </a>

          <button
            onClick={handleSubmit}
            disabled={!title.trim() || submitLoading}
            className="w-full py-3 bg-orange-500 text-white font-semibold rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {submitLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            기사 추가
          </button>
        </div>
      )}

      {/* 검색 모드: 결과 리스트 */}
      {searchResults && (
        <div className="space-y-3">
          {/* 상단 액션 바 */}
          <div className="flex items-center justify-between">
            <button
              onClick={toggleSelectAll}
              className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              {allSelected ? (
                <CheckSquare className="w-4 h-4 text-orange-500" />
              ) : someSelected ? (
                <MinusSquare className="w-4 h-4 text-orange-500" />
              ) : (
                <Square className="w-4 h-4" />
              )}
              전체선택
              {selectableItems.length > 0 && (
                <span className="text-zinc-500">({selectableItems.length})</span>
              )}
            </button>

            {selectedUrls.size > 0 && (
              <button
                onClick={handleBatchAdd}
                disabled={batchLoading}
                className="px-4 py-2 bg-orange-500 text-white text-sm font-semibold rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {batchLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                {selectedUrls.size}개 추가
              </button>
            )}
          </div>

          {/* 검색 결과 리스트 */}
          {searchResults.items.length === 0 ? (
            <div className="text-center py-8 text-zinc-500 text-sm">
              검색 결과가 없습니다
            </div>
          ) : (
            <div className="divide-y divide-zinc-800">
              {searchResults.items.map((item) => (
                <SearchResultItem
                  key={item.url}
                  item={item}
                  selected={selectedUrls.has(item.url)}
                  onToggle={() => toggleSelect(item.url)}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function SearchResultItem({ item, selected, onToggle }) {
  const isDuplicate = item.is_duplicate

  return (
    <button
      onClick={isDuplicate ? undefined : onToggle}
      disabled={isDuplicate}
      className={`w-full text-left py-3 flex gap-3 items-start transition-colors ${
        isDuplicate ? 'opacity-50 cursor-default' : 'hover:bg-zinc-900/50 cursor-pointer'
      }`}
    >
      {/* 체크박스 */}
      <div className="pt-0.5 shrink-0">
        {isDuplicate ? (
          <Square className="w-4 h-4 text-zinc-600" />
        ) : selected ? (
          <CheckSquare className="w-4 h-4 text-orange-500" />
        ) : (
          <Square className="w-4 h-4 text-zinc-500" />
        )}
      </div>

      {/* 내용 */}
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-zinc-200 line-clamp-2">
          {item.title}
        </div>
        {item.summary && (
          <div className="text-xs text-zinc-500 mt-1 line-clamp-1">
            {item.summary}
          </div>
        )}
        <div className="flex items-center gap-2 mt-1 text-xs text-zinc-500">
          {item.source_ref && <span>{item.source_ref}</span>}
          {item.source_ref && item.published_at && <span>·</span>}
          {item.published_at && <span>{getTimeAgo(item.published_at)}</span>}
          {isDuplicate && (
            <span className="flex items-center gap-1 text-amber-500/80">
              <AlertCircle className="w-3 h-3" />
              이미 등록됨
            </span>
          )}
        </div>
      </div>
    </button>
  )
}
