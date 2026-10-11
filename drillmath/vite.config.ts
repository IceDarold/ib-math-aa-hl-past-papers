import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

/** Тренажёр ходит в ту же службу, что и атлас: ib-drill на 8042.
 *  Своего бэкенда у сайта нет и не нужно — журнал один на оба входа. */
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '127.0.0.1',
    port: 5174,
    proxy: {
      '/api/drill': process.env.DRILL_PORT
        ? `http://127.0.0.1:${process.env.DRILL_PORT}`
        : 'http://127.0.0.1:8042',
    },
  },
})
