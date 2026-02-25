import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Key, Plus, Trash2, Copy, Check, RefreshCw, AlertTriangle } from 'lucide-react'
import ErrorAlert from '../components/common/ErrorAlert'
import { adminApi } from '../api/feed'
import { extractApiError } from '../api/client'

export default function ApiKeysPage() {
  const [keys, setKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [newKeyName, setNewKeyName] = useState('')
  const [creating, setCreating] = useState(false)
  const [createdKey, setCreatedKey] = useState(null)
  const [copiedId, setCopiedId] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  const fetchKeys = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await adminApi.getApiKeys()
      setKeys(data.keys)
    } catch (err) {
      setError(extractApiError(err).message || 'API 키 목록을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchKeys()
  }, [fetchKeys])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newKeyName.trim()) return

    try {
      setCreating(true)
      setError(null)
      const data = await adminApi.createApiKey(newKeyName.trim())
      setCreatedKey(data)
      setNewKeyName('')
      await fetchKeys()
    } catch (err) {
      setError(extractApiError(err).message || 'API 키 생성에 실패했습니다.')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (keyId) => {
    try {
      setError(null)
      await adminApi.deleteApiKey(keyId)
      setDeleteConfirm(null)
      if (createdKey?.id === keyId) setCreatedKey(null)
      await fetchKeys()
    } catch (err) {
      setError(extractApiError(err).message || 'API 키 삭제에 실패했습니다.')
    }
  }

  const handleCopy = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      setError('클립보드 복사에 실패했습니다.')
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      timeZone: 'Asia/Seoul',
    })
  }

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Key className="w-5 h-5 text-orange-500" />
          <h1 className="text-xl font-bold">API Keys</h1>
        </div>
        <button
          onClick={fetchKeys}
          disabled={loading}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-zinc-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Error */}
      <ErrorAlert message={error} />

      <div className="mb-4 flex items-center justify-between gap-2 text-xs">
        <span className="text-zinc-500">Settings / API Keys</span>
        <Link
          to="/settings/sources"
          className="text-orange-400 hover:text-orange-300 transition-colors"
        >
          Custom Sources 관리
        </Link>
      </div>

      {/* Create Form */}
      <form onSubmit={handleCreate} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="API Key name"
            className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
          />
          <button
            type="submit"
            disabled={creating || !newKeyName.trim()}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-orange-600 hover:bg-orange-500 disabled:bg-zinc-700 disabled:text-zinc-500 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Create</span>
          </button>
        </div>
      </form>

      {/* Newly Created Key Alert */}
      {createdKey && (
        <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-orange-400 mt-0.5 shrink-0" />
            <p className="text-sm text-orange-300">
              API Key created. Copy it now - it won&apos;t be shown in full again.
            </p>
          </div>
          <div className="flex items-center gap-2 mt-3">
            <code className="flex-1 bg-zinc-900/80 px-3 py-2 rounded text-sm text-zinc-100 font-mono break-all">
              {createdKey.key}
            </code>
            <button
              onClick={() => handleCopy(createdKey.key, 'new')}
              className="p-2 rounded-lg hover:bg-zinc-800 transition-colors shrink-0"
            >
              {copiedId === 'new' ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <Copy className="w-4 h-4 text-zinc-400" />
              )}
            </button>
          </div>
        </div>
      )}

      {/* Keys List */}
      {loading && keys.length === 0 ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-zinc-900 rounded-lg p-4 animate-pulse">
              <div className="h-4 bg-zinc-800 rounded w-1/3 mb-2" />
              <div className="h-3 bg-zinc-800 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : keys.length === 0 ? (
        <div className="text-center py-16">
          <Key className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-zinc-400 mb-2">No API Keys</h3>
          <p className="text-sm text-zinc-500">Create an API key to access the External API</p>
        </div>
      ) : (
        <div className="space-y-3">
          {keys.map((apiKey) => (
            <div
              key={apiKey.id}
              className="bg-zinc-900 border border-zinc-800 rounded-lg p-4"
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm truncate">{apiKey.name}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      apiKey.is_active
                        ? 'bg-green-500/10 text-green-400'
                        : 'bg-red-500/10 text-red-400'
                    }`}>
                      {apiKey.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <code className="text-xs text-zinc-500 font-mono">
                      {apiKey.masked_key}
                    </code>
                  </div>
                  <p className="text-xs text-zinc-600 mt-1">{formatDate(apiKey.created_at)}</p>
                </div>
                <div className="ml-4 shrink-0">
                  {deleteConfirm === apiKey.id ? (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDelete(apiKey.id)}
                        className="text-xs px-2 py-1 bg-red-600 hover:bg-red-500 rounded transition-colors"
                      >
                        Delete
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(null)}
                        className="text-xs px-2 py-1 bg-zinc-700 hover:bg-zinc-600 rounded transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setDeleteConfirm(apiKey.id)}
                      className="p-2 rounded-lg hover:bg-zinc-800 transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-zinc-500 hover:text-red-400" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
