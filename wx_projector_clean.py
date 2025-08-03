#!/usr/bin/env python3
"""
wxPython Web Page Projector
Native desktop application using wxPython for both UI and web projection
"""

import wx
import wx.html2
import wx.lib.buttons as buttons
import re
import threading
import time
import csv
import os
from screeninfo import get_monitors


class ProjectionFrame(wx.Frame):
    """Fullscreen projection window for displaying web content"""
    
    def __init__(self, parent, url, monitor, projection_type="web"):
        super().__init__(
            parent, 
            title="Web Page Projection" if projection_type == "web" else 
                  "Slides Projection" if projection_type == "slides" else
                  "Bible Projection",
            style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP
        )
        
        self.parent_app = parent
        self.url = url
        self.monitor = monitor
        self.is_hidden = False
        self.is_fullscreen = False
        self.projection_type = projection_type
        
        print(f"Creating projection on monitor: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
        
        # Set window size and position for target monitor with extra coverage
        # Add a small buffer to ensure complete coverage
        extra_pixels = 10
        self.SetSize(monitor.width + extra_pixels, monitor.height + extra_pixels)
        self.SetPosition((monitor.x - extra_pixels//2, monitor.y - extra_pixels//2))
        
        # Create web view
        self.browser = wx.html2.WebView.New(self)
        
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
        
        # Load URL
        print(f"Loading URL: {url}")
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
                print(f"Display geometry: {geometry}")
                
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
            
            # Also try the traditional fullscreen method
            self.ShowFullScreen(True, 
                wx.FULLSCREEN_NOTOOLBAR | 
                wx.FULLSCREEN_NOSTATUSBAR | 
                wx.FULLSCREEN_NOBORDER | 
                wx.FULLSCREEN_NOMENUBAR |
                wx.FULLSCREEN_NOCAPTION)
            
            self.is_fullscreen = True
            print(f"Window coverage ensured: {self.GetSize()} at {self.GetPosition()}")
        except Exception as e:
            print(f"Error ensuring coverage: {e}")
            # Fallback to original method
            self.make_fullscreen_fallback()
            
    def make_fullscreen_fallback(self):
        """Fallback fullscreen method"""
        try:
            self.SetSize(self.monitor.width, self.monitor.height)
            self.SetPosition((self.monitor.x, self.monitor.y))
            self.ShowFullScreen(True)
            self.is_fullscreen = True
            print("Using fallback fullscreen method")
        except Exception as e:
            print(f"Fallback fullscreen failed: {e}")
    
    def on_page_loaded(self, event):
        """Called when page finishes loading"""
        print("Page loaded successfully")
        if self.projection_type == "slides":
            self.parent_app.on_slides_projection_loaded()
        elif self.projection_type == "bible":
            self.parent_app.on_bible_projection_loaded()
        else:
            self.parent_app.on_projection_loaded()
        
    def on_page_error(self, event):
        """Called when page fails to load"""
        error_msg = f"Failed to load: {self.url}"
        print(f"Page load error: {error_msg}")
        if self.projection_type == "slides":
            self.parent_app.on_slides_projection_error(error_msg)
        elif self.projection_type == "bible":
            self.parent_app.on_bible_projection_error(error_msg)
        else:
            self.parent_app.on_projection_error(error_msg)
        
    def on_key_down(self, event):
        """Handle keyboard events"""
        keycode = event.GetKeyCode()
        
        # Multiple escape methods for better reliability
        if keycode == wx.WXK_ESCAPE:
            print("ESC key pressed - stopping projection")
            if self.projection_type == "slides":
                self.parent_app.stop_slides_projection()
            elif self.projection_type == "bible":
                self.parent_app.stop_bible_projection()
            else:
                self.parent_app.stop_projection()
        # Add Ctrl+Q as alternative quit method (Mac/Linux style)
        elif keycode == ord('Q') and event.ControlDown():
            print("Ctrl+Q pressed - stopping projection")
            if self.projection_type == "slides":
                self.parent_app.stop_slides_projection()
            elif self.projection_type == "bible":
                self.parent_app.stop_bible_projection()
            else:
                self.parent_app.stop_projection()
        # Add Ctrl+W as alternative close method
        elif keycode == ord('W') and event.ControlDown():
            print("Ctrl+W pressed - stopping projection")
            if self.projection_type == "slides":
                self.parent_app.stop_slides_projection()
            elif self.projection_type == "bible":
                self.parent_app.stop_bible_projection()
            else:
                self.parent_app.stop_projection()
        # Add F11 to toggle fullscreen (emergency exit)
        elif keycode == wx.WXK_F11:
            print("F11 pressed - toggling fullscreen")
            if self.is_fullscreen:
                self.ShowFullScreen(False)
                self.is_fullscreen = False
            else:
                self.ensure_complete_coverage()
        else:
            event.Skip()
    
    def on_close(self, event):
        """Handle window close event"""
        if self.projection_type == "slides":
            self.parent_app.stop_slides_projection()
        elif self.projection_type == "bible":
            self.parent_app.stop_bible_projection()
        else:
            self.parent_app.stop_projection()
        
    def hide_projection(self, auto_hide=False):
        """Hide the projection window"""
        self.Hide()
        self.is_hidden = True
    
    def show_projection(self):
        """Show the projection window"""
        self.Show()
        self.Raise()
        self.SetFocus()
        
        # Always go through the fullscreen process to ensure proper restoration
        wx.CallLater(200, self.ensure_complete_coverage)
        self.is_hidden = False
        
    def reload_url(self, url):
        """Reload with new URL"""
        self.url = url
        self.browser.LoadURL(url)


class MainFrame(wx.Frame):
    """Main application window with controls"""
    
    def __init__(self):
        super().__init__(
            None, 
            title="🖥️ Web Page Projector", 
            size=(800, 750),
            style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER
        )
        
        # Variables
        self.projection_frame = None
        self.is_projecting = False
        self.slides_projection_frame = None
        self.is_projecting_slides = False
        self.bible_projection_frame = None
        self.is_projecting_bible = False
        
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
        
    def setup_ui(self):
        """Create the user interface"""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(248, 248, 248))  # Very light gray for better contrast
        
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="🖥️ Web Page Projector")
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
            size=(280, 36)
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
            size=(200, 36)
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
        
        slides_row_sizer.Add(self.slides_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        slides_row_sizer.Add(self.hymn_dropdown_btn, 0, wx.RIGHT, 5)
        slides_row_sizer.Add(self.slides_btn, 0, wx.RIGHT, 5)
        slides_row_sizer.Add(self.slides_toggle_btn, 0, 0)
        slides_sizer.Add(slides_row_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Status text for current selection
        self.slides_status = wx.StaticText(panel, label="Enter hymn ID (123, A123, C456) or Google Slides ID/URL")
        self.slides_status.SetForegroundColour(wx.Colour(127, 140, 141))
        slides_sizer.Add(self.slides_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        main_sizer.Add(slides_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        
        # Bible Verses section
        bible_box = wx.StaticBox(panel, label="Bible Verses:")
        bible_sizer = wx.StaticBoxSizer(bible_box, wx.VERTICAL)
        
        # Bible input with buttons on same row
        bible_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Bible input control (narrower)
        self.bible_ctrl = wx.TextCtrl(
            panel, 
            value="",
            style=wx.TE_PROCESS_ENTER | wx.BORDER_THEME,
            size=(200, 36)  # Narrower width
        )
        bible_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.bible_ctrl.SetFont(bible_font)
        self.bible_ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.bible_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        
        # Disable any built-in autocomplete features
        if hasattr(self.bible_ctrl, 'AutoComplete'):
            self.bible_ctrl.AutoComplete([])
        if hasattr(self.bible_ctrl, 'SetMaxLength'):
            # Allow reasonable length for book names + verse
            self.bible_ctrl.SetMaxLength(100)
            
        # Bind events
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
        bible_row_sizer.Add(self.bible_toggle_btn, 0, 0)
        bible_row_sizer.Add(self.prev_verse_btn, 0, wx.RIGHT, 5)
        bible_row_sizer.Add(self.next_verse_btn, 0, wx.LEFT, 5)
        bible_sizer.Add(bible_row_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Bible version checkboxes
        self.version_label = wx.StaticText(panel, label="Select versions to display:")
        self.version_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.version_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        bible_sizer.Add(self.version_label, 0, wx.LEFT | wx.RIGHT, 10)
        
        # Version checkboxes in a horizontal layout
        version_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.bible_versions = {
            'cuv': '和合本',
            'kjv': 'KJV',
            'nas': 'NAS', 
            'niv': 'NIV',
            'dby': 'Darby'
        }
        
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
            version_sizer.Add(checkbox, 0, wx.RIGHT, 15)
        
        bible_sizer.Add(version_sizer, 0, wx.ALL, 10)
        
        # Font size controls
        self.font_size_label = wx.StaticText(panel, label="Font sizes:")
        self.font_size_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.font_size_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        bible_sizer.Add(self.font_size_label, 0, wx.LEFT | wx.RIGHT, 10)
        
        # Font size controls in horizontal layout
        font_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Chinese font size
        self.chinese_label = wx.StaticText(panel, label="Chinese:")
        self.chinese_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.chinese_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.chinese_font_choice = wx.Choice(panel, choices=['18', '20', '22', '24', '26', '28', '30', '32', '36', '40'])
        self.chinese_font_choice.SetSelection(3)  # Default to 24 (index 3)
        self.chinese_font_choice.SetSize((80, 30))  # Increased width from 60 to 80
        self.chinese_font_choice.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.chinese_font_choice.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.chinese_font_choice.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        self.chinese_font_choice.Refresh()  # Force refresh to apply colors
        
        # English font size  
        self.english_label = wx.StaticText(panel, label="English:")
        self.english_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.english_label.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.english_font_choice = wx.Choice(panel, choices=['16', '18', '20', '22', '24', '26', '28', '30', '32', '36'])
        self.english_font_choice.SetSelection(3)  # Default to 22 (index 3)
        self.english_font_choice.SetSize((80, 30))  # Increased width from 60 to 80
        self.english_font_choice.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.english_font_choice.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.english_font_choice.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        self.english_font_choice.Refresh()  # Force refresh to apply colors
        
        font_size_sizer.Add(self.chinese_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        font_size_sizer.Add(self.chinese_font_choice, 0, wx.RIGHT, 20)
        font_size_sizer.Add(self.english_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        font_size_sizer.Add(self.english_font_choice, 0, 0)
        
        bible_sizer.Add(font_size_sizer, 0, wx.ALL, 10)
        
        # Status text for bible input
        self.bible_status = wx.StaticText(panel, label="Enter book name and verse - 1 version selected: 和合本")
        self.bible_status.SetForegroundColour(wx.Colour(127, 140, 141))
        bible_sizer.Add(self.bible_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Bible preview area
        self.bible_preview_panel = wx.Panel(panel)
        self.bible_preview_panel.SetBackgroundColour(wx.Colour(250, 250, 250))  # Very light gray
        # Always visible - no Hide() call
        
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
        
        # No close button - always visible
        
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
        
        # Set focus to URL input
        self.url_ctrl.SetFocus()
        
        # Force color updates after layout (macOS compatibility)
        wx.CallAfter(self.force_color_updates)
        
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
                
            # Fix all labels with explicit black text
            if hasattr(self, 'version_label'):
                self.version_label.SetForegroundColour(text_color)
                self.version_label.Refresh()
            if hasattr(self, 'font_size_label'):
                self.font_size_label.SetForegroundColour(text_color)
                self.font_size_label.Refresh()
            if hasattr(self, 'chinese_label'):
                self.chinese_label.SetForegroundColour(text_color)
                self.chinese_label.Refresh()
            if hasattr(self, 'english_label'):
                self.english_label.SetForegroundColour(text_color)
                self.english_label.Refresh()
                
            # Fix checkboxes - explicitly black text
            for checkbox in self.version_checkboxes.values():
                checkbox.SetForegroundColour(text_color)
                checkbox.SetBackgroundColour(wx.Colour(248, 248, 248))  # Very light gray
                checkbox.Refresh()
                
            # Fix font size dropdowns - black text on white
            for choice in [self.chinese_font_choice, self.english_font_choice]:
                choice.SetForegroundColour(text_color)
                choice.SetBackgroundColour(bg_color)
                choice.Refresh()
                
            # Fix buttons - black text on light gray  
            for btn in [self.bible_clear_btn, self.bible_preview_btn, self.bible_history_btn, self.prev_chapter_btn, self.next_chapter_btn, self.prev_verse_btn, self.next_verse_btn]:
                btn.SetForegroundColour(text_color)
                btn.SetBackgroundColour(wx.Colour(240, 240, 240))  # Light gray
                btn.Refresh()
                
            # Update the whole frame and panel
            self.Refresh()
            self.Update()
            
        except Exception as e:
            print(f"Error forcing color updates: {e}")
        
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
        """Load bible books data from CSV file"""
        csv_path = os.path.join(os.getcwd(), "books.csv")
        try:
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as file:
                    for line_num, line in enumerate(file, 1):
                        line = line.strip()
                        if not line:
                            continue
                            
                        try:
                            # Parse format like: 'Genesis':[1,50],
                            # Split by : to separate book name from array
                            if ':' not in line:
                                print(f"Line {line_num}: No ':' separator found in line: {line}")
                                continue
                                
                            parts = line.split(':', 1)  # Split only on first ':'
                            if len(parts) != 2:
                                print(f"Line {line_num}: Could not split line properly: {line}")
                                continue
                                
                            # Parse book name (remove quotes and whitespace)
                            book_name = parts[0].strip().strip("'\"")
                            
                            # Parse array part (remove trailing comma and whitespace)
                            array_part = parts[1].strip().rstrip(',')
                            
                            # Parse array [book_id, chapter_count]
                            if array_part.startswith('[') and array_part.endswith(']'):
                                array_content = array_part[1:-1]  # Remove brackets
                                array_values = [x.strip() for x in array_content.split(',')]
                                
                                if len(array_values) >= 2:
                                    try:
                                        # Book ID can be integer or expression like "39+23"
                                        book_id_str = array_values[0].strip()
                                        if '+' in book_id_str or '-' in book_id_str or '*' in book_id_str or '/' in book_id_str:
                                            # Evaluate mathematical expression safely
                                            book_id = eval(book_id_str, {"__builtins__": {}}, {})
                                        else:
                                            book_id = int(book_id_str)
                                        
                                        chapter_count = int(array_values[1])
                                        self.bible_books[book_name] = [book_id, chapter_count]
                                        self.bible_book_names.append(book_name)
                                        print(f"Loaded: {book_name} -> vol{book_id:02d}, {chapter_count} chapters (ID: {book_id_str})")
                                    except (ValueError, SyntaxError, TypeError) as e:
                                        print(f"Line {line_num}: Error evaluating book ID '{array_values[0]}': {e}")
                                else:
                                    print(f"Line {line_num}: Array doesn't have enough values: {array_part}")
                            else:
                                print(f"Line {line_num}: Array format incorrect: {array_part}")
                                
                        except ValueError as e:
                            print(f"Line {line_num}: Error parsing numbers in line '{line}': {e}")
                        except Exception as e:
                            print(f"Line {line_num}: Error parsing line '{line}': {e}")
                            
                print(f"Successfully loaded {len(self.bible_books)} bible books from {csv_path}")
            else:
                print(f"Bible books file not found: {csv_path}")
        except Exception as e:
            print(f"Error loading bible books data: {e}")
            
    # Remove autocomplete popup - not needed for ID-based lookup
        
    def on_slides_text_change(self, event):
        """Handle text changes in slides input - check for hymn ID match"""
        text = self.slides_ctrl.GetValue().strip()
        
        if text:
            # Check if it's a hymn ID (exact match - case insensitive)
            text_upper = text.upper()
            if text_upper in self.hymns_data:
                slides_id = self.hymns_data[text_upper]
                # Find original case for display
                original_case = next((hid for hid in self.hymns_ids if hid.upper() == text_upper), text)
                self.slides_status.SetLabel(f"Hymn ID {original_case} found - will use: {slides_id[:20]}...")
                self.slides_status.SetForegroundColour(wx.Colour(39, 174, 96))
            # Check if it might be a direct slides ID or URL
            elif self.is_slides_id_format(text):
                self.slides_status.SetLabel("Google Slides ID/URL detected")
                self.slides_status.SetForegroundColour(wx.Colour(52, 152, 219))
            # Check if it's a partial hymn ID match (case insensitive)
            elif self.is_hymn_id_format(text):
                partial_matches = [hid for hid in self.hymns_ids if hid.upper().startswith(text_upper)]
                if partial_matches:
                    self.slides_status.SetLabel(f"Partial match - {len(partial_matches)} hymn(s) start with {text}")
                    self.slides_status.SetForegroundColour(wx.Colour(243, 156, 18))
                else:
                    self.slides_status.SetLabel(f"No hymn found with ID {text}")
                    self.slides_status.SetForegroundColour(wx.Colour(231, 76, 60))
            else:
                self.slides_status.SetLabel("Enter hymn ID or Google Slides ID/URL")
                self.slides_status.SetForegroundColour(wx.Colour(127, 140, 141))
        else:
            self.slides_status.SetLabel("Enter hymn ID (123, A123, C456) or Google Slides ID/URL")
            self.slides_status.SetForegroundColour(wx.Colour(127, 140, 141))
            
    def is_hymn_id_format(self, text):
        """Check if text looks like a hymn ID format (numeric, or A/C + numeric) - case insensitive"""
        if text.isdigit():
            return True
        if len(text) >= 2 and text[0].upper() in ['A', 'C'] and text[1:].isdigit():
            return True
        return False
        
    def is_slides_id_format(self, text):
        """Check if text looks like a Google Slides ID or URL"""
        # Check for Google Slides URL patterns
        if 'docs.google.com/presentation' in text:
            return True
        # Check for ID pattern (alphanumeric, typically 44 characters)
        if re.match(r'^[a-zA-Z0-9_-]{20,}$', text):
            return True
        return False
        
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
        """Handle special keys for bible autocomplete navigation"""
        keycode = event.GetKeyCode()
        
        # Only handle Escape key to close popup
        if keycode == wx.WXK_ESCAPE:
            if (hasattr(self, 'bible_popup') and 
                self.bible_popup and 
                self.bible_popup.IsShown()):
                self.hide_bible_popup()
                return
                    
        # Let all other keys process normally
        event.Skip()
    
             
    
    def show_bible_popup(self, matches):
        """Show autocomplete popup for bible books using a simple list"""
        try:
            # Hide any existing popup first
            self.hide_bible_popup()
            
            # Don't show popup if no matches
            if not matches:
                return
            
            # Create a simple popup frame
            self.bible_popup = wx.Frame(
                self, 
                style=wx.FRAME_NO_TASKBAR | wx.BORDER_SIMPLE | wx.STAY_ON_TOP
            )
            
            # Calculate popup size
            popup_height = min(200, len(matches) * 25 + 10)
            popup_width = 300
            self.bible_popup.SetSize((popup_width, popup_height))
            
            # Create list control
            self.bible_list = wx.ListCtrl(
                self.bible_popup, 
                style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER
            )
            self.bible_list.AppendColumn("Book", width=280)
            
            # Add matches to list
            for i, book_name in enumerate(matches):
                self.bible_list.InsertItem(i, book_name)
            
            # Bind single-click selection
            self.bible_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_bible_list_select)
            self.bible_list.Bind(wx.EVT_LEFT_UP, self.on_bible_list_click)
            
            # Layout the list in the frame
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.bible_list, 1, wx.EXPAND)
            self.bible_popup.SetSizer(sizer)
            
            # Position popup below text control
            text_pos = self.bible_ctrl.GetScreenPosition()
            text_size = self.bible_ctrl.GetSize()
            popup_x = text_pos.x
            popup_y = text_pos.y + text_size.height + 2
            
            # Make sure popup doesn't go off screen
            screen = wx.Display.GetFromPoint(text_pos)
            if screen != wx.NOT_FOUND:
                screen_rect = wx.Display(screen).GetGeometry()
                if popup_x + popup_width > screen_rect.width:
                    popup_x = screen_rect.width - popup_width - 10
                if popup_y + popup_height > screen_rect.height:
                    popup_y = text_pos.y - popup_height - 2
            
            self.bible_popup.SetPosition((popup_x, popup_y))
            
            # Show popup
            self.bible_popup.Show(True)
            
        except Exception as e:
            print(f"Error showing bible popup: {e}")
            self.hide_bible_popup()
            
            
    def on_bible_list_click(self, event):
        """Handle single click on bible list item"""
        try:
            if hasattr(self, 'bible_list') and self.bible_list:
                selected = self.bible_list.GetFirstSelected()
                if selected >= 0:
                    book_name = self.bible_list.GetItemText(selected)
                    self.select_bible_book(book_name)
        except Exception as e:
            print(f"Error handling bible list click: {e}")
            
    def on_bible_list_select(self, event):
        """Handle double-click or activation on bible list item"""
        try:
            if hasattr(self, 'bible_list') and self.bible_list:
                selected = self.bible_list.GetFirstSelected()
                if selected >= 0:
                    book_name = self.bible_list.GetItemText(selected)
                    self.select_bible_book(book_name)
        except Exception as e:
            print(f"Error handling bible list selection: {e}")
        
    def hide_bible_popup(self):
        """Hide the autocomplete popup"""
        try:
            if hasattr(self, 'bible_popup') and self.bible_popup:
                self.bible_popup.Hide()
                self.bible_popup.Destroy()
                self.bible_popup = None
            if hasattr(self, 'bible_list'):
                self.bible_list = None
        except Exception as e:
            print(f"Error hiding bible popup: {e}")
            if hasattr(self, 'bible_popup'):
                self.bible_popup = None
            
    def select_bible_book(self, book_name):
        """Select a bible book from autocomplete"""
        try:
            # Check if there's already verse info in the text
            current_text = self.bible_ctrl.GetValue().strip()
            
            # If there's already a space and more text, preserve verse info
            if ' ' in current_text:
                parts = current_text.split(' ', 1)
                if len(parts) > 1 and parts[1].strip():
                    # User has already started typing verse info, preserve it
                    verse_part = parts[1].strip()
                    new_text = f"{book_name} {verse_part}"
                else:
                    new_text = f"{book_name} "
            else:
                new_text = f"{book_name} "
                
            # Hide popup first
            self.hide_bible_popup()
            
            # Update text control
            self.bible_ctrl.SetValue(new_text)
            self.bible_ctrl.SetInsertionPointEnd()
            
            # Update status
            self.bible_status.SetLabel(f"Selected: {book_name} - Now enter chapter:verse (e.g., 3:16)")
            self.bible_status.SetForegroundColour(wx.Colour(39, 174, 96))
            
            # Return focus to text control for continued typing
            self.bible_ctrl.SetFocus()
            
            # If there's already verse info, validate it
            if ' ' in new_text and len(new_text.split(' ', 1)) > 1:
                verse_text = new_text.split(' ', 1)[1].strip()
                if verse_text:
                    self.parse_and_validate_bible_input(new_text)
                    
        except Exception as e:
            print(f"Error selecting bible book: {e}")
            self.hide_bible_popup()
        
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
            
            # Validate and adjust verse number by checking actual file content
            if book_info:
                book_id = book_info[0]
                vol_folder = f"vol{book_id:02d}"
                chapter_file = f"chap{chapter:03d}.txt"
                
                # Try to determine available versions to check verse count
                max_verses = 150  # Default fallback
                for version in ['kjv', 'nas', 'niv', 'dby', 'cuv']:
                    file_path = os.path.join("books", version, vol_folder, chapter_file)
                    if os.path.exists(file_path):
                        try:
                            encoding = 'gb2312' if version == 'cuv' else 'utf-8'
                            with open(file_path, 'r', encoding=encoding) as f:
                                verses = [line.strip() for line in f.readlines() if line.strip()]
                                max_verses = len(verses)
                                break
                        except:
                            continue
                
                # Adjust verse if it's out of range
                if verse < 1:
                    verse = 1
                elif verse > max_verses:
                    verse = max_verses
                    self.bible_status.SetLabel(f"Chapter {chapter} has {max_verses} verses - using verse {verse}")
                    self.bible_status.SetForegroundColour(wx.Colour(243, 156, 18))
            
            # Success message
            if chapter == 1 and verse == 1 and (not re.search(r'\d', text)):
                self.bible_status.SetLabel(f"✓ {book_name} 1:1 (default) - Ready to project")
            else:
                self.bible_status.SetLabel(f"✓ {book_name} {chapter}:{verse} - Ready to project")
            self.bible_status.SetForegroundColour(wx.Colour(39, 174, 96))
            
            return {
                'book': book_name,
                'chapter': chapter,
                'verse': verse,
                'book_id': book_info[0] if book_info else None
            }
            
        except Exception as e:
            self.bible_status.SetLabel(f"Invalid format - try 'Book Chapter:Verse' or 'Chapter Verse Book'")
            self.bible_status.SetForegroundColour(wx.Colour(231, 76, 60))
            return None
            
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
            self.bible_status.SetLabel("Enter book name and verse (e.g., 'John 3:16') - Select versions to display")
            
        self.bible_status.SetForegroundColour(wx.Colour(127, 140, 141))
        self.hide_bible_popup()
            
    def select_hymn_by_id(self, hymn_id):
        """Select a hymn by ID and populate the slides ID"""
        # Use original case hymn_id for display, but lookup with uppercase
        if hymn_id.upper() in self.hymns_data:
            slides_id = self.hymns_data[hymn_id.upper()]
            self.slides_ctrl.SetValue(hymn_id)  # Set original case ID
            self.slides_status.SetLabel(f"Selected hymn {hymn_id}: {slides_id[:30]}...")
            self.slides_status.SetForegroundColour(wx.Colour(39, 174, 96))
            
    def show_hymns_dropdown(self, event):
        """Show dropdown with all available hymn IDs"""
        if not self.hymns_ids:
            wx.MessageBox("No hymns data loaded. Please ensure hymns.csv exists.", 
                         "No Hymns Data", wx.OK | wx.ICON_INFORMATION)
            return
            
        # Create popup menu organized by type
        menu = wx.Menu()
        
        # Separate numeric and letter-based IDs
        numeric_ids = sorted([hid for hid in self.hymns_ids if hid.isdigit()], key=int)
        a_ids = sorted([hid for hid in self.hymns_ids if hid.startswith('A')])
        c_ids = sorted([hid for hid in self.hymns_ids if hid.startswith('C')])
        
        # Add numeric hymns
        if numeric_ids:
            numeric_menu = wx.Menu()
            for hymn_id in numeric_ids[:15]:  # Limit to first 15
                item = numeric_menu.Append(wx.ID_ANY, hymn_id)
                self.Bind(wx.EVT_MENU, lambda evt, h=hymn_id: self.select_hymn_by_id(h), item)
            if len(numeric_ids) > 15:
                numeric_menu.AppendSeparator()
                info_item = numeric_menu.Append(wx.ID_ANY, f"... and {len(numeric_ids) - 15} more")
                info_item.Enable(False)
            menu.AppendSubMenu(numeric_menu, f"Numeric IDs ({len(numeric_ids)})")
        
        # Add A-series hymns
        if a_ids:
            a_menu = wx.Menu()
            for hymn_id in a_ids[:15]:
                item = a_menu.Append(wx.ID_ANY, hymn_id)
                self.Bind(wx.EVT_MENU, lambda evt, h=hymn_id: self.select_hymn_by_id(h), item)
            if len(a_ids) > 15:
                a_menu.AppendSeparator()
                info_item = a_menu.Append(wx.ID_ANY, f"... and {len(a_ids) - 15} more")
                info_item.Enable(False)
            menu.AppendSubMenu(a_menu, f"A-Series ({len(a_ids)})")
        
        # Add C-series hymns
        if c_ids:
            c_menu = wx.Menu()
            for hymn_id in c_ids[:15]:
                item = c_menu.Append(wx.ID_ANY, hymn_id)
                self.Bind(wx.EVT_MENU, lambda evt, h=hymn_id: self.select_hymn_by_id(h), item)
            if len(c_ids) > 15:
                c_menu.AppendSeparator()
                info_item = c_menu.Append(wx.ID_ANY, f"... and {len(c_ids) - 15} more")
                info_item.Enable(False)
            menu.AppendSubMenu(c_menu, f"C-Series ({len(c_ids)})")
        
        # Show menu
        btn_pos = self.hymn_dropdown_btn.GetPosition()
        btn_size = self.hymn_dropdown_btn.GetSize()
        self.PopupMenu(menu, (btn_pos.x, btn_pos.y + btn_size.height))
        
    def update_monitor_info(self):
        """Update monitor information display"""
        try:
            monitors = get_monitors()
            if len(monitors) >= 2:
                info_text = f"✓ {len(monitors)} monitors detected - Ready for projection"
                color = wx.Colour(39, 174, 96)
            else:
                info_text = f"⚠ {len(monitors)} monitor detected - Will project on main screen"
                color = wx.Colour(243, 156, 18)
                
            self.monitor_text.SetLabel(info_text)
            self.monitor_text.SetForegroundColour(color)
            
        except Exception as e:
            self.monitor_text.SetLabel("Monitor detection failed")
            self.monitor_text.SetForegroundColour(wx.Colour(231, 76, 60))
            
    def validate_url(self, url):
        """Validate and format URL"""
        if not url:
            return False, ""
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Basic validation
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
        return url_pattern.match(url) is not None, url
        
    def validate_slides_id(self, slides_input):
        """Validate and extract Google Slides ID, return presentation URL"""
        if not slides_input:
            return False, ""
            
        slides_input = slides_input.strip()
        
        # Check if it's already a full Google Slides URL
        if 'docs.google.com/presentation' in slides_input:
            # Extract ID from various URL formats
            if '/d/' in slides_input:
                slides_id = slides_input.split('/d/')[1].split('/')[0]
            else:
                return False, ""
        else:
            # Assume it's just the ID
            slides_id = slides_input
            
        # Validate ID format (should be alphanumeric and underscores, typically 44 chars)
        if not re.match(r'^[a-zA-Z0-9_-]+$', slides_id):
            return False, ""
            
        # Create presentation URL
        presentation_url = f"https://docs.google.com/presentation/d/{slides_id}/present"
        return True, presentation_url
        
    def on_main_button_click(self, event):
        """Handle main button click - always projects/reloads content"""
        url = self.url_ctrl.GetValue().strip()
        
        if not url:
            wx.MessageBox("Please enter a URL", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        is_valid, formatted_url = self.validate_url(url)
        if not is_valid:
            wx.MessageBox("Please enter a valid URL", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Update URL display
        self.url_ctrl.SetValue(formatted_url)
        
        # Always start new projection (reload content)
        self.start_projection(formatted_url)
        
    def start_slides_projection(self, url):
        """Start projecting slides to second screen"""
        try:
            # Hide any existing web projection to avoid conflicts
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
                
            # Stop existing slides projection
            if self.slides_projection_frame:
                self.slides_projection_frame.Destroy()
                self.slides_projection_frame = None
                
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
            
            print(f"Starting slides projection to monitor: {target_monitor}")
            
            # Update status immediately
            self.status_text.SetLabel("Creating slides projection...")
            self.slides_btn.Enable(False)
            
            # Create slides projection window
            self.slides_projection_frame = ProjectionFrame(self, url, target_monitor, "slides")
            
            # Update status
            self.status_text.SetLabel("Loading slides presentation...")
            
        except Exception as e:
            print(f"Slides projection error: {e}")
            self.on_slides_projection_error(f"Failed to start slides projection: {str(e)}")
            
    def on_slides_projection_loaded(self):
        """Called when slides projection loads successfully"""
        self.is_projecting_slides = True
        self.status_text.SetLabel("✓ Slides projection active - ESC/Ctrl+Q/Ctrl+W to close, F11 to toggle fullscreen")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
        
        # Enable and configure toggle button
        self.slides_toggle_btn.Enable(True)
        self.slides_toggle_btn.SetLabel("🗕 Hide")
        self.slides_toggle_btn.SetBackgroundColour(wx.Colour(243, 156, 18))  # Orange for hide
        
        # Update button states and text
        self.slides_btn.Enable(True)
        self.update_slides_button_state()
        
    def on_slides_projection_error(self, error_msg):
        """Called when slides projection fails"""
        self.status_text.SetLabel("Slides projection failed")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))
        
        wx.MessageBox(f"Slides projection failed:\n{error_msg}", "Error", wx.OK | wx.ICON_ERROR)
        
    def on_slides_button_click(self, event):
        """Handle slides button click - always presents/reloads content"""
        slides_input = self.slides_ctrl.GetValue().strip()
        
        if not slides_input:
            wx.MessageBox("Please enter a hymn ID or Google Slides ID/URL", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # Check if it's a hymn ID first (case insensitive)
        slides_upper = slides_input.upper()
        if slides_upper in self.hymns_data:
            # It's a hymn ID, get the actual slides ID
            actual_slides_id = self.hymns_data[slides_upper]
            is_valid, presentation_url = self.validate_slides_id(actual_slides_id)
            # Find original case for display
            original_case = next((hid for hid in self.hymns_ids if hid.upper() == slides_upper), slides_input)
            display_id = original_case  # Use original case for display
        else:
            # Treat as direct slides ID/URL
            is_valid, presentation_url = self.validate_slides_id(slides_input)
            display_id = slides_input
            
        if not is_valid:
            wx.MessageBox("Please enter a valid hymn ID or Google Slides ID/URL", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Update slides display
        self.slides_ctrl.SetValue(display_id)
        
        # Always start new slides projection (reload content)
        self.start_slides_projection(presentation_url)
    
    def start_projection(self, url):
        """Start projecting to second screen"""
        try:
            # Hide any existing slides projection to avoid conflicts
            if self.is_projecting_slides and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                self.hide_slides_projection(auto_hide=True)
                
            # Stop existing projection
            if self.projection_frame:
                self.projection_frame.Destroy()
                self.projection_frame = None
                
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
            
            print(f"Starting projection to monitor: {target_monitor}")
            
            # Update status immediately
            self.status_text.SetLabel("Creating projection window...")
            self.main_btn.Enable(False)
            
            # Create projection window
            self.projection_frame = ProjectionFrame(self, url, target_monitor, "web")
            
            # Update status
            self.status_text.SetLabel("Loading webpage...")
            
        except Exception as e:
            print(f"Projection error: {e}")
            self.on_projection_error(f"Failed to start projection: {str(e)}")
            
    def on_projection_loaded(self):
        """Called when projection loads successfully"""
        self.is_projecting = True
        self.status_text.SetLabel("✓ Web projection active - ESC/Ctrl+Q/Ctrl+W to close, F11 to toggle fullscreen")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
        
        # Enable and configure toggle button
        self.url_toggle_btn.Enable(True)
        self.url_toggle_btn.SetLabel("🗕 Hide")
        self.url_toggle_btn.SetBackgroundColour(wx.Colour(243, 156, 18))  # Orange for hide
        
        # Update button states and text
        self.main_btn.Enable(True)
        self.main_btn.SetLabel("🗕 Hide Projection")
        self.main_btn.SetBackgroundColour(wx.Colour(243, 156, 18))  # Orange for hide
        self.main_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.stop_btn.Enable(True)
        
    def on_projection_error(self, error_msg):
        """Called when projection fails"""
        self.status_text.SetLabel("Projection failed")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))
        
        wx.MessageBox(f"Projection failed:\n{error_msg}", "Error", wx.OK | wx.ICON_ERROR)
        
    def update_main_button_state(self):
        """Update the main button appearance based on current state"""
        if not self.is_projecting:
            # Not projecting - show project button
            self.main_btn.SetLabel("🔗 Project Webpage")
            self.main_btn.SetBackgroundColour(wx.Colour(52, 152, 219))  # Blue
        elif self.projection_frame and self.projection_frame.is_hidden:
            # Hidden - show "show" button
            self.main_btn.SetLabel("👁 Show Webpage")
            self.main_btn.SetBackgroundColour(wx.Colour(39, 174, 96))  # Green
        else:
            # Showing - show "hide" button
            self.main_btn.SetLabel("🗕 Hide Webpage")
            self.main_btn.SetBackgroundColour(wx.Colour(243, 156, 18))  # Orange
        
        self.main_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        
    def update_slides_button_state(self):
        """Update the slides button appearance based on current state"""
        if not self.is_projecting_slides:
            # Not projecting - show present button
            self.slides_btn.SetLabel("📊 Present Slides")
            self.slides_btn.SetBackgroundColour(wx.Colour(142, 68, 173))  # Purple
        elif self.slides_projection_frame and self.slides_projection_frame.is_hidden:
            # Hidden - show "show" button
            self.slides_btn.SetLabel("👁 Show Slides")
            self.slides_btn.SetBackgroundColour(wx.Colour(39, 174, 96))  # Green
        else:
            # Showing - show "hide" button
            self.slides_btn.SetLabel("🗕 Hide Slides")
            self.slides_btn.SetBackgroundColour(wx.Colour(243, 156, 18))  # Orange
        
        self.slides_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            
    def hide_projection(self, auto_hide=False):
        """Hide the projection window"""
        self.Hide()
        self.is_hidden = True
    
    def show_projection(self):
        """Show the projection window"""
        self.Show()
        self.Raise()
        self.SetFocus()
        
        # Always go through the fullscreen process to ensure proper restoration
        wx.CallLater(200, self.ensure_complete_coverage)
        self.is_hidden = False
        
    def reload_url(self, url):
        """Reload with new URL"""
        self.url = url
        self.browser.LoadURL(url)

    def hide_slides_projection(self, auto_hide=False):
        """Hide the slides projection window"""
        if self.slides_projection_frame:
            self.slides_projection_frame.hide_projection()
            self.update_slides_button_state()
            if auto_hide:
                self.status_text.SetLabel("📱 Slides auto-hidden for webpage")
            else:
                self.status_text.SetLabel("📱 Slides hidden - desktop visible")
            
    def show_slides_projection(self):
        """Show the slides projection window"""
        if self.slides_projection_frame:
            # Hide any visible web projection first
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
                
            self.slides_projection_frame.show_projection()
            self.update_slides_button_state()
            self.status_text.SetLabel("✓ Slides projection restored")
            
    def on_stop_click(self, event):
        """Handle stop projection"""
        self.stop_projection()
        
    def stop_projection(self):
        """Stop the projection"""
        if self.projection_frame:
            self.projection_frame.Destroy()
            self.projection_frame = None
            
        self.is_projecting = False
        
        # Reset UI
        self.status_text.SetLabel("Projection stopped")
        self.status_text.SetForegroundColour(wx.Colour(127, 140, 141))
        self.url_toggle_btn.Enable(False)
        self.url_toggle_btn.SetLabel("👁 Show")
        self.url_toggle_btn.SetBackgroundColour(wx.Colour(95, 95, 95))
        
    def stop_slides_projection(self):
        """Stop the slides projection"""
        if self.slides_projection_frame:
            self.slides_projection_frame.Destroy()
            self.slides_projection_frame = None
            
        self.is_projecting_slides = False
        
        # Reset UI
        self.status_text.SetLabel("Slides projection stopped")
        self.status_text.SetForegroundColour(wx.Colour(127, 140, 141))
        self.slides_toggle_btn.Enable(False)
        self.slides_toggle_btn.SetLabel("👁 Show")
        self.slides_toggle_btn.SetBackgroundColour(wx.Colour(95, 95, 95))

    def on_bible_button_click(self, event):
        """Handle bible projection button click"""
        bible_input = self.bible_ctrl.GetValue().strip()
        
        if not bible_input:
            wx.MessageBox("Please enter a bible verse (e.g., 'John 3:16')", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        # Parse and validate input
        parsed = self.parse_and_validate_bible_input(bible_input)
        if not parsed:
            return
            
        # Start bible projection
        self.start_bible_projection(parsed)
        
    def start_bible_projection(self, bible_info, is_navigation=False):
        """Start projecting bible chapter to second screen"""
        try:
            # Hide any existing projections to avoid conflicts
            if self.is_projecting and self.projection_frame and not self.projection_frame.is_hidden:
                self.hide_projection(auto_hide=True)
            if self.is_projecting_slides and self.slides_projection_frame and not self.slides_projection_frame.is_hidden:
                self.hide_slides_projection(auto_hide=True)
                
            # Stop existing bible projection
            if self.bible_projection_frame:
                self.bible_projection_frame.Destroy()
                self.bible_projection_frame = None
                
            # Get selected bible versions from checkboxes
            selected_versions = []
            for version_key, checkbox in self.version_checkboxes.items():
                if checkbox.GetValue():
                    selected_versions.append(version_key)
            
            if not selected_versions:
                wx.MessageBox("Please select at least one Bible version to display.", "No Version Selected", wx.OK | wx.ICON_WARNING)
                return
                
            # Load chapter content and generate HTML for multiple versions
            html_content = self.generate_bible_html_multi_version(bible_info, selected_versions)
            if not html_content:
                return
                
            # Create data URL
            import base64
            html_bytes = html_content.encode('utf-8')
            html_b64 = base64.b64encode(html_bytes).decode('ascii')
            data_url = f"data:text/html;charset=utf-8;base64,{html_b64}"
            
            # Get target monitor
            monitors = get_monitors()
            target_monitor = monitors[1] if len(monitors) >= 2 else monitors[0]
            
            versions_text = ", ".join([self.bible_versions[v] for v in selected_versions])
            print(f"Starting bible projection: {bible_info['book']} {bible_info['chapter']}:{bible_info['verse']} ({versions_text})")
            
            # Store projection info for history when it loads successfully (only if not navigation)
            if not is_navigation:
                self.pending_bible_projection = {
                    'bible_info': bible_info.copy(),
                    'selected_versions': selected_versions.copy()
                }
            else:
                # For navigation, just clear any pending projection
                self.pending_bible_projection = None
            
            # Store current projection info for verse navigation
            self.current_projected_bible = {
                'bible_info': bible_info.copy(),
                'selected_versions': selected_versions.copy()
            }
            
            # Update status immediately
            self.status_text.SetLabel("Creating bible projection...")
            self.bible_btn.Enable(False)
            
            # Create bible projection window
            self.bible_projection_frame = ProjectionFrame(self, data_url, target_monitor, "bible")
            
            # Update status
            self.status_text.SetLabel(f"Loading {bible_info['book']} {bible_info['chapter']} ({versions_text})...")
            
        except Exception as e:
            print(f"Bible projection error: {e}")
            self.on_bible_projection_error(f"Failed to start bible projection: {str(e)}")
            
    def on_bible_projection_loaded(self):
        """Called when bible projection loads successfully"""
        self.is_projecting_bible = True
        self.status_text.SetLabel("✓ Bible projection active - ESC/Ctrl+Q/Ctrl+W to close, F11 to toggle fullscreen")
        self.status_text.SetForegroundColour(wx.Colour(39, 174, 96))
        
        # Enable and configure toggle button
        self.bible_toggle_btn.Enable(True)
        self.bible_toggle_btn.SetLabel("🗕 Hide")
        self.bible_toggle_btn.SetBackgroundColour(wx.Colour(243, 156, 18))  # Orange for hide
        
        # Add to history if projection info is available
        if hasattr(self, 'pending_bible_projection') and self.pending_bible_projection:
            self.add_to_bible_history(
                self.pending_bible_projection['bible_info'],
                self.pending_bible_projection['selected_versions']
            )
            # Clear pending projection info
            self.pending_bible_projection = None
        
        # Enable verse navigation buttons and update their state
        self.update_verse_navigation_buttons()
        
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
        
    def on_prev_verse_click(self, event):
        """Handle previous verse navigation"""
        if self.current_projected_bible and self.bible_projection_frame:
            bible_info = self.current_projected_bible['bible_info'].copy()
            if bible_info['verse'] > 1:
                bible_info['verse'] -= 1
                
                # Update the text control to reflect the navigation
                self.bible_ctrl.SetValue(f"{bible_info['book']} {bible_info['chapter']}:{bible_info['verse']}")
                
                # Update highlighting via JavaScript instead of reloading
                self.navigate_to_verse_via_javascript(bible_info['verse'])
                
                # Update current projection info
                self.current_projected_bible['bible_info'] = bible_info
                
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
                
                # Update highlighting via JavaScript instead of reloading
                self.navigate_to_verse_via_javascript(bible_info['verse'])
                
                # Update current projection info
                self.current_projected_bible['bible_info'] = bible_info
                
                # Update navigation button states
                self.update_verse_navigation_buttons()
                
    def navigate_to_verse_via_javascript(self, verse_number):
        """Navigate to a verse using JavaScript without reloading the page"""
        if self.bible_projection_frame and hasattr(self.bible_projection_frame, 'browser'):
            try:
                # Execute JavaScript to highlight the new verse
                javascript_code = f"highlightVerse({verse_number});"
                self.bible_projection_frame.browser.RunScript(javascript_code)
                print(f"Navigated to verse {verse_number} via JavaScript")
            except Exception as e:
                print(f"Error executing JavaScript navigation: {e}")
                # Fallback to full reload if JavaScript fails
                bible_info = self.current_projected_bible['bible_info'].copy()
                bible_info['verse'] = verse_number
                self.start_bible_projection(bible_info, is_navigation=True)
        
    def on_bible_projection_error(self, error_msg):
        """Called when bible projection fails"""
        self.status_text.SetLabel("Bible projection failed")
        self.status_text.SetForegroundColour(wx.Colour(231, 76, 60))
        
        # Clear pending projection info since projection failed
        if hasattr(self, 'pending_bible_projection'):
            self.pending_bible_projection = None
        
        # Clear current projection info and disable navigation buttons
        self.current_projected_bible = None
        self.prev_verse_btn.Enable(False)
        self.next_verse_btn.Enable(False)
        
        wx.MessageBox(f"Bible projection failed:\n{error_msg}", "Error", wx.OK | wx.ICON_ERROR)
        
    def stop_bible_projection(self):
        """Stop the bible projection"""
        if self.bible_projection_frame:
            self.bible_projection_frame.Destroy()
            self.bible_projection_frame = None
            
        self.is_projecting_bible = False
        
        # Clear current projection info and disable navigation buttons
        self.current_projected_bible = None
        self.prev_verse_btn.Enable(False)
        self.next_verse_btn.Enable(False)
        
        # Reset UI
        self.status_text.SetLabel("Bible projection stopped")
        self.status_text.SetForegroundColour(wx.Colour(127, 140, 141))
        self.bible_toggle_btn.Enable(False)
        self.bible_toggle_btn.SetLabel("👁 Show")
        self.bible_toggle_btn.SetBackgroundColour(wx.Colour(95, 95, 95))

    def generate_bible_html_multi_version(self, bible_info, selected_versions):
        """Generate HTML content for multiple bible versions displayed horizontally"""
        try:
            # Get selected font sizes
            chinese_font_size = self.chinese_font_choice.GetStringSelection()
            english_font_size = self.english_font_choice.GetStringSelection()
            
            # Load content for all selected versions
            versions_data = {}
            
            for version in selected_versions:
                # Construct file path
                book_id = bible_info['book_id']
                chapter = bible_info['chapter']
                verse_num = bible_info['verse']
                
                vol_folder = f"vol{book_id:02d}"
                chapter_file = f"chap{chapter:03d}.txt"
                file_path = os.path.join("books", version, vol_folder, chapter_file)
                
                if not os.path.exists(file_path):
                    wx.MessageBox(f"Bible text file not found: {file_path}", "Error", wx.OK | wx.ICON_ERROR)
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
                        if version == 'cuv':
                            with open(file_path, 'r', encoding='latin-1') as f:
                                verses = [line.strip() for line in f.readlines() if line.strip()]
                        else:
                            with open(file_path, 'r', encoding='gb2312') as f:
                                verses = [line.strip() for line in f.readlines() if line.strip()]
                
                if verses:
                    versions_data[version] = verses
                    
            if not versions_data:
                wx.MessageBox("No valid bible text found for selected versions.", "Error", wx.OK | wx.ICON_ERROR)
                return None
            
            # Validate verse number
            max_verses = max(len(verses) for verses in versions_data.values())
            if verse_num > max_verses:
                wx.MessageBox(f"Verse {verse_num} not found. Chapter {chapter} has at most {max_verses} verses.", 
                             "Error", wx.OK | wx.ICON_ERROR)
                return None
            
            # Define version colors and names
            version_names = {'cuv': '和合本', 'kjv': 'King James Version', 'nas': 'New American Standard', 
                           'niv': 'New International Version', 'dby': 'Darby'}
            
            version_colors = {
                'cuv': '#c0392b',    # Red
                'kjv': '#2980b9',    # Blue
                'nas': '#27ae60',    # Green  
                'niv': '#8e44ad',    # Purple
                'dby': '#e67e22'     # Orange
            }
            
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
            font-size: {english_font_size}px;
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
        .versions-info {{
            font-size: 16px;
            color: #bdc3c7;
            font-style: italic;
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
