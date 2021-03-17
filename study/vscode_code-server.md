# VSCode

### Monaco Editor

```
# Create
require(['vs/editor/editor.main'], function () {
   var editor_api = api = monaco.editor.create(dom_container, editor_options, service_overrides);
});

# Destroy
editor_api.dispose();

# Resize
editor_api.layout();

# Hook Language
monaco.languages.register({ id: 'new_lang', extensions: [ '.lang' ] });

# Define New Language
# ref: https://microsoft.github.io/monaco-editor/monarch.html
monaco.languages.setMonarchTokensProvider('new_lang', { tokenizer: { root: [ /0-9+/, 'lang-number' ] } });

# Define New Theme
monaco.editor.defineTheme('new_lang', {
   base: 'vs',
   inherit: false,
   rules: [{ token: 'lang-number', foreground: '008888' }]
});

# Set Text
editor_api.setValue(text);

# Set Langauge
var model = editor_api.getModel();
monaco.editor.setModelLanguage(model, lang_id || 'javascript');

# Set Theme
monaco.editor.setTheme(theme_id || 'vs-dark');

# Goto Position
editor_api.revealPositionInCenter({ lineNumber: 1, column: 1 });

# Set Selection
editor_api.setSelection({ startLineNumber:1, startColumn:1, endLineNumber: 1, endColumn: 1 });

# Partial Text Update
# ref: https://github.com/microsoft/vscode/blob/master/src/vs/editor/common/core/editOperation.ts
# type: insert, delete, replace, replaceMove; no update history (cannot undo)
var model = editor_api.getModel();
var editOperation = require('vs/editor/common/core/editOperation').EditOperation;
model.applyEdits([editOperation.insert({lineNumber:1, column: 1}, 'hello')]);

# Integration File Loading with Restful API
function SomeTextModelService() {}
SomeTextModelService.prototype = {
   createModelReference: function (uri) { return this.getModel(uri); },
   registerTextModelContentProvider: function () { return { dispose: function () {} }; },
   hasTextModelContentProvider: function (schema) { return true; },
   _buildReference: function (model) {
      var lifecycle = require('vs/base/common/lifecycle');
      var ref = new lifecycle.ImmortalReference({ textEditorModel: model });
      return { object: ref.object, dispose: function () { ref.dispose(); } };
   },
   getModel: function (uri) {
      var _this = this;
      return new Promise(function (r) {
         var model = monaco.editor.getModel(uri);
         if (!model) { /* ajax.get('http://path/to/file').then(function (contents) { r(monaco.editor.createModel(contents, 'javascript', uri)); return; }) */ }
         r(_this._buildReference(model));
      });
   }
};
var editor_api = monaco.editor.create(dom_container, editor_options, {
	textModelService: new SomeTextModelService()
});

# Support Minimap Scroll on Mobile
function patch_minimap_touch(editor_api) {
   // get ViewPart[minimap]
   var minimap = editor_api._modelData.view.viewParts.filter(function (x) { return x._slider; })[0];
   if (!minimap) return;
   var vscode_dom = require('vs/base/browser/dom');
   minimap._sliderTouchStartListener = vscode_dom.addStandardDisposableListener(
      minimap._slider.domNode, 'touchstart', function(evt) {
         evt.preventDefault();
         var touch = evt.touches[0];
         if (!touch) return;
         if (!minimap._lastRenderData) return;
         minimap._slider.toggleClassName('active', true);
         var initialMousePosition = touch.clientY;
         var initialSliderState = minimap._lastRenderData.renderedLayout;
         var monitor_move = vscode_dom.addStandardDisposableListener(document.body, 'touchmove', function (e) {
            var touch = e.touches[0];
            if (!touch) return;
            var mouseDelta = touch.clientY - initialMousePosition;
            minimap._context.viewLayout.setScrollPositionNow({
               scrollTop: initialSliderState.getDesiredScrollTopFromDelta(mouseDelta)
            });
         });
         var monitor_stop = vscode_dom.addStandardDisposableListener(document.body, 'touchend', function (e) {
            minimap._slider.toggleClassName('active', false);
            monitor_move.dispose();
            monitor_stop.dispose();
         });
      }  
   ); 
}

# Mouse Hover Token Tip
if (!window.monaco_patched) {
   window.monaco_patched = true;
   var hoverProvider = {
      provideHover: function (model, position, token) {
         return Promise.resolve({ // TODO: ajax
         	contents: [ { value: 'hello world' } ],
         	range: { startLineNumber:1, startColumn:1, endLineNumber: 1, endColumn: 1 }
         });
      }
   };
   var definitionProvider = {
      provideDefinition: function (model, position, token) {
         return Promise.resolve([{ // TODO: ajax
         	uri: monaco.Uri.parse('http://host/to_file_name'),
         	range: { startLineNumber:1, startColumn:1, endLineNumber: 1, endColumn: 1 }
         }]);
      }
   };
   lang.forEach(function (lang) {
    	monaco.languages.onLanguage(lang, function () {
        	monaco.languages.registerHoverProvider(lang, hoverProvider);
        	monaco.languages.registerDefinitionProvider(lang, definitionProvider);
    	});
   }); // foreach; register worker to language
}

# Extra Button on Peek Definition Widget
_patchReferencesController() {
    let rc = this.editor.getEditorApi().getContribution('editor.contrib.referencesController');
    this._backup.rc_toggleWidget = rc.toggleWidget;
    rc.toggleWidget = (range, modelPromise, options) => {
       let _widget = this._backup.rc_widget;
       this._backup.rc_toggleWidget.call(rc, range, modelPromise, options);
       if (_widget !== rc._widget) {
          _widget = rc._widget;
          this._backup.rc_widget = _widget;
          let lib = window['require']('vs/base/common/actions')
          let bar = _widget._actionbarWidget;
          bar.push(new lib.Action('flame.openInNewTab', '⬒', 'class', true, () => {
             if (!_widget) return;
             if (!_widget._previewModelReference) return;
             if (!_widget._previewModelReference.object) return;
             if (!_widget._previewModelReference.object.textEditorModel) return;
             let model = _widget._previewModelReference.object.textEditorModel;
             let uri = model.uri;
             let loc = '';
             let range = _widget && _widget._revealedReference && _widget._revealedReference._range;
             if (range) {
                if (range.startLineNumber === range.endLineNumber && range.startColumn === range.endColumn) {
                   loc = `#L${range.startLineNumber}.${range.startColumn}`;
                } else {
                   loc = `#L${range.startLineNumber}.${range.startColumn}-${range.endLineNumber}.${range.endColumn}`;
                }
             }
             window.open('/url/to/browse/' + uri.authority + uri.path + loc);
          }), { index: 0 });
       }
    };
}
```

# Code-Server

ref: https://github.com/cdr/code-server

```
build:

docker pull python
docker run --rm -it -v `pwd`:/opt/code-server python bash
# apt-get install -y build-essential pkg-config libx11-dev libxkbfile-dev libsecret-1-dev python3 jq rsync
# cd /opt
# wget https://nodejs.org/dist/v14.16.0/node-v14.16.0-linux-x64.tar.xz
# tar Jxf node-v14.16.0-linux-x64.tar.xz
# export PATH=$PATH:/opt/node-v14.16.0-linux-x64/bin
# npm config set python python3
# npm install -g yarn
# ./node_modules/.bin/yarn install
# cd /opt/code-server
# yarn install
# npm run build && npm run build:vscode && npm run release && npm run release:standalone
```

```
run:
PASSWORD='shitest' ./bin/code-server --auth password \
   --bind-addr <ip>:19443 \
   --user-data-dir ./local/user \
   --extensions-dir ./local/ext \
   --disable-telemetry --disable-update-check

[node]:bin/code-server ->
   [node]:bin/code-server ->
      [node]:lib/vscode/out/vs/server/fork ->
         visitor => editor >> [node]:lib/vscode/out/bootstrap-fork(--type=extensionHost)
	 visitor => terminal >> [bash]

[webUI] -> (each:visitor 2 ws channels)
   [resource]:/static
   [api]:/vscode-remote-resource
   [api:ws]:?reconnectionToken=<uuid>&reconnection=false&skipWebSocketFrames=false
   [api:ws]:?reconnectionToken=<uuid>&reconnection=false&skipWebSocketFrames=false
```
