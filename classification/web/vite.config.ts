import { createReadStream, existsSync, statSync } from 'node:fs'
import { resolve, sep } from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import type { Connect, Plugin } from 'vite'
import { defineConfig } from 'vite'

const archiveRoot = resolve(import.meta.dirname, '../../AA_HL')
const practicumRoot = resolve(import.meta.dirname, '../../practicum')

function fileMiddleware(root: string, contentType: string): Connect.NextHandleFunction {
  return (request, response, next) => {
    if (!request.url || !['GET', 'HEAD'].includes(request.method ?? 'GET')) {
      next()
      return
    }

    const pathname = decodeURIComponent(request.url.split('?')[0] ?? '')
    const relativePath = pathname.replace(/^\/+/, '')
    const filePath = resolve(root, relativePath)

    if (
      filePath !== root &&
      !filePath.startsWith(`${root}${sep}`)
    ) {
      response.statusCode = 403
      response.end('Forbidden')
      return
    }

    if (!existsSync(filePath) || !statSync(filePath).isFile()) {
      next()
      return
    }

    response.setHeader('Content-Type', contentType)
    response.setHeader('Content-Length', statSync(filePath).size)
    if (request.method === 'HEAD') {
      response.end()
      return
    }
    createReadStream(filePath).pipe(response)
  }
}

function serveArchive(): Plugin {
  const archiveHandler = fileMiddleware(archiveRoot, 'application/pdf')
  const practicumHandler = fileMiddleware(practicumRoot, 'application/x-ipynb+json; charset=utf-8')
  return {
    name: 'serve-learning-materials',
    configureServer(server) {
      server.middlewares.use('/AA_HL', archiveHandler)
      server.middlewares.use('/practicum', practicumHandler)
    },
    configurePreviewServer(server) {
      server.middlewares.use('/AA_HL', archiveHandler)
      server.middlewares.use('/practicum', practicumHandler)
    },
  }
}

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss(), serveArchive()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      // Порядок важен: тренажёр живёт на своём порту, и его префикс длиннее.
      // Порт можно перебить: на боевой машине служба уже занимает 8042, и
      // поднять рядом вторую для проверки иначе не выйдет.
      '/api/drill': process.env.DRILL_PORT
        ? `http://127.0.0.1:${process.env.DRILL_PORT}`
        : 'http://127.0.0.1:8042',
      // Атлас тоже можно перебить портом: рядом с боевой службой
      // поднимается вторая, чтобы проверить, не тронув первую.
      '/api': process.env.ATLAS_PORT
        ? `http://127.0.0.1:${process.env.ATLAS_PORT}`
        : 'http://127.0.0.1:8041',
    },
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
  },
})
