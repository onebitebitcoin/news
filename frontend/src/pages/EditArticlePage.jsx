import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { ArrowLeft, Save, Loader2, ExternalLink } from 'lucide-react'
import { feedApi } from '../api/feed'
import { extractApiError } from '../api/client'

export default function EditArticlePage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const [article, setArticle] = useState(null)
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [category, setCategory] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await feedApi.getDetail(id)
        const item = data?.data || data
        if (item.source !== 'manual') {
          setError('수동 추가 기사만 편집할 수 있습니다')
          return
        }
        setArticle(item)
        setTitle(item.title || '')
        setSummary(item.summary || '')
        setImageUrl(item.image_url || '')
        setCategory(item.category || '')
      } catch (err) {
        const apiErr = extractApiError(err)
        setError(apiErr.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('제목을 입력해주세요')
      return
    }
    setError(null)
    setSubmitLoading(true)
    try {
      await feedApi.updateArticle(id, {
        title: title.trim(),
        summary: summary.trim() || null,
        image_url: imageUrl.trim() || null,
        category: category.trim() || null,
      })
      setSuccess('기사가 수정되었습니다')
      setTimeout(() => navigate('/'), 1500)
    } catch (err) {
      const apiErr = extractApiError(err)
      setError(apiErr.message)
    } finally {
      setSubmitLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-screen-md mx-auto px-4 sm:px-6 py-4 flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
      </div>
    )
  }

  return (
    <div className="max-w-screen-md mx-auto px-4 sm:px-6 py-4">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-6">
        <Link to="/" className="p-2 rounded-lg hover:bg-zinc-800 transition-colors">
          <ArrowLeft className="w-5 h-5 text-zinc-400" />
        </Link>
        <h1 className="font-bold text-lg">기사 편집</h1>
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

      {article && (
        <div className="space-y-4">
          {/* 이미지 미리보기 */}
          {imageUrl && (
            <div className="rounded-lg overflow-hidden bg-zinc-900">
              <img src={imageUrl} alt="" className="w-full aspect-video object-cover" />
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
            <div>
              <label className="block text-sm text-zinc-400 mb-1">카테고리</label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
                placeholder="예: Bitcoin, Ethereum"
              />
            </div>
          </div>

          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span className="truncate">{article.url}</span>
          </a>

          <button
            onClick={handleSubmit}
            disabled={!title.trim() || submitLoading}
            className="w-full py-3 bg-orange-500 text-white font-semibold rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {submitLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            저장
          </button>
        </div>
      )}
    </div>
  )
}
