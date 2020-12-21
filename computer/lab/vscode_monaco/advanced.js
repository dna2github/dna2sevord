// # change decorations
decorationId = ui.editor.api.deltaDecorations([], [
   {
      range: new monaco.Range(1, 1, 1, 4),
      options: {
         inlineClassName: 'marker-test',
         stickiness: 10,
         hoverMessage: {value: 'hello my friend'}
      }
   }
]);

// # Load file content
FlameTextModelService.prototype = {
   createModelReference: function (uri) {
      return this.getModel(uri);
   },
   registerTextModelContentProvider: function () {
      return { dispose: function () {} };
   },
   hasTextModelContentProvider: function (schema) {
      return true;
   },
   _buildReference: function (model) {
      var lifecycle = require('vs/base/common/lifecycle');
      var ref = new lifecycle.ImmortalReference({ textEditorModel: model });
      return {
         object: ref.object,
         dispose: function () { ref.dispose(); }
      };
   },
   getModel: function (uri) {
      var _this = this;
      return new Promise(function (r) {
         var model = monaco.editor.getModel(uri);
         if (!model) {
            // ajax.get('http://host/to_file_name').then((contents) => {
            //	r(monaco.editor.createModel(contents, 'javascript', uri);)
            // });
            // return;
         }
         r(_this._buildReference(model));
      });
   }
};

var editor_api = monaco.editor.create(dom_container, editor_options, {
	textModelService: new FlameTextModelService()
});

// # Patch minimap to support mobile touch
function patch_minimap_touch(editor_api) {
   // 找到 minimap 的 ViewPart
   var minimap = editor_api._modelData.view.viewParts.filter((x) => x._slider)[0];
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

// # register token hover and xref
if (!window.monaco_patched) {
   window.monaco_patched = true;
   var hoverProvider = {
      provideHover: function (model, position, token) {
      	 // ajax + return new Promise(function (resolve, reject) { ... })
         return Promise.resolve({
         	contents: [ { value: 'hello world' } ],
         	range: { startLineNumber:1, startColumn:1, endLineNumber: 1, endColumn: 1 }
         });
      }
   };
   var definitionProvider = {
      provideDefinition: function (model, position, token) {
      	 // ajax + return new Promise(function (resolve, reject) { ... })
         return Promise.resolve([{
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


https://github.com/Microsoft/vscode/blob/master/src/vs/editor/browser/viewParts/selections/selections.ts (SelectionsOverlay)
https://github.com/Microsoft/vscode/blob/master/src/vs/editor/browser/view/viewImpl.ts (View.createViewParts)
https://github.com/Microsoft/vscode/blob/master/src/vs/editor/browser/view/dynamicViewOverlay.ts (dynamicViewOverlay)
https://github.com/Microsoft/vscode/blob/master/src/vs/editor/common/viewModel/viewEventHandler.ts (viewEventHandler)
SelectionsOverlay implements dynamicViewOverlay
dynamicViewOverlay, View implements viewEventHandler
ui.editor.api._modelData.view.viewParts

