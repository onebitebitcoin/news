import { useCallback } from 'react'
import { bookmarkApi } from '../api/feed'

/**
 * 북마크 토글 기능을 제공하는 훅
 * @param {Function} onToggle - 토글 성공 시 호출되는 콜백 (itemId, newBookmarkState) => void
 */
export function useBookmarkToggle(onToggle) {
  const toggle = useCallback(async (itemId, isCurrentlyBookmarked) => {
    try {
      if (isCurrentlyBookmarked) {
        await bookmarkApi.remove(itemId)
      } else {
        await bookmarkApi.add(itemId)
      }
      onToggle?.(itemId, !isCurrentlyBookmarked)
      return true
    } catch (err) {
      console.error('Bookmark toggle failed:', err)
      return false
    }
  }, [onToggle])

  return { toggle }
}
