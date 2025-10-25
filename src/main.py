#!/usr/bin/env python3
"""
Webpage Projector - Main Entry Point
Phase 2: WebView UI + Projection Window
"""

import wx
import wx.html2
import os
from pathlib import Path
from ui.projection_window import ProjectionWindow, get_display_info
from bridge_simple import setup_simple_bridge
from core.bible_engine import BibleEngine
from core.content_renderer import render_bible_verses
from data.hymn_repository import HymnRepository
from data.config_manager import ConfigManager


class MainWindow(wx.Frame):
    """Main application window with embedded WebView"""

    def __init__(self):
        # Initialize configuration manager FIRST
        self.config = ConfigManager(config_path="config.json")

        # Get saved window size and position
        width, height = self.config.get_window_size()
        saved_pos = self.config.get_window_position()

        super().__init__(
            parent=None,
            title="NCF Bible and Hymn Projector - Control Panel",
            size=(width, height),
            style=wx.DEFAULT_FRAME_STYLE  # Allow resizing and maximize
        )

        # Set window position (center if not saved, otherwise use saved position)
        if saved_pos:
            self.SetPosition(saved_pos)
            print(f"[MainWindow] Restored window position: {saved_pos}")
        else:
            self.Centre()

        # Detect displays
        self.displays = get_display_info()
        self._print_display_info()

        # Create projection windows (all use secondary display if available)
        display_index = 1 if len(self.displays) > 1 else 0

        # Separate window for Bible content (to preserve scroll state independently)
        self.bible_window = ProjectionWindow(display_index=display_index, window_name="Bible", main_window=self)

        # Separate window for hymns/slides/websites
        self.hymn_window = ProjectionWindow(display_index=display_index, window_name="Hymn", main_window=self)

        # Separate window for agenda
        self.agenda_window = ProjectionWindow(display_index=display_index, window_name="Agenda", main_window=self)

        # Keep reference to projection_window for backward compatibility (points to hymn window)
        self.projection_window = self.hymn_window

        # Initialize Bible engine
        self.bible_engine = BibleEngine(books_dir="books", books_csv="books.csv")
        self.current_book = None  # Track currently selected book for context

        # Initialize Hymn repository
        self.hymn_repository = HymnRepository(hymns_csv="hymns.csv")

        # Create WebView
        self.webview = wx.html2.WebView.New(self)

        # Load the HTML file
        html_path = self._get_html_path()
        if html_path.exists():
            # Use file:// URL for local file
            file_url = html_path.as_uri()
            print(f"Loading HTML from: {file_url}")
            self.webview.LoadURL(file_url)
        else:
            print(f"ERROR: HTML file not found at {html_path}")
            self.show_error_page()

        # Set up JavaScript-Python bridge
        setup_simple_bridge(self)

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _get_html_path(self) -> Path:
        """Get the path to the index.html file"""
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        html_path = script_dir / "ui" / "web" / "index.html"
        return html_path.resolve()

    def show_error_page(self):
        """Show an error page if HTML file is not found"""
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f8fafc;
                }
                .error-container {
                    text-align: center;
                    padding: 2rem;
                }
                h1 {
                    color: #ef4444;
                    font-size: 2rem;
                    margin-bottom: 1rem;
                }
                p {
                    color: #64748b;
                    font-size: 1rem;
                }
                code {
                    background-color: #f1f5f9;
                    padding: 0.25rem 0.5rem;
                    border-radius: 0.25rem;
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>❌ HTML File Not Found</h1>
                <p>Could not find <code>src/ui/web/index.html</code></p>
                <p>Please ensure the file exists and try again.</p>
            </div>
        </body>
        </html>
        """
        self.webview.SetPage(error_html, "")

    def _print_display_info(self):
        """Print information about detected displays"""
        print(f"\nDetected {len(self.displays)} display(s):")
        for display in self.displays:
            primary_str = " (PRIMARY)" if display['is_primary'] else ""
            print(f"  Display {display['index']}: {display['name']}{primary_str}")
            print(f"    Position: ({display['geometry']['x']}, {display['geometry']['y']})")
            print(f"    Size: {display['geometry']['width']}x{display['geometry']['height']}")
        print()

    def on_close(self, event):
        """Handle window close event"""
        # Save window position and size before closing
        pos = self.GetPosition()
        size = self.GetSize()
        self.config.save_window_position(pos.x, pos.y)
        self.config.save_window_size(size.width, size.height)

        # Save configuration to file
        self.config.save()
        print(f"[MainWindow] Saved window settings: pos=({pos.x}, {pos.y}), size=({size.width}x{size.height})")

        # Close projection windows
        if hasattr(self, 'bible_window'):
            self.bible_window.Destroy()
        if hasattr(self, 'hymn_window'):
            self.hymn_window.Destroy()
        if hasattr(self, 'agenda_window'):
            self.agenda_window.Destroy()

        self.Destroy()


class WebpageProjectorApp(wx.App):
    """Main application class"""

    def OnInit(self):
        """Initialize the application"""
        self.main_window = MainWindow()
        self.main_window.Show()
        return True


def main():
    """Main entry point"""
    print("=" * 60)
    print("NCF Bible and Hymn Projector - Phase 2")
    print("=" * 60)
    print()
    print("Launching application...")
    print()

    app = WebpageProjectorApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()