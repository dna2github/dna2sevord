    _patchReferencesController() {
        let rc = editor_api.getContribution('editor.contrib.referencesController');
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
