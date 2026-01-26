import { formatDistanceToNow, format } from 'date-fns'
import { ko } from 'date-fns/locale'

/**
 * UTC 시간 문자열을 Date 객체로 파싱
 * timezone 정보가 없으면 UTC로 간주하여 'Z' 추가
 */
export function parseDate(dateStr) {
  if (!dateStr) return null
  const hasTimezone = dateStr.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(dateStr)
  return new Date(hasTimezone ? dateStr : dateStr + 'Z')
}

/**
 * 상대 시간 표시 (방금 전, N분 전, N시간 전, N일 전)
 * date-fns 없이 직접 계산
 */
export function getRelativeTime(dateString) {
  if (!dateString) return null

  const date = parseDate(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 1) return '방금 전'
  if (diffMinutes < 60) return `${diffMinutes}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  return `${diffDays}일 전`
}

/**
 * date-fns를 사용한 상대 시간 표시
 * "약 1시간 전" 등의 형태로 반환
 */
export function getTimeAgo(dateString) {
  if (!dateString) return ''
  const date = parseDate(dateString)
  if (!date) return ''
  return formatDistanceToNow(date, { addSuffix: true, locale: ko })
}

/**
 * 한국어 형식의 날짜 포맷
 * "2024년 1월 15일 14:30" 형태로 반환
 */
export function formatKoreanDate(dateString) {
  if (!dateString) return ''
  const date = parseDate(dateString)
  if (!date) return ''
  return format(date, 'yyyy년 M월 d일 HH:mm', { locale: ko })
}
