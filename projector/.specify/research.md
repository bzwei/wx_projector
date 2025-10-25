# Phase 0: UX Research & Technology Decisions

**Date**: 2025-10-12
**Status**: Complete
**Related**: [plan.md](./plan.md), [specification.md](./specification.md)

## Overview

This document captures research findings for building the Webpage Projector UI-first, focusing on wxPython best practices, desktop presentation software UX patterns, and technical decisions for building a professional dual-window projection application.

---

## 1. wxPython UI Best Practices

### 1.1 Layout Management for Fixed-Size Windows

**Decision**: Use `wx.BoxSizer` with nested sizers for structured layouts

**Rationale**:
- `wx.BoxSizer` provides flexible, maintainable layouts without hardcoded positions
- Supports both vertical and horizontal stacking
- Easy to add spacing and borders for consistent padding
- Better than absolute positioning for maintainability
- Works well with fixed-size windows (800×900 control panel)

**Implementation Pattern**:
```python
# Main vertical sizer for control panel sections
main_sizer = wx.BoxSizer(wx.VERTICAL)

# Each section gets its own static box
url_box = wx.StaticBox(panel, label="URL Projection")
url_sizer = wx.StaticBoxSizer(url_box, wx.VERTICAL)

# Add components with spacing
url_sizer.Add(url_input, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
url_sizer.Add(button_sizer, proportion=0, flag=wx.ALIGN_RIGHT|wx.ALL, border=5)

main_sizer.Add(url_sizer, proportion=0, flag=wx.EXPAND|wx.ALL, border=10)
```

**Alternatives Considered**:
- `wx.GridBagSizer`: Too complex for this simple stacked layout
- Absolute positioning: Not maintainable, breaks with font size changes
- `wx.FlexGridSizer`: Overkill for mostly vertical layout

---

### 1.2 Auto-Complete Book Selection Component

**Decision**: Use `wx.ComboBox` with `wx.TE_PROCESS_ENTER` style for book selection

**Rationale**:
- `wx.ComboBox` supports both dropdown and text entry
- Can be populated with all 66 book names (English + Chinese)
- Supports auto-complete via `AutoComplete()` method
- Fires events on selection change for validation
- Standard control that users understand

**Implementation Pattern**:
```python
book_choices = ["Genesis创世记", "Exodus出埃及记", "John约翰福音", ...]
book_combo = wx.ComboBox(
    panel,
    choices=book_choices,
    style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
)

# Enable auto-complete
book_combo.AutoComplete(book_choices)

# Bind selection event
book_combo.Bind(wx.EVT_COMBOBOX, self.on_book_selected)
book_combo.Bind(wx.EVT_TEXT_ENTER, self.on_book_entered)
```

**Alternatives Considered**:
- `wx.TextCtrl` with custom dropdown: Too much custom code
- `wx.Choice`: Doesn't support text entry/auto-complete
- Third-party autocomplete widget: Unnecessary dependency

---

### 1.3 Chapter Preview Scrollable Panel

**Decision**: Use `wx.ListBox` with single selection for chapter preview

**Rationale**:
- `wx.ListBox` natively supports scrolling, selection, keyboard navigation
- Can populate with formatted verse strings ("1. In the beginning...")
- Supports highlight on selection (visual feedback)
- Built-in double-click event for verse selection
- Efficient rendering even with 100+ verses

**Implementation Pattern**:
```python
preview_list = wx.ListBox(
    panel,
    size=(400, 300),
    style=wx.LB_SINGLE | wx.LB_NEEDED_SB  # Single selection, scrollbar if needed
)

# Populate with verses
verses = ["1. In the beginning God created...", "2. And the earth was..."]
preview_list.Set(verses)

# Bind selection event
preview_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_verse_selected)

# Programmatic selection
preview_list.SetSelection(15)  # Highlight verse 16 (0-indexed)
```

**Alternatives Considered**:
- `wx.html.HtmlWindow`: Overkill, harder to handle selection
- `wx.ScrolledWindow` with custom rendering: Too much custom code
- `wx.grid.Grid`: Too complex for simple list

---

### 1.4 Multi-Version Bible Verse Display

**Decision**: Use `wx.html.HtmlWindow` for projection window Bible content

**Rationale**:
- Supports rich HTML formatting (fonts, sizes, colors, spacing)
- Can render complex multi-version row layout easily
- Supports UTF-8 and Chinese characters natively
- Can apply CSS-like styling via HTML tags
- Easy to update content dynamically (SetPage())

**HTML Template Pattern**:
```html
<html>
<body style="background-color: black; color: white; font-family: Arial;">
  <div style="padding: 20px;">
    <h2 style="text-align: center; font-size: 36px;">John 3:16-17</h2>

    <!-- Verse 16 - All versions in rows -->
    <div style="margin-bottom: 30px;">
      <p style="font-size: 24px; margin: 10px 0;">
        <strong>Verse 16</strong>
      </p>
      <p style="font-size: 24px; margin: 5px 0; padding-left: 20px;">
        <span style="color: #FFD700;">和合本:</span> 神爱世人，甚至将他的独生子赐给他们...
      </p>
      <p style="font-size: 22px; margin: 5px 0; padding-left: 20px;">
        <span style="color: #87CEEB;">KJV:</span> For God so loved the world...
      </p>
    </div>

    <!-- Verse 17 -->
    <div style="margin-bottom: 30px;">
      ...
    </div>
  </div>
</body>
</html>
```

**Alternatives Considered**:
- `wx.TextCtrl` with rich text: Limited formatting options
- `wx.WebView`: Overkill for static HTML, higher resource usage
- Custom painting: Too complex, hard to maintain

---

### 1.5 Projection Window Fullscreen Management

**Decision**: Use `wx.Frame` with `ShowFullScreen()` for projection window

**Rationale**:
- `ShowFullScreen()` is cross-platform native fullscreen
- Hides title bar, borders, menu bar automatically
- `wx.FULLSCREEN_ALL` flag hides taskbar/dock as well
- Easy to toggle on/off for show/hide functionality
- Works with multi-monitor setups via `SetPosition()`

**Implementation Pattern**:
```python
# Create borderless frame
projection_frame = wx.Frame(
    None,
    style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP
)

# Position on secondary display
display_rect = wx.Display(1).GetGeometry()  # Display 1 = secondary
projection_frame.SetPosition((display_rect.x, display_rect.y))
projection_frame.SetSize((display_rect.width, display_rect.height))

# Enter fullscreen
projection_frame.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)

# Exit fullscreen (for single display mode)
projection_frame.ShowFullScreen(False)
```

**Alternatives Considered**:
- Maximize window: Doesn't hide taskbar/title bar
- Borderless maximized window: Still shows taskbar on some platforms
- Platform-specific APIs: Not cross-platform

---

## 2. Desktop Presentation Software UX Patterns

### 2.1 Competitive Analysis

**Applications Analyzed**:
1. **ProPresenter 7** (industry standard for worship services)
2. **EasyWorship** (popular church presentation software)
3. **OpenLP** (open-source worship software)

### 2.2 Key UX Patterns Observed

#### Control Panel Layout
- **Vertical sections** for different content types (most common pattern)
- **Clear visual separation** between sections (borders, spacing)
- **Inline status messages** below input fields (not modal dialogs)
- **Preview panels** always visible (don't hide in separate windows)
- **Action buttons** grouped horizontally (Project, Hide, Clear)
- **Fixed window size** to maintain consistent layout

**Decision**: Adopt vertical section layout with clear separators

#### Bible Verse Input
- **Separate book and reference fields** (better UX than single field parsing)
- **Book autocomplete dropdown** (faster than scrolling through 66 books)
- **Chapter preview panel** (essential for quick verse selection)
- **Visual feedback** for current verse in preview (highlight/arrow)

**Decision**: Separate book dropdown + chapter:verse text field

#### Version Selection
- **Checkbox grid** for version selection (not dropdown)
- **1-5 versions max** (more becomes unreadable)
- **Default to 1-2 versions** (CUV + KJV for this use case)
- **Version abbreviations** clearly labeled (full names too long)

**Decision**: Horizontal checkbox row for version selection

#### Projection Window
- **Black background** for Bible text (reduces eye strain, professional)
- **White or yellow text** on black (high contrast)
- **Generous padding** around content (don't cram text to edges)
- **Verse numbers** clearly visible but not distracting
- **Version labels** color-coded for quick identification

**Decision**: Black background, white/gold text, version-specific colors

---

### 2.3 Progressive Verse Loading Pattern

**Common Pattern**: Load only requested verses initially, expand on demand

**Rationale**:
- Reduces cognitive load (don't show entire chapter by default)
- Keeps projection window clean and focused
- Allows quick navigation without scrolling
- "Load More" buttons common in modern UIs (familiar pattern)

**Decision**: Implement "Load Previous Verses ↑" and "Load Remaining Verses ↓" buttons

**User Flow**:
1. User enters "John 3:16" → Only verse 16 displays
2. User clicks "Load Previous Verses" → Verses 1-15 added above
3. User clicks "Load Remaining Verses" → Verses 17-21 added below
4. All verses remain visible until new selection

---

## 3. Multi-Monitor Detection & Management

### 3.1 Technology Decision

**Decision**: Use `screeninfo` library for monitor detection

**Rationale**:
- Cross-platform (macOS, Windows, Linux)
- Simple API: `get_monitors()` returns list of Monitor objects
- Provides position, resolution, primary flag
- Actively maintained (2024 updates)
- Pure Python, no native dependencies

**Installation**:
```bash
uv add screeninfo
```

**Implementation Pattern**:
```python
from screeninfo import get_monitors

monitors = get_monitors()
print(f"Detected {len(monitors)} monitor(s)")

for i, monitor in enumerate(monitors):
    print(f"Display {i}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
    if monitor.is_primary:
        print("  ^ Primary display")
```

**Alternatives Considered**:
- `wx.Display`: Available but less flexible than screeninfo
- Platform-specific APIs (Cocoa, Win32): Not cross-platform
- Manual configuration: Poor UX, error-prone

---

### 3.2 Display Selection Logic

**Decision**: Automatic secondary display selection with manual override

**Logic**:
```
IF 2+ displays detected:
    Primary = display containing control panel (usually display 0)
    Target = first non-primary display (usually display 1)
    Mode = Fullscreen
ELSE (1 display):
    Primary = display 0
    Target = display 0
    Mode = Windowed (NOT fullscreen)
```

**Rationale**:
- Users with 2+ displays expect automatic projection to secondary
- Single display users need windowed mode (can't hide control panel in fullscreen)
- Manual override in settings for edge cases

---

## 4. Font Size & Text Rendering

### 4.1 Chinese vs English Font Sizing

**Decision**: Separate font size controls for Chinese and English text

**Rationale**:
- Chinese characters need slightly larger size for readability (more complex strokes)
- Default: Chinese 24px, English 22px
- Users may have different preferences based on display resolution
- Separate controls provide maximum flexibility

**Implementation**:
```html
<p style="font-size: {chinese_size}px; font-family: 'Microsoft YaHei', SimHei, sans-serif;">
  和合本: {chinese_text}
</p>
<p style="font-size: {english_size}px; font-family: Arial, sans-serif;">
  KJV: {english_text}
</p>
```

---

### 4.2 Font Families

**Decision**: Use system fonts for cross-platform compatibility

**Chinese Fonts** (in order of preference):
1. Microsoft YaHei (Windows, modern)
2. SimHei (macOS, classic)
3. sans-serif (fallback)

**English Fonts**:
1. Arial (universal, readable)
2. Helvetica (macOS fallback)
3. sans-serif (fallback)

**Rationale**:
- No embedded fonts needed (reduces app size)
- System fonts render faster
- Users familiar with these fonts
- Guaranteed to be available on target platforms

---

## 5. Data File Formats & Loading

### 5.1 Bible Text File Encoding

**Decision**: Detect encoding automatically, support UTF-8 and GB2312

**Current File Structure** (from specification):
```
books/
├── cuv/         # Chinese (GB2312 encoding)
│   └── vol01/chap001.txt
├── kjv/         # English (UTF-8 encoding)
│   └── vol01/chap001.txt
```

**Implementation Pattern**:
```python
def load_chapter(version: str, book_id: int, chapter: int) -> list[str]:
    path = f"books/{version}/vol{book_id:02d}/chap{chapter:03d}.txt"

    # Try UTF-8 first (most common)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            verses = f.readlines()
    except UnicodeDecodeError:
        # Fallback to GB2312 for Chinese versions
        with open(path, 'r', encoding='gb2312') as f:
            verses = f.readlines()

    return [v.strip() for v in verses if v.strip()]
```

**Rationale**:
- Existing data uses mixed encodings (can't change easily)
- Try UTF-8 first (modern standard, works for English)
- Fallback to GB2312 for older Chinese versions
- Graceful error handling

---

### 5.2 CSV File Loading

**Decision**: Use Python's built-in `csv` module for hymns.csv and books.csv

**books.csv Format**:
```csv
'Genesis创世记':[1, 50],
'Exodus出埃及记':[2, 40],
```

**Implementation Pattern**:
```python
import csv
import ast

def load_books() -> dict:
    books = {}
    with open('books.csv', 'r', encoding='utf-8') as f:
        content = f.read()
        # Parse custom format (Python dict literal)
        for line in content.strip().split('\n'):
            if line.strip():
                # Parse: 'BookName':[book_id, chapter_count]
                name, data = line.split(':', 1)
                name = name.strip().strip("'")
                book_id, chapter_count = ast.literal_eval(data.strip().rstrip(','))
                books[name] = {'id': book_id, 'chapters': chapter_count}
    return books
```

**hymns.csv** (standard CSV):
```python
import csv

def load_hymns() -> dict:
    hymns = {}
    with open('hymns.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hymns[row['HymnID'].upper()] = row['GoogleSlidesID']
    return hymns
```

---

## 6. Mock Data Strategy for UI Development

### 6.1 Mock Data Structure

**Decision**: Create centralized mock data module for Phases 2-3

**File**: `src/utils/mock_data.py`

```python
# Mock Bible Books
MOCK_BOOKS = [
    "Genesis创世记",
    "Exodus出埃及记",
    "Leviticus利未记",
    "John约翰福音",
    "Romans罗马书",
]

# Mock Book Metadata
MOCK_BOOK_INFO = {
    "Genesis创世记": {"id": 1, "chapters": 50},
    "John约翰福音": {"id": 43, "chapters": 21},
}

# Mock Hymns
MOCK_HYMNS = {
    "A01": {"name": "Amazing Grace", "slides_id": "1saIavtk49GG2zSinkdAgWltEba0xiRv7Cf5KbksYKwk"},
    "C002": {"name": "Come Thou Fount", "slides_id": "1O6uLRuKGDsgkgtHSYw2HVfmYvEHDqziz_MiGaDKRsVg"},
}

# Mock Bible Verses
MOCK_VERSES = {
    "John": {
        3: {
            16: {
                "cuv": "神爱世人，甚至将他的独生子赐给他们，叫一切信他的，不至灭亡，反得永生。",
                "kjv": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "niv": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."
            },
            17: {
                "cuv": "因为神差他的儿子降世，不是要定世人的罪，乃是要叫世人因他得救。",
                "kjv": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
                "niv": "For God did not send his Son into the world to condemn the world, but to save the world through him."
            }
        }
    }
}

# Mock Chapter Preview
MOCK_CHAPTER_VERSES = [
    "1. In the beginning was the Word, and the Word was with God, and the Word was God.",
    "2. The same was in the beginning with God.",
    "3. All things were made by him; and without him was not any thing made that was made.",
    # ... up to verse 21
]

# Mock History
MOCK_HISTORY = [
    {"ref": "John 3:16", "versions": ["cuv", "kjv"], "timestamp": "14:30"},
    {"ref": "Genesis 1:1", "versions": ["cuv"], "timestamp": "14:25"},
    {"ref": "Romans 8:28", "versions": ["cuv", "kjv", "niv"], "timestamp": "14:20"},
]

# Mock Display Info
MOCK_DISPLAYS = [
    {"name": "Display 1 (Primary)", "resolution": "1920x1080", "position": (0, 0)},
    {"name": "Display 2 (Secondary)", "resolution": "1920x1080", "position": (1920, 0)},
]
```

**Rationale**:
- Centralized mock data easy to update
- Consistent data across all UI components
- Clear separation between mock and real data
- Easy to swap out when implementing backend

---

## 7. State Management Strategy

### 7.1 Application State Pattern

**Decision**: Use class-based state management with event callbacks

**Pattern**:
```python
class AppState:
    def __init__(self):
        self.current_projection = None  # "url" | "slides" | "bible" | None
        self.bible_selection = {
            "book": None,
            "chapter": None,
            "verses": None,
            "versions": ["cuv"]  # Default
        }
        self.font_sizes = {
            "chinese": 24,
            "english": 22
        }
        self.display_config = {
            "target_display": 1,  # Secondary display
            "fullscreen": True
        }
        self.history = []  # Last 30 projections

    def update_bible_selection(self, **kwargs):
        self.bible_selection.update(kwargs)
        # Notify observers

    def add_to_history(self, entry):
        self.history.insert(0, entry)
        if len(self.history) > 30:
            self.history = self.history[:30]
```

**Rationale**:
- Single source of truth for app state
- Easy to persist to JSON config
- Clear interface for state updates
- Supports event-driven UI updates

---

## 8. Development Environment Setup

### 8.1 Virtual Environment with uv

**Setup Commands**:
```bash
# Initialize project (already done)
cd /Users/billwei/webpage_projector
source venv/bin/activate  # Or create with: uv venv

# Add dependencies
uv add wxPython
uv add screeninfo

# Development dependencies
uv add --dev pytest
uv add --dev pytest-qt
uv add --dev black
uv add --dev ruff
```

### 8.2 Project Structure Initialization

**Commands**:
```bash
# Create source structure
mkdir -p src/ui/components src/ui/styles
mkdir -p src/core src/data src/utils
mkdir -p tests/ui tests/core tests/integration

# Create __init__.py files
touch src/__init__.py
touch src/ui/__init__.py
touch src/ui/components/__init__.py
touch src/core/__init__.py
touch src/data/__init__.py
touch src/utils/__init__.py
```

---

## 9. Key Technical Decisions Summary

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Layout Manager** | wx.BoxSizer | Flexible, maintainable, standard |
| **Book Selection** | wx.ComboBox | Auto-complete support, familiar UX |
| **Chapter Preview** | wx.ListBox | Built-in scrolling, selection, keyboard nav |
| **Bible Display** | wx.html.HtmlWindow | Rich formatting, easy HTML templates |
| **Projection Fullscreen** | ShowFullScreen() | Cross-platform, native, simple |
| **Monitor Detection** | screeninfo library | Cross-platform, simple API, maintained |
| **Font Handling** | System fonts | Fast, compatible, no bundling |
| **Bible File Encoding** | Auto-detect UTF-8/GB2312 | Supports existing data format |
| **Mock Data** | Centralized module | Consistent, easy to swap for real data |
| **State Management** | Class-based AppState | Single source of truth, clear interface |

---

## 10. Next Steps (Phase 1)

Based on this research, proceed to **Phase 1: Data Models & Component Contracts**:

1. Create `data-model.md` defining:
   - `ProjectionState` model
   - `BibleVerseRequest` model
   - `ChapterPreviewState` model
   - `HistoryEntry` model
   - `DisplayConfig` model

2. Create `contracts/component-interfaces.md` defining:
   - `IProjectionWindow` interface
   - `IBiblePanel` interface
   - `IChapterPreview` interface
   - `IHistoryManager` interface

3. Create `quickstart.md` with:
   - Environment setup instructions
   - Running the application
   - Development workflow
   - Testing procedures

---

**Research Complete**: Ready for Phase 1
**Next Command**: Generate data models and component contracts