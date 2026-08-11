# Question Atlas Design System

## Direction

Question Atlas is a light, dense research interface. It uses a three-panel shell: filters, a scannable result table, and a provenance-rich inspector. The interface avoids dashboard cards, decorative illustration, gradients, and marketing patterns.

## Color

- Canvas: `oklch(1 0 0)`
- Subtle surface: `oklch(0.978 0.004 18)`
- Ink: `oklch(0.20 0.015 18)`
- Muted ink: `oklch(0.48 0.018 18)`
- Border: `oklch(0.90 0.008 18)`
- Primary crimson: `oklch(0.56 0.20 18)`
- Selected surface: `oklch(0.965 0.022 18)`
- Calculator cyan: `oklch(0.60 0.15 225)`
- Verified green: `oklch(0.55 0.14 150)`

Crimson indicates selection and primary action. Cyan is reserved for calculator/numerical information. Green is reserved for verified state.

## Typography

The UI uses the operating system sans-serif stack for compact, familiar controls. Identifiers, taxonomy keys, tags, and mathematical paths use a monospace stack. Base text is 13px on desktop and never drops below 12px.

## Structure and behavior

- 4px and 8px spacing rhythm
- 1px dividers; shadows only on narrow-screen overlays
- Sticky top bar, column headers, and inspector title
- Up/down selects results; `/` focuses search; Escape closes overlays
- At narrow widths filters become a drawer and the inspector becomes an overlay
- Motion is short and functional, and removed under `prefers-reduced-motion`

## Frontend implementation

The interface is implemented with React and TypeScript on Vite. Tailwind CSS v4 utilities carry layout and component styling; the shared OKLCH palette and font stacks live in `classification/web/src/index.css` as Tailwind theme tokens.

Mathematical fragments are rendered inline with KaTeX and include MathML output for assistive technology. UI prose remains in the system sans-serif stack; only recognized expressions switch to mathematical typography.
