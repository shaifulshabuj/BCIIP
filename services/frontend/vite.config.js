import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react(),
        VitePWA({
            registerType: 'autoUpdate',
            includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
            manifest: {
                name: 'BCIIP Intelligence',
                short_name: 'BCIIP',
                description: 'Bangladesh Continuous Internet Intelligence Platform',
                theme_color: '#ffffff',
                icons: [
                    {
                        src: 'pwa-192x192.png',
                        sizes: '192x192',
                        type: 'image/png'
                    },
                    {
                        src: 'pwa-512x512.png',
                        sizes: '512x512',
                        type: 'image/png'
                    }
                ]
            }
        })
    ],
    server: {
        host: true, // Listen on all addresses (already done via CLI but good to have)
        port: 3000,
        allowedHosts: true, // Allow any host (needed for Docker network access via aliases)
        proxy: {
            '/articles': 'http://api:8000',
            '/search': 'http://api:8000',
            '/topics': 'http://api:8000',
            '/entities': 'http://api:8000'
        }
    }
})
