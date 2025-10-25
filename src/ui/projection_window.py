#!/usr/bin/env python3
"""
Projection Window - Borderless fullscreen window for secondary display
Displays Bible verses, hymns, slides, or webpages
"""

import wx
import wx.html2


class ProjectionWindow(wx.Frame):
    """Borderless fullscreen window for projection on secondary display"""

    def __init__(self, display_index=1, window_name="Projection", main_window=None):
        """
        Initialize projection window

        Args:
            display_index: Index of display to use (0 = primary, 1 = secondary, etc.)
            window_name: Name for this window (e.g., "Hymn", "Agenda", "Bible")
            main_window: Reference to main window for command forwarding
        """
        # Store window name for logging
        self.window_name = window_name
        self.main_window = main_window

        # Get display information
        self.display_index = display_index
        self.display = self._get_display(display_index)

        if not self.display:
            # Fallback to primary display if secondary not available
            print(f"[{window_name}Window] Warning: Display {display_index} not found, using primary display")
            self.display = wx.Display(0)
            self.display_index = 0

        # Get display geometry
        display_rect = self.display.GetGeometry()

        print(f"[{window_name}Window] Creating on Display {display_index}:")
        print(f"  Position: ({display_rect.x}, {display_rect.y})")
        print(f"  Size: {display_rect.width}x{display_rect.height}")

        # Create frameless window
        super().__init__(
            parent=None,
            title=f"{window_name} Projection Window",
            pos=(display_rect.x, display_rect.y),
            size=(display_rect.width, display_rect.height),
            style=wx.NO_BORDER | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR
        )

        # Store display geometry for later use
        self.display_rect = display_rect

        # Set black background
        self.SetBackgroundColour(wx.BLACK)

        # Create main panel
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.BLACK)

        # Create sizer for layout
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)


        # Content tracking
        self.content_type = None  # 'url' or 'html'
        self.current_url = None  # Track current URL to avoid unnecessary reloads
        self.current_html_hash = None  # Track HTML content hash to avoid unnecessary reloads

        # Create single WebView for all content
        self.webview = wx.html2.WebView.New(self.panel)
        self.sizer.Add(self.webview, 1, wx.EXPAND)

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Bind title changes to capture JavaScript console.log
        self.webview.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.on_title_changed)

        # Initially hide the window
        self.Hide()

    def on_title_changed(self, event):
        """Handle title changes from JavaScript (used for console logging and commands)"""
        title = event.GetString()

        # Handle console logs
        if title.startswith('LOG:'):
            print(f"[{self.window_name}Window JS] {title[4:]}")
        elif title.startswith('ERROR:'):
            print(f"[{self.window_name}Window JS ERROR] {title[6:]}")
        elif title.startswith('CMD:'):
            # Handle commands from projection window
            print(f"[{self.window_name}Window CMD] {title[4:]}")
            # Forward command to main window's webview so bridge can process it
            if self.main_window and hasattr(self.main_window, 'webview'):
                # Trigger the main window's title change handler by setting its title
                wx.CallAfter(lambda: self._forward_command(title))

    def _forward_command(self, cmd_title):
        """Forward command from projection window to main window's bridge"""
        try:
            import json
            # Use JSON encoding to safely pass command string
            cmd_title_json = json.dumps(cmd_title)
            script = f"document.title = {cmd_title_json};"
            self.main_window.webview.RunScript(script)
            print(f"[{self.window_name}Window] Forwarded command to main window")
        except Exception as e:
            print(f"[{self.window_name}Window] Error forwarding command: {e}")

    def _get_display(self, index):
        """Get display by index, return None if not available"""
        display_count = wx.Display.GetCount()
        if 0 <= index < display_count:
            return wx.Display(index)
        return None

    def _ensure_focus(self, webview):
        """Helper method to ensure focus is set to webview"""
        try:
            self.Raise()
            self.SetFocus()
            webview.SetFocus()
        except:
            pass  # Ignore errors if window/webview no longer exists

    def show_url(self, url, force_reload=False):
        """
        Show a URL/webpage/hymn/slides in the projection window

        Args:
            url: URL to display
            force_reload: If True, reload even if URL hasn't changed
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url

        # Reload if URL changed OR if force_reload is True
        if self.current_url != url or force_reload:
            print(f"[{self.window_name}Window] Loading URL: {url}" + (" (force reload)" if force_reload else ""))
            self.webview.LoadURL(url)
            self.current_url = url
        else:
            print(f"[{self.window_name}Window] URL unchanged, preserving current page position")

        self.content_type = 'url'
        self._show_window()

    def show_html(self, html_content, preserve_scroll=False):
        """
        Show HTML content in the projection window

        Args:
            html_content: HTML content to display (e.g., Bible verses, custom content)
            preserve_scroll: If True, save and restore scroll position
        """
        import hashlib

        # Calculate hash of HTML content to detect if it's changed
        html_hash = hashlib.md5(html_content.encode('utf-8')).hexdigest()

        # Check if content is the same and window is already showing HTML
        if (self.content_type == 'html' and
            self.current_html_hash == html_hash and
            not preserve_scroll):
            # Content hasn't changed, just show the window without reloading
            print(f"[{self.window_name}Window] HTML content unchanged, just showing window")
            self._show_window()
            return

        print(f"[{self.window_name}Window] Loading HTML content (preserve_scroll={preserve_scroll}, content_changed={self.current_html_hash != html_hash})")

        # Save scroll position before reload if requested
        saved_scroll = None
        if preserve_scroll and self.content_type == 'html':
            try:
                # Get current scroll position via JavaScript
                scroll_script = "window.pageYOffset || document.documentElement.scrollTop || 0"
                saved_scroll = self.webview.RunScript(scroll_script)
                if saved_scroll:
                    print(f"[{self.window_name}Window] Saved scroll position: {saved_scroll}")
            except Exception as e:
                print(f"[{self.window_name}Window] Could not save scroll position: {e}")

        # Load new content
        self.webview.SetPage(html_content, "")
        self.current_url = None  # Not a URL
        self.content_type = 'html'
        self.current_html_hash = html_hash  # Save hash for future comparisons

        # Restore scroll position after content loads
        if saved_scroll is not None and preserve_scroll:
            def restore_scroll():
                try:
                    # Convert saved_scroll to int/float if it's a string
                    scroll_pos = int(float(str(saved_scroll))) if saved_scroll else 0
                    restore_script = f"window.scrollTo(0, {scroll_pos});"
                    self.webview.RunScript(restore_script)
                    print(f"[{self.window_name}Window] Restored scroll position: {scroll_pos}")
                except Exception as e:
                    print(f"[{self.window_name}Window] Could not restore scroll position: {e}")

            # Restore after a delay to ensure content is loaded
            wx.CallLater(200, restore_scroll)

        self._show_window()

    def show_bible(self, html_content, preserve_scroll=False):
        """
        Show Bible verses (convenience wrapper for show_html)

        Args:
            html_content: HTML content for Bible verses (from content_renderer)
            preserve_scroll: If True, save and restore scroll position
        """
        self.show_html(html_content, preserve_scroll=preserve_scroll)

    def _show_window(self):
        """Internal method to show and raise the window"""
        # Show window if hidden - use ShowFullScreen to hide macOS menu bar
        if not self.IsShown():
            print(f"[{self.window_name}Window] Positioning at ({self.display_rect.x}, {self.display_rect.y})")
            self.SetPosition((self.display_rect.x, self.display_rect.y))
            self.SetSize((self.display_rect.width, self.display_rect.height))
            self.Show()
            # Use ShowFullScreen to hide macOS menu bar
            wx.CallLater(100, lambda: self.ShowFullScreen(True,
                wx.FULLSCREEN_NOTOOLBAR |
                wx.FULLSCREEN_NOSTATUSBAR |
                wx.FULLSCREEN_NOBORDER |
                wx.FULLSCREEN_NOMENUBAR |
                wx.FULLSCREEN_NOCAPTION))

        # Always raise to front (even if already visible)
        self.Raise()

        # Give focus to webview so keyboard navigation works
        self.SetFocus()
        self.webview.SetFocus()
        # Also set focus after a delay to ensure content has loaded
        wx.CallLater(100, lambda: self._ensure_focus(self.webview))

        self.panel.Layout()


    def hide_projection(self):
        """Hide the projection window (preserves content state for quick switching)"""
        print(f"[{self.window_name}Window] Hiding (preserving content state)")
        # Exit fullscreen mode first
        if self.IsFullScreen():
            self.ShowFullScreen(False)
        self.Hide()
        # DO NOT reset content_type or current_url - preserve state for quick switching
        # self.content_type = None
        # self.current_url = None


    def is_visible(self):
        """Check if projection window is currently visible"""
        return self.IsShown()

    def get_content_type(self):
        """Get current content type"""
        return self.content_type

    def on_close(self, event):
        """Handle window close event"""
        # Don't destroy, just hide
        self.hide_projection()


def get_display_info():
    """
    Get information about all available displays

    Returns:
        List of dicts with display information
    """
    displays = []
    count = wx.Display.GetCount()

    for i in range(count):
        display = wx.Display(i)
        geometry = display.GetGeometry()

        displays.append({
            'index': i,
            'name': display.GetName(),
            'geometry': {
                'x': geometry.x,
                'y': geometry.y,
                'width': geometry.width,
                'height': geometry.height
            },
            'is_primary': display.IsPrimary()
        })

    return displays
