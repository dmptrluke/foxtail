import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
    base: '/static/',
    root: 'assets',
    build: {
        outDir: resolve(__dirname, 'build/static'),
        emptyOutDir: true,
        manifest: false,
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'assets/js/main.js'),
                profile_edit: resolve(__dirname, 'assets/js/profile_edit.js'),
            },
            output: {
                entryFileNames: '[name].js',
                chunkFileNames: '[name].js',
                assetFileNames: '[name][extname]',
            },
        },
        sourcemap: 'hidden',
    },
    css: {
        preprocessorOptions: {
            scss: { quietDeps: true },
        },
    },
});
