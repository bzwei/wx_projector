"""
URL Projection Panel Component

Allows users to input and project web URLs.
Phase 2: UI only with mock functionality.
"""

import wx
from ui.styles import theme


class URLPanel(wx.Panel):
    """URL projection panel for control window"""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetMinSize((700, -1))  # Minimum width for proper layout
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components"""

        # Create static box sizer
        box_sizer = theme.create_static_box(self, "URL Projection")

        # URL input field with label
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)

        url_label = theme.create_label(self, "URL:")
        input_sizer.Add(url_label, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.url_input = theme.create_text_input(self)
        self.url_input.SetHint("Enter URL (e.g., google.com, youtube.com, localhost:3000)")
        input_sizer.Add(self.url_input, proportion=1, flag=wx.EXPAND)

        box_sizer.Add(input_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.project_btn = theme.create_button(
            self,
            "Project",
            size=(theme.Sizes.BUTTON_WIDTH_MEDIUM, theme.Sizes.BUTTON_HEIGHT)
        )
        self.project_btn.SetBackgroundColour(theme.Colors.PRIMARY)
        self.project_btn.SetForegroundColour(wx.WHITE)
        self.project_btn.Bind(wx.EVT_BUTTON, self._on_project)

        self.hide_btn = theme.create_button(
            self,
            f"{theme.Icons.HIDE} Hide",
            size=(theme.Sizes.BUTTON_WIDTH_MEDIUM, theme.Sizes.BUTTON_HEIGHT)
        )
        self.hide_btn.Bind(wx.EVT_BUTTON, self._on_hide)

        button_sizer.Add(self.project_btn, proportion=0, flag=wx.RIGHT, border=theme.Spacing.PADDING_SMALL)
        button_sizer.Add(self.hide_btn, proportion=0)

        box_sizer.Add(button_sizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Helper text
        helper_text = wx.StaticText(
            self,
            label="Examples: google.com, youtube.com/watch?v=..., localhost:3000"
        )
        helper_text.SetFont(theme.Fonts.get_default_font(9))
        helper_text.SetForegroundColour(theme.Colors.TEXT_LIGHT)
        box_sizer.Add(helper_text, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=theme.Spacing.PADDING_MEDIUM)

        # Error message label (hidden by default)
        self.error_label = wx.StaticText(self, label="")
        self.error_label.SetForegroundColour(theme.Colors.ERROR)
        self.error_label.SetFont(theme.Fonts.get_default_font(9))
        self.error_label.Hide()
        box_sizer.Add(self.error_label, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=theme.Spacing.PADDING_MEDIUM)

        self.SetSizer(box_sizer)

    def _on_project(self, event):
        """Handle Project button click"""
        url = self.url_input.GetValue().strip()

        if not url:
            self.show_error("Please enter a URL")
            return

        # Phase 2: Show placeholder
        self.clear_error()
        theme.show_not_implemented(self)

    def _on_hide(self, event):
        """Handle Hide button click"""
        # Phase 2: Show placeholder
        theme.show_not_implemented(self)

    def get_url(self):
        """Get current URL input value"""
        return self.url_input.GetValue().strip()

    def set_url(self, url):
        """Set URL input value"""
        self.url_input.SetValue(url)

    def clear_url(self):
        """Clear URL input"""
        self.url_input.Clear()
        self.clear_error()

    def show_error(self, message):
        """Show inline error message"""
        self.error_label.SetLabel(message)
        self.error_label.Show()
        self.Layout()

    def clear_error(self):
        """Clear error message"""
        self.error_label.Hide()
        self.Layout()