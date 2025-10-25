"""
UI Theme and Styling Constants

Centralized styling configuration for consistent UI appearance.
"""

import wx

# Color Palette
class Colors:
    """Application color scheme"""

    # Primary colors
    PRIMARY = wx.Colour(41, 128, 185)  # Blue
    PRIMARY_DARK = wx.Colour(31, 97, 141)
    PRIMARY_LIGHT = wx.Colour(93, 173, 226)

    # Status colors
    SUCCESS = wx.Colour(39, 174, 96)  # Green
    ERROR = wx.Colour(231, 76, 60)  # Red
    WARNING = wx.Colour(243, 156, 18)  # Orange
    INFO = wx.Colour(52, 152, 219)  # Light blue

    # Neutral colors
    BACKGROUND = wx.Colour(255, 255, 255)  # White
    BACKGROUND_DARK = wx.Colour(236, 240, 241)  # Light gray
    TEXT = wx.Colour(44, 62, 80)  # Dark gray
    TEXT_LIGHT = wx.Colour(127, 140, 141)  # Medium gray
    BORDER = wx.Colour(189, 195, 199)  # Gray

    # Projection window
    PROJECTION_BG = wx.Colour(0, 0, 0)  # Black
    PROJECTION_TEXT = wx.Colour(255, 255, 255)  # White
    PROJECTION_VERSE_NUMBER = wx.Colour(255, 215, 0)  # Gold


class Fonts:
    """Application font configurations"""

    @staticmethod
    def get_default_font(size=10):
        """Get default application font"""
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    @staticmethod
    def get_header_font(size=14):
        """Get header font (bold)"""
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

    @staticmethod
    def get_label_font(size=10):
        """Get label font"""
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    @staticmethod
    def get_button_font(size=10):
        """Get button font"""
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

    @staticmethod
    def get_monospace_font(size=10):
        """Get monospace font (for verse references, etc.)"""
        return wx.Font(size, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)


class Spacing:
    """Spacing constants for consistent layout"""

    # Padding
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 15
    PADDING_XLARGE = 20

    # Margins
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 15

    # Border widths
    BORDER_THIN = 1
    BORDER_MEDIUM = 2
    BORDER_THICK = 3


class Sizes:
    """Size constants for UI elements"""

    # Main window
    MAIN_WINDOW_WIDTH = 800
    MAIN_WINDOW_HEIGHT = 900

    # Input fields
    INPUT_HEIGHT = 30
    BUTTON_HEIGHT = 30
    BUTTON_WIDTH_SMALL = 60
    BUTTON_WIDTH_MEDIUM = 80
    BUTTON_WIDTH_LARGE = 120

    # Chapter preview
    CHAPTER_PREVIEW_HEIGHT = 200

    # Status bar
    STATUS_BAR_HEIGHT = 25


class Icons:
    """Icon/emoji constants for buttons"""

    # Using emoji for cross-platform compatibility
    HYMN = "🎵"
    CLEAR = "✕"
    PREVIEW = "👁"
    HISTORY = "📜"
    PREV = "◀"
    NEXT = "▶"
    PREV_CHAPTER = "◀"
    NEXT_CHAPTER = "▶"
    SETTINGS = "⚙"
    HIDE = "⊟"


def create_static_box(parent, label):
    """
    Create a styled static box sizer for section grouping

    Args:
        parent: Parent window
        label: Section label

    Returns:
        wx.StaticBoxSizer
    """
    box = wx.StaticBox(parent, label=label)
    box.SetFont(Fonts.get_header_font(11))
    box.SetForegroundColour(Colors.TEXT)  # Ensure label is visible
    sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
    return sizer


def create_button(parent, label, size=None):
    """
    Create a styled button

    Args:
        parent: Parent window
        label: Button label
        size: Optional size tuple (width, height)

    Returns:
        wx.Button
    """
    if size:
        btn = wx.Button(parent, label=label, size=size)
    else:
        btn = wx.Button(parent, label=label)

    btn.SetFont(Fonts.get_button_font())
    return btn


def create_text_input(parent, value="", size=None):
    """
    Create a styled text input field

    Args:
        parent: Parent window
        value: Initial value
        size: Optional size tuple (width, height)

    Returns:
        wx.TextCtrl
    """
    style = wx.TE_PROCESS_ENTER | wx.BORDER_THEME
    if size:
        ctrl = wx.TextCtrl(parent, value=value, size=size, style=style)
    else:
        ctrl = wx.TextCtrl(parent, value=value, style=style)

    ctrl.SetFont(Fonts.get_default_font())
    ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
    ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
    return ctrl


def create_label(parent, text, bold=False):
    """
    Create a styled label

    Args:
        parent: Parent window
        text: Label text
        bold: Whether to use bold font

    Returns:
        wx.StaticText
    """
    label = wx.StaticText(parent, label=text)

    if bold:
        label.SetFont(Fonts.get_label_font())
        label.SetFont(label.GetFont().Bold())
    else:
        label.SetFont(Fonts.get_label_font())

    label.SetForegroundColour(Colors.TEXT)  # Ensure text is visible
    return label


def create_checkbox(parent, label):
    """
    Create a styled checkbox

    Args:
        parent: Parent window
        label: Checkbox label

    Returns:
        wx.CheckBox
    """
    checkbox = wx.CheckBox(parent, label=label)
    checkbox.SetFont(Fonts.get_default_font())
    checkbox.SetForegroundColour(Colors.TEXT)  # Ensure text is visible
    return checkbox


def show_info_dialog(parent, title, message):
    """Show information dialog"""
    dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def show_error_dialog(parent, title, message):
    """Show error dialog"""
    dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


def show_not_implemented(parent):
    """Show 'not implemented' placeholder dialog"""
    show_info_dialog(
        parent,
        "Coming Soon",
        "This feature is not yet implemented.\n\nPhase 2 focuses on UI layout and design validation."
    )