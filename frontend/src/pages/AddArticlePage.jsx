import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Search, Plus, Loader2, ExternalLink } from 'lucide-react'
import { feedApi } from '../api/feed'
import { extractApiError } from '../api/client'

export default function AddArticlePage() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [preview, setPreview] = useState(null)
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [previewLoading, setPreviewLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handlePreview = async () => {
    if (!url.trim()) return
    setError(null)
    setPreview(null)
    setPreviewLoading(true)
    try {
      const data = await feedApi.previewUrl(url.trim())
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
        url: url.trim(),
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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handlePreview()
    }
  }

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

      {/* URL 입력 */}
      <div className="flex gap-2 mb-4">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="기사 URL을 입력하세요"
          className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
        />
        <button
          onClick={handlePreview}
          disabled={!url.trim() || previewLoading}
          className="px-4 py-3 bg-zinc-800 text-zinc-300 rounded-lg hover:bg-zinc-700 transition-colors disabled:opacity-50 flex items-center gap-2 shrink-0"
        >
          {previewLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          <span className="hidden sm:inline">미리보기</span>
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

      {/* 미리보기 결과 */}
      {preview && (
        <div className="space-y-4">
          {/* 미리보기 카드 */}
          {imageUrl && (
            <div className="rounded-lg overflow-hidden bg-zinc-900">
              <img
                src={imageUrl}
                alt=""
                className="w-full aspect-video object-cover"
              />
            </div>
          )}

          {/* 편집 필드 */}
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

          {/* 원본 URL 링크 */}
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span className="truncate">{url}</span>
          </a>

          {/* 추가 버튼 */}
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
    </div>
  )
}
