import webpack from 'webpack';
import path from 'path';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import BundleTracker from 'webpack-bundle-tracker';

const ROOT_DIR = path.resolve(import.meta.dirname, '..');

export default {
    entry: {
        main: ['./js/main.js', './scss/index.scss'],
        profile_edit: ['./js/profile_edit.js'],
    },
    output: {
        path: path.resolve(ROOT_DIR, 'build/webpack_bundles'),
        publicPath: '',
        filename: '[name].[contenthash].js',
        clean: true,
    },
    context: path.resolve(ROOT_DIR, 'assets'),
    performance: {
        hints: false,
    },
    optimization: {
        moduleIds: 'deterministic',
        runtimeChunk: 'single',
    },
    resolve: {
        alias: {
            '~': path.resolve(ROOT_DIR, 'node_modules'),
        },
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name].[contenthash].css',
        }),
        new BundleTracker({
            path: path.join(ROOT_DIR, '/build'),
            filename: 'webpack-stats.json',
        }),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
        }),
    ],
    module: {
        rules: [
            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: { sourceMap: true },
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: ['autoprefixer'],
                            },
                            sourceMap: true,
                        },
                    },
                    {
                        loader: 'sass-loader',
                        options: { sourceMap: true },
                    },
                ],
            },
            {
                test: /\.(png|webp|jpg|gif)$/,
                type: 'asset/resource',
                generator: {
                    filename: 'images/[contenthash][ext]',
                },
            },
            {
                test: /\.(woff2?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                type: 'asset/resource',
                generator: {
                    filename: 'fonts/[contenthash][ext]',
                },
            },
        ],
    },
};
