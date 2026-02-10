import { useState, useEffect, useCallback } from 'react'
import { marketApi } from '../api/feed'

export function useMarketData() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    try {
      setError(null)
      const result = await marketApi.getData()
      setData(result)
    } catch (err) {
      setError(err.message || 'Failed to fetch market data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    // 30초마다 자동 갱신
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  return { data, loading, error, refresh: fetchData }
}
