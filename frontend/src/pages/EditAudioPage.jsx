import { useState, useEffect } from 'react'
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import { audioApi } from '../api/audio'
import { extractApiError } from '../api/client'
import { useAudioList } from '../hooks/useAudio'

export default function EditAudioPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  // navigation state에서 오디오 데이터 가져오기, 없으면 목록에서 찾기
  const { items, loading: listLoading } = useAudioList()
  const audioFromState = location.state?.audio

  const [audio, setAudio] = useState(audioFromState || null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [thumbnailUrl, setThumbnailUrl] = useState('')

  // state로 안 넘어온 경우 목록에서 찾기
  useEffect(() => {
    if (!audio && !listLoading) {
      const found = items.find((a) => a.id === parseInt(id))
      if (found) {
        setAudio(found)
      } else if (items.length > 0) {
        // 목록에 없으면 오디오 페이지로 이동
        navigate('/audio', { replace: true })
      }
    }
  }, [audio, items, listLoading, id, navigate])

  // 오디오 데이터가 세팅되면 폼 초기화
  useEffect(() => {
    if (audio) {
      setTitle(audio.title || '')
      setDescription(audio.description || '')
      setThumbnailUrl(audio.thumbnail_url || '')
    }
  }, [audio])

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('제목을 입력해주세요')
      return
    }
    setError(null)
    setSubmitLoading(true)
    try {
      await audioApi.update(parseInt(id), {
        title: title.trim(),
        description: description.trim() || null,
        thumbnail_url: thumbnailUrl.trim() || null,
      })
      setSuccess('오디오 정보가 수정되었습니다')
      setTimeout(() => navigate('/audio'), 1500)
    } catch (err) {
      const apiErr = extractApiError(err)
      setError(apiErr.message)
    } finally {
      setSubmitLoading(false)
    }
  }

  const isLoading = !audio && listLoading

  if (isLoading) {
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
        <Link to="/audio" className="p-2 rounded-lg hover:bg-zinc-800 transition-colors">
          <ArrowLeft className="w-5 h-5 text-zinc-400" />
        </Link>
        <h1 className="font-bold text-lg">오디오 편집</h1>
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

      {audio && (
        <div className="space-y-4">
          {/* 썸네일 미리보기 */}
          {thumbnailUrl && (
            <div className="rounded-lg overflow-hidden bg-zinc-900 w-32 h-32">
              <img src={thumbnailUrl} alt="" className="w-full h-full object-cover" />
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
              <label className="block text-sm text-zinc-400 mb-1">설명</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-colors resize-none"
                placeholder="오디오 설명 (선택사항)"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-1">썸네일 URL</label>
              <input
                type="url"
                value={thumbnailUrl}
                onChange={(e) => setThumbnailUrl(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
                placeholder="https://..."
              />
            </div>
          </div>

          <div className="text-xs text-zinc-500">
            파일명: {audio.filename}
          </div>

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
