#!/usr/bin/env python3
"""
JavaScript-Python Bridge
Handles communication between WebView (JavaScript) and Python backend
"""

import wx
import wx.html2
import json


class MessageHandler(wx.html2.WebViewHandler):
    """Custom handler for JavaScript messages"""

    def __init__(self, main_window):
        super().__init__("custom")
        self.main_window = main_window

    def OnRequest(self, webview, request):
        # This is for custom protocol handling, not used for message passing
        return None


def setup_bridge(main_window):
    """
    Set up bidirectional communication between JavaScript and Python

    Args:
        main_window: MainWindow instance with webview and projection_window
    """

    # Inject JavaScript bridge into the page
    script = """
    (function() {
        // Create Python bridge object
        window.pythonBridge = {
            // Show URL in projection window
            showURL: function(url) {
                console.log('Bridge: showURL', url);
                window.location.hash = '#cmd=showURL&url=' + encodeURIComponent(url);
            },

            // Show Bible verse in projection window
            showBible: function(text, chineseSize, englishSize) {
                console.log('Bridge: showBible', text, chineseSize, englishSize);
                var data = {
                    text: text,
                    chineseSize: chineseSize || 26,
                    englishSize: englishSize || 24
                };
                window.location.hash = '#cmd=showBible&data=' + encodeURIComponent(JSON.stringify(data));
            },

            // Show Agenda in projection window
            showAgenda: function(html) {
                console.log('Bridge: showAgenda', html);
                window.location.hash = '#cmd=showAgenda&html=' + encodeURIComponent(html);
            },

            // Hide projection window
            hideProjection: function() {
                console.log('Bridge: hideProjection');
                window.location.hash = '#cmd=hideProjection';
            },

            // Update display status
            updateDisplayStatus: function(text) {
                console.log('Bridge: updateDisplayStatus', text);
                var elem = document.getElementById('monitor-status');
                if (elem) {
                    var textElem = elem.querySelector('.status-text');
                    if (textElem) {
                        textElem.textContent = text;
                    }
                }
            }
        };

        console.log('Python bridge initialized');
    })();
    """

    def on_loaded(event):
        """Called when the page finishes loading"""
        if event.GetURL().startswith('file://'):
            main_window.webview.RunScript(script)
            print("JavaScript bridge injected")

            # Update display status
            display_count = len(main_window.displays)
            if display_count > 1:
                status_script = f"pythonBridge.updateDisplayStatus('{display_count} displays detected');"
            else:
                status_script = "pythonBridge.updateDisplayStatus('1 display (no secondary)');"

            main_window.webview.RunScript(status_script)

    def on_url_changed(event):
        """Monitor URL changes to capture commands from JavaScript"""
        url = event.GetURL()

        # Check for hash commands
        if '#cmd=' in url:
            try:
                # Parse command from hash
                hash_part = url.split('#')[1]
                params = {}

                for param in hash_part.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value

                command = params.get('cmd', '')

                if command == 'showURL':
                    url_to_show = params.get('url', '')
                    if url_to_show:
                        from urllib.parse import unquote
                        url_to_show = unquote(url_to_show)
                        print(f"Python: Showing URL: {url_to_show}")
                        main_window.projection_window.show_url(url_to_show)

                elif command == 'showBible':
                    data_json = params.get('data', '')
                    if data_json:
                        from urllib.parse import unquote
                        data = json.loads(unquote(data_json))
                        print(f"Python: Showing Bible: {data['text'][:50]}...")
                        main_window.projection_window.show_bible(
                            data['text'],
                            int(data.get('chineseSize', 26)),
                            int(data.get('englishSize', 24))
                        )

                elif command == 'showAgenda':
                    html = params.get('html', '')
                    if html:
                        from urllib.parse import unquote
                        html = unquote(html)
                        print(f"Python: Showing Agenda")
                        main_window.projection_window.show_agenda(html)

                elif command == 'hideProjection':
                    print("Python: Hiding projection")
                    main_window.projection_window.hide_projection()

                # Clear the hash to allow repeated commands
                wx.CallAfter(lambda: main_window.webview.RunScript("window.location.hash = '';"))

            except Exception as e:
                print(f"Error processing command: {e}")

    # Bind events
    main_window.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, on_loaded)
    main_window.webview.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, on_url_changed)

    print("Bridge setup complete")
