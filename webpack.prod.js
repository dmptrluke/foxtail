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
            minimizer: {
                implementation: ImageMinimizerPlugin.imageminMinify,
                options: {

                    plugins: [
                        ['jpegtran', {progressive: true}],
                        ['optipng', {optimizationLevel: 5}],
                        [
                            "svgo",
                            {
                              plugins: [
                                {
                                  name: "preset-default",
                                  params: {
                                    overrides: {
                                      removeViewBox: false,
                                      addAttributesToSVGElement: {
                                        params: {
                                          attributes: [
                                            { xmlns: "http://www.w3.org/2000/svg" },
                                          ],
                                        },
                                      },
                                    },
                                  },
                                },
                              ],
                            },
                        ],
                    ],
                },
            },
        }),
        new CompressionPlugin({
            filename: '[path][base].gz',
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
