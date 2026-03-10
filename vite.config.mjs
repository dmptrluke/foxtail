import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ mode }) => ({
    base: '/static/',
    root: 'assets',
    build: {
        outDir: resolve(__dirname, 'build/static'),
        emptyOutDir: true,
        manifest: false,
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'assets/js/main.js'),
            },
            output: {
                entryFileNames: '[name].js',
                chunkFileNames: '[name]-[hash].js',
                assetFileNames: '[name][extname]',
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
