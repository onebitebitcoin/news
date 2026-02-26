import { useState, useEffect, useCallback } from 'react'
import { audioApi } from '../api/audio'

export function useAudioList() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await audioApi.getList()
      setItems(data?.items || [])
    } catch (e) {
      setError(e.message || '오디오 목록을 불러오지 못했습니다')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
  }, [fetch])

  const upload = useCallback(async (title, file, description) => {
    const fd = new FormData()
    fd.append('title', title)
    fd.append('file', file)
    if (description) fd.append('description', description)
    const created = await audioApi.upload(fd)
    setItems((prev) => [created, ...prev])
    return created
  }, [])

  const remove = useCallback(async (id) => {
    await audioApi.delete(id)
    setItems((prev) => prev.filter((a) => a.id !== id))
  }, [])

  return { items, loading, error, refresh: fetch, upload, remove }
}
