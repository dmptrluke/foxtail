import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ mode }) => ({
    base: '/static/',
    root: 'assets',
    server: {
        host: '0.0.0.0',
        port: 5173,
        strictPort: true,
        hmr: {
            host: 'localhost',
        },
        watch: {
            usePolling: true,
        },
    },
    build: {
        outDir: resolve(__dirname, 'build/static'),
        emptyOutDir: true,
        manifest: true,
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'assets/js/main.js'),
            },
        },
        sourcemap: true,
        cssMinify: mode !== 'development',
        minify: mode !== 'development',
    },
    css: {
        preprocessorOptions: {
            scss: {
                quietDeps: true,
                silenceDeprecations: ['import', 'global-builtin'],
            },
        },
    },
}));
