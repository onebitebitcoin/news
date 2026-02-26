import { useState, useRef } from 'react'
import { X, Upload, Music } from 'lucide-react'

const ACCEPTED = '.mp3,.mp4,.m4a,.wav,.ogg,.flac,.aac,.webm'

export default function UploadModal({ onUpload, onClose }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const fileRef = useRef(null)

  const handleFile = (e) => {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    if (!title) {
      setTitle(f.name.replace(/\.[^.]+$/, ''))
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files?.[0]
    if (!f) return
    setFile(f)
    if (!title) setTitle(f.name.replace(/\.[^.]+$/, ''))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) { setError('파일을 선택해주세요'); return }
    if (!title.trim()) { setError('제목을 입력해주세요'); return }

    setUploading(true)
    setError(null)
    try {
      await onUpload(title.trim(), file, description.trim() || undefined)
      onClose()
    } catch (err) {
      setError(err.message || '업로드에 실패했습니다')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      {/* 배경 */}
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />

      {/* 모달 */}
      <div className="relative w-full sm:max-w-md bg-zinc-900 border border-zinc-800 rounded-t-2xl sm:rounded-2xl p-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold">오디오 업로드</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 파일 선택 영역 */}
          <div
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
              file
                ? 'border-orange-500/50 bg-orange-500/5'
                : 'border-zinc-700 hover:border-zinc-600'
            }`}
            onClick={() => fileRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            <input
              ref={fileRef}
              type="file"
              accept={ACCEPTED}
              onChange={handleFile}
              className="hidden"
            />
            {file ? (
              <>
                <Music className="w-8 h-8 text-orange-500 mx-auto mb-2" />
                <p className="text-sm font-medium text-zinc-200 truncate px-2">{file.name}</p>
                <p className="text-xs text-zinc-500 mt-1">
                  {(file.size / (1024 * 1024)).toFixed(1)}MB
                </p>
              </>
            ) : (
              <>
                <Upload className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
                <p className="text-sm text-zinc-400">클릭하거나 파일을 드래그하세요</p>
                <p className="text-xs text-zinc-600 mt-1">mp3, m4a, wav, ogg, flac, webm</p>
              </>
            )}
          </div>

          {/* 제목 */}
          <input
            type="text"
            placeholder="제목"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
          />

          {/* 설명 (선택) */}
          <input
            type="text"
            placeholder="설명 (선택)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
          />

          {/* 에러 */}
          {error && <p className="text-sm text-red-400">{error}</p>}

          {/* 제출 */}
          <button
            type="submit"
            disabled={uploading || !file}
            className="w-full py-3 bg-orange-500 hover:bg-orange-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-colors"
          >
            {uploading ? '업로드 중...' : '업로드'}
          </button>
        </form>
      </div>
    </div>
  )
}
