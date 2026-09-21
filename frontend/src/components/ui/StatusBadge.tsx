import type { PropsWithChildren } from 'react'

type StatusTone =
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'neutral'

type StatusBadgeProps = PropsWithChildren<{
  tone?: StatusTone
  className?: string
}>

function StatusBadge({
  children,
  tone = 'neutral',
  className = '',
}: StatusBadgeProps) {
  const classes = [
    'ui-status-badge',
    `ui-status-badge--${tone}`,
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <span className={classes}>
      {children}
    </span>
  )
}

export default StatusBadge