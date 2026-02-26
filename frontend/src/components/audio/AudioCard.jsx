import { Play, Pause, Trash2, Clock } from 'lucide-react'

function formatDuration(seconds) {
  if (!seconds) return null
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function formatFileSize(bytes) {
  if (!bytes) return null
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return `${Math.floor(diff / 86400)}일 전`
}

export default function AudioCard({ audio, isPlaying, onPlay, onDelete }) {
  const duration = formatDuration(audio.duration)
  const fileSize = formatFileSize(audio.file_size)

  return (
    <div
      className={`flex items-center gap-3 p-4 rounded-xl border transition-colors cursor-pointer ${
        isPlaying
          ? 'bg-orange-500/10 border-orange-500/40'
          : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
      }`}
      onClick={() => onPlay(audio)}
    >
      {/* Play/Pause 버튼 */}
      <button
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
          isPlaying
            ? 'bg-orange-500 text-white'
            : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
        }`}
        onClick={(e) => {
          e.stopPropagation()
          onPlay(audio)
        }}
      >
        {isPlaying ? (
          <Pause className="w-4 h-4" />
        ) : (
          <Play className="w-4 h-4 ml-0.5" />
        )}
      </button>

      {/* 정보 */}
      <div className="flex-1 min-w-0">
        <p
          className={`font-medium truncate text-sm ${
            isPlaying ? 'text-orange-400' : 'text-zinc-100'
          }`}
        >
          {audio.title}
        </p>
        {audio.description && (
          <p className="text-xs text-zinc-400 truncate mt-0.5">{audio.description}</p>
        )}
        <div className="flex items-center gap-1.5 mt-0.5 text-xs text-zinc-500 flex-wrap">
          <span className="truncate max-w-[120px]">{audio.filename}</span>
          {duration && (
            <>
              <span>·</span>
              <span className="flex items-center gap-0.5 flex-shrink-0">
                <Clock className="w-3 h-3" />
                {duration}
              </span>
            </>
          )}
          {fileSize && (
            <>
              <span>·</span>
              <span className="flex-shrink-0">{fileSize}</span>
            </>
          )}
          <span>·</span>
          <span className="flex-shrink-0">{formatDate(audio.uploaded_at)}</span>
        </div>
      </div>

      {/* 삭제 버튼 */}
      <button
        className="flex-shrink-0 p-2 rounded-lg hover:bg-zinc-800 text-zinc-600 hover:text-red-400 transition-colors"
        onClick={(e) => {
          e.stopPropagation()
          onDelete(audio.id)
        }}
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  )
}
