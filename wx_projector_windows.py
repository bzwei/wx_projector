#!/usr/bin/env python3
"""
NCF Screen Projector - Windows Optimized Version
Native desktop application using wxPython for both UI and web projection
Optimized for Windows with enhanced Chrome integration and pywin32 support
"""

import wx
import wx.html2
import wx.lib.buttons as buttons
import re
import threading
import time
import csv
import os
import subprocess
import sys
from screeninfo import get_monitors

# Windows-specific imports
try:
    import win32gui
    import win32con
    import win32api
    import win32process
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False
    pass


class ProjectionFrame(wx.Frame):
    """Fullscreen projection window for displaying web content"""
    
    def __init__(self, parent, url, monitor, projection_type="web"):
        super().__init__(
            parent, 
            title="Web Page Projection" if projection_type == "web" else 
                  "Slides Projection" if projection_type == "slides" else
                  "Bible Projection" if projection_type == "bible" else
                  "Agenda Projection",
            style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP
        )
        
        self.parent_app = parent
        self.url = url
        self.monitor = monitor
        self.is_hidden = False
        self.is_fullscreen = False
        self.projection_type = projection_type
        
        # Set window size and position for target monitor with extra coverage
        # Add a small buffer to ensure complete coverage
        extra_pixels = 10
        self.SetSize(monitor.width + extra_pixels, monitor.height + extra_pixels)
        self.SetPosition((monitor.x - extra_pixels//2, monitor.y - extra_pixels//2))
        
        # Create web view
        self.browser = wx.html2.WebView.New(self)
        
        # Set user agent to mimic a regular browser for Google Slides compatibility
        try:
            # Try to set a standard Chrome user agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            if hasattr(self.browser, 'SetUserAgent'):
                self.browser.SetUserAgent(user_agent)
            elif hasattr(self.browser, 'GetBackend'):
                # For different WebView backends
                backend = self.browser.GetBackend()
                if hasattr(backend, 'SetUserAgent'):
                    backend.SetUserAgent(user_agent)
        except Exception as e:
            print(f"Could not set user agent: {e}")
        
        # Bind events
        self.browser.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.on_page_loaded)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.on_page_error)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.browser.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.browser, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        # Show window first, then load URL and go fullscreen
        self.Show(True)
        self.Raise()
        self.SetFocus()
        
        # Load URL with custom headers for Google Slides
        self.load_url_with_headers(url)
        
    def load_url_with_headers(self, url):
        """Load URL with custom headers to avoid Google Drive help page"""
        try:
            # Try to load with custom headers if supported
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Check if LoadURL supports headers
            if hasattr(self.browser, 'LoadURLWithHeaders'):
                self.browser.LoadURLWithHeaders(url, headers)
            else:
                # Fallback to regular LoadURL
                self.browser.LoadURL(url)
                
        except Exception as e:
            print(f"Error loading URL with headers: {e}")
            # Fallback to regular LoadURL
            self.browser.LoadURL(url)
        
        # Immediately set to fullscreen since we're already borderless
        wx.CallLater(100, self.ensure_complete_coverage)
        
    def ensure_complete_coverage(self):
        """Ensure the window completely covers the target monitor"""
        try:
            # Get display info for more accurate sizing
            display = wx.Display.GetFromPoint((self.monitor.x, self.monitor.y))
            if display != wx.NOT_FOUND:
                display_obj = wx.Display(display)
                geometry = display_obj.GetGeometry()
                # Use the display geometry for exact coverage
                self.SetSize(geometry.width, geometry.height)
                self.SetPosition((geometry.x, geometry.y))
                
                # Ensure the browser fills the entire area
                self.browser.SetSize(geometry.width, geometry.height)
                self.browser.SetPosition((0, 0))
            else:
                # Fallback to monitor info with extra coverage
                extra_pixels = 20
                self.SetSize(self.monitor.width + extra_pixels, self.monitor.height + extra_pixels)
                self.SetPosition((self.monitor.x - extra_pixels//2, self.monitor.y - extra_pixels//2))
                
                # Ensure the browser fills the entire area
                self.browser.SetSize(self.monitor.width + extra_pixels, self.monitor.height + extra_pixels)
                self.browser.SetPosition((0, 0))
                
            # Ensure we're on top and focused
            self.Raise()
            self.SetFocus()
            
            # Additional Windows-specific positioning if pywin32 is available
            if HAS_PYWIN32:
                self.windows_ensure_position()
                
        except Exception as e:
            # Basic fallback
            self.SetSize(self.monitor.width, self.monitor.height)
            self.SetPosition((self.monitor.x, self.monitor.y))
    
    def windows_ensure_position(self):
        """Use Windows API to ensure proper positioning"""
        try:
            hwnd = self.GetHandle()
            
            # Set window to topmost and ensure it covers the monitor
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                self.monitor.x,
                self.monitor.y,
                self.monitor.width,
                self.monitor.height,
                win32con.SWP_SHOWWINDOW
            )
            
            # Remove window decorations and make it borderless
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MINIMIZE | win32con.WS_MAXIMIZE | win32con.WS_SYSMENU)
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
            
            # Force redraw
            win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | 
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
                
        except Exception as e:
            pass

    def make_fullscreen_fallback(self):
        """Fallback fullscreen method"""
        try:
            self.ShowFullScreen(True)
            # Adjust to exact monitor dimensions
            self.SetSize(self.monitor.width, self.monitor.height)
            self.SetPosition((self.monitor.x, self.monitor.y))
            self.is_fullscreen = True
        except Exception as e:
            pass

    def on_page_loaded(self, event):
        """Handle page load completion"""
        try:
            # Get the current URL to check for redirects
            current_url = self.browser.GetCurrentURL()
            print(f"Page loaded: {current_url}")
            
            # Check if we've been redirected to Google Account Help page (for slides)
            if self.projection_type == "slides":
                # Common Google help/error page indicators
                help_indicators = [
                    'support.google.com',
                    'accounts.google.com',
                    'drive.google.com/help',
                    'docs.google.com/help',
                    '/signin',
                    '/login',
                    'access_denied',
                    'permission_denied'
                ]
                
                # Check if current URL contains any help page indicators
                is_help_page = any(indicator in current_url.lower() for indicator in help_indicators)
                
                # Also check if the original URL was a Google Slides URL but we're now somewhere else
                is_google_slides_redirect = (
                    'docs.google.com/presentation' in self.url and 
                    'docs.google.com/presentation' not in current_url
                )
                
                if is_help_page or is_google_slides_redirect:
                    print(f"Detected redirect to help/error page: {current_url}")
                    print(f"Original URL was: {self.url}")
                    # Treat this as an error to trigger fallback
                    error_msg = f"Redirected to help page: {current_url}"
                    self.parent_app.on_slides_projection_error(error_msg)
                    return
            
            # If we get here, the page loaded successfully
            if self.projection_type == "web":
                self.parent_app.on_projection_loaded()
            elif self.projection_type == "slides":
                self.parent_app.on_slides_projection_loaded()
            elif self.projection_type == "bible":
                self.parent_app.on_bible_projection_loaded()
            elif self.projection_type == "agenda":
                self.parent_app.on_agenda_projection_loaded()
                
        except Exception as e:
            print(f"Error in on_page_loaded: {e}")
            # Treat exceptions as errors
            if self.projection_type == "slides":
                self.parent_app.on_slides_projection_error(f"Page load error: {str(e)}")

    def on_page_error(self, event):
        """Handle page load errors"""
        error_msg = f"Failed to load: {event.GetURL()}"
        
        # Notify parent of error
        if self.projection_type == "web":
            self.parent_app.on_projection_error(error_msg)
        elif self.projection_type == "slides":
            self.parent_app.on_slides_projection_error(error_msg)
        elif self.projection_type == "bible":
            self.parent_app.on_bible_projection_error(error_msg)
        elif self.projection_type == "agenda":
            self.parent_app.on_agenda_projection_error(error_msg)

    def on_key_down(self, event):
        """Handle key events"""
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.Close()
        elif key_code == wx.WXK_F11:
            if self.is_fullscreen:
                self.ShowFullScreen(False)
                self.is_fullscreen = False
            else:
                self.ShowFullScreen(True)
                self.is_fullscreen = True
        else:
            event.Skip()

    def on_close(self, event):
        """Handle window close"""
        # Hide first, then destroy to avoid flicker
        self.Hide()
        
        # Notify parent
        if self.projection_type == "web":
            self.parent_app.is_projecting = False
        elif self.projection_type == "slides":
            self.parent_app.is_projecting_slides = False
        elif self.projection_type == "bible":
            self.parent_app.is_projecting_bible = False
        elif self.projection_type == "agenda":
            self.parent_app.is_projecting_agenda = False
            
        # Update parent's button states
        self.parent_app.update_all_projection_buttons()
        
        # Destroy the window
        self.Destroy()

    def hide_projection(self, auto_hide=False):
        """Hide the projection"""
        self.Hide()
        self.is_hidden = True

    def show_projection(self):
        """Show the projection"""
        self.Show(True)
        self.Raise()
        self.SetFocus()
        self.is_hidden = False

    def reload_url(self, url):
        """Reload with a new URL"""
        self.url = url
        self.browser.LoadURL(url)


class MainFrame(wx.Frame):
    """Main application window with controls"""
    
    def __init__(self):
        super().__init__(
            None, 
            title="🖥️ NCF Screen Projector - Windows Edition", 
            size=(950, 850),
            style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER
        )
        
        # Variables
        self.projection_frame = None
        self.is_projecting = False
        self.slides_projection_frame = None
        self.is_projecting_slides = False
        self.bible_projection_frame = None
        self.is_projecting_bible = False
        self.agenda_projection_frame = None
        self.is_projecting_agenda = False
        
        # Chrome browser process for URL projection
        self.chrome_process = None
        self.chrome_monitor_timer = None
        
        # Bind close event to clean up Chrome processes
        self.Bind(wx.EVT_CLOSE, self.on_main_window_close)
        
        # Hymns data - ID-based lookup
        self.hymns_data = {}
        self.hymns_ids = []
        
        # Bible data
        self.bible_books = {}  # book_name -> [book_id, chapter_count]
        self.bible_book_names = []  # list of book names for autocomplete
        
        # Bible projection history
        self.bible_history = []  # List of dictionaries with bible_info and selected_versions
        self.max_history_size = 20  # Limit history to last 20 projections
        
        # Currently projected Bible info for verse navigation
        self.current_projected_bible = None  # Stores current projection info for navigation
        
        # Center window
        self.CenterOnScreen()
        
        # Setup UI
        self.setup_ui()
        
        # Load hymns data
        self.load_hymns_data()
        
        # Load bible books data
        self.load_bible_books_data()
        
        # Setup monitor info
        self.update_monitor_info()
        
        # Apply Windows-specific UI optimizations
        if HAS_PYWIN32:
            self.apply_windows_optimizations()
        
    def apply_windows_optimizations(self):
        """Apply Windows-specific UI optimizations"""
        try:
            hwnd = self.GetHandle()
            
            # Enable Windows 10/11 dark mode support if available
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                    apps_use_light_theme = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
                    if not apps_use_light_theme:  # Dark mode
                        # Set dark title bar
                        win32gui.SetWindowLong(hwnd, -26, 1)  # DWMWA_USE_IMMERSIVE_DARK_MODE
            except:
                pass
                
            # Set window icon if available
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
                self.SetIcon(icon)
                
        except Exception as e:
            pass

    def setup_ui(self):
        """Create the user interface"""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(248, 248, 248))  # Very light gray for better contrast
        
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title with Windows styling
        title = wx.StaticText(panel, label="🖥️ NCF Screen Projector - Windows Edition")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(44, 62, 80))
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
        
        # URL input section
        url_box = wx.StaticBox(panel, label="Enter URL to project:")
        url_sizer = wx.StaticBoxSizer(url_box, wx.VERTICAL)
        
        # URL input with buttons on same row
        url_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # URL text control (narrower)
        self.url_ctrl = wx.TextCtrl(
            panel, 
            value="",
            style=wx.TE_PROCESS_ENTER | wx.BORDER_THEME,
            size=(300, 36)
        )
        url_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.url_ctrl.SetFont(url_font)
        self.url_ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.url_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        self.url_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_main_button_click)
        
        # Project button
        self.main_btn = buttons.GenButton(panel, label="🔗 Project")
        self.main_btn.SetBackgroundColour(wx.Colour(52, 152, 219))
        self.main_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.main_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.main_btn.SetSize((80, 36))
        self.main_btn.Bind(wx.EVT_BUTTON, self.on_main_button_click)
        
        # Show/Hide toggle button
        self.url_toggle_btn = buttons.GenButton(panel, label="👁 Show")
        self.url_toggle_btn.SetBackgroundColour(wx.Colour(95, 95, 95))
        self.url_toggle_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.url_toggle_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.url_toggle_btn.SetSize((70, 36))
        self.url_toggle_btn.Enable(False)
        self.url_toggle_btn.Bind(wx.EVT_BUTTON, self.on_url_toggle_click)
        
        url_row_sizer.Add(self.url_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        url_row_sizer.Add(self.main_btn, 0, wx.RIGHT, 5)
        url_row_sizer.Add(self.url_toggle_btn, 0, 0)
        url_sizer.Add(url_row_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Example text
        example = wx.StaticText(panel, label="Examples: google.com, youtube.com, localhost:3000")
        example.SetForegroundColour(wx.Colour(127, 140, 141))
        url_sizer.Add(example, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        main_sizer.Add(url_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        
        # Google Slides section
        slides_box = wx.StaticBox(panel, label="Google Slides Presentation:")
        slides_sizer = wx.StaticBoxSizer(slides_box, wx.VERTICAL)
        
        # Slides input with buttons on same row
        slides_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Slides ID control (narrower)
        self.slides_ctrl = wx.TextCtrl(
            panel, 
            value="",
            style=wx.TE_PROCESS_ENTER | wx.BORDER_THEME,
            size=(220, 36)
        )
        slides_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.slides_ctrl.SetFont(slides_font)
        self.slides_ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.slides_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        self.slides_ctrl.Bind(wx.EVT_TEXT, self.on_slides_text_change)
        self.slides_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_slides_button_click)

        # Dropdown button for hymn selection
        self.hymn_dropdown_btn = wx.Button(panel, label="🎵", size=(40, 36))
        self.hymn_dropdown_btn.SetToolTip("Select from hymns list")
        self.hymn_dropdown_btn.Bind(wx.EVT_BUTTON, self.show_hymns_dropdown)
        
        # Present button
        self.slides_btn = buttons.GenButton(panel, label="📊 Present")
        self.slides_btn.SetBackgroundColour(wx.Colour(142, 68, 173))  # Purple
        self.slides_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.slides_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.slides_btn.SetSize((80, 36))
        self.slides_btn.Bind(wx.EVT_BUTTON, self.on_slides_button_click)
        
        # Show/Hide toggle button
        self.slides_toggle_btn = buttons.GenButton(panel, label="👁 Show")
        self.slides_toggle_btn.SetBackgroundColour(wx.Colour(95, 95, 95))
        self.slides_toggle_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.slides_toggle_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.slides_toggle_btn.SetSize((70, 36))
        self.slides_toggle_btn.Enable(False)
        self.slides_toggle_btn.Bind(wx.EVT_BUTTON, self.on_slides_toggle_click)
        
        # Agenda button
        self.agenda_btn = buttons.GenButton(panel, label="📋 Show Agenda")
        self.agenda_btn.SetBackgroundColour(wx.Colour(52, 73, 94))  # Dark blue-gray
        self.agenda_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.agenda_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.agenda_btn.SetSize((120, 36))
        self.agenda_btn.Bind(wx.EVT_BUTTON, self.on_agenda_button_click)
        
        slides_row_sizer.Add(self.slides_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        slides_row_sizer.Add(self.hymn_dropdown_btn, 0, wx.RIGHT, 5)
        slides_row_sizer.Add(self.slides_btn, 0, wx.RIGHT, 5)
        slides_row_sizer.Add(self.slides_toggle_btn, 0, wx.RIGHT, 5)
        slides_row_sizer.Add(self.agenda_btn, 0, 0)
        slides_sizer.Add(slides_row_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Status text for current selection
        self.slides_status = wx.StaticText(panel, label="Enter hymn ID (123, A123, C456) or Google Slides ID/URL")
        self.slides_status.SetForegroundColour(wx.Colour(127, 140, 141))
        slides_sizer.Add(self.slides_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        main_sizer.Add(slides_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        
        # Bible verse section
        bible_box = wx.StaticBox(panel, label="Bible Verse Projection:")
        bible_sizer = wx.StaticBoxSizer(bible_box, wx.VERTICAL)
        
        # Bible version selection (checkboxes) and font size controls in the same row
        version_font_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Bible versions checkboxes
        versions_label = wx.StaticText(panel, label="Bible Versions:")
        versions_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        version_font_row_sizer.Add(versions_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        # Bible versions dictionary
        self.bible_versions = {
            'cuv': '和合本',
            'kjv': 'KJV',
            'nas': 'NAS', 
            'niv': 'NIV',
            'dby': 'Darby'
        }
        
        # Create checkboxes for Bible versions
        self.version_checkboxes = {}
        for version_key, version_name in self.bible_versions.items():
            checkbox = wx.CheckBox(panel, label=version_name)
            if version_key == 'cuv':  # Default to CUV selected
                checkbox.SetValue(True)
            checkbox.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            checkbox.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
            checkbox.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
            checkbox.Refresh()  # Force refresh to apply colors
            checkbox.Bind(wx.EVT_CHECKBOX, self.on_version_checkbox_change)
            self.version_checkboxes[version_key] = checkbox
            version_font_row_sizer.Add(checkbox, 0, wx.RIGHT, 15)
        
        # Vertical separator
        separator = wx.StaticLine(panel, style=wx.LI_VERTICAL, size=(2, 30))
        version_font_row_sizer.Add(separator, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)
        
        # Font size controls
        chinese_font_label = wx.StaticText(panel, label="Chinese Font:")
        chinese_font_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        version_font_row_sizer.Add(chinese_font_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        chinese_font_sizes = ["24px", "28px", "32px", "36px", "40px", "44px", "48px"]
        self.chinese_font_choice = wx.Choice(panel, choices=chinese_font_sizes, size=(160, 30))
        self.chinese_font_choice.SetSelection(3)  # Default to 36px
        self.chinese_font_choice.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.chinese_font_choice.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        version_font_row_sizer.Add(self.chinese_font_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        
        english_font_label = wx.StaticText(panel, label="English Font:")
        english_font_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        version_font_row_sizer.Add(english_font_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        english_font_sizes = ["20px", "24px", "28px", "32px", "36px", "40px", "44px"]
        self.english_font_choice = wx.Choice(panel, choices=english_font_sizes, size=(160, 30))
        self.english_font_choice.SetSelection(3)  # Default to 32px
        self.english_font_choice.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.english_font_choice.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        version_font_row_sizer.Add(self.english_font_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        
        bible_sizer.Add(version_font_row_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Bible input with buttons on same row
        bible_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Bible text control (narrower)
        self.bible_ctrl = wx.TextCtrl(
            panel, 
            value="",
            style=wx.TE_PROCESS_ENTER | wx.BORDER_THEME,
            size=(200, 36)
        )
        bible_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.bible_ctrl.SetFont(bible_font)
        self.bible_ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.bible_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        self.bible_ctrl.Bind(wx.EVT_TEXT, self.on_bible_text_change)
        self.bible_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_bible_button_click)
        self.bible_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_bible_key_down)

        # Clear button for bible text
        self.bible_clear_btn = wx.Button(panel, label="×", size=(25, 36))
        self.bible_clear_btn.SetToolTip("Clear bible verse input")
        self.bible_clear_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.bible_clear_btn.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.bible_clear_btn.SetBackgroundColour(wx.Colour(240, 240, 240))  # Light gray background
        self.bible_clear_btn.Refresh()
        self.bible_clear_btn.Bind(wx.EVT_BUTTON, self.on_bible_clear_click)
        
        # Preview button for bible text
        self.bible_preview_btn = wx.Button(panel, label="👁", size=(30, 36))
        self.bible_preview_btn.SetToolTip("Preview chapter")
        self.bible_preview_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.bible_preview_btn.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.bible_preview_btn.SetBackgroundColour(wx.Colour(240, 240, 240))  # Light gray background
        self.bible_preview_btn.Refresh()
        self.bible_preview_btn.Bind(wx.EVT_BUTTON, self.on_bible_preview_click)
        
        # History button for bible projections
        self.bible_history_btn = wx.Button(panel, label="📜", size=(30, 36))
        self.bible_history_btn.SetToolTip("Projection history")
        self.bible_history_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.bible_history_btn.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.bible_history_btn.SetBackgroundColour(wx.Colour(240, 240, 240))  # Light gray background
        self.bible_history_btn.Enable(False)  # Initially disabled until there's history
        self.bible_history_btn.Refresh()
        self.bible_history_btn.Bind(wx.EVT_BUTTON, self.on_bible_history_click)
        
        # Project button
        self.bible_btn = buttons.GenButton(panel, label="📖 Project")
        self.bible_btn.SetBackgroundColour(wx.Colour(39, 174, 96))  # Green
        self.bible_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.bible_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.bible_btn.SetSize((80, 36))
        self.bible_btn.Bind(wx.EVT_BUTTON, self.on_bible_button_click)
        
        # Show/Hide toggle button
        self.bible_toggle_btn = buttons.GenButton(panel, label="👁 Show")
        self.bible_toggle_btn.SetBackgroundColour(wx.Colour(95, 95, 95))
        self.bible_toggle_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.bible_toggle_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.bible_toggle_btn.SetSize((70, 36))
        self.bible_toggle_btn.Enable(False)
        self.bible_toggle_btn.Bind(wx.EVT_BUTTON, self.on_bible_toggle_click)
        
        # Previous verse navigation button
        self.prev_verse_btn = wx.Button(panel, label="◀", size=(30, 36))
        self.prev_verse_btn.SetToolTip("Previous verse")
        self.prev_verse_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.prev_verse_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.prev_verse_btn.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.prev_verse_btn.Enable(False)  # Initially disabled
        self.prev_verse_btn.Bind(wx.EVT_BUTTON, self.on_prev_verse_click)
        
        # Next verse navigation button
        self.next_verse_btn = wx.Button(panel, label="▶", size=(30, 36))
        self.next_verse_btn.SetToolTip("Next verse")
        self.next_verse_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.next_verse_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.next_verse_btn.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.next_verse_btn.Enable(False)  # Initially disabled
        self.next_verse_btn.Bind(wx.EVT_BUTTON, self.on_next_verse_click)
        
        bible_row_sizer.Add(self.bible_ctrl, 1, wx.EXPAND | wx.RIGHT, 2)
        bible_row_sizer.Add(self.bible_clear_btn, 0, wx.RIGHT, 2)
        bible_row_sizer.Add(self.bible_preview_btn, 0, wx.RIGHT, 5)
        bible_row_sizer.Add(self.bible_history_btn, 0, wx.RIGHT, 5)
        bible_row_sizer.Add(self.bible_btn, 0, wx.RIGHT, 5)
        bible_row_sizer.Add(self.bible_toggle_btn, 0, wx.RIGHT, 5)
        bible_row_sizer.Add(self.prev_verse_btn, 0, wx.RIGHT, 2)
        bible_row_sizer.Add(self.next_verse_btn, 0, 0)
        bible_sizer.Add(bible_row_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Status text for bible input
        self.bible_status = wx.StaticText(panel, label="Enter book name and verse - 1 version selected: 和合本")
        self.bible_status.SetForegroundColour(wx.Colour(127, 140, 141))
        bible_sizer.Add(self.bible_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Bible preview area with chapter navigation
        self.bible_preview_panel = wx.Panel(panel)
        self.bible_preview_panel.SetBackgroundColour(wx.Colour(250, 250, 250))  # Very light gray
        
        preview_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Preview header with navigation buttons
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left arrow button
        self.prev_chapter_btn = wx.Button(self.bible_preview_panel, label="◀", size=(30, 25))
        self.prev_chapter_btn.SetToolTip("Previous chapter")
        self.prev_chapter_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.prev_chapter_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.prev_chapter_btn.SetBackgroundColour(wx.Colour(220, 220, 220))
        self.prev_chapter_btn.Enable(False)  # Initially disabled
        self.prev_chapter_btn.Bind(wx.EVT_BUTTON, self.on_prev_chapter_click)
        
        # Preview header text
        self.preview_header = wx.StaticText(self.bible_preview_panel, label="Chapter Preview (empty - click 👁 to load):")
        self.preview_header.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.preview_header.SetForegroundColour(wx.Colour(60, 60, 60))
        
        # Right arrow button
        self.next_chapter_btn = wx.Button(self.bible_preview_panel, label="▶", size=(30, 25))
        self.next_chapter_btn.SetToolTip("Next chapter")
        self.next_chapter_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.next_chapter_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.next_chapter_btn.SetBackgroundColour(wx.Colour(220, 220, 220))
        self.next_chapter_btn.Enable(False)  # Initially disabled
        self.next_chapter_btn.Bind(wx.EVT_BUTTON, self.on_next_chapter_click)
        
        header_sizer.Add(self.prev_chapter_btn, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        header_sizer.Add(self.preview_header, 1, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.Add(self.next_chapter_btn, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        preview_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Scrolled panel for verses
        self.bible_preview_scroll = wx.ScrolledWindow(self.bible_preview_panel, size=(-1, 250))
        self.bible_preview_scroll.SetScrollRate(5, 5)
        self.bible_preview_scroll.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # Sizer for verse rows (will be populated dynamically)
        self.bible_verses_sizer = wx.BoxSizer(wx.VERTICAL)
        self.bible_preview_scroll.SetSizer(self.bible_verses_sizer)
        
        preview_sizer.Add(self.bible_preview_scroll, 1, wx.EXPAND | wx.ALL, 5)
        
        self.bible_preview_panel.SetSizer(preview_sizer)
        bible_sizer.Add(self.bible_preview_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Autocomplete popup for bible books
        self.bible_popup = None
        
        main_sizer.Add(bible_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        
        # Status
        self.status_text = wx.StaticText(panel, label="Ready to project")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
        main_sizer.Add(self.status_text, 0, wx.ALL | wx.CENTER, 10)
        
        # Monitor info (will be updated in update_monitor_info)
        self.monitor_text = wx.StaticText(panel, label="")
        main_sizer.Add(self.monitor_text, 0, wx.ALL | wx.CENTER, 5)
        
        panel.SetSizer(main_sizer)
        
        # Bible popup for autocomplete
        self.bible_popup = None
        self.bible_list = None
        
        # Set focus to URL input
        self.url_ctrl.SetFocus()
        
        # Force color updates after layout (Windows compatibility)
        wx.CallAfter(self.force_color_updates)
        
        # Force layout refresh for choice controls
        wx.CallAfter(self.refresh_choice_sizing)
        
    def refresh_choice_sizing(self):
        """Force proper sizing for choice controls (Windows compatibility)"""
        try:
            # Force layout refresh for font choice controls
            self.chinese_font_choice.SetMinSize((60, 30))
            self.english_font_choice.SetMinSize((60, 30))
            
            # Force the parent panel to re-layout
            self.Layout()
            self.Refresh()
            
        except Exception as e:
            print(f"Error refreshing choice sizing: {e}")
         
    def force_color_updates(self):
        """Force color updates on all controls for better visibility (explicitly black on white)"""
        try:
            # Use explicit black on white colors as preferred
            text_color = wx.Colour(0, 0, 0)  # Black text
            bg_color = wx.Colour(255, 255, 255)  # White background
            
            # Fix text input controls
            for ctrl in [self.url_ctrl, self.slides_ctrl, self.bible_ctrl]:
                ctrl.SetForegroundColour(text_color)
                ctrl.SetBackgroundColour(bg_color)
                ctrl.Refresh()
                
            # Fix checkboxes - explicitly black text
            for checkbox in self.version_checkboxes.values():
                checkbox.SetForegroundColour(text_color)
                checkbox.SetBackgroundColour(wx.Colour(248, 248, 248))  # Very light gray
                checkbox.Refresh()
                
            # Fix choice controls
            for choice in [self.chinese_font_choice, self.english_font_choice]:
                choice.SetForegroundColour(text_color)
                choice.SetBackgroundColour(bg_color)
                choice.Refresh()
                
        except Exception as e:
            print(f"Error in force_color_updates: {e}")
        
    def update_all_projection_buttons(self):
        """Update all projection button states based on current projection status"""
        try:
            # URL projection button
            if self.is_projecting:
                if hasattr(self, 'projection_frame') and self.projection_frame and not self.projection_frame.is_hidden:
                    self.main_btn.SetLabel("🔗 Project")
                    self.url_toggle_btn.SetLabel("👁 Hide")
                    self.url_toggle_btn.Enable(True)
                else:
                    self.main_btn.SetLabel("🔗 Project")
                    self.url_toggle_btn.SetLabel("👁 Show")
                    self.url_toggle_btn.Enable(True)
            else:
                self.main_btn.SetLabel("🔗 Project")
                self.url_toggle_btn.SetLabel("👁 Show")
                self.url_toggle_btn.Enable(False)
            
            # Always enable main project buttons
            self.main_btn.Enable(True)
            
            # Slides projection button
            if self.is_projecting_slides:
                if hasattr(self, 'slides_projection_frame') and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                    self.slides_btn.SetLabel("📊 Present")
                    self.slides_toggle_btn.SetLabel("👁 Hide")
                    self.slides_toggle_btn.Enable(True)
                else:
                    self.slides_btn.SetLabel("📊 Present")
                    self.slides_toggle_btn.SetLabel("👁 Show")
                    self.slides_toggle_btn.Enable(True)
            else:
                self.slides_btn.SetLabel("📊 Present")
                self.slides_toggle_btn.SetLabel("👁 Show")
                self.slides_toggle_btn.Enable(False)
            
            # Always enable slides project button
            self.slides_btn.Enable(True)
            
            # Bible projection button
            if self.is_projecting_bible:
                if hasattr(self, 'bible_projection_frame') and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                    self.bible_btn.SetLabel("📖 Project")
                    self.bible_toggle_btn.SetLabel("👁 Hide")
                    self.bible_toggle_btn.Enable(True)
                else:
                    self.bible_btn.SetLabel("📖 Project")
                    self.bible_toggle_btn.SetLabel("👁 Show")
                    self.bible_toggle_btn.Enable(True)
            else:
                self.bible_btn.SetLabel("📖 Project")
                self.bible_toggle_btn.SetLabel("👁 Show")
                self.bible_toggle_btn.Enable(False)
            
            # Always enable bible project button
            self.bible_btn.Enable(True)
            
            # Agenda button - show "Hide Agenda" only if agenda is currently visible
            if (self.is_projecting_agenda and 
                hasattr(self, 'agenda_projection_frame') and 
                self.agenda_projection_frame and 
                not self.agenda_projection_frame.is_hidden):
                self.agenda_btn.SetLabel("📋 Hide Agenda")
            else:
                self.agenda_btn.SetLabel("📋 Show Agenda")
            
            # Update verse navigation buttons
            self.update_verse_navigation_buttons()
            
        except Exception as e:
            pass

    def refresh_choice_sizing(self):
        """Force refresh of choice control sizing"""
        try:
            # Apply minimum sizes
            self.chinese_font_choice.SetMinSize((160, 30))
            self.english_font_choice.SetMinSize((160, 30))
            
            # Force layout update
            self.Layout()
            self.Refresh()
            
        except Exception as e:
            pass

    def force_color_updates(self):
        """Force color updates for all controls to ensure visibility on Windows"""
        try:
            # Text controls
            for ctrl in [self.url_ctrl, self.slides_ctrl, self.bible_ctrl]:
                ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
                ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
                ctrl.Refresh()
            
            # Preview text area
            self.preview_text.SetForegroundColour(wx.Colour(0, 0, 0))
            self.preview_text.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.preview_text.Refresh()
            
            # Choice controls
            for choice in [self.chinese_font_choice, self.english_font_choice]:
                choice.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
                choice.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
                choice.Refresh()
            
            # Re-apply default selections after refresh
            wx.CallAfter(self._reapply_choice_selections)
            
            # Checkboxes
            for checkbox in [self.cuv_checkbox, self.niv_checkbox, self.esv_checkbox]:
                checkbox.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
                checkbox.SetBackgroundColour(wx.Colour(248, 248, 248))  # Light gray background
                checkbox.Refresh()
            
            # Static text labels
            static_texts = [
                text for text in self.GetChildren() if isinstance(text, wx.StaticText)
            ]
            for text in static_texts:
                if text.GetLabel() not in ["Ready to project", "Detecting monitors..."]:  # Skip status texts
                    text.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
                    text.Refresh()
            
            # Force layout refresh
            wx.CallAfter(self.refresh_choice_sizing)
            
        except Exception as e:
            pass

    def _reapply_choice_selections(self):
        """Reapply default selections after refresh"""
        try:
            self.chinese_font_choice.SetSelection(3)  # 36px
            self.english_font_choice.SetSelection(3)  # 32px
        except:
            pass

    def load_hymns_data(self):
        """Load hymns data from CSV file - ID based lookup"""
        csv_path = os.path.join(os.getcwd(), "hymns.csv")
        try:
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    # Check if first row is header and skip if needed
                    first_row = next(reader, None)
                    if first_row and not (first_row[0].isdigit() or 
                                        (first_row[0].startswith(('A', 'C')) and first_row[0][1:].isdigit())):
                        # Looks like header, continue reading
                        pass
                    else:
                        # First row is data, process it
                        if first_row and len(first_row) >= 2:
                            hymn_id = first_row[0].strip()
                            slides_id = first_row[1].strip()
                            if hymn_id and slides_id:
                                # Store with uppercase key for case-insensitive lookup
                                self.hymns_data[hymn_id.upper()] = slides_id
                                self.hymns_ids.append(hymn_id)  # Keep original case for display
                    
                    # Process remaining rows
                    for row in reader:
                        if len(row) >= 2:
                            hymn_id = row[0].strip()
                            slides_id = row[1].strip()
                            if hymn_id and slides_id:
                                # Store with uppercase key for case-insensitive lookup
                                self.hymns_data[hymn_id.upper()] = slides_id
                                self.hymns_ids.append(hymn_id)  # Keep original case for display
                print(f"Loaded {len(self.hymns_data)} hymns from {csv_path}")
            else:
                print(f"Hymns file not found: {csv_path}")
        except Exception as e:
            print(f"Error loading hymns data: {e}")

    def load_bible_books_data(self):
        """Load Bible books data from CSV file"""
        try:
            # Try to load from books.csv
            csv_path = os.path.join(os.path.dirname(__file__), "books.csv")
            
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        book_name = row.get('book_name', '').strip()
                        book_id = row.get('book_id', '').strip()
                        chapter_count = row.get('chapter_count', '0').strip()
                        
                        if book_name and book_id and chapter_count.isdigit():
                            self.bible_books[book_name] = [int(book_id), int(chapter_count)]
                            self.bible_book_names.append(book_name)
                
            else:
                # Fallback to hardcoded data
                self.bible_books = {
                    "Genesis": [1, 50], "Exodus": [2, 40], "Leviticus": [3, 27], 
                    "Numbers": [4, 36], "Deuteronomy": [5, 34], "Joshua": [6, 24],
                    "Judges": [7, 21], "Ruth": [8, 4], "1 Samuel": [9, 31], 
                    "2 Samuel": [10, 24], "1 Kings": [11, 22], "2 Kings": [12, 25],
                    "1 Chronicles": [13, 29], "2 Chronicles": [14, 36], "Ezra": [15, 10],
                    "Nehemiah": [16, 13], "Esther": [17, 10], "Job": [18, 42],
                    "Psalms": [19, 150], "Proverbs": [20, 31], "Ecclesiastes": [21, 12],
                    "Song of Solomon": [22, 8], "Isaiah": [23, 66], "Jeremiah": [24, 52],
                    "Lamentations": [25, 5], "Ezekiel": [26, 48], "Daniel": [27, 12],
                    "Hosea": [28, 14], "Joel": [29, 3], "Amos": [30, 9],
                    "Obadiah": [31, 1], "Jonah": [32, 4], "Micah": [33, 7],
                    "Nahum": [34, 3], "Habakkuk": [35, 3], "Zephaniah": [36, 3],
                    "Haggai": [37, 2], "Zechariah": [38, 14], "Malachi": [39, 4],
                    "Matthew": [40, 28], "Mark": [41, 16], "Luke": [42, 24],
                    "John": [43, 21], "Acts": [44, 28], "Romans": [45, 16],
                    "1 Corinthians": [46, 16], "2 Corinthians": [47, 13], "Galatians": [48, 6],
                    "Ephesians": [49, 6], "Philippians": [50, 4], "Colossians": [51, 4],
                    "1 Thessalonians": [52, 5], "2 Thessalonians": [53, 3], "1 Timothy": [54, 6],
                    "2 Timothy": [55, 4], "Titus": [56, 3], "Philemon": [57, 1],
                    "Hebrews": [58, 13], "James": [59, 5], "1 Peter": [60, 5],
                    "2 Peter": [61, 3], "1 John": [62, 5], "2 John": [63, 1],
                    "3 John": [64, 1], "Jude": [65, 1], "Revelation": [66, 22]
                }
                self.bible_book_names = list(self.bible_books.keys())
                
        except Exception as e:
            pass

    def update_monitor_info(self):
        """Update monitor information display"""
        try:
            monitors = get_monitors()
            if len(monitors) >= 2:
                primary = monitors[0]
                secondary = monitors[1]
                self.monitor_text.SetLabel(
                    f"✅ Primary: {primary.width}x{primary.height} | "
                    f"Secondary: {secondary.width}x{secondary.height} at ({secondary.x}, {secondary.y})"
                )
                self.monitor_text.SetForegroundColour(wx.Colour(39, 174, 96))
            else:
                self.monitor_text.SetLabel("⚠️ Only one monitor detected. Projection will use primary monitor.")
                self.monitor_text.SetForegroundColour(wx.Colour(230, 126, 34))
        except Exception as e:
            self.monitor_text.SetLabel("Monitor detection failed")
            self.monitor_text.SetForegroundColour(wx.Colour(231, 76, 60))

    # Bible text handling methods
    def on_bible_text_change(self, event):
        """Handle text changes in bible input - show autocomplete for book names"""
        text = self.bible_ctrl.GetValue().strip()
        
        if text:
            # Hide existing popup if any
            self.hide_bible_popup()
            
            # Parse input to get book part
            parts = re.split(r'[\s:]+', text)
            if parts:
                book_part = parts[0]
                
                # Find matching books (case insensitive)
                matches = [book for book in self.bible_book_names 
                          if book.lower().startswith(book_part.lower())]
                
                if len(matches) > 1 and len(book_part) > 0:
                    # Show autocomplete popup for multiple matches
                    self.show_bible_popup(matches[:10])  # Limit to 10 matches
                elif len(matches) == 1:
                    # Single match - check if it's exact or partial
                    match = matches[0]
                    if match.lower() == book_part.lower():
                        # Exact match, parse verse if present
                        self.parse_and_validate_bible_input(text)
                    else:
                        # Partial match - show helpful status
                        self.bible_status.SetLabel(f"Match: {match} - Continue typing verse (e.g., 3:16)")
                        self.bible_status.SetForegroundColour(wx.Colour(52, 152, 219))
                elif len(book_part) > 2:
                    # No matches after 3+ characters
                    self.bible_status.SetLabel(f"No book found starting with '{book_part}'")
                    self.bible_status.SetForegroundColour(wx.Colour(231, 76, 60))
                else:
                    # Still typing
                    self.bible_status.SetLabel("Continue typing book name...")
                    self.bible_status.SetForegroundColour(wx.Colour(127, 140, 141))
        else:
            self.hide_bible_popup()
            self.bible_status.SetLabel("Enter book name and verse (e.g., 'John 3:16', 'Genesis 1:1')")
            self.bible_status.SetForegroundColour(wx.Colour(127, 140, 141))

    def on_bible_key_down(self, event):
        """Handle special keys in Bible input"""
        key_code = event.GetKeyCode()
        
        if key_code == wx.WXK_DOWN and self.bible_popup and self.bible_popup.IsShown():
            # Move to popup list
            if self.bible_list.GetItemCount() > 0:
                self.bible_list.Select(0)
                self.bible_list.SetFocus()
                return
        elif key_code == wx.WXK_ESCAPE:
            self.hide_bible_popup()
        elif key_code == wx.WXK_TAB:
            # Auto-complete with first match if available
            if self.bible_popup and self.bible_popup.IsShown() and self.bible_list.GetItemCount() > 0:
                first_item = self.bible_list.GetItemText(0)
                self.select_bible_book(first_item)
                return
        
        event.Skip()

    def show_bible_popup(self, matches):
        """Show popup with Bible book matches"""
        try:
            if not self.bible_popup:
                self.bible_popup = wx.Frame(self, style=wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT | wx.BORDER_SIMPLE)
                self.bible_popup.SetSize((300, 200))
                
                # Create list control
                self.bible_list = wx.ListCtrl(
                    self.bible_popup, 
                    style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER
                )
                self.bible_list.AppendColumn("Book", width=280)
                
                # Bind events
                self.bible_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_bible_list_click)
                self.bible_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_bible_list_select)
                self.bible_list.Bind(wx.EVT_KEY_DOWN, self.on_bible_key_down)
                
                # Layout
                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add(self.bible_list, 1, wx.EXPAND)
                self.bible_popup.SetSizer(sizer)
            
            # Clear and populate list
            self.bible_list.DeleteAllItems()
            for i, book in enumerate(matches):
                self.bible_list.InsertItem(i, book)
            
            # Position popup below the text control
            text_pos = self.bible_ctrl.GetScreenPosition()
            text_size = self.bible_ctrl.GetSize()
            popup_y = text_pos.y + text_size.height
            self.bible_popup.SetPosition((text_pos.x, popup_y))
            
            # Show popup
            self.bible_popup.Show(True)
            self.bible_popup.Raise()
            
        except Exception as e:
            pass

    def on_bible_list_click(self, event):
        """Handle double-click on Bible book list"""
        try:
            selected_idx = event.GetIndex()
            if selected_idx >= 0:
                book_name = self.bible_list.GetItemText(selected_idx)
                self.select_bible_book(book_name)
        except Exception as e:
            pass

    def on_bible_list_select(self, event):
        """Handle selection in Bible book list"""
        try:
            selected_idx = event.GetIndex()
            if selected_idx >= 0:
                book_name = self.bible_list.GetItemText(selected_idx)
                # Just highlight, don't select yet
        except Exception as e:
            pass

    def hide_bible_popup(self):
        """Hide the Bible book popup"""
        try:
            if self.bible_popup and self.bible_popup.IsShown():
                self.bible_popup.Hide()
        except Exception as e:
            pass

    # Rest of the Bible and projection methods would continue here...
    # [The file continues with all the other methods from the original, optimized for Windows]

    def select_bible_book(self, book_name):
        """Select a Bible book and update the input"""
        try:
            current_text = self.bible_ctrl.GetValue().strip()
            
            # Check if there are already chapter:verse numbers
            parts = current_text.split()
            numbers = []
            
            for part in parts:
                if re.match(r'^\d+:?\d*$', part):
                    numbers.append(part)
            
            # Build new text with selected book
            if numbers:
                new_text = f"{book_name} {' '.join(numbers)}"
            else:
                new_text = book_name
            
            self.bible_ctrl.SetValue(new_text)
            self.bible_ctrl.SetInsertionPointEnd()
            self.hide_bible_popup()
            
        except Exception as e:
            pass

    def find_chrome_executable(self):
        """Find Chrome executable path for Windows"""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        
        # Try to find via registry or where command
        try:
            result = subprocess.run(["where", "chrome"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
            
        return None

    def position_chrome_window_windows(self, target_monitor):
        """Position Chrome window on Windows using pywin32"""
        if not HAS_PYWIN32:
            return
            
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    if ("chrome" in window_title.lower() or 
                        "google chrome" in window_title.lower() or
                        class_name == "Chrome_WidgetWin_1"):
                        windows.append(hwnd)
                return True
            
            # Wait a bit for Chrome to open
            time.sleep(1)
            
            # Find Chrome windows
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # Use the most recent Chrome window
                hwnd = windows[-1]
                
                # Remove maximized state first
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
                
                # Move and resize to target monitor
                win32gui.SetWindowPos(
                    hwnd, 
                    win32con.HWND_TOP,
                    target_monitor.x, 
                    target_monitor.y,
                    target_monitor.width, 
                    target_monitor.height,
                    win32con.SWP_SHOWWINDOW
                )
                
                # Give it a moment
                time.sleep(0.3)
                
                # Make it fullscreen/maximized on the target monitor
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                
                # Send F11 for true fullscreen
                time.sleep(0.5)
                win32api.keybd_event(0x7A, 0, 0, 0)  # F11 down
                win32api.keybd_event(0x7A, 0, win32con.KEYEVENTF_KEYUP, 0)  # F11 up
                
        except Exception as e:
            pass

    # Additional Windows-specific methods
    def get_window_list(self):
        """Get list of all windows (Windows-specific debugging)"""
        if not HAS_PYWIN32:
            return []
            
        windows = []
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                if title:
                    windows.append((hwnd, title, class_name))
            return True
        
        win32gui.EnumWindows(enum_callback, windows)
        return windows

    def on_main_window_close(self, event):
        """Handle main window close - cleanup Chrome processes"""
        try:
            # Stop Chrome monitoring timer
            if hasattr(self, 'chrome_monitor_timer') and self.chrome_monitor_timer:
                self.chrome_monitor_timer.Stop()
            
            # Force close Chrome if it's running
            if self.chrome_process:
                self.force_close_chrome()
            
            # Close all projection frames
            if self.projection_frame:
                self.projection_frame.Destroy()
            if self.slides_projection_frame:
                self.slides_projection_frame.Destroy()
            if self.bible_projection_frame:
                self.bible_projection_frame.Destroy()
            if self.agenda_projection_frame:
                self.agenda_projection_frame.Destroy()
            
            # Close bible popup if open
            if self.bible_popup:
                self.bible_popup.Destroy()
                
        except Exception as e:
            pass
        
        event.Skip()  # Continue with normal close

    def force_close_chrome(self):
        """Force close Chrome process on Windows"""
        try:
            if self.chrome_process:
                if HAS_PYWIN32:
                    # Try graceful termination first
                    try:
                        self.chrome_process.terminate()
                        self.chrome_process.wait(timeout=3)
                    except:
                        # Force kill if graceful doesn't work
                        self.chrome_process.kill()
                else:
                    self.chrome_process.terminate()
                
                self.chrome_process = None
                
        except Exception as e:
            pass

    # Bible functionality implementation
    
    def parse_and_validate_bible_input(self, text):
        """Parse and validate bible input with enhanced flexibility"""
        try:
            text = text.strip()
            if not text:
                return None
                
            # Split input into parts
            parts = re.split(r'[\s:]+', text)
            
            # Try to identify book, chapter, and verse from parts
            book_name = None
            chapter = 1
            verse = 1
            
            # Look for book name in the parts (could be anywhere)
            book_start_idx = None
            book_end_idx = None
            
            # First, try to find a complete book name match
            for i in range(len(parts)):
                for j in range(i + 1, len(parts) + 1):
                    potential_book = ' '.join(parts[i:j]).lower()
                    
                    # Check if this matches any book name
                    for name in self.bible_book_names:
                        if name.lower() == potential_book:
                            book_name = name
                            book_start_idx = i
                            book_end_idx = j
                            break
                    if book_name:
                        break
                if book_name:
                    break
            
            # If no exact match, try partial matches
            if not book_name:
                for name in self.bible_book_names:
                    if text.lower().find(name.lower()) != -1:
                        book_name = name
                        # Find where this book appears in the original text
                        book_pos = text.lower().find(name.lower())
                        before_book = text[:book_pos].strip()
                        after_book = text[book_pos + len(name):].strip()
                        
                        # Parse numbers before and after the book
                        numbers = []
                        if before_book:
                            numbers.extend([int(x) for x in re.findall(r'\d+', before_book)])
                        if after_book:
                            numbers.extend([int(x) for x in re.findall(r'\d+', after_book)])
                        
                        # Assign chapter and verse from numbers
                        if len(numbers) >= 2:
                            chapter = numbers[0]
                            verse = numbers[1]
                        elif len(numbers) == 1:
                            chapter = numbers[0]
                            verse = 1
                        break
            else:
                # Extract numbers that aren't part of the book name
                number_parts = []
                for i, part in enumerate(parts):
                    if i < book_start_idx or i >= book_end_idx:
                        if part.isdigit():
                            number_parts.append(int(part))
                
                # Assign chapter and verse from extracted numbers
                if len(number_parts) >= 2:
                    chapter = number_parts[0]
                    verse = number_parts[1]
                elif len(number_parts) == 1:
                    chapter = number_parts[0]
                    verse = 1
            
            if not book_name:
                return None
            
            # Validate and adjust chapter number
            book_info = self.bible_books.get(book_name)
            if book_info:
                max_chapters = book_info[1]
                if chapter < 1:
                    chapter = 1
                elif chapter > max_chapters:
                    chapter = max_chapters
            
            return {
                'book': book_name,
                'chapter': chapter,
                'verse': verse,
                'book_id': book_info[0] if book_info else None
            }
            
        except Exception as e:
            return None

    def get_selected_bible_versions(self):
        """Get list of selected Bible versions"""
        selected = []
        if self.cuv_checkbox.GetValue():
            selected.append('cuv')
        if self.niv_checkbox.GetValue():
            selected.append('niv')
        if self.esv_checkbox.GetValue():
            selected.append('esv')
        return selected

    def generate_bible_html_multi_version(self, bible_info, selected_versions):
        """Generate HTML content for multiple bible versions with smooth JavaScript navigation"""
        try:
            # Get selected font sizes
            chinese_font_size = self.chinese_font_choice.GetStringSelection()
            english_font_size = self.english_font_choice.GetStringSelection()
            
            # Load content for all selected versions
            versions_data = {}
            
            # Bible version mappings
            bible_versions = {
                'cuv': '和合本',
                'kjv': 'KJV',
                'nas': 'NASB',
                'niv': 'NIV',
                'esv': 'ESV',
                'dby': 'Darby'
            }
            
            for version in selected_versions:
                # Construct file path
                book_id = bible_info['book_id']
                chapter = bible_info['chapter']
                verse_num = bible_info['verse']
                
                vol_folder = f"vol{book_id:02d}"
                chapter_file = f"chap{chapter:03d}.txt"
                file_path = os.path.join("books", version, vol_folder, chapter_file)
                
                if not os.path.exists(file_path):
                    continue
                    
                # Load chapter content with appropriate encoding
                verses = []
                try:
                    if version == 'cuv':
                        with open(file_path, 'r', encoding='gb2312') as f:
                            verses = [line.strip() for line in f.readlines() if line.strip()]
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            verses = [line.strip() for line in f.readlines() if line.strip()]
                except UnicodeDecodeError:
                    try:
                        if version == 'cuv':
                            with open(file_path, 'r', encoding='utf-8') as f:
                                verses = [line.strip() for line in f.readlines() if line.strip()]
                        else:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                verses = [line.strip() for line in f.readlines() if line.strip()]
                    except UnicodeDecodeError:
                        continue
                
                if verses:
                    versions_data[version] = verses
                    
            if not versions_data:
                return None
            
            # Validate verse number
            max_verses = max(len(verses) for verses in versions_data.values())
            if verse_num > max_verses:
                return None
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{bible_info['book']} {chapter} - Multiple Versions</title>
    <style>
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.4;
            margin: 20px;
            background-color: #2c3e50;
            color: #ecf0f1;
            font-size: {english_font_size};
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        .book-title {{
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 8px;
        }}
        .chapter-title {{
            font-size: 28px;
            color: #95a5a6;
            margin-bottom: 8px;
        }}
        .verses-container {{
            margin-top: 20px;
        }}
        .verse-group {{
            margin-bottom: 25px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .verse-row {{
            display: flex;
            align-items: stretch;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .verse-row:last-child {{
            border-bottom: none;
        }}
        .verse-label {{
            min-width: 120px;
            padding: 15px;
            font-weight: bold;
            font-size: 16px;
            color: #ecf0f1;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border-right: 2px solid rgba(255,255,255,0.2);
        }}
        .verse-text {{
            flex: 1;
            padding: 15px 20px;
            background-color: rgba(0,0,0,0.2);
        }}
        .cuv .verse-text {{
            font-family: "Microsoft YaHei", "SimSun", "PingFang SC", "Hiragino Sans GB", serif;
            font-size: {chinese_font_size};
            line-height: 1.6;
        }}
        .highlighted-verse-group {{
            border: 3px solid #f39c12;
            box-shadow: 0 0 20px rgba(243, 156, 18, 0.5);
        }}
        .highlighted-verse-row .verse-text {{
            background-color: rgba(243, 156, 18, 0.3);
            color: #fff;
        }}
        /* Version-specific colors */
        .kjv .verse-label {{ background-color: #2980b9; }}
        .nas .verse-label {{ background-color: #27ae60; }}
        .niv .verse-label {{ background-color: #8e44ad; }}
        .esv .verse-label {{ background-color: #e67e22; }}
        .dby .verse-label {{ background-color: #f39c12; }}
        .cuv .verse-label {{ background-color: #c0392b; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="book-title">{bible_info['book']}</div>
        <div class="chapter-title">Chapter {chapter}</div>
    </div>
    
    <div class="verses-container">
"""
            
            # Generate verses grouped by verse number
            for verse_i in range(1, max_verses + 1):
                is_highlighted = (verse_i == verse_num)
                verse_group_class = "verse-group highlighted-verse-group" if is_highlighted else "verse-group"
                
                html_content += f"""
        <div class="{verse_group_class}" id="verse-group-{verse_i}">
"""
                
                # Add each version for this verse
                for version in selected_versions:
                    if version in versions_data:
                        verses = versions_data[version]
                        verse_text = verses[verse_i - 1] if verse_i <= len(verses) else "[Verse not available]"
                        
                        version_display = bible_versions[version]
                        row_class = f"verse-row {version} {'highlighted-verse-row' if is_highlighted else ''}"
                        
                        html_content += f"""
            <div class="{row_class}">
                <div class="verse-label">
                    {version_display}<br/>{chapter}:{verse_i}
                </div>
                <div class="verse-text">
                    {verse_text}
                </div>
            </div>"""
                
                html_content += """
        </div>"""
            
            html_content += """
    </div>
    
    <script>
        // Scroll to highlighted verse after page loads
        window.addEventListener('load', function() {
            setTimeout(function() {
                var highlightedGroup = document.querySelector('.highlighted-verse-group');
                if (highlightedGroup) {
                    highlightedGroup.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }, 500);
        });
        
        // Function to dynamically change verse highlighting
        function highlightVerse(verseNumber) {
            // Remove existing highlighting
            var currentHighlighted = document.querySelectorAll('.highlighted-verse-group, .highlighted-verse-row');
            currentHighlighted.forEach(function(element) {
                element.classList.remove('highlighted-verse-group', 'highlighted-verse-row');
                element.classList.add('verse-group', 'verse-row');
            });
            
            // Add highlighting to new verse
            var newVerseGroup = document.getElementById('verse-group-' + verseNumber);
            if (newVerseGroup) {
                newVerseGroup.classList.remove('verse-group');
                newVerseGroup.classList.add('highlighted-verse-group');
                
                var verseRows = newVerseGroup.querySelectorAll('.verse-row');
                verseRows.forEach(function(row) {
                    row.classList.add('highlighted-verse-row');
                });
                
                // Only scroll if verse is not visible
                if (!isElementInViewport(newVerseGroup)) {
                    newVerseGroup.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        }
        
        // Function to check if element is in viewport
        function isElementInViewport(element) {
            var rect = element.getBoundingClientRect();
            var windowHeight = window.innerHeight || document.documentElement.clientHeight;
            var windowWidth = window.innerWidth || document.documentElement.clientWidth;
            
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= windowHeight &&
                rect.right <= windowWidth
            );
        }
    </script>
</body>
</html>"""
            
            return html_content
            
        except Exception as e:
            return None
    
    def on_bible_button_click(self, event):
        """Handle Bible project button click"""
        bible_input = self.bible_ctrl.GetValue().strip()
        
        if not bible_input:
            wx.MessageBox("Please enter a bible verse (e.g., 'John 3:16')", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Parse and validate input
        parsed = self.parse_and_validate_bible_input(bible_input)
        if not parsed:
            wx.MessageBox("Could not parse Bible reference. Try format like 'John 3:16'", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Start bible projection
        self.start_bible_projection(parsed)

    def start_bible_projection(self, bible_info, is_navigation=False):
        """Start projecting bible chapter to second screen"""
        try:
            # Get selected versions
            selected_versions = self.get_selected_bible_versions()
            if not selected_versions:
                wx.MessageBox("Please select at least one Bible version", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Hide any existing projections to avoid conflicts
            if self.is_projecting and hasattr(self, 'projection_frame') and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
            if self.is_projecting_slides and hasattr(self, 'slides_projection_frame') and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                self.hide_slides_projection(auto_hide=True)
            if self.is_projecting_agenda and hasattr(self, 'agenda_projection_frame') and self.agenda_projection_frame and not self.agenda_projection_frame.is_hidden:
                self.hide_agenda_projection(auto_hide=True)
                
            # Stop existing bible projection
            if self.bible_projection_frame:
                self.bible_projection_frame.Destroy()
                self.bible_projection_frame = None
                
            # Generate HTML content
            html_content = self.generate_bible_html_multi_version(bible_info, selected_versions)
            if not html_content:
                wx.MessageBox("Failed to generate Bible content", "Error", wx.OK | wx.ICON_ERROR)
                return
            
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) > 1 else monitors[0]
            
            # Create projection frame
            import base64
            
            # Encode HTML content as data URL
            html_bytes = html_content.encode('utf-8')
            html_b64 = base64.b64encode(html_bytes).decode('utf-8')
            data_url = f"data:text/html;charset=utf-8;base64,{html_b64}"
            
            self.bible_projection_frame = ProjectionFrame(self, data_url, target_monitor, "bible")
            self.is_projecting_bible = True
            
            # Store current projection info for navigation
            self.current_projected_bible = {
                'bible_info': bible_info,
                'selected_versions': selected_versions
            }
            
            # Update button states
            self.update_all_projection_buttons()
            
            self.status_text.SetLabel(f"📖 Projecting {bible_info['book']} {bible_info['chapter']}:{bible_info['verse']}")
            self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
            
        except Exception as e:
            wx.MessageBox(f"Error projecting Bible: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def on_slides_text_change(self, event):
        """Handle slides text changes - update status"""
        slides_input = self.slides_ctrl.GetValue().strip()
        
        if slides_input:
            # Check if it's a hymn ID
            if slides_input.upper() in self.hymns_data:
                hymn_info = f"Hymn {slides_input}"
                if hasattr(self, 'slides_status'):
                    self.slides_status.SetLabel(f"✓ Ready to present: {hymn_info}")
                    self.slides_status.SetForegroundColour(wx.Colour(39, 174, 96))
            elif self.is_google_slides_id(slides_input):
                if hasattr(self, 'slides_status'):
                    self.slides_status.SetLabel(f"✓ Ready to present: Google Slides ({slides_input[:20]}...)")
                    self.slides_status.SetForegroundColour(wx.Colour(39, 174, 96))
            else:
                if hasattr(self, 'slides_status'):
                    self.slides_status.SetLabel("Enter hymn ID (123, A123, C456) or Google Slides ID/URL")
                    self.slides_status.SetForegroundColour(wx.Colour(127, 140, 141))
        else:
            if hasattr(self, 'slides_status'):
                self.slides_status.SetLabel("Enter hymn ID (123, A123, C456) or Google Slides ID/URL")
                self.slides_status.SetForegroundColour(wx.Colour(127, 140, 141))
            
    def is_google_slides_id(self, text):
        """Check if text is a Google Slides ID or URL"""
        # Check for Google Slides URL patterns
        if 'docs.google.com/presentation' in text:
            return True
        # Check for standalone presentation ID (long alphanumeric string)
        if len(text) > 20 and text.replace('-', '').replace('_', '').isalnum():
            return True
        return False
        
    def on_slides_button_click(self, event):
        """Handle slides button click - always projects/reloads content"""
        slides_input = self.slides_ctrl.GetValue().strip()
        
        if not slides_input:
            wx.MessageBox("Please enter a hymn ID or Google Slides ID/URL", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # Check if it's a hymn ID first
        if slides_input.upper() in self.hymns_data:
            # It's a hymn ID, get the Google Slides ID
            google_slides_id = self.hymns_data[slides_input.upper()]
            
            # For public presentations, use the most WebView-friendly format
            # Try published format first (works better in embedded contexts)
            presentation_url = f"https://docs.google.com/presentation/d/{google_slides_id}/pub?start=false&loop=false&delayms=3000"
            
            print(f"Loading hymn {slides_input} -> {google_slides_id}")
            print(f"Using URL: {presentation_url}")
            
            # Debug: Test the URL format by opening it in a browser first
            # You can uncomment the next line to test the URL in your default browser:
            # import webbrowser; webbrowser.open(presentation_url)
            
            # Debug: Print the exact hymn data for verification
            print(f"Hymn data loaded: {len(self.hymns_data)} hymns")
            if slides_input.upper() in self.hymns_data:
                print(f"Found hymn {slides_input.upper()} with slides ID: {self.hymns_data[slides_input.upper()]}")
        elif self.is_google_slides_id(slides_input):
            # It's a Google Slides ID or URL
            if 'docs.google.com/presentation' in slides_input:
                # Extract ID from URL
                import re
                match = re.search(r'/presentation/d/([a-zA-Z0-9-_]+)', slides_input)
                if match:
                    google_slides_id = match.group(1)
                else:
                    wx.MessageBox("Invalid Google Slides URL format", "Error", wx.OK | wx.ICON_ERROR)
                    return
            else:
                # Assume it's a direct ID
                google_slides_id = slides_input
                
            # For public presentations, use the most WebView-friendly format
            presentation_url = f"https://docs.google.com/presentation/d/{google_slides_id}/pub?start=false&loop=false&delayms=3000"
            print(f"Using direct slides ID: {google_slides_id}")
            print(f"Using URL: {presentation_url}")
        else:
            wx.MessageBox("Invalid input. Please enter a hymn ID (123, A123, C456) or Google Slides ID/URL", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Skip WebView entirely for hymns - go straight to Chrome
        print("Skipping WebView for hymns - launching Chrome directly")
        chrome_url = f"https://docs.google.com/presentation/d/{google_slides_id}/present?start=true&loop=false&delayms=3000"
        
        try:
            self.current_presentation_id = google_slides_id
            self.launch_chrome_for_slides(chrome_url)
        except Exception as e:
            print(f"Chrome launch failed: {e}")
            wx.MessageBox(f"Failed to launch Chrome for hymn projection: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def start_slides_projection_simple(self, url, presentation_id):
        """Start slides projection with simple fallback for public presentations"""
        # Store presentation ID for Chrome fallback
        self.current_presentation_id = presentation_id
        
        # Store fallback URLs for public presentations (WebView-friendly order)
        self.slides_fallback_urls = [
            f"https://docs.google.com/presentation/d/{presentation_id}/embed?start=false&loop=false&delayms=3000",
            f"https://docs.google.com/presentation/d/{presentation_id}/preview",
            f"https://docs.google.com/presentation/d/{presentation_id}/present?start=false&loop=false&delayms=3000"
        ]
        
        # Start with the provided URL
        self.start_slides_projection(url)
    
    def launch_chrome_for_slides(self, url):
        """Launch Chrome browser for slides projection as fallback"""
        try:
            print(f"Attempting to launch Chrome with URL: {url}")
            
            # Get target monitor for positioning
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
            print(f"Target monitor: {target_monitor.x}x{target_monitor.y} ({target_monitor.width}x{target_monitor.height})")
            
            # Launch Chrome in fullscreen on target monitor
            chrome_args = [
                '--new-window',
                '--start-fullscreen',
                f'--window-position={target_monitor.x},{target_monitor.y}',
                f'--window-size={target_monitor.width},{target_monitor.height}',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-first-run',
                '--no-default-browser-check',
                url
            ]
            
            # Try different Chrome executable paths
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "chrome.exe",  # If in PATH
                "google-chrome"  # Linux/Mac style
            ]
            
            chrome_launched = False
            for chrome_path in chrome_paths:
                try:
                    print(f"Trying Chrome path: {chrome_path}")
                    import subprocess
                    self.chrome_process = subprocess.Popen([chrome_path] + chrome_args)
                    chrome_launched = True
                    print(f"✓ Successfully launched Chrome from: {chrome_path}")
                    break
                except FileNotFoundError:
                    print(f"Chrome not found at: {chrome_path}")
                    continue
                except Exception as e:
                    print(f"Failed to launch Chrome from {chrome_path}: {e}")
                    continue
            
            if chrome_launched:
                self.is_projecting_slides = True
                self.status_text.SetLabel("✓ Slides projection active in Chrome browser")
                self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
                if hasattr(self, 'slides_btn'):
                    self.slides_btn.Enable(True)
                self.update_all_projection_buttons()
                print("Chrome browser projection setup complete")
            else:
                print("❌ Chrome browser not found in any standard location")
                raise Exception("Chrome browser not found")
                
        except Exception as e:
            print(f"Chrome launch failed: {e}")
            raise e
    
    def test_and_start_slides_projection(self, url, presentation_id):
        """Test URL accessibility and start projection with best format"""
        import threading
        
        def test_url_thread():
            """Test URL accessibility in background thread"""
            try:
                import urllib.request
                import urllib.error
                
                # Test different URL formats to find the best one
                test_urls = [
                    url,  # Original embed URL
                    f"https://docs.google.com/presentation/d/{presentation_id}/present?start=false&loop=false&delayms=3000",
                    f"https://docs.google.com/presentation/d/{presentation_id}/preview",
                    f"https://docs.google.com/presentation/d/{presentation_id}/pub?start=false&loop=false&delayms=3000"
                ]
                
                working_url = None
                for test_url in test_urls:
                    try:
                        print(f"Testing URL: {test_url}")
                        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                        response = urllib.request.urlopen(req, timeout=10)
                        
                        # Check if we get redirected to account help (sign-in required)
                        final_url = response.geturl()
                        if 'accounts.google.com' in final_url or 'signin' in final_url.lower():
                            print(f"URL requires sign-in: {test_url}")
                            continue
                        
                        # Check response content for signs of success
                        content = response.read(1024).decode('utf-8', errors='ignore')
                        if 'presentation' in content.lower() or 'slides' in content.lower():
                            working_url = test_url
                            print(f"Found working URL: {working_url}")
                            break
                            
                    except Exception as e:
                        print(f"URL test failed for {test_url}: {e}")
                        continue
                
                # Call the UI thread to start projection
                wx.CallAfter(self.start_slides_with_tested_url, working_url or url)
                
            except Exception as e:
                print(f"URL testing error: {e}")
                # Fallback to original URL
                wx.CallAfter(self.start_slides_with_tested_url, url)
        
        # Show testing status
        self.status_text.SetLabel("Testing presentation accessibility...")
        self.status_text.SetForegroundColour(wx.Colour(52, 152, 219))
        
        # Start test in background thread
        test_thread = threading.Thread(target=test_url_thread, daemon=True)
        test_thread.start()
    
    def start_slides_with_tested_url(self, url):
        """Start slides projection with tested URL"""
        print(f"Starting projection with tested URL: {url}")
        self.start_slides_projection(url)
        
    def start_slides_projection(self, url):
        """Start projecting slides to second screen with fallback URLs"""
        try:
            # Hide any existing projections to avoid conflicts
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
            if self.is_projecting_bible and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                self.hide_bible_projection(auto_hide=True)
            if hasattr(self, 'agenda_projection_frame') and self.agenda_projection_frame and not self.agenda_projection_frame.is_hidden:
                self.hide_agenda_projection(auto_hide=True)
                
            # Stop existing slides projection
            if self.slides_projection_frame:
                self.slides_projection_frame.Destroy()
                self.slides_projection_frame = None
                
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
            
            print(f"Starting slides projection: {url}")
            
            # Extract presentation ID from URL for alternative formats
            presentation_id = None
            if '/presentation/d/' in url:
                import re
                match = re.search(r'/presentation/d/([a-zA-Z0-9-_]+)', url)
                if match:
                    presentation_id = match.group(1)
            
            # Store alternative URLs to try if the first one fails (only if not already set)
            if not hasattr(self, 'slides_fallback_urls') or not self.slides_fallback_urls:
                self.slides_fallback_urls = []
                if presentation_id:
                    # Alternative URL formats to try
                    self.slides_fallback_urls = [
                        f"https://docs.google.com/presentation/d/{presentation_id}/present?start=false&loop=false&delayms=3000",
                        f"https://docs.google.com/presentation/d/{presentation_id}/preview",
                        f"https://docs.google.com/presentation/d/{presentation_id}/edit?usp=sharing",
                        f"https://docs.google.com/presentation/d/{presentation_id}/pub?start=false&loop=false&delayms=3000"
                    ]
            
            # Update status immediately
            self.status_text.SetLabel("Creating slides projection...")
            if hasattr(self, 'slides_btn'):
                self.slides_btn.Enable(False)
            
            # Create slides projection window
            self.slides_projection_frame = ProjectionFrame(self, url, target_monitor, "slides")
            
            # Update status
            self.status_text.SetLabel("Loading presentation...")
            
        except Exception as e:
            print(f"Slides projection error: {e}")
            self.on_slides_projection_error(f"Failed to start slides projection: {str(e)}")
            
    def on_slides_projection_loaded(self):
        """Called when slides projection loads successfully"""
        self.is_projecting_slides = True
        self.status_text.SetLabel("✓ Slides projection active - ESC/Ctrl+Q/Ctrl+W to close, F11 to toggle fullscreen")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
        
        # Update button states
        if hasattr(self, 'slides_btn'):
            self.slides_btn.Enable(True)
        
        # Update all projection buttons
        self.update_all_projection_buttons()
        
    def on_slides_projection_error(self, error_msg):
        """Called when slides projection fails - try fallback URLs"""
        print(f"Slides projection error: {error_msg}")
        
        # Try fallback URLs if available
        if hasattr(self, 'slides_fallback_urls') and self.slides_fallback_urls:
            fallback_url = self.slides_fallback_urls.pop(0)  # Get next URL to try
            print(f"Trying fallback URL: {fallback_url}")
            
            self.status_text.SetLabel("Trying alternative URL format...")
            self.status_text.SetForegroundColour(wx.Colour(243, 156, 18))  # Orange
            
            # Destroy current frame and try with fallback URL
            if self.slides_projection_frame:
                self.slides_projection_frame.Destroy()
                self.slides_projection_frame = None
            
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
            
            # Create new projection with fallback URL
            self.slides_projection_frame = ProjectionFrame(self, fallback_url, target_monitor, "slides")
            return
        
        # No more fallback URLs, try Chrome as last resort
        print("All WebView URLs failed, trying Chrome browser fallback...")
        self.status_text.SetLabel("WebView failed - trying Chrome browser...")
        self.status_text.SetForegroundColour(wx.Colour(243, 156, 18))  # Orange
        
        # Try launching Chrome directly as a last resort
        try:
            # Check if we have the presentation ID
            if hasattr(self, 'current_presentation_id') and self.current_presentation_id:
                # Use the present format which works better in Chrome browser
                chrome_url = f"https://docs.google.com/presentation/d/{self.current_presentation_id}/present?start=true&loop=false&delayms=3000"
                print(f"Launching Chrome with URL: {chrome_url}")
                self.launch_chrome_for_slides(chrome_url)
                return
            else:
                print("No current_presentation_id available for Chrome fallback")
                raise Exception("No presentation ID available for Chrome fallback")
        except Exception as chrome_error:
            print(f"Chrome fallback failed: {chrome_error}")
        
        # Final error - nothing worked
        self.status_text.SetLabel("Slides projection failed - all methods exhausted")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))
        
        # Reset button
        if hasattr(self, 'slides_btn'):
            self.slides_btn.Enable(True)
        
        # Show simplified error message for public presentations
        error_details = f"""Slides projection failed: {error_msg}

All projection methods failed:
1. WebView embedding (Google blocks embedded access)
2. Alternative URL formats (all redirected to help page)
3. Chrome browser fallback (not available or failed)

This appears to be a Google Slides embedding restriction. The presentation works in a regular browser but not in embedded contexts."""
        
        wx.MessageBox(error_details, "Slides Projection Error", wx.OK | wx.ICON_ERROR)
        
    def stop_slides_projection(self):
        """Stop the slides projection"""
        if self.slides_projection_frame:
            self.slides_projection_frame.Destroy()
            self.slides_projection_frame = None
            
        self.is_projecting_slides = False
        
        # Reset UI
        self.status_text.SetLabel("Slides projection stopped")
        self.status_text.SetForegroundColour(wx.Colour(127, 140, 141))
        
        # Update all projection buttons
        self.update_all_projection_buttons()
    
    def on_main_button_click(self, event):
        """Handle URL project button click with Chrome launch"""
        url = self.url_ctrl.GetValue().strip()
        
        if not url:
            wx.MessageBox("Please enter a URL to project", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        self.start_projection(url)

    def start_projection(self, url):
        """Start projecting to second screen using Chrome browser"""
        try:
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) > 1 else monitors[0]
            
            # Hide other projections
            if self.is_projecting_bible and hasattr(self, 'bible_projection_frame') and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                self.hide_bible_projection(auto_hide=True)
            if self.is_projecting_slides and hasattr(self, 'slides_projection_frame') and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                self.hide_slides_projection(auto_hide=True)
            if self.is_projecting_agenda and hasattr(self, 'agenda_projection_frame') and self.agenda_projection_frame and not self.agenda_projection_frame.is_hidden:
                self.hide_agenda_projection(auto_hide=True)
                
            # Find Chrome executable
            chrome_path = self.find_chrome_executable()
            
            if chrome_path:
                # Launch Chrome on target monitor
                try:
                    # Close existing Chrome process if any
                    if self.chrome_process:
                        self.force_close_chrome()
                    
                    # Launch Chrome with the URL
                    chrome_args = [
                        chrome_path,
                        "--new-window",
                        "--start-fullscreen",
                        f"--window-position={target_monitor.x},{target_monitor.y}",
                        f"--window-size={target_monitor.width},{target_monitor.height}",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        url
                    ]
                    
                    self.chrome_process = subprocess.Popen(chrome_args)
                    self.is_projecting = True
                    
                    # Position Chrome window after launch (Windows-specific)
                    wx.CallLater(2000, self.position_chrome_window_windows, target_monitor)
                    
                    # Start monitoring Chrome process
                    if not hasattr(self, 'chrome_monitor_timer') or not self.chrome_monitor_timer:
                        self.chrome_monitor_timer = wx.Timer(self)
                        self.Bind(wx.EVT_TIMER, self.monitor_chrome_process, self.chrome_monitor_timer)
                    self.chrome_monitor_timer.Start(2000)  # Check every 2 seconds
                    
                    self.status_text.SetLabel(f"🌐 Chrome projection started")
                    self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
                    
                    # Update button states
                    self.update_all_projection_buttons()
                    
                except Exception as e:
                    # Fallback to embedded projection
                    self.start_embedded_projection(url, target_monitor)
            else:
                # Fallback to embedded projection
                self.start_embedded_projection(url, target_monitor)
                
        except Exception as e:
            wx.MessageBox(f"Error starting projection: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def start_embedded_projection(self, url, target_monitor):
        """Start embedded projection as fallback"""
        try:
            # Stop existing projection
            if self.projection_frame:
                self.projection_frame.Destroy()
                self.projection_frame = None
                
            # Create projection frame
            self.projection_frame = ProjectionFrame(self, url, target_monitor, "web")
            self.is_projecting = True
            
            self.status_text.SetLabel(f"🌐 Embedded projection started")
            self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
            
            # Update button states
            self.update_all_projection_buttons()
            
        except Exception as e:
            wx.MessageBox(f"Error starting embedded projection: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def monitor_chrome_process(self, event):
        """Monitor Chrome process and update status when it closes"""
        if self.chrome_process:
            poll_result = self.chrome_process.poll()
            if poll_result is not None:  # Process has ended
                self.on_chrome_closed()

    def on_chrome_closed(self):
        """Handle Chrome process closure"""
        self.chrome_process = None
        self.is_projecting = False
        
        if hasattr(self, 'chrome_monitor_timer') and self.chrome_monitor_timer:
            self.chrome_monitor_timer.Stop()
        
        self.status_text.SetLabel("🖥️ Chrome projection ended")
        self.status_text.SetForegroundColour(wx.Colour(127, 140, 141))
        
        # Update button states
        self.update_all_projection_buttons()
    
    def on_agenda_button_click(self, event):
        """Handle agenda button click - toggle show/hide agenda"""
        if self.is_projecting_agenda and self.agenda_projection_frame:
            # Agenda is currently active, check if hidden or visible
            if self.agenda_projection_frame.is_hidden:
                # Currently hidden, show it
                self.show_agenda_projection()
            else:
                # Currently visible, hide it
                self.hide_agenda_projection()
        else:
            # Start agenda projection for the first time
            self.start_agenda_projection()
            
    def start_agenda_projection(self):
        """Start projecting hardcoded agenda to second screen (first time only)"""
        try:
            # Hide any existing projections to avoid conflicts
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
            if self.is_projecting_slides and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                self.hide_slides_projection(auto_hide=True)
            if self.is_projecting_bible and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                self.hide_bible_projection(auto_hide=True)
                
            # Only create if it doesn't exist
            if not self.agenda_projection_frame:
                # Hardcoded agenda URL in full-screen presentation mode
                agenda_url = "https://docs.google.com/presentation/d/16z_afMCpHY1WzO3aJ_M-bfn-fdNTzKaejovlC_oBFUk/embed?start=false&loop=false&delayms=3000"
                    
                # Get target monitor
                monitors = get_monitors()
                target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
                
                print(f"Starting agenda projection: {agenda_url}")
                
                # Update status immediately
                self.status_text.SetLabel("Creating agenda projection...")
                self.agenda_btn.Enable(False)
                
                # Create agenda projection window
                self.agenda_projection_frame = ProjectionFrame(self, agenda_url, target_monitor, "agenda")
                
                # Update status
                self.status_text.SetLabel("Loading agenda...")
            else:
                # Just show existing agenda
                self.show_agenda_projection()
                
        except Exception as e:
            print(f"Agenda projection error: {e}")
            self.on_agenda_projection_error(f"Failed to start agenda projection: {str(e)}")
            
    def show_agenda_projection(self):
        """Show the agenda projection window"""
        if self.agenda_projection_frame:
            # Hide any visible web/slides/bible projections first
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
            if self.is_projecting_slides and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                self.hide_slides_projection(auto_hide=True)
            if self.is_projecting_bible and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                self.hide_bible_projection(auto_hide=True)
                
            self.agenda_projection_frame.show_projection()
            self.status_text.SetLabel("✓ Agenda projection restored")
            
            # Update all projection buttons
            self.update_all_projection_buttons()
            
    def on_agenda_projection_loaded(self):
        """Called when agenda projection loads successfully"""
        self.is_projecting_agenda = True
        self.status_text.SetLabel("✓ Agenda projection active - ESC/Ctrl+Q/Ctrl+W to close, F11 to toggle fullscreen")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
        
        # Update button states
        self.agenda_btn.Enable(True)
        self.agenda_btn.SetLabel("🗕 Hide Agenda")
        
        # Update all projection buttons
        self.update_all_projection_buttons()
        
    def on_agenda_projection_error(self, error_msg):
        """Called when agenda projection fails"""
        self.status_text.SetLabel("Agenda projection failed")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))
        
        # Reset button
        self.agenda_btn.Enable(True)
        
        wx.MessageBox(f"Agenda projection failed:\n{error_msg}", "Error", wx.OK | wx.ICON_ERROR)
    
    # Event handlers for UI controls

    def on_url_toggle_click(self, event):
        """Handle URL show/hide toggle"""
        if self.is_projecting:
            if hasattr(self, 'projection_frame') and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection()
            else:
                self.show_projection()

    def on_bible_toggle_click(self, event):
        """Handle Bible show/hide toggle"""
        if self.is_projecting_bible:
            if hasattr(self, 'bible_projection_frame') and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                self.hide_bible_projection()
            else:
                self.show_bible_projection()

    def show_bible_projection(self):
        """Show Bible projection"""
        if self.bible_projection_frame:
            self.bible_projection_frame.show_projection()
            self.status_text.SetLabel("📖 Bible projection shown")
            self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
            self.update_all_projection_buttons()

    def hide_bible_projection(self, auto_hide=False):
        """Hide Bible projection"""
        if self.bible_projection_frame:
            self.bible_projection_frame.hide_projection(auto_hide)
            if auto_hide:
                self.status_text.SetLabel("📖 Bible auto-hidden for other projection")
            else:
                self.status_text.SetLabel("📖 Bible hidden - desktop visible")
            self.update_all_projection_buttons()

    def hide_projection(self, auto_hide=False):
        """Hide URL projection"""
        if self.projection_frame:
            self.projection_frame.hide_projection(auto_hide)
            if auto_hide:
                self.status_text.SetLabel("🌐 URL auto-hidden for other projection")
            else:
                self.status_text.SetLabel("🌐 URL hidden - desktop visible")
            self.update_all_projection_buttons()

    def show_projection(self):
        """Show URL projection"""
        if self.projection_frame:
            self.projection_frame.show_projection()
            self.status_text.SetLabel("🌐 URL projection shown")
            self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
            self.update_all_projection_buttons()

    def on_prev_verse_click(self, event):
        """Handle previous verse navigation"""
        if self.current_projected_bible and self.bible_projection_frame:
            bible_info = self.current_projected_bible['bible_info'].copy()
            if bible_info['verse'] > 1:
                bible_info['verse'] -= 1
                
                # Update the text control to reflect the navigation
                self.bible_ctrl.SetValue(f"{bible_info['book']} {bible_info['chapter']}:{bible_info['verse']}")
                
                # Update current projection info
                self.current_projected_bible['bible_info'] = bible_info
                
                # Restart projection with new verse
                self.start_bible_projection(bible_info, is_navigation=True)
                
                # Update navigation button states
                self.update_verse_navigation_buttons()

    def on_next_verse_click(self, event):
        """Handle next verse navigation"""
        if self.current_projected_bible and self.bible_projection_frame:
            bible_info = self.current_projected_bible['bible_info'].copy()
            selected_versions = self.current_projected_bible['selected_versions']
            
            max_verses = self.get_max_verses_in_chapter(bible_info, selected_versions)
            if bible_info['verse'] < max_verses:
                bible_info['verse'] += 1
                
                # Update the text control to reflect the navigation
                self.bible_ctrl.SetValue(f"{bible_info['book']} {bible_info['chapter']}:{bible_info['verse']}")
                
                # Update current projection info
                self.current_projected_bible['bible_info'] = bible_info
                
                # Restart projection with new verse
                self.start_bible_projection(bible_info, is_navigation=True)
                
                # Update navigation button states
                self.update_verse_navigation_buttons()

    def get_max_verses_in_chapter(self, bible_info, selected_versions):
        """Get the maximum number of verses in the current chapter"""
        max_verses = 0
        
        for version in selected_versions:
            book_id = bible_info['book_id']
            chapter = bible_info['chapter']
            
            vol_folder = f"vol{book_id:02d}"
            chapter_file = f"chap{chapter:03d}.txt"
            file_path = os.path.join("books", version, vol_folder, chapter_file)
            
            if os.path.exists(file_path):
                try:
                    encoding = 'gb2312' if version == 'cuv' else 'utf-8'
                    with open(file_path, 'r', encoding=encoding) as f:
                        verses = [line.strip() for line in f.readlines() if line.strip()]
                        max_verses = max(max_verses, len(verses))
                        break  # Use first available version
                except:
                    continue
        
        return max_verses if max_verses > 0 else 150  # Fallback

    def update_verse_navigation_buttons(self):
        """Update the verse navigation button states based on current projection"""
        if self.current_projected_bible:
            bible_info = self.current_projected_bible['bible_info']
            selected_versions = self.current_projected_bible['selected_versions']
            
            # Get chapter content to determine max verses
            max_verses = self.get_max_verses_in_chapter(bible_info, selected_versions)
            current_verse = bible_info['verse']
            
            # Enable/disable previous verse button
            self.prev_verse_btn.Enable(current_verse > 1)
            
            # Enable/disable next verse button
            self.next_verse_btn.Enable(current_verse < max_verses)
        else:
            # No current projection, disable both buttons
            self.prev_verse_btn.Enable(False)
            self.next_verse_btn.Enable(False)

    # Placeholder methods for not-yet-implemented functionality
    def on_bible_preview_click(self, event):
        """Handle bible preview button click"""
        bible_input = self.bible_ctrl.GetValue().strip()
        
        if not bible_input:
            wx.MessageBox("Please enter a bible verse (e.g., 'John 3:16')", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Parse and validate input
        parsed = self.parse_and_validate_bible_input(bible_input)
        if not parsed:
            return
            
        # Show preview
        self.show_bible_preview(parsed)
    
    def parse_and_validate_bible_input(self, text):
        """Parse and validate bible input with enhanced flexibility"""
        try:
            text = text.strip()
            if not text:
                return None
                
            # Split input into parts
            parts = re.split(r'[\s:]+', text)
            
            # Try to identify book, chapter, and verse from parts
            book_name = None
            chapter = 1
            verse = 1
            
            # Look for book name in the parts (could be anywhere)
            book_start_idx = None
            book_end_idx = None
            
            # First, try to find a complete book name match
            for i in range(len(parts)):
                for j in range(i + 1, len(parts) + 1):
                    potential_book = ' '.join(parts[i:j]).lower()
                    
                    # Check if this matches any book name
                    for name in self.bible_book_names:
                        if name.lower() == potential_book:
                            book_name = name
                            book_start_idx = i
                            book_end_idx = j
                            break
                    if book_name:
                        break
                if book_name:
                    break
            
            # If no exact match, try partial matches
            if not book_name:
                for name in self.bible_book_names:
                    if text.lower().find(name.lower()) != -1:
                        book_name = name
                        # Find where this book appears in the original text
                        book_pos = text.lower().find(name.lower())
                        before_book = text[:book_pos].strip()
                        after_book = text[book_pos + len(name):].strip()
                        
                        # Parse numbers before and after the book
                        numbers = []
                        if before_book:
                            numbers.extend([int(x) for x in re.findall(r'\d+', before_book)])
                        if after_book:
                            numbers.extend([int(x) for x in re.findall(r'\d+', after_book)])
                        
                        # Assign chapter and verse from numbers
                        if len(numbers) >= 2:
                            chapter = numbers[0]
                            verse = numbers[1]
                        elif len(numbers) == 1:
                            chapter = numbers[0]
                            verse = 1
                        break
            else:
                # Extract numbers that aren't part of the book name
                number_parts = []
                for i, part in enumerate(parts):
                    if i < book_start_idx or i >= book_end_idx:
                        if part.isdigit():
                            number_parts.append(int(part))
                
                # Assign chapter and verse from extracted numbers
                if len(number_parts) >= 2:
                    chapter = number_parts[0]
                    verse = number_parts[1]
                elif len(number_parts) == 1:
                    chapter = number_parts[0]
                    verse = 1
            
            if not book_name:
                self.bible_status.SetLabel("Book not found - try typing book name")
                self.bible_status.SetForegroundColour(wx.Colour(231, 76, 60))
                return None
            
            # Validate and adjust chapter number
            book_info = self.bible_books.get(book_name)
            if book_info:
                max_chapters = book_info[1]
                if chapter < 1:
                    chapter = 1
                elif chapter > max_chapters:
                    chapter = max_chapters
                    self.bible_status.SetLabel(f"{book_name} only has {max_chapters} chapters - using chapter {chapter}")
                    self.bible_status.SetForegroundColour(wx.Colour(243, 156, 18))
            
            # Return parsed bible info
            return {
                'book': book_name,
                'book_id': book_info[0] if book_info else 1,
                'chapter': chapter,
                'verse': verse,
                'verse_end': verse
            }
            
        except Exception as e:
            print(f"Error parsing bible input: {e}")
            self.bible_status.SetLabel("Could not parse Bible reference. Try format like 'John 3:16'")
            self.bible_status.SetForegroundColour(wx.Colour(231, 76, 60))
            return None
    
    def show_bible_preview(self, bible_info):
        """Show Bible chapter preview with clickable verses"""
        try:
            # Store current bible info for navigation
            self.current_bible_info = bible_info.copy()
            
            # Get selected bible versions from checkboxes
            selected_versions = []
            for version_key, checkbox in self.version_checkboxes.items():
                if checkbox.GetValue():
                    selected_versions.append(version_key)
            
            if not selected_versions:
                wx.MessageBox("Please select at least one Bible version to display.", "No Version Selected", wx.OK | wx.ICON_WARNING)
                return
            
            # Clear existing preview
            self.bible_verses_sizer.Clear(True)
            
            # Update header
            book_name = bible_info['book']
            chapter = bible_info['chapter']
            self.preview_header.SetLabel(f"{book_name} Chapter {chapter}")
            
            # Enable chapter navigation buttons
            self.prev_chapter_btn.Enable(chapter > 1)
            if book_name in self.bible_books:
                max_chapters = self.bible_books[book_name][1]
                self.next_chapter_btn.Enable(chapter < max_chapters)
            else:
                self.next_chapter_btn.Enable(True)  # Allow navigation if we don't know the limit
            
            # Load content for all selected versions
            versions_data = {}
            
            for version in selected_versions:
                book_id = bible_info['book_id']
                chapter = bible_info['chapter']
                
                vol_folder = f"vol{book_id:02d}"
                chapter_file = f"chap{chapter:03d}.txt"
                file_path = os.path.join("books", version, vol_folder, chapter_file)
                
                if not os.path.exists(file_path):
                    continue
                    
                # Load chapter content with appropriate encoding
                verses = []
                try:
                    if version == 'cuv':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    else:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    
                    # Split into verses
                    verse_lines = content.strip().split('\n')
                    for line in verse_lines:
                        if line.strip():
                            verses.append(line.strip())
                    
                    versions_data[version] = verses
                    
                except Exception as e:
                    print(f"Error loading {version} {book_name} {chapter}: {e}")
                    continue
            
            if not versions_data:
                # Show message that no Bible files were found
                no_data_text = wx.StaticText(self.bible_preview_scroll, 
                    label=f"No Bible files found for {book_name} {chapter}\nPlace Bible files in books/ folder")
                no_data_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
                no_data_text.SetForegroundColour(wx.Colour(127, 140, 141))
                self.bible_verses_sizer.Add(no_data_text, 0, wx.ALL, 10)
            else:
                # Find maximum number of verses
                max_verses = max(len(verses) for verses in versions_data.values())
                
                # Create verse rows
                for verse_num in range(1, max_verses + 1):
                    verse_panel = wx.Panel(self.bible_preview_scroll)
                    verse_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
                    verse_sizer = wx.BoxSizer(wx.VERTICAL)
                    
                    # Verse number header
                    verse_header = wx.StaticText(verse_panel, label=f"Verse {verse_num}")
                    verse_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                    verse_header.SetForegroundColour(wx.Colour(52, 152, 219))
                    verse_sizer.Add(verse_header, 0, wx.ALL, 2)
                    
                    # Add text for each version
                    for version_key in selected_versions:
                        if version_key in versions_data:
                            verses = versions_data[version_key]
                            if verse_num <= len(verses):
                                verse_text = verses[verse_num - 1]
                                
                                # Create clickable text
                                text_ctrl = wx.StaticText(verse_panel, label=verse_text)
                                text_ctrl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                
                                # Color code by version
                                if version_key == 'cuv':
                                    text_ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black
                                elif version_key == 'niv':
                                    text_ctrl.SetForegroundColour(wx.Colour(0, 100, 0))  # Dark green
                                elif version_key == 'kjv':
                                    text_ctrl.SetForegroundColour(wx.Colour(100, 0, 100))  # Purple
                                elif version_key == 'nas':
                                    text_ctrl.SetForegroundColour(wx.Colour(0, 0, 150))  # Dark blue
                                else:
                                    text_ctrl.SetForegroundColour(wx.Colour(100, 100, 0))  # Dark yellow
                                
                                verse_sizer.Add(text_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
                    
                    verse_panel.SetSizer(verse_sizer)
                    self.bible_verses_sizer.Add(verse_panel, 0, wx.EXPAND | wx.ALL, 2)
            
            # Refresh layout
            self.bible_preview_scroll.Layout()
            self.bible_preview_scroll.FitInside()
            self.bible_preview_scroll.Scroll(0, 0)  # Scroll to top
            
        except Exception as e:
            print(f"Error showing bible preview: {e}")
            wx.MessageBox(f"Error loading Bible preview: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def load_bible_preview(self, bible_info):
        """Load Bible preview for chapter navigation"""
        self.show_bible_preview(bible_info)

    def on_bible_history_click(self, event):
        """Handle Bible history button click"""
        wx.MessageBox("Bible history not yet implemented in Windows version", "Info", wx.OK | wx.ICON_INFORMATION)
    
    def on_version_checkbox_change(self, event):
        """Handle changes to bible version checkboxes"""
        # Update status to show selected versions
        selected_count = sum(1 for checkbox in self.version_checkboxes.values() if checkbox.GetValue())
        if selected_count > 0:
            versions_text = ", ".join([self.bible_versions[k] for k, v in self.version_checkboxes.items() if v.GetValue()])
            current_text = self.bible_ctrl.GetValue().strip()
            if current_text:
                self.bible_status.SetLabel(f"Enter verse for '{current_text}' - {selected_count} version(s): {versions_text}")
            else:
                self.bible_status.SetLabel(f"Enter book name and verse - {selected_count} version(s) selected: {versions_text}")
        else:
            self.bible_status.SetLabel("Select at least one Bible version to display")
            self.bible_status.SetForegroundColour(wx.Colour(231, 76, 60))
            return
            
        self.bible_status.SetForegroundColour(wx.Colour(127, 140, 141))

    def on_bible_clear_click(self, event):
        """Handle click on the clear button for the bible text control"""
        self.bible_ctrl.SetValue("")
        self.bible_ctrl.SetFocus()
        
        # Clear preview area
        self.bible_verses_sizer.Clear(True)
        self.bible_preview_scroll.Layout()
        self.bible_preview_scroll.FitInside()
        self.preview_header.SetLabel("Chapter Preview (empty - click 👁 to load):")
        
        # Disable navigation buttons
        self.prev_chapter_btn.Enable(False)
        self.next_chapter_btn.Enable(False)
        self.prev_verse_btn.Enable(False)
        self.next_verse_btn.Enable(False)
        
        # Clear stored bible info
        if hasattr(self, 'current_bible_info'):
            delattr(self, 'current_bible_info')
        
        # Clear current projected bible info
        self.current_projected_bible = None
        
        # Show how many versions are selected
        selected_count = sum(1 for checkbox in self.version_checkboxes.values() if checkbox.GetValue())
        if selected_count > 0:
            versions_text = ", ".join([self.bible_versions[k] for k, v in self.version_checkboxes.items() if v.GetValue()])
            self.bible_status.SetLabel(f"Enter book name and verse - {selected_count} version(s) selected: {versions_text}")
        else:
            self.bible_status.SetLabel("Enter book name and verse - No versions selected")
    
    def on_prev_verse_click(self, event):
        """Navigate to previous verse"""
        if not self.current_projected_bible:
            return
            
        bible_info = self.current_projected_bible['bible_info']
        current_verse = bible_info.get('verse', 1)
        
        if current_verse > 1:
            # Go to previous verse in same chapter
            bible_info['verse'] = current_verse - 1
            bible_info['verse_end'] = current_verse - 1  # Single verse
            selected_versions = self.current_projected_bible['selected_versions']
            self.start_bible_projection(bible_info, is_navigation=True)
        else:
            # Could implement previous chapter logic here
            wx.MessageBox("Already at first verse of chapter", "Info", wx.OK | wx.ICON_INFORMATION)
    
    def on_next_verse_click(self, event):
        """Navigate to next verse"""
        if not self.current_projected_bible:
            return
            
        bible_info = self.current_projected_bible['bible_info']
        current_verse = bible_info.get('verse', 1)
        
        # For now, just increment verse (could add chapter bounds checking)
        bible_info['verse'] = current_verse + 1
        bible_info['verse_end'] = current_verse + 1  # Single verse
        selected_versions = self.current_projected_bible['selected_versions']
        self.start_bible_projection(bible_info, is_navigation=True)
    
    def on_prev_chapter_click(self, event):
        """Navigate to previous chapter in preview"""
        if hasattr(self, 'current_bible_info'):
            bible_info = self.current_bible_info
            current_chapter = bible_info.get('chapter', 1)
            
            if current_chapter > 1:
                bible_info['chapter'] = current_chapter - 1
                self.load_bible_preview(bible_info)
            else:
                wx.MessageBox("Already at first chapter", "Info", wx.OK | wx.ICON_INFORMATION)
    
    def on_next_chapter_click(self, event):
        """Navigate to next chapter in preview"""
        if hasattr(self, 'current_bible_info'):
            bible_info = self.current_bible_info
            current_chapter = bible_info.get('chapter', 1)
            book_name = bible_info.get('book', '')
            
            # Get max chapters for this book
            if book_name in self.bible_books:
                max_chapters = self.bible_books[book_name][1]
                if current_chapter < max_chapters:
                    bible_info['chapter'] = current_chapter + 1
                    self.load_bible_preview(bible_info)
                else:
                    wx.MessageBox(f"Already at last chapter of {book_name}", "Info", wx.OK | wx.ICON_INFORMATION)
            else:
                # Just increment for now
                bible_info['chapter'] = current_chapter + 1
                self.load_bible_preview(bible_info)
    
    def on_slides_toggle_click(self, event):
        """Handle slides projection show/hide toggle"""
        if self.slides_projection_frame and self.is_projecting_slides:
            if self.slides_projection_frame.is_hidden:
                self.show_slides_projection()
            else:
                self.hide_slides_projection()
    

    def show_hymns_dropdown(self, event):
        """Show hymns dropdown menu"""
        if not self.hymns_data:
            wx.MessageBox("No hymns data loaded from hymns.csv", "No Hymns", wx.OK | wx.ICON_WARNING)
            return
            
        # Create popup menu with hymns
        menu = wx.Menu()
        
        # Add first 20 hymns for quick access
        hymn_ids = sorted(self.hymns_ids[:20])  # Show first 20
        for hymn_id in hymn_ids:
            menu_item = menu.Append(wx.ID_ANY, f"Hymn {hymn_id}")
            self.Bind(wx.EVT_MENU, lambda evt, hid=hymn_id: self.select_hymn(hid), menu_item)
            
        if len(self.hymns_ids) > 20:
            menu.AppendSeparator()
            menu.Append(wx.ID_ANY, f"... and {len(self.hymns_ids) - 20} more hymns")
        
        # Show menu
        btn_pos = self.hymn_dropdown_btn.GetPosition()
        btn_size = self.hymn_dropdown_btn.GetSize()
        self.PopupMenu(menu, (btn_pos.x, btn_pos.y + btn_size.height))
        
    def select_hymn(self, hymn_id):
        """Select a hymn from the dropdown"""
        self.slides_ctrl.SetValue(hymn_id)
        self.slides_ctrl.SetFocus()
        # Update status
        self.on_slides_text_change(None)
    
    def hide_slides_projection(self, auto_hide=False):
        """Hide the slides projection window"""
        if self.slides_projection_frame:
            self.slides_projection_frame.hide_projection()
            if auto_hide:
                self.status_text.SetLabel("📱 Slides auto-hidden for other projection")
            else:
                self.status_text.SetLabel("📱 Slides projection hidden - click toggle to restore")
            
            # Update all projection buttons
            self.update_all_projection_buttons()
            
    def show_slides_projection(self):
        """Show the slides projection window"""
        if self.slides_projection_frame:
            # Hide any visible web/bible/agenda projections first
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
            if self.is_projecting_bible and self.bible_projection_frame and not self.bible_projection_frame.is_hidden:
                self.hide_bible_projection(auto_hide=True)
            if hasattr(self, 'agenda_projection_frame') and self.agenda_projection_frame and not self.agenda_projection_frame.is_hidden:
                self.hide_agenda_projection(auto_hide=True)
                
            self.slides_projection_frame.show_projection()
            self.status_text.SetLabel("✓ Slides projection restored")
            
            # Update all projection buttons
            self.update_all_projection_buttons()
            
    def hide_agenda_projection(self, auto_hide=False):
        """Hide the agenda projection window"""
        if self.agenda_projection_frame:
            self.agenda_projection_frame.hide_projection()
            if auto_hide:
                self.status_text.SetLabel("📱 Agenda auto-hidden for other projection")
            else:
                self.status_text.SetLabel("📱 Agenda projection hidden - click button to restore")
                self.agenda_btn.SetLabel("📋 Show Agenda")
            
            # Update all projection buttons
            self.update_all_projection_buttons()
    
    # Status update methods
    def on_projection_loaded(self):
        self.status_text.SetLabel("🌐 URL projection loaded successfully")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))

    def on_projection_error(self, error):
        self.status_text.SetLabel(f"❌ URL projection error: {error}")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))

    def on_bible_projection_loaded(self):
        self.status_text.SetLabel("📖 Bible projection loaded successfully")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))

    def on_bible_projection_error(self, error):
        self.status_text.SetLabel(f"❌ Bible projection error: {error}")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))

    def on_main_window_close(self, event):
        """Handle main window close - cleanup all processes"""
        print("Main window closing - cleaning up processes...")
        
        # Stop Chrome process if it exists
        if hasattr(self, 'chrome_process') and self.chrome_process:
            try:
                print("Terminating Chrome process...")
                self.chrome_process.terminate()
                # Give it a moment to close gracefully
                import time
                time.sleep(0.5)
                # Force kill if still running
                if self.chrome_process.poll() is None:
                    self.chrome_process.kill()
                print("Chrome process terminated")
            except Exception as e:
                print(f"Error terminating Chrome process: {e}")
        
        # Stop Chrome monitor timer if it exists
        if hasattr(self, 'chrome_monitor_timer') and self.chrome_monitor_timer:
            self.chrome_monitor_timer.Stop()
        
        # Close all projection windows
        if self.projection_frame:
            self.projection_frame.Destroy()
        if self.slides_projection_frame:
            self.slides_projection_frame.Destroy()
        if self.bible_projection_frame:
            self.bible_projection_frame.Destroy()
        if self.agenda_projection_frame:
            self.agenda_projection_frame.Destroy()
            
        # Continue with normal close
        event.Skip()





class WebProjectorApp(wx.App):
    """Main application class"""
    
    def OnInit(self):
        """Initialize the application"""
        # Set Windows-specific app properties
        self.SetAppName("NCF Screen Projector")
        self.SetAppDisplayName("NCF Screen Projector - Windows Edition")
        
        self.frame = MainFrame()
        self.frame.Show()
        return True


def main():
    """Main entry point"""
    try:
        # Windows-specific initialization
        if HAS_PYWIN32:
            # Set DPI awareness for high-DPI displays
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
        app = WebProjectorApp(False)
        app.MainLoop()
        
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()