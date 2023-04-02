```
            string uri = string.Format("{0}\\Static\\index.html", System.IO.Path.GetDirectoryName(Application.ExecutablePath));
            webviewMain.Source = new Uri(uri);
            webviewMain.EnsureCoreWebView2Async();
```

```
        private void initWebviewSettings()
        {
            Stat.WebviewStat.IsReady = true;
            webviewMain.CoreWebView2.Settings.AreDevToolsEnabled = false;
            webviewMain.CoreWebView2.Settings.IsZoomControlEnabled = false;
            webviewMain.CoreWebView2.Settings.IsStatusBarEnabled = false;
            webviewMain.CoreWebView2.Settings.IsPinchZoomEnabled = false;
            webviewMain.CoreWebView2.Settings.IsPasswordAutosaveEnabled = false;
            webviewMain.CoreWebView2.Settings.HiddenPdfToolbarItems = (Microsoft.Web.WebView2.Core.CoreWebView2PdfToolbarItems)0xffffff;
            webviewMain.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
            webviewMain.CoreWebView2.Settings.AreBrowserAcceleratorKeysEnabled = false;
            webviewMain.CoreWebView2.NewWindowRequested += delegate (object s, Microsoft.Web.WebView2.Core.CoreWebView2NewWindowRequestedEventArgs args)
            {
                // TODO: check args.Uri and decide
                args.NewWindow = (Microsoft.Web.WebView2.Core.CoreWebView2)s;
            };
        }
        private void webviewMain_CoreWebView2InitializationCompleted(object sender, Microsoft.Web.WebView2.Core.CoreWebView2InitializationCompletedEventArgs e)
        {
            initWebviewSettings();
        }
```

index.js

```
'use strict';

var lastTitle = "";
window.chrome.webview.addEventListener("message", function (evt) {
    var json = JSON.parse(evt.data);
    if (lastTitle !== json.name) {
        lastTitle = json.name;
        document.body.innerHTML = "";
        document.body.appendChild(document.createTextNode("Hello " + json.name + "!"));
    }
});
```
