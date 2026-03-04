import { merge } from 'webpack-merge';
import common from './common.mjs';

export default merge(common, {
    mode: 'development',
    devtool: 'source-map',
});
