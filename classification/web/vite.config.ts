import { createReadStream, existsSync, statSync } from 'node:fs'
import { resolve, sep } from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import type { Connect, Plugin } from 'vite'
import { defineConfig } from 'vite'

const archiveRoot = resolve(import.meta.dirname, '../../AA_HL')

function archiveMiddleware(): Connect.NextHandleFunction {
  return (request, response, next) => {
    if (!request.url || !['GET', 'HEAD'].includes(request.method ?? 'GET')) {
      next()
      return
    }

    const pathname = decodeURIComponent(request.url.split('?')[0] ?? '')
    const relativePath = pathname.replace(/^\/AA_HL\/?/, '').replace(/^\/+/, '')
    const filePath = resolve(archiveRoot, relativePath)

    if (
      filePath !== archiveRoot &&
      !filePath.startsWith(`${archiveRoot}${sep}`)
    ) {
      response.statusCode = 403
      response.end('Forbidden')
      return
    }

    if (!existsSync(filePath) || !statSync(filePath).isFile()) {
      next()
      return
    }

    response.setHeader('Content-Type', 'application/pdf')
    response.setHeader('Content-Length', statSync(filePath).size)
    if (request.method === 'HEAD') {
      response.end()
      return
    }
    createReadStream(filePath).pipe(response)
  }
}

function serveArchive(): Plugin {
  const handler = archiveMiddleware()
  return {
    name: 'serve-aa-hl-archive',
    configureServer(server) {
      server.middlewares.use('/AA_HL', handler)
    },
    configurePreviewServer(server) {
      server.middlewares.use('/AA_HL', handler)
    },
  }
}

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss(), serveArchive()],
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
  },
})
