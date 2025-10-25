"""
Main Control Panel Window

The primary control window with all projection control panels.
Phase 2: Complete UI with mock data.
"""

import wx
from ui.styles import theme
from ui.components.url_panel import URLPanel
from ui.components.slides_panel import SlidesPanel
from ui.components.bible_panel import BiblePanel
from utils import mock_data


class MainWindow(wx.Frame):
    """Main control panel window"""

    def __init__(self):
        super().__init__(
            None,
            title="Webpage Projector - Control Panel",
            size=(theme.Sizes.MAIN_WINDOW_WIDTH, theme.Sizes.MAIN_WINDOW_HEIGHT),
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        )

        self._init_ui()
        self._center_on_screen()

    def _init_ui(self):
        """Initialize UI components"""

        # Create main panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(theme.Colors.BACKGROUND)

        # Main vertical sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add title/header
        header = self._create_header(panel)
        main_sizer.Add(header, proportion=0, flag=wx.EXPAND | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Add separator
        line = wx.StaticLine(panel)
        main_sizer.Add(line, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=theme.Spacing.PADDING_MEDIUM)

        # Create scrolled window for panels (in case content is too long)
        scrolled = wx.ScrolledWindow(panel)
        scrolled.SetScrollRate(0, 20)
        scrolled.SetMinSize((theme.Sizes.MAIN_WINDOW_WIDTH - 40, -1))  # Ensure min width

        scrolled_sizer = wx.BoxSizer(wx.VERTICAL)

        # URL Panel
        self.url_panel = URLPanel(scrolled)
        scrolled_sizer.Add(
            self.url_panel,
            proportion=0,
            flag=wx.EXPAND | wx.ALL,
            border=theme.Spacing.PADDING_MEDIUM
        )

        # Google Slides Panel
        self.slides_panel = SlidesPanel(scrolled)
        scrolled_sizer.Add(
            self.slides_panel,
            proportion=0,
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            border=theme.Spacing.PADDING_MEDIUM
        )

        # Bible Panel
        self.bible_panel = BiblePanel(scrolled)
        scrolled_sizer.Add(
            self.bible_panel,
            proportion=0,
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            border=theme.Spacing.PADDING_MEDIUM
        )

        scrolled.SetSizer(scrolled_sizer)
        main_sizer.Add(scrolled, proportion=1, flag=wx.EXPAND)

        # Status bar
        self._create_status_bar()

        panel.SetSizer(main_sizer)
        panel.Layout()  # Force layout calculation

        # Fit scrolled window after panel is laid out
        scrolled.FitInside()

        # Set app icon (optional, using default for now)
        self._setup_menu_bar()

    def _create_header(self, parent):
        """Create header section"""
        header_panel = wx.Panel(parent)
        header_panel.SetBackgroundColour(theme.Colors.PRIMARY)

        header_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(header_panel, label="Webpage Projector")
        title.SetFont(theme.Fonts.get_header_font(18))
        title.SetForegroundColour(wx.WHITE)
        header_sizer.Add(title, proportion=0, flag=wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Subtitle
        subtitle = wx.StaticText(
            header_panel,
            label="Control panel for worship service presentations"
        )
        subtitle.SetFont(theme.Fonts.get_default_font(10))
        subtitle.SetForegroundColour(wx.Colour(220, 230, 240))
        header_sizer.Add(
            subtitle,
            proportion=0,
            flag=wx.LEFT | wx.RIGHT | wx.BOTTOM,
            border=theme.Spacing.PADDING_MEDIUM
        )

        header_panel.SetSizer(header_sizer)
        return header_panel

    def _create_status_bar(self):
        """Create status bar with display info"""
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-2, -1])

        # Phase 2: Show mock display info
        self._update_status("Ready to project")
        self._update_display_info()

    def _update_status(self, message):
        """Update status bar message"""
        self.status_bar.SetStatusText(message, 0)

    def _update_display_info(self):
        """Update display information in status bar"""
        # Phase 2: Use mock display data
        display_count = len(mock_data.MOCK_DISPLAYS)
        display_text = f"{display_count} display{'s' if display_count > 1 else ''} detected"

        if display_count >= 2:
            display_text += " - Ready for projection"

        self.status_bar.SetStatusText(display_text, 1)

    def _setup_menu_bar(self):
        """Create menu bar"""
        menubar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        quit_item = file_menu.Append(wx.ID_EXIT, "&Quit\tCtrl+Q", "Quit application")
        self.Bind(wx.EVT_MENU, self._on_quit, quit_item)

        # View menu
        view_menu = wx.Menu()
        displays_item = view_menu.Append(wx.ID_ANY, "Display &Info", "Show display information")
        self.Bind(wx.EVT_MENU, self._on_show_displays, displays_item)

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About Webpage Projector")
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

        menubar.Append(file_menu, "&File")
        menubar.Append(view_menu, "&View")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

    def _center_on_screen(self):
        """Center window on screen"""
        self.Centre()

    def _on_quit(self, event):
        """Handle quit menu item"""
        self.Close()

    def _on_show_displays(self, event):
        """Show display information dialog"""
        display_info = "Detected Displays:\n\n"
        for i, display in enumerate(mock_data.MOCK_DISPLAYS):
            primary = " (Primary)" if display["primary"] else ""
            display_info += f"Display {i + 1}{primary}\n"
            display_info += f"  Name: {display['name']}\n"
            display_info += f"  Resolution: {display['resolution']}\n"
            display_info += f"  Position: {display['position']}\n\n"

        display_info += "\nNote: Using mock data for Phase 2.\nReal display detection in Phase 4."

        theme.show_info_dialog(self, "Display Information", display_info)

    def _on_about(self, event):
        """Show about dialog"""
        about_text = (
            "Webpage Projector v1.0.0\n\n"
            "A desktop application for worship service presentations.\n\n"
            "Features:\n"
            "• Google Slides projection\n"
            "• Multi-version Bible verse display\n"
            "• Web URL projection\n"
            "• Multi-monitor support\n\n"
            "Phase 2: UI Design Validation\n"
            "Currently showing control panel with mock data.\n\n"
            "Built with Python 3.12 and wxPython 4.2"
        )

        theme.show_info_dialog(self, "About Webpage Projector", about_text)


class WebpageProjectorApp(wx.App):
    """Main application class"""

    def OnInit(self):
        """Initialize application"""
        self.main_window = MainWindow()
        self.main_window.Show()
        return True


def main():
    """Application entry point"""
    app = WebpageProjectorApp()
    app.MainLoop()


if __name__ == "__main__":
    main()