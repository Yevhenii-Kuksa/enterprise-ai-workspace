import type { ReactNode } from 'react'

type KpiCardProps = {
  label: string
  value: ReactNode
  meta?: ReactNode
  icon?: ReactNode
  action?: ReactNode
}

function KpiCard({
  label,
  value,
  meta,
  icon,
  action,
}: KpiCardProps) {
  return (
    <article className="ui-kpi-card">
      {(icon || action) && (
        <div className="ui-kpi-card__top">
          {icon ? (
            <div className="ui-kpi-card__icon">
              {icon}
            </div>
          ) : (
            <span />
          )}

          {action}
        </div>
      )}

      <span className="ui-kpi-card__label">
        {label}
      </span>

      <strong className="ui-kpi-card__value">
        {value}
      </strong>

      {meta ? (
        <div className="ui-kpi-card__meta">
          {meta}
        </div>
      ) : null}
    </article>
  )
}

export default KpiCard