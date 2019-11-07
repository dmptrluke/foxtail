const merge = require('webpack-merge');
const CompressionPlugin = require('compression-webpack-plugin');
const ImageminPlugin = require('imagemin-webpack-plugin').default;
const zopfli = require('@gfx/zopfli');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'production',
    devtool: 'source-map',
    plugins: [
        new ImageminPlugin({ test: /\.(jpe?g|png|gif|svg)$/i }),
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