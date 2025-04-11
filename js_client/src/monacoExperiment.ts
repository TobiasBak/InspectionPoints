import * as monaco from 'monaco-editor';
import { loadWASM } from 'onigasm';
import { Registry } from 'monaco-textmate';
import { wireTmGrammars } from 'monaco-editor-textmate';

// Inspired by the following:
//https://stackblitz.com/edit/1-monaco-editor-textmate-grammar-loading-example?file=src%2Fmain.ts
// https://www.npmjs.com/package/monaco-editor-textmate?activeTab=readme
//

const code = `
while True:
  set_digital_out(0,True)
end

if a== False:
  movej(a, [1,2,3,4,5,6])
end
`;

const editorElement = document.getElementById('editor');

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

    const editor = monaco.editor.create(editorElement!, {
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


