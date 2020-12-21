require(
	[
    	'vs/editor/editor.main'
    ], function () {
    	var editor_api = api = monaco.editor.create(dom_container, editor_options, service_overrides);
	}
);


editor_api.dispose();

/* after update container size */ editor_api.layout();

monaco.languages.register({ id: 'new_lang', extensions: [ '.lang' ] });

// Monarch doc: https://microsoft.github.io/monaco-editor/monarch.html
monaco.languages.setMonarchTokensProvider('new_lang', {
	tokenizer: {
		root: [ /0-9+/, 'lang-number' ]
	}
});

monaco.editor.defineTheme('new_lang', {
	base: 'vs',
	inherit: false,
	rules: [
		{ token: 'lang-number', foreground: '008888' }
	]
});

editor_api.setValue(text);

editor_api.revealPositionInCenter({ lineNumber: 1, column: 1 });

editor_api.setSelection({ startLineNumber:1, startColumn:1, endLineNumber: 1, endColumn: 1 });

var model = editor_api.getModel();
monaco.editor.setModelLanguage(model, lang_id || 'javascript');
monaco.editor.setTheme(theme_id || 'vs-dark');

var editOperation = require('vs/editor/common/core/editOperation').EditOperation;
// ref: https://github.com/microsoft/vscode/blob/master/src/vs/editor/common/core/editOperation.ts
// support insert, delete, replace, replaceMove
model.applyEdits([editOperation.insert({lineNumber:1, column: 1}, 'hello')]);


