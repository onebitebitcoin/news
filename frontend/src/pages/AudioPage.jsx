import { useState } from 'react'
import { Plus, Headphones, RefreshCw } from 'lucide-react'
import { useAudioList } from '../hooks/useAudio'
import AudioCard from '../components/audio/AudioCard'
import AudioPlayer from '../components/audio/AudioPlayer'
import UploadModal from '../components/audio/UploadModal'
import ErrorAlert from '../components/common/ErrorAlert'
import SkeletonLoader from '../components/common/SkeletonLoader'

export default function AudioPage() {
  const { items, loading, error, refresh, upload, remove } = useAudioList()
  const [currentAudio, setCurrentAudio] = useState(null)
  const [showUpload, setShowUpload] = useState(false)

  const handlePlay = (audio) => {
    if (currentAudio?.id === audio.id) {
      setCurrentAudio(null)
    } else {
      setCurrentAudio(audio)
    }
  }

  const handleDelete = async (id) => {
    if (currentAudio?.id === id) setCurrentAudio(null)
    try {
      await remove(id)
    } catch (e) {
      console.error('[AudioPage] delete error', e)
    }
  }

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">Audio</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={refresh}
            disabled={loading}
            className="p-2 rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 text-zinc-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-orange-500 hover:bg-orange-400 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">업로드</span>
          </button>
        </div>
      </div>

      {/* 에러 */}
      <ErrorAlert message={error} onRetry={refresh} />

      {/* 로딩 스켈레톤 */}
      {loading && items.length === 0 && (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <SkeletonLoader key={i} />
          ))}
        </div>
      )}

      {/* 빈 상태 */}
      {!loading && items.length === 0 && !error && (
        <div className="text-center py-16">
          <Headphones className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-zinc-400 mb-2">오디오가 없습니다</h3>
          <p className="text-sm text-zinc-500 mb-6">+ 버튼으로 오디오 파일을 업로드하세요</p>
          <button
            onClick={() => setShowUpload(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-orange-500 hover:bg-orange-400 text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            첫 번째 오디오 업로드
          </button>
        </div>
      )}

      {/* 오디오 목록 */}
      {items.length > 0 && (
        <div className={`space-y-3 ${currentAudio ? 'pb-32' : 'pb-4'}`}>
          {items.map((audio) => (
            <AudioCard
              key={audio.id}
              audio={audio}
              isPlaying={currentAudio?.id === audio.id}
              onPlay={handlePlay}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* 플레이어 */}
      {currentAudio && (
        <AudioPlayer
          audio={currentAudio}
          onClose={() => setCurrentAudio(null)}
        />
      )}

      {/* 업로드 모달 */}
      {showUpload && (
        <UploadModal
          onUpload={upload}
          onClose={() => setShowUpload(false)}
        />
      )}
    </div>
  )
}
