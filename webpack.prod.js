const {merge} = require('webpack-merge');
const CompressionPlugin = require('compression-webpack-plugin');
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');
const zopfli = require('@gfx/zopfli');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'production',
    devtool: 'source-map',
    plugins: [
        new ImageMinimizerPlugin({
            minimizerOptions: {
                plugins: [
                    ['jpegtran', {progressive: true}],
                    ['optipng', {optimizationLevel: 5}],
                    [
                        'svgo',
                        {
                            plugins: [
                                {
                                    removeViewBox: false,
                                },
                            ],
                        },
                    ],
                ],
            },
        }),
        new CompressionPlugin({
            filename: '[path].gz[query]',
            test: /\.(js|css|html|svg)$/,
            compressionOptions: {
                numiterations: 15,
            },
            algorithm(input, compressionOptions, callback) {
                return zopfli.gzip(input, compressionOptions, callback);
            },
            deleteOriginalAssets: false,
        })
    ]
});
