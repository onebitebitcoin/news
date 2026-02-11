import { useState } from 'react'
import { Bookmark, Link as LinkIcon, Clock, Sparkles, Check } from 'lucide-react'
import { getTimeAgo } from '../../utils/dateUtils'

export default function FeedCard({ item, onBookmark }) {
  const [copied, setCopied] = useState(false)

  const timeAgo = getTimeAgo(item.published_at)

  const handleCopyLink = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    try {
      await navigator.clipboard.writeText(item.url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <article className="bg-zinc-900 rounded-lg overflow-hidden card-hover">
      <a href={item.url} target="_blank" rel="noopener noreferrer" className="block">
        {/* 이미지 */}
        {item.image_url && (
          <div className="aspect-video bg-zinc-800 overflow-hidden relative">
            <img
              src={item.image_url}
              alt=""
              className="w-full h-full object-cover"
              loading="lazy"
            />
            {item.is_new && (
              <span className="absolute top-2 right-2 px-2 py-0.5 text-xs font-bold bg-red-500 text-white rounded flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                NEW
              </span>
            )}
          </div>
        )}

        {/* 콘텐츠 */}
        <div className="p-3">
          {/* 카테고리 + 소스 + NEW 태그 */}
          <div className="flex items-center gap-2 mb-2">
            {item.category && (
              <span className="px-2 py-0.5 text-xs font-medium bg-orange-500/20 text-orange-500 rounded">
                {item.category}
              </span>
            )}
            {item.is_new && !item.image_url && (
              <span className="px-2 py-0.5 text-xs font-bold bg-red-500 text-white rounded flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                NEW
              </span>
            )}
            <span className="text-xs text-zinc-500">
              {item.source === 'manual' ? '수동 추가' : item.source}
            </span>
          </div>

          {/* 제목 */}
          <h3 className="font-semibold text-white mb-2 line-clamp-2">
            {item.title}
          </h3>

          {/* 요약 */}
          {item.summary && (
            <p className="text-sm text-zinc-400 line-clamp-2 mb-3">
              {item.summary}
            </p>
          )}

          {/* 메타 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1 text-xs text-zinc-500">
              <Clock className="w-3.5 h-3.5" />
              <span>{timeAgo}</span>
            </div>
          </div>
        </div>
      </a>

      {/* 액션 버튼 */}
      <div className="flex items-center gap-2 px-3 pb-3">
        <button
          onClick={(e) => {
            e.preventDefault()
            onBookmark?.(item.id)
          }}
          className={`p-2 rounded-lg transition-colors ${
            item.is_bookmarked
              ? 'bg-orange-500/20 text-orange-500'
              : 'bg-zinc-800 text-zinc-400 hover:text-white'
          }`}
        >
          <Bookmark className={`w-4 h-4 ${item.is_bookmarked ? 'fill-current' : ''}`} />
        </button>
        <button
          onClick={handleCopyLink}
          className={`p-2 rounded-lg transition-colors ${
            copied
              ? 'bg-green-500/20 text-green-500'
              : 'bg-zinc-800 text-zinc-400 hover:text-white'
          }`}
          title="링크 복사"
        >
          {copied ? <Check className="w-4 h-4" /> : <LinkIcon className="w-4 h-4" />}
        </button>
      </div>
    </article>
  )
}
