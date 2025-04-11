const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    mode: 'development', // For production, use 'production' (is set to development for dev server to work properly)
    entry: {
        // input: './src/input.ts',
        // input_highlight: './src/SyntaxHighlighting/inputFieldHighlight.ts',
        robot_socket: './src/robot_socket.ts',
        style: './src/style.css',
        colors: './src/colors.css',
        elements: './src/elements.css',
        robot_3d_plot: './src/robot3dplot.png',
        dark_mode: './src/Toolbox/auto_dark_mode.ts',
        undo_handler: './src/undoEventHandler.ts',
        executing_feedback: './src/interaction/robot_executing_feedback.ts',
        collapseUndoneCommands: './src/interaction/collapseUndoneCommands.ts',
        monacoEditor: './src/monacoExperiment.ts',
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
        })
    ],
    optimization: {
        runtimeChunk: 'single',
    },
};