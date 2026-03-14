import { defineConfig } from 'vite';
import { resolve } from 'path';
import { NodePackageImporter } from 'sass';

export default defineConfig(({ mode }) => ({
    base: '/static/',
    root: 'assets',
    server: {
        port: 5173,
        origin: 'http://localhost:5173',
        strictPort: true,
    },
    build: {
        outDir: resolve(__dirname, 'build/static'),
        emptyOutDir: true,
        manifest: true,
        rolldownOptions: {
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
                silenceDeprecations: ['import', 'global-builtin', 'color-functions'],
                importers: [new NodePackageImporter()],
                loadPaths: [resolve(__dirname, 'node_modules')],
            },
        },
    },
}));
