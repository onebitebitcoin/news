import { useState, useEffect, useRef } from 'react'
import { Play, Pause, X } from 'lucide-react'
import { audioApi } from '../../api/audio'

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function AudioPlayer({ audio, onClose }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  const streamUrl = audioApi.getStreamUrl(audio.id)

  useEffect(() => {
    const el = audioRef.current
    if (!el) return
    el.src = streamUrl
    el.load()
    el.play()
      .then(() => setPlaying(true))
      .catch(() => {})
    return () => {
      el.pause()
    }
  }, [audio.id, streamUrl])

  const togglePlay = () => {
    const el = audioRef.current
    if (!el) return
    if (playing) {
      el.pause()
      setPlaying(false)
    } else {
      el.play()
      setPlaying(true)
    }
  }

  const handleSeek = (e) => {
    const el = audioRef.current
    if (!el || !duration) return
    const rect = e.currentTarget.getBoundingClientRect()
    const ratio = (e.clientX - rect.left) / rect.width
    el.currentTime = Math.max(0, Math.min(ratio * duration, duration))
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div className="fixed bottom-16 left-0 right-0 z-40 bg-zinc-900/95 backdrop-blur-sm border-t border-zinc-800 px-4 py-3">
      <audio
        ref={audioRef}
        onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime || 0)}
        onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
        onEnded={() => setPlaying(false)}
      />

      <div className="max-w-screen-xl mx-auto">
        {/* 제목 & 닫기 */}
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-zinc-100 truncate flex-1 mr-3">
            {audio.title}
          </p>
          <button
            onClick={onClose}
            className="flex-shrink-0 p-1 rounded hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* 프로그레스 바 */}
        <div
          className="w-full h-1.5 bg-zinc-700 rounded-full cursor-pointer mb-2 group"
          onClick={handleSeek}
        >
          <div
            className="h-full bg-orange-500 rounded-full relative transition-all"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-orange-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        {/* 컨트롤 */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-zinc-500 w-10">{formatTime(currentTime)}</span>

          <button
            onClick={togglePlay}
            className="w-9 h-9 rounded-full bg-orange-500 hover:bg-orange-400 flex items-center justify-center transition-colors"
          >
            {playing ? (
              <Pause className="w-4 h-4 text-white" />
            ) : (
              <Play className="w-4 h-4 text-white ml-0.5" />
            )}
          </button>

          <span className="text-xs text-zinc-500 w-10 text-right">{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  )
}
