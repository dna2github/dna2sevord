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



   function FlameTextModelService (editor) {
      this.editor = editor;
   }
   FlameTextModelService.prototype = {
      createModelReference: function (uri) {
         return this.getModel(uri).then(function (model) {
            var object = {
               load: function () { return Promise.resolve(object); },
               dispose: function () {},
               textEditorModel: model
            };
            return Promise.resolve({
               object: object,
               dispose: function () {}
            });
         });
      },
      registerTextModelContentProvider: function () {
         return { dispose: function () {} };
      },
      hasTextModelContentProvider: function (schema) {
         return true;
      },
      getModel: function (uri) {
         return new Promise(function (r) {
            var model = monaco.editor.getModel(uri);
            if (!model) {
               // TODO: monaco.editor.createModel('', 'javascript', uri);
            }
            r(model);
         });
      }
   };
