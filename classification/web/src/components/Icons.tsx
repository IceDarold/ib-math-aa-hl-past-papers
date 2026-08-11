import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

const base = {
  width: 16,
  height: 16,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
}

export function MenuIcon(props: IconProps) {
  return <svg {...base} {...props}><path d="M4 7h16M4 12h16M4 17h16" /></svg>
}

export function PanelLeftIcon(props: IconProps) {
  return <svg {...base} {...props}><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M9 4v16" /></svg>
}

export function CloseIcon(props: IconProps) {
  return <svg {...base} {...props}><path d="m6 6 12 12M18 6 6 18" /></svg>
}

export function SearchIcon(props: IconProps) {
  return <svg {...base} {...props}><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></svg>
}

export function CheckIcon(props: IconProps) {
  return <svg {...base} {...props}><path d="m5 12 4 4L19 6" /></svg>
}

export function ResetIcon(props: IconProps) {
  return <svg {...base} {...props}><path d="M4 4v6h6" /><path d="M5.5 15a7 7 0 1 0 .4-7.5L4 10" /></svg>
}

export function FileIcon(props: IconProps) {
  return <svg {...base} {...props}><path d="M6 2h8l4 4v16H6z" /><path d="M14 2v5h5M9 13h6M9 17h4" /></svg>
}

export function ArrowUpDownIcon(props: IconProps) {
  return <svg {...base} {...props}><path d="m8 7 4-4 4 4M12 3v18M16 17l-4 4-4-4" /></svg>
}
