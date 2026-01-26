import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, Bookmark, Clock, User } from 'lucide-react'
import { feedApi, bookmarkApi } from '../api/feed'
import { parseDate, getTimeAgo, formatKoreanDate } from '../utils/dateUtils'

export default function ItemDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchItem = async () => {
      try {
        setLoading(true)
        const data = await feedApi.getDetail(id)
        setItem(data)
      } catch (err) {
        setError(err.message || 'Failed to load article')
      } finally {
        setLoading(false)
      }
    }
    fetchItem()
  }, [id])

  const handleBookmark = async () => {
    if (!item) return
    try {
      if (item.is_bookmarked) {
        await bookmarkApi.remove(item.id)
      } else {
        await bookmarkApi.add(item.id)
      }
      setItem({ ...item, is_bookmarked: !item.is_bookmarked })
    } catch (err) {
      console.error('Bookmark failed:', err)
    }
  }

  if (loading) {
    return (
      <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
        <div className="animate-pulse space-y-4">
          <div className="w-8 h-8 bg-zinc-800 rounded-lg" />
          <div className="aspect-video bg-zinc-800 rounded-lg" />
          <div className="space-y-3">
            <div className="h-8 bg-zinc-800 rounded w-3/4" />
            <div className="h-4 bg-zinc-800 rounded w-1/4" />
            <div className="h-4 bg-zinc-800 rounded w-full" />
            <div className="h-4 bg-zinc-800 rounded w-full" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
        <Link to="/" className="inline-flex items-center gap-2 text-zinc-400 mb-4">
          <ArrowLeft className="w-5 h-5" />
          <span>뒤로</span>
        </Link>
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    )
  }

  if (!item) return null

  const publishedDate = parseDate(item.published_at)
  const timeAgo = getTimeAgo(item.published_at)
  const formattedDate = formatKoreanDate(item.published_at)

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
      {/* Back Button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-zinc-400 hover:text-white mb-4 transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>뒤로</span>
      </Link>

      {/* Image */}
      {item.image_url && (
        <div className="aspect-video bg-zinc-800 rounded-lg overflow-hidden mb-4">
          <img
            src={item.image_url}
            alt=""
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Category + Source */}
      <div className="flex items-center gap-2 mb-3">
        {item.category && (
          <span className="px-2.5 py-1 text-xs font-medium bg-orange-500/20 text-orange-500 rounded">
            {item.category}
          </span>
        )}
        <span className="text-sm text-zinc-500">{item.source}</span>
      </div>

      {/* Title */}
      <h1 className="text-2xl font-bold text-white mb-4">{item.title}</h1>

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-500 mb-6">
        {item.author && (
          <div className="flex items-center gap-1">
            <User className="w-4 h-4" />
            <span>{item.author}</span>
          </div>
        )}
        {publishedDate && (
          <div className="flex items-center gap-1" title={formattedDate}>
            <Clock className="w-4 h-4" />
            <span>{timeAgo}</span>
          </div>
        )}
      </div>

      {/* Summary */}
      {item.summary && (
        <div className="bg-zinc-900 rounded-lg p-4 mb-6">
          <p className="text-zinc-300 leading-relaxed">{item.summary}</p>
        </div>
      )}

      {/* Tags */}
      {item.tags && item.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {item.tags.map((tag) => (
            <span
              key={tag}
              className="px-3 py-1 text-xs bg-zinc-800 text-zinc-400 rounded-full"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleBookmark}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-lg transition-colors ${
            item.is_bookmarked
              ? 'bg-orange-500/20 text-orange-500'
              : 'bg-zinc-800 text-zinc-300 hover:text-white'
          }`}
        >
          <Bookmark className={`w-5 h-5 ${item.is_bookmarked ? 'fill-current' : ''}`} />
          <span>{item.is_bookmarked ? '저장됨' : '저장'}</span>
        </button>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2.5 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
        >
          <ExternalLink className="w-5 h-5" />
          <span>원문 보기</span>
        </a>
      </div>
    </div>
  )
}
