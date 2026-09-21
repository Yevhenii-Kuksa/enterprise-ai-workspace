import type {
  ButtonHTMLAttributes,
  PropsWithChildren,
  ReactNode,
} from 'react'

type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'ghost'
  | 'danger'

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant
    icon?: ReactNode
  }
>

function Button({
  children,
  variant = 'primary',
  icon,
  className = '',
  type = 'button',
  ...props
}: ButtonProps) {
  const classes = [
    'ui-button',
    `ui-button--${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button
      className={classes}
      type={type}
      {...props}
    >
      {icon}
      {children}
    </button>
  )
}

export default Button