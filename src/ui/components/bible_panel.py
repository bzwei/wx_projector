"""
Bible Verses Panel Component

Allows users to select and project Bible verses with multiple versions.
Phase 2: UI only with mock book data and version checkboxes.
"""

import wx
from ui.styles import theme
from utils import mock_data


class BiblePanel(wx.Panel):
    """Bible verses panel for control window"""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetMinSize((700, -1))  # Minimum width for proper layout
        self.version_checkboxes = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components"""

        # Create static box sizer
        box_sizer = theme.create_static_box(self, "Bible Verses")

        # Book selection row
        book_sizer = wx.BoxSizer(wx.HORIZONTAL)

        book_label = theme.create_label(self, "Book:")
        book_sizer.Add(book_label, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.book_combo = wx.ComboBox(
            self,
            choices=mock_data.MOCK_BOOKS,
            style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
        )
        self.book_combo.SetFont(theme.Fonts.get_default_font())
        self.book_combo.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        self.book_combo.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
        self.book_combo.SetHint("Select or type book name")
        self.book_combo.AutoComplete(mock_data.MOCK_BOOKS)
        book_sizer.Add(self.book_combo, proportion=1, flag=wx.EXPAND)

        box_sizer.Add(book_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Chapter+Verse input row
        verse_sizer = wx.BoxSizer(wx.HORIZONTAL)

        verse_label = theme.create_label(self, "Chapter:Verse:")
        verse_sizer.Add(verse_label, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.verse_input = theme.create_text_input(self)
        self.verse_input.SetHint("e.g., 3:16 or 3:16-17 or 13")
        verse_sizer.Add(self.verse_input, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        # Action buttons (inline with verse input)
        self.clear_btn = theme.create_button(
            self,
            f"{theme.Icons.CLEAR}",
            size=(theme.Sizes.BUTTON_WIDTH_SMALL, theme.Sizes.BUTTON_HEIGHT)
        )
        self.clear_btn.SetToolTip("Clear input")
        self.clear_btn.Bind(wx.EVT_BUTTON, self._on_clear)
        verse_sizer.Add(self.clear_btn, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.preview_btn = theme.create_button(
            self,
            f"{theme.Icons.PREVIEW}",
            size=(theme.Sizes.BUTTON_WIDTH_SMALL, theme.Sizes.BUTTON_HEIGHT)
        )
        self.preview_btn.SetToolTip("Load chapter preview")
        self.preview_btn.Bind(wx.EVT_BUTTON, self._on_preview)
        verse_sizer.Add(self.preview_btn, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.history_btn = theme.create_button(
            self,
            f"{theme.Icons.HISTORY}",
            size=(theme.Sizes.BUTTON_WIDTH_SMALL, theme.Sizes.BUTTON_HEIGHT)
        )
        self.history_btn.SetToolTip("Show history")
        self.history_btn.Bind(wx.EVT_BUTTON, self._on_history)
        verse_sizer.Add(self.history_btn, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)

        box_sizer.Add(verse_sizer, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=theme.Spacing.PADDING_MEDIUM)

        # Main action buttons
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.project_btn = theme.create_button(
            self,
            "Project",
            size=(theme.Sizes.BUTTON_WIDTH_MEDIUM, theme.Sizes.BUTTON_HEIGHT)
        )
        self.project_btn.SetBackgroundColour(theme.Colors.PRIMARY)
        self.project_btn.SetForegroundColour(wx.WHITE)
        self.project_btn.Bind(wx.EVT_BUTTON, self._on_project)
        action_sizer.Add(self.project_btn, proportion=0, flag=wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.prev_btn = theme.create_button(
            self,
            f"{theme.Icons.PREV}",
            size=(theme.Sizes.BUTTON_WIDTH_SMALL, theme.Sizes.BUTTON_HEIGHT)
        )
        self.prev_btn.SetToolTip("Previous verse")
        self.prev_btn.Bind(wx.EVT_BUTTON, self._on_prev_verse)
        action_sizer.Add(self.prev_btn, proportion=0, flag=wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.next_btn = theme.create_button(
            self,
            f"{theme.Icons.NEXT}",
            size=(theme.Sizes.BUTTON_WIDTH_SMALL, theme.Sizes.BUTTON_HEIGHT)
        )
        self.next_btn.SetToolTip("Next verse")
        self.next_btn.Bind(wx.EVT_BUTTON, self._on_next_verse)
        action_sizer.Add(self.next_btn, proportion=0)

        box_sizer.Add(action_sizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Version selection
        version_label = theme.create_label(self, "Versions:", bold=True)
        box_sizer.Add(version_label, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=theme.Spacing.PADDING_MEDIUM)

        version_sizer = wx.BoxSizer(wx.HORIZONTAL)

        for version_code in mock_data.BIBLE_VERSION_CODES:
            version_name = mock_data.BIBLE_VERSIONS[version_code]
            checkbox = theme.create_checkbox(self, version_name)

            # Default: CUV checked
            if version_code == "cuv":
                checkbox.SetValue(True)

            self.version_checkboxes[version_code] = checkbox
            version_sizer.Add(checkbox, proportion=0, flag=wx.RIGHT, border=theme.Spacing.PADDING_MEDIUM)

        box_sizer.Add(version_sizer, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=theme.Spacing.PADDING_MEDIUM)

        # Font size controls
        font_label = theme.create_label(self, "Font Size:", bold=True)
        box_sizer.Add(font_label, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=theme.Spacing.PADDING_MEDIUM)

        font_sizer = wx.BoxSizer(wx.HORIZONTAL)

        chinese_label = theme.create_label(self, "Chinese:")
        font_sizer.Add(chinese_label, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.chinese_size = wx.SpinCtrl(self, value="24", min=16, max=40, size=(70, theme.Sizes.INPUT_HEIGHT))
        self.chinese_size.SetForegroundColour(wx.Colour(0, 0, 0))
        self.chinese_size.SetBackgroundColour(wx.Colour(255, 255, 255))
        font_sizer.Add(self.chinese_size, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_LARGE)

        english_label = theme.create_label(self, "English:")
        font_sizer.Add(english_label, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=theme.Spacing.PADDING_SMALL)

        self.english_size = wx.SpinCtrl(self, value="22", min=16, max=40, size=(70, theme.Sizes.INPUT_HEIGHT))
        self.english_size.SetForegroundColour(wx.Colour(0, 0, 0))
        self.english_size.SetBackgroundColour(wx.Colour(255, 255, 255))
        font_sizer.Add(self.english_size, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)

        box_sizer.Add(font_sizer, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=theme.Spacing.PADDING_MEDIUM)

        # Chapter preview placeholder (will be implemented in Phase 3)
        preview_label = theme.create_label(self, "Chapter Preview:", bold=True)
        box_sizer.Add(preview_label, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=theme.Spacing.PADDING_MEDIUM)

        self.preview_placeholder = wx.StaticText(
            self,
            label="Chapter preview will appear here (Phase 3)\nClick 👁 to load chapter preview"
        )
        self.preview_placeholder.SetFont(theme.Fonts.get_default_font(9))
        self.preview_placeholder.SetForegroundColour(theme.Colors.TEXT_LIGHT)

        preview_box = wx.StaticBox(self, label="")
        preview_box_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)
        preview_box_sizer.Add(
            self.preview_placeholder,
            proportion=1,
            flag=wx.EXPAND | wx.ALL,
            border=theme.Spacing.PADDING_MEDIUM
        )
        preview_box_sizer.SetMinSize((-1, theme.Sizes.CHAPTER_PREVIEW_HEIGHT))

        box_sizer.Add(preview_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=theme.Spacing.PADDING_MEDIUM)

        # Error message label (hidden by default)
        self.error_label = wx.StaticText(self, label="")
        self.error_label.SetForegroundColour(theme.Colors.ERROR)
        self.error_label.SetFont(theme.Fonts.get_default_font(9))
        self.error_label.Hide()
        box_sizer.Add(self.error_label, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=theme.Spacing.PADDING_MEDIUM)

        self.SetSizer(box_sizer)

    def _on_clear(self, event):
        """Handle Clear button click"""
        self.book_combo.SetValue("")
        self.verse_input.Clear()
        self.clear_error()

    def _on_preview(self, event):
        """Handle Preview button click"""
        # Phase 2: Show placeholder
        theme.show_info_dialog(
            self,
            "Chapter Preview",
            "Chapter preview will be implemented in Phase 3.\n\nThis will show all verses in the selected chapter\nfor easy verse selection."
        )

    def _on_history(self, event):
        """Handle History button click"""
        # Phase 2: Show mock history
        history_text = "Recent Projections:\n\n"
        for entry in mock_data.MOCK_HISTORY:
            versions_str = ", ".join(entry["versions"])
            history_text += f"• {entry['ref']} ({versions_str}) - {entry['timestamp']}\n"

        theme.show_info_dialog(self, "Projection History", history_text)

    def _on_project(self, event):
        """Handle Project button click"""
        book = self.book_combo.GetValue().strip()
        verse_ref = self.verse_input.GetValue().strip()

        if not book:
            self.show_error("Please select a book")
            return

        if not verse_ref:
            self.show_error("Please enter chapter and verse (e.g., 3:16)")
            return

        # Get selected versions
        selected_versions = self.get_selected_versions()
        if not selected_versions:
            self.show_error("Please select at least one version")
            return

        self.clear_error()

        # Phase 2: Show placeholder
        versions_str = ", ".join([mock_data.BIBLE_VERSIONS[v] for v in selected_versions])
        theme.show_info_dialog(
            self,
            "Ready to Project",
            f"Book: {book}\nReference: {verse_ref}\nVersions: {versions_str}\n\nProjection will be implemented in Phase 3."
        )

    def _on_prev_verse(self, event):
        """Handle Previous Verse button click"""
        theme.show_not_implemented(self)

    def _on_next_verse(self, event):
        """Handle Next Verse button click"""
        theme.show_not_implemented(self)

    def get_book(self):
        """Get selected book name"""
        return self.book_combo.GetValue().strip()

    def set_book(self, book):
        """Set selected book"""
        self.book_combo.SetValue(book)

    def get_verse_input(self):
        """Get chapter+verse input value"""
        return self.verse_input.GetValue().strip()

    def set_verse_input(self, value):
        """Set chapter+verse input value"""
        self.verse_input.SetValue(value)

    def get_selected_versions(self):
        """Get list of selected Bible versions"""
        selected = []
        for version_code, checkbox in self.version_checkboxes.items():
            if checkbox.GetValue():
                selected.append(version_code)
        return selected

    def set_selected_versions(self, versions):
        """Set selected Bible versions"""
        for version_code, checkbox in self.version_checkboxes.items():
            checkbox.SetValue(version_code in versions)

    def get_font_sizes(self):
        """Get current font size configuration"""
        return {
            "chinese": self.chinese_size.GetValue(),
            "english": self.english_size.GetValue()
        }

    def set_font_sizes(self, chinese, english):
        """Set font size configuration"""
        self.chinese_size.SetValue(chinese)
        self.english_size.SetValue(english)

    def show_error(self, message):
        """Show inline error message"""
        self.error_label.SetLabel(message)
        self.error_label.Show()
        self.Layout()

    def clear_error(self):
        """Clear error message"""
        self.error_label.Hide()
        self.Layout()