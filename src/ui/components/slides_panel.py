"""
Google Slides Projection Panel Component

Allows users to input hymn IDs or Google Slides URLs.
Phase 2: UI only with mock hymn data.
"""

import wx
from ui.styles import theme
from utils import mock_data


class SlidesPanel(wx.Panel):
    """Google Slides projection panel for control window"""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetMinSize((700, -1))  # Minimum width for proper layout
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components"""

        # Create static box sizer
        box_sizer = theme.create_static_box(self, "Google Slides Presentation")

        # Input field with hymn button
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)

        input_label = theme.create_label(self, "Hymn/Slides ID:")
        input_sizer.Add(input_label, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.slides_input = theme.create_text_input(self)
        self.slides_input.SetHint("Enter hymn ID (A01, C002) or Google Slides URL")
        input_sizer.Add(self.slides_input, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        # Hymn dropdown button
        self.hymn_btn = theme.create_button(
            self,
            f"{theme.Icons.HYMN}",
            size=(theme.Sizes.BUTTON_WIDTH_SMALL, theme.Sizes.BUTTON_HEIGHT)
        )
        self.hymn_btn.SetToolTip("Browse hymns")
        self.hymn_btn.Bind(wx.EVT_BUTTON, self._on_hymn_browse)
        input_sizer.Add(self.hymn_btn, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)

        box_sizer.Add(input_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.present_btn = theme.create_button(
            self,
            "Present",
            size=(theme.Sizes.BUTTON_WIDTH_MEDIUM, theme.Sizes.BUTTON_HEIGHT)
        )
        self.present_btn.SetBackgroundColour(theme.Colors.PRIMARY)
        self.present_btn.SetForegroundColour(wx.WHITE)
        self.present_btn.Bind(wx.EVT_BUTTON, self._on_present)

        self.hide_btn = theme.create_button(
            self,
            f"{theme.Icons.HIDE} Hide",
            size=(theme.Sizes.BUTTON_WIDTH_MEDIUM, theme.Sizes.BUTTON_HEIGHT)
        )
        self.hide_btn.Bind(wx.EVT_BUTTON, self._on_hide)

        button_sizer.Add(self.present_btn, proportion=0, flag=wx.RIGHT, border=theme.Spacing.PADDING_SMALL)
        button_sizer.Add(self.hide_btn, proportion=0)

        box_sizer.Add(button_sizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Status text
        self.status_text = wx.StaticText(
            self,
            label="Enter hymn ID or Google Slides URL"
        )
        self.status_text.SetFont(theme.Fonts.get_default_font(9))
        self.status_text.SetForegroundColour(theme.Colors.TEXT_LIGHT)
        box_sizer.Add(self.status_text, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=theme.Spacing.PADDING_MEDIUM)

        # Error message label (hidden by default)
        self.error_label = wx.StaticText(self, label="")
        self.error_label.SetForegroundColour(theme.Colors.ERROR)
        self.error_label.SetFont(theme.Fonts.get_default_font(9))
        self.error_label.Hide()
        box_sizer.Add(self.error_label, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=theme.Spacing.PADDING_MEDIUM)

        self.SetSizer(box_sizer)

    def _on_hymn_browse(self, event):
        """Handle hymn browse button click - show dropdown menu"""
        # Create popup menu with hymn list
        menu = wx.Menu()

        for hymn_id, hymn_info in sorted(mock_data.MOCK_HYMNS.items()):
            item = menu.Append(wx.ID_ANY, f"{hymn_id} - {hymn_info['name']}")
            self.Bind(wx.EVT_MENU, lambda evt, hid=hymn_id: self._on_hymn_selected(hid), item)

        # Show menu at button position
        self.PopupMenu(menu, self.hymn_btn.GetPosition())
        menu.Destroy()

    def _on_hymn_selected(self, hymn_id):
        """Handle hymn selection from dropdown"""
        self.slides_input.SetValue(hymn_id)
        self.clear_error()

        # Update status text
        hymn_info = mock_data.MOCK_HYMNS.get(hymn_id)
        if hymn_info:
            self.status_text.SetLabel(f"Selected: {hymn_info['name']}")

    def _on_present(self, event):
        """Handle Present button click"""
        input_value = self.slides_input.GetValue().strip()

        if not input_value:
            self.show_error("Please enter a hymn ID or Slides URL")
            return

        # Phase 2: Check if it's a known mock hymn
        hymn_id = input_value.upper()
        if hymn_id in mock_data.MOCK_HYMNS:
            hymn_info = mock_data.MOCK_HYMNS[hymn_id]
            self.status_text.SetLabel(f"Ready to project: {hymn_info['name']}")
            self.clear_error()
        else:
            self.status_text.SetLabel("Ready to project Slides")
            self.clear_error()

        # Phase 2: Show placeholder
        theme.show_not_implemented(self)

    def _on_hide(self, event):
        """Handle Hide button click"""
        # Phase 2: Show placeholder
        theme.show_not_implemented(self)

    def get_input(self):
        """Get current input value"""
        return self.slides_input.GetValue().strip()

    def set_input(self, value):
        """Set input value"""
        self.slides_input.SetValue(value)

    def clear_input(self):
        """Clear input"""
        self.slides_input.Clear()
        self.status_text.SetLabel("Enter hymn ID or Google Slides URL")
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