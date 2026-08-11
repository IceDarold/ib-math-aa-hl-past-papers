import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MotionConfig } from 'motion/react'
import 'katex/dist/katex.min.css'
import App from './App'
import { I18nProvider } from './i18n'
import './index.css'

const root = document.getElementById('root')
if (!root) throw new Error('Root element not found')

createRoot(root).render(
  <StrictMode>
    <MotionConfig reducedMotion="user" transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}>
      <I18nProvider>
        <App />
      </I18nProvider>
    </MotionConfig>
  </StrictMode>,
)
