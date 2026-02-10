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
 * 상대 시간 표시 (date-fns 사용)
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
