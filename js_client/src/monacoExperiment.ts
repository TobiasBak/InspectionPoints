import * as monaco from 'monaco-editor';
import { loadWASM } from 'onigasm';
import { Registry } from 'monaco-textmate';
import { wireTmGrammars } from 'monaco-editor-textmate';

// Inspired by the following:
//https://stackblitz.com/edit/1-monaco-editor-textmate-grammar-loading-example?file=src%2Fmain.ts
// https://www.npmjs.com/package/monaco-editor-textmate?activeTab=readme
// needed https://github.com/Nishkalkashyap/monaco-vscode-textmate-theme-converter/tree/master/src to convert the theme and get nicer colors

//as always, shoutout to Ahern guo for the TextMate grammar
// https://github.com/ahernguo/urscript-extension/blob/master/syntaxes/urscript.tmLanguage.json

const code = `
a = p[-0.421, -0.436, 0.1, 2.61, -1.806, -0.019]
movej(a, a=0.3, v=0.3)

b = p[-0.194, -0.6, 0.066, 2.61, -1.806, -0.019]
movej(b, a=0.3, v=0.3)
`;

const editorElement = document.getElementById('editor');

export let editor: monaco.editor.IStandaloneCodeEditor | null = null;

// @ts-ignore
(async () => {
    const onigasmResponse = await fetch(
        'https://cdn.jsdelivr.net/npm/onigasm@latest/lib/onigasm.wasm' // use for web (to prevent CORS etc.)
        // 'onigasm/lib/onigasm.wasm' // use while working on local or custom loaders (webpack, vite, etc.)
    );

    if (
        onigasmResponse.status !== 200 ||
        onigasmResponse.headers.get('content-type') !== 'application/wasm'
    ) {
        console.warn("Failed to load onigasm.wasm");
        return null;
    }

    const wasmContent = await onigasmResponse.arrayBuffer();

    if (wasmContent) {
        await loadWASM(wasmContent);
    }

    const registry = new Registry({
        getGrammarDefinition: async (scopeName: string): Promise<any> => {
            console.log('scopeName', scopeName);

            const res: any = {
                format: 'json',
                content: await (
                    await fetch('https://raw.githubusercontent.com/ahernguo/urscript-extension/refs/heads/master/syntaxes/urscript.tmLanguage.json')
                ).text(),
            };

            console.log('grammarContent', res);

            return res;
        },
    });

    const grammars = new Map();

    monaco.languages.register({ id: 'urscript' });

    grammars.set('urscript', 'source.urscript');

    console.log(grammars);

    // #endregion


    console.log(await (await fetch("theme/monaco-dark-modern.json")).text())
    const monacoTheme = JSON.parse(await (await fetch("theme/monaco-dark-modern.json")).text())
    // #region Init Editor
    monaco.editor.defineTheme('vs-code-theme-converted', monacoTheme);

    editor = monaco.editor.create(editorElement!, {
        value: code,
        language: 'urscript',
        theme: 'vs-code-theme-converted',
        minimap: {
            enabled: false,
        },
    });

    // #endregion

    // #region Wire Grammars

    await wireTmGrammars(monaco, registry, grammars, editor);

})();


