const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack'); // Import webpack for ProvidePlugin

module.exports = {
    mode: 'development', // For production, use 'production' (is set to development for dev server to work properly)
    entry: {
        robot_socket: './src/robot_socket.ts',
        style: './src/style.css',
        colors: './src/colors.css',
        elements: './src/elements.css',
        robot_3d_plot: './src/robot3dplot.png',
        dark_mode: './src/Toolbox/auto_dark_mode.ts',
        inspectionPoints: './src/interaction/inspectionPoints.ts',
        runCode: './src/interaction/runCode.ts',
        monacoEditor: './src/monacoExperiment.ts',
        inspectionGraph: './src/inspectionPointGraph/InspectionGraph.ts',
    },
    devtool: 'inline-source-map',
    devServer: {
        static: './dist',
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
                // exclude: /node_modules/,
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
                exclude: /node_modules/,
            }
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
        fallback: {
            path: require.resolve('path-browserify'), // Add the fallback for 'path'
            stream: require.resolve('stream-browserify'),
            assert: require.resolve('assert-browserify'),
            buffer: require.resolve('buffer-browserify'),
        },
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'dist'),
        clean: true, // Clean the output directory before emit.
    },
    plugins: [
        new HtmlWebpackPlugin({ // Generate index.html based on src/index.html
            hash: true,
            template: './src/index.html',
            filename: './index.html' //relative to root of the application
        }),
        new webpack.ProvidePlugin({
            process: 'process/browser',
        }),
    ],
    optimization: {
        runtimeChunk: 'single',
    },
    cache: {
        type: "filesystem"
    }
};