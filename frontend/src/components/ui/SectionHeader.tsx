import type { ReactNode } from 'react'

type SectionHeaderProps = {
  title: string
  description?: string
  meta?: ReactNode
}

function SectionHeader({
  title,
  description,
  meta,
}: SectionHeaderProps) {
  return (
    <div className="ui-section-header">
      <div>
        <h2 className="ui-section-header__title">
          {title}
        </h2>

        {description ? (
          <p className="ui-section-header__description">
            {description}
          </p>
        ) : null}
      </div>

      {meta ? (
        <div className="ui-section-header__meta">
          {meta}
        </div>
      ) : null}
    </div>
  )
}

export default SectionHeader