const webpack = require('webpack');
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    entry: {
        main: ['./js/main.js', './scss/index.scss'],
        profile_edit: ['./js/profile_edit.js']
    },
    output: {
        path: path.resolve('./storage/bundles'),
        filename: '[name].[contenthash].js'
    },
    context: path.resolve(__dirname, "assets"),
    performance: {
        hints: false
    },
    node: false,
    optimization: {
        moduleIds: 'deterministic',
        runtimeChunk: 'single',
    },
    resolve: {
        alias: {
            '~': path.resolve(__dirname, 'node_modules')
        },
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name].[contenthash].css'
        }),
        new CleanWebpackPlugin(),
        new BundleTracker({filename: './storage/webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
    ],
    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env',
                                {
                                    "useBuiltIns": "usage",
                                    "corejs": 3
                                }
                            ]
                        ]
                    }
                }
            },

            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                    },
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: true,
                        },
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: [
                                    [
                                        'autoprefixer'
                                    ],
                                ],
                            },
                            sourceMap: true,
                        },
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sassOptions: {
                                sourceMap: true
                            }
                        },
                    },
                ],
            },
            {
                test: /\.(png|webp|jpg|gif)$/,
                use: {
                    loader: 'file-loader',
                    options: {
                        name: '[contenthash].[ext]',
                        outputPath: 'images/'
                    }
                }
            },
            {
                test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: '[contenthash].[ext]',
                            outputPath: 'fonts/'
                        }
                    }
                ]
            }
        ],
    }
    ,
}
;
