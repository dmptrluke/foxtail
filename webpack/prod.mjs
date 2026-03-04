import { merge } from 'webpack-merge';
import CssMinimizerPlugin from 'css-minimizer-webpack-plugin';
import common from './common.mjs';

export default merge(common, {
    mode: 'production',
    devtool: 'hidden-source-map',
    optimization: {
        minimizer: [
            '...',
            new CssMinimizerPlugin(),
        ],
    },
});
