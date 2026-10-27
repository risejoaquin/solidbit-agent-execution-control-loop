/**
 * SolidBit SACL - Contextual Date & Time Formatter (SB-ENG-HB-001 v1.0)
 *
 * Replaces naive toLocaleTimeString() calls that discarded date context and
 * confused historical events with current actions. Provides clear relative
 * and full contextual labels:
 * - "Hoy, 14:32:05"
 * - "Ayer, 23:15:10"
 * - "26 Oct 2026, 01:39:34"
 */

export function parseDate(input: string | number | Date | null | undefined): Date | null {
  if (!input) return null
  const d = new Date(input)
  return isNaN(d.getTime()) ? null : d
}

/**
 * Formats a timestamp with full contextual awareness (Today, Yesterday, Date + Time).
 */
export function formatSmartDateTime(
  input: string | number | Date | null | undefined,
  includeSeconds = true
): string {
  const d = parseDate(input)
  if (!d) return 'Fecha no disponible'

  const now = new Date()
  const isSameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()

  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const isYesterday =
    d.getFullYear() === yesterday.getFullYear() &&
    d.getMonth() === yesterday.getMonth() &&
    d.getDate() === yesterday.getDate()

  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  const timeStr = includeSeconds ? `${hours}:${minutes}:${seconds}` : `${hours}:${minutes}`

  if (isSameDay) {
    return `Hoy, ${timeStr}`
  }

  if (isYesterday) {
    return `Ayer, ${timeStr}`
  }

  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
  const day = d.getDate()
  const month = months[d.getMonth()]
  const isCurrentYear = d.getFullYear() === now.getFullYear()

  if (isCurrentYear) {
    return `${day} ${month}, ${timeStr}`
  }

  return `${day} ${month} ${d.getFullYear()}, ${timeStr}`
}

/**
 * Relative time calculation ("hace 2 min", "hace 4 horas", "hace 3 días").
 */
export function formatRelativeTime(input: string | number | Date | null | undefined): string {
  const d = parseDate(input)
  if (!d) return 'Desconocido'

  const now = new Date()
  const diffMs = now.getTime() - d.getTime()

  // Future timestamp guard
  if (diffMs < -1000) {
    return 'En el futuro'
  }

  const diffSec = Math.floor(diffMs / 1000)
  if (diffSec < 45) return 'Hace un momento'
  if (diffSec < 90) return 'Hace 1 min'

  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `Hace ${diffMin} min`

  const diffHours = Math.floor(diffMin / 60)
  if (diffHours < 24) return `Hace ${diffHours} h`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `Hace ${diffDays} d`

  return formatSmartDateTime(d, false)
}

/**
 * Exact ISO representation for forensic and audit tooltips.
 */
export function formatIsoUtc(input: string | number | Date | null | undefined): string {
  const d = parseDate(input)
  return d ? d.toISOString() : ''
}
