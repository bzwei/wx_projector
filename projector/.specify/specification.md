# Webpage Projector - Technical Specification

**Version:** 2.0.0 (Hybrid Architecture)
**Last Updated:** 2025-10-12
**Platform:** Desktop (macOS primary, Windows/Linux compatible)
**Technology Stack:** Python 3.12, wxPython (wx.html2.WebView), HTML/CSS/JavaScript, uv package manager
**Architecture:** Hybrid (Web UI + Native Projection)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Feature Requirements](#feature-requirements)
4. [User Interface Specifications](#user-interface-specifications)
5. [Data Models](#data-models)
6. [Technical Requirements](#technical-requirements)
7. [API & Integration](#api--integration)
8. [Testing Strategy](#testing-strategy)
9. [Deployment & Distribution](#deployment--distribution)

---

## 1. Project Overview

### 1.1 Purpose
Webpage Projector is a hybrid desktop application designed for worship services and presentations. It uses a **web-based control panel** (HTML/CSS/JavaScript in wx.html2.WebView) for a beautiful, modern UI, and **native borderless windows** for true fullscreen projection. The application specializes in displaying Google Slides presentations and Bible verses with multiple translations side-by-side.

**Architecture Choice**: Hybrid approach combines the best of both worlds:
- **Control Panel**: Web technologies (HTML/CSS/JS) for modern, beautiful UI inspired by ncfnj.org/bible
- **Projection Window**: Native wxPython borderless fullscreen for true multi-monitor support

### 1.2 Key Capabilities
- Dual-window architecture: control panel + projection window
- Google Slides presentation projection
- Multi-version Bible verse display with row-based layout (all versions of one verse, then next verse)
- Bible verse preview with chapter navigation
- Progressive verse loading (show selected verse first, expand up/down)
- Projection history (last 30 projections) for quick re-projection
- Automated Google Meet joining and screen sharing
- Intelligent display detection and management
- Separate book and chapter+verse input fields

### 1.3 Target Users
- Worship service coordinators
- Church AV operators
- Presentation managers
- Remote worship coordinators

---

## 2. System Architecture

### 2.1 High-Level Architecture (Hybrid)

```
┌──────────────────────────────────────────────────────────────┐
│  wxPython Main Window (800×900px)                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  wx.html2.WebView (Embedded Browser)                   │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  HTML/CSS/JavaScript Control Panel               │  │  │
│  │  │  - Modern web UI (inspired by ncfnj.org/bible)   │  │  │
│  │  │  - URL input, Slides input, Bible selection      │  │  │
│  │  │  - Beautiful styling with CSS                    │  │  │
│  │  │  - Interactive with JavaScript                   │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  JavaScript ↔ Python Bridge (wx.html2 message handlers)     │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ Python Backend
                            │ (Bible Engine, Display Manager, etc.)
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Native Projection Windows (Borderless, Fullscreen)          │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │ Bible Content  │  │ Google Slides  │  │  Web URL      │  │
│  │ (wx.html2)     │  │ (wx.html2)     │  │  (wx.html2)   │  │
│  └────────────────┘  └────────────────┘  └───────────────┘  │
│  • True borderless fullscreen                                │
│  • Multi-monitor support via Display Manager                 │
│  • System-level window control (STAY_ON_TOP)                │
└──────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            │                                │
      ┌─────▼──────┐                  ┌─────▼──────┐
      │  Primary   │                  │ Secondary  │
      │  Display   │                  │  Display   │
      │ (Control)  │                  │(Projection)│
      └────────────┘                  └────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Frontend Components (Web-based Control Panel)
- **HTML Control Panel** (`src/ui/web/index.html`): Main UI structure
- **CSS Styling** (`src/ui/web/styles.css`): Modern, responsive styling inspired by ncfnj.org/bible
- **JavaScript Controller** (`src/ui/web/app.js`): UI logic and Python bridge communication
- **JavaScript Modules**:
  - `url_controller.js`: Handles URL projection UI
  - `slides_controller.js`: Handles Google Slides UI
  - `bible_controller.js`: Handles Bible verse selection UI
  - `bridge.js`: JavaScript ↔ Python communication layer

#### 2.2.2 Native Components (wxPython)
- **MainWindow** (`src/ui/main_window.py`): wx.Frame containing wx.html2.WebView
- **WebViewController** (`src/ui/web_controller.py`): Manages WebView and message handlers
- **ProjectionWindow** (`src/ui/projection_window.py`): Native borderless fullscreen window for projection
- **DisplayManager** (`src/core/display_manager.py`): Manages monitor detection and window placement

#### 2.2.3 Backend Components (Python)
- **BibleEngine** (`src/core/bible_engine.py`): Loads and formats Bible verses from file storage
- **ContentRenderer** (`src/core/content_renderer.py`): Renders different content types (web, slides, Bible) as HTML
- **HistoryManager** (`src/core/history_manager.py`): Tracks and manages projection history

#### 2.2.4 Data Components
- **BibleRepository** (`src/data/bible_repository.py`): Manages Bible text files (multiple versions)
- **SlidesRepository** (`src/data/slides_repository.py`): Maps hymn IDs to Google Slides IDs
- **ConfigManager** (`src/data/config_manager.py`): Manages application settings and preferences

#### 2.2.5 JavaScript ↔ Python Bridge
**Communication Pattern:**
```python
# Python → JavaScript (send data to web UI)
webview.RunScript(f"window.updateBiblePreview({json.dumps(verses)})")

# JavaScript → Python (send commands from web UI)
// In JavaScript:
window.webkit.messageHandlers.backend.postMessage({
    action: "project_bible",
    data: { book: "John", chapter: 3, verse: 16, versions: ["cuv", "kjv"] }
})

// In Python:
def on_message_received(self, event):
    message = json.loads(event.GetString())
    if message['action'] == 'project_bible':
        self.bible_engine.project(**message['data'])
```

---

## 3. Feature Requirements

### 3.1 Display Management

#### FR-DM-001: Multi-Monitor Detection
**Priority:** CRITICAL
**Description:** Application must detect all connected displays on startup and when displays are connected/disconnected.

**Acceptance Criteria:**
- Detect all monitors using platform-native APIs
- Display monitor count and resolution in control panel
- Support for 1-2 displays

**Technical Notes:**
- Use `screeninfo` library for cross-platform monitor detection

---

#### FR-DM-002: Projection Window Placement
**Priority:** CRITICAL
**Description:** Projection window placement logic based on available displays.

**Acceptance Criteria:**
- **If 2+ displays:** Project to secondary display (non-primary) in full-screen mode
- **If 1 display:** Project to primary display in windowed mode (NOT full-screen)
- Allow manual display selection in settings
- Remember last used display preference

**Technical Notes:**
- Primary display = display containing the control panel
- Secondary display = first non-primary display detected
- Full-screen mode must use native OS full-screen APIs (no borders, taskbar hidden)

---

### 3.2 Google Slides Projection

#### FR-GS-001: Google Slides URL Input
**Priority:** HIGH
**Description:** Accept and validate Google Slides URLs or presentation IDs.

**Acceptance Criteria:**
- Accept full Google Slides URLs (docs.google.com/presentation/d/{ID}/...)
- Accept presentation ID only (extract from URL if needed)
- Accept hymn ID from hymns.csv lookup table
- Validate presentation ID format (alphanumeric, 40+ characters)

**Input Formats:**
```
# Full URL
https://docs.google.com/presentation/d/1ABC...XYZ/edit

# Presentation ID only
1ABC...XYZ

# Hymn ID (from hymns.csv)
A01
C002
123
```

---

#### FR-GS-002: Slides Presentation Mode
**Priority:** HIGH
**Description:** Project Google Slides in presentation mode (not edit mode).

**Acceptance Criteria:**
- Convert any Google Slides URL to presentation mode (/present)
- Load slides in full-screen projection window
- Handle authentication errors gracefully (prompt user if private)
- Support keyboard navigation in presentation (arrow keys)

**Technical Notes:**
- Presentation URL format: `https://docs.google.com/presentation/d/{ID}/present`
- Use WebView component to render presentation
- May require user to authenticate in popup if slides are private

---

#### FR-GS-003: Hymn ID Mapping
**Priority:** HIGH
**Description:** Map hymn IDs to Google Slides presentation IDs using CSV lookup.

**Acceptance Criteria:**
- Load hymns.csv on application startup
- Support hymn ID formats: numeric (123), A-series (A01), C-series (C002)
- Case-insensitive hymn ID lookup
- Display hymn ID in control panel when matched

**CSV Format:**
```csv
HymnID,SlidesID
A01,1saIavtk49GG2zSinkdAgWltEba0xiRv7Cf5KbksYKwk
C002,1O6uLRuKGDsgkgtHSYw2HVfmYvEHDqziz_MiGaDKRsVg
```

---

### 3.3 Bible Verse Projection

#### FR-BV-001: Bible Verse Input Parsing
**Priority:** CRITICAL
**Description:** Parse Bible verse references with separate book and chapter+verse input fields.

**Acceptance Criteria:**
- **Book Input Field**: Separate dropdown/autocomplete field for book selection
  - Auto-complete book names (suggest matches as user types)
  - Book names appear as English and Chinese combined:
    - `John约翰福音`
    - `Genesis创世记`
    - `1 Corinthians哥林多前书`
  - Dropdown shows all available books when clicked
- **Chapter+Verse Input Field**: Separate text field for chapter and verse
  - Support multiple input formats:
    - `3:16` (chapter 3, verse 16 only)
    - `3 16` (chapter 3, verse 16 only)
    - `1:1-3` (chapter 1, verses 1-3)
    - `13` (chapter 13, **entire chapter**)
    - `23:1-4` (chapter 23, verses 1-4)
- Validate chapter and verse numbers against available data
- Show validation errors inline
- **Default behavior**: If only chapter number is entered, select and display the entire chapter

**Technical Notes:**
- Use regex pattern matching for flexible chapter+verse parsing
- Refer to books.csv for book metadata (chapter counts)
- When only chapter is specified (e.g., `13`), load all verses in that chapter

---

#### FR-BV-002: Multi-Version Display
**Priority:** CRITICAL
**Description:** Display multiple Bible versions in row-based layout in projection window.

**Acceptance Criteria:**
- Support at least 5 Bible versions:
  - 和合本 (Chinese Union Version - CUV)
  - King James Version (KJV)
  - New American Standard (NAS)
  - New International Version (NIV)
  - Darby Translation (DBY)
- Allow user to select 1-5 versions via checkboxes
- **Display versions in ROWS** (not columns):
  - Show all selected versions for verse 1
  - Then all selected versions for verse 2
  - Continue for each verse
- **Progressive Loading**: Display selected verses first, with expand buttons:
  - Initially show only the selected verse(s) specified by user
  - Provide "Load Previous Verses" button (loads from verse 1 to current verse - 1)
  - Provide "Load Remaining Verses" button (loads from current verse + 1 to end of chapter)
  - Buttons appear in control panel

**Layout Example (2 versions, verse 16 selected):**
```
┌──────────────────────────────────────────────────────┐
│              John 3:16 - Multiple Versions            │
├──────────────────────────────────────────────────────┤
│  [Load Previous Verses ↑]                            │
│                                                       │
│  Verse 16:                                            │
│  ├─ 和合本 (CUV): 神爱世人，甚至将他的独生子赐给他们...│
│  └─ King James (KJV): For God so loved the world...  │
│                                                       │
│  [Load Remaining Verses ↓]                           │
└──────────────────────────────────────────────────────┘

After clicking "Load Remaining Verses":
┌──────────────────────────────────────────────────────┐
│              John 3:16-21 - Multiple Versions         │
├──────────────────────────────────────────────────────┤
│  [Load Previous Verses ↑]                            │
│                                                       │
│  Verse 16:                                            │
│  ├─ 和合本 (CUV): 神爱世人，甚至将他的独生子赐给他们...│
│  └─ King James (KJV): For God so loved the world...  │
│                                                       │
│  Verse 17:                                            │
│  ├─ 和合本 (CUV): 因为神差他的儿子降世...            │
│  └─ King James (KJV): For God sent not his Son...    │
│                                                       │
│  Verse 18:                                            │
│  ├─ 和合本 (CUV): 信他的人，不被定罪...              │
│  └─ King James (KJV): He that believeth on him...    │
│                                                       │
│  ... (continues to verse 21)                         │
└──────────────────────────────────────────────────────┘
```

---

#### FR-BV-003: Bible Text Storage
**Priority:** CRITICAL
**Description:** Store Bible texts in structured file format for fast retrieval.

**Acceptance Criteria:**
- Organize files by version → book → chapter
- File structure: `books/{version}/vol{book_id}/chap{chapter_id}.txt`
- One verse per line in chapter files
- Support UTF-8 encoding (English) and GB2312 encoding (Chinese)
- Load chapter file on demand (not all at startup)

**Directory Structure:**
```
books/
├── cuv/              # Chinese Union Version
│   ├── vol01/        # Genesis
│   │   ├── chap001.txt
│   │   ├── chap002.txt
│   │   └── ...
│   ├── vol02/        # Exodus
│   └── ...
├── kjv/              # King James Version
├── nas/              # New American Standard
├── niv/              # New International Version
└── dby/              # Darby Translation
```

**Chapter File Format:**
```
In the beginning God created the heaven and the earth.
And the earth was without form, and void; and darkness was upon the face of the deep.
And God said, Let there be light: and there was light.
...
```

---

#### FR-BV-004: Font Size Customization
**Priority:** HIGH
**Description:** Allow users to customize font sizes for Chinese and English text separately.

**Acceptance Criteria:**
- Separate font size controls for Chinese and English
- Font size range: 16px - 40px
- Default sizes: Chinese 24px, English 22px
- Apply font sizes immediately to projection window
- Persist font size preferences

---

#### FR-BV-005: Bible Verse Preview
**Priority:** HIGH
**Description:** Show chapter preview in control panel with verse selection capability.

**Acceptance Criteria:**
- Display chapter preview panel in control panel (always visible)
- Show all verses in selected chapter
- Highlight selected verse in preview
- Click on verse in preview to select for projection. Project single verse first, and buttons to load previous or remaining verses.
- Support keyboard navigation (arrow keys to navigate verses)
- Show verse numbers in preview

**Preview Panel Layout:**
```
┌─────────────────────────────────────────┐
│  Chapter Preview: John 3                │
│  [◀ Prev Chapter] [Next Chapter ▶]     │
├─────────────────────────────────────────┤
│ Scrollable Area                         │
│                                         │
│  1  In the beginning was the Word...    │
│  2  The same was in the beginning...    │
│  ...                                    │
│  ▶ 16 For God so loved the world...     │
│  17 For God sent not his Son into...    │
│                                         │
└─────────────────────────────────────────┘
```

---

#### FR-BV-006: Chapter Navigation
**Priority:** MEDIUM
**Description:** Navigate to previous/next chapters in preview panel.

**Acceptance Criteria:**
- Previous/Next chapter buttons in preview panel
- Disable "Previous" on chapter 1
- Disable "Next" on last chapter of book
- Load new chapter content when navigating
- Maintain book context when changing chapters

---

#### FR-BV-007: Projection History
**Priority:** HIGH
**Description:** Track Bible verse projection history for quick re-projection.

**Acceptance Criteria:**
- Store last 30 projected Bible verses in current session only
- History is cleared when application starts (no persistence between sessions)
- History includes: book, chapter, verse, selected versions
- Display history in dropdown menu or popup
- Click history item to re-project with same settings
- Clear history option (clears current session history)

**History Entry Format:**
```json
{
  "book": "John",
  "chapter": 3,
  "verse": 16,
  "versions": ["cuv", "kjv"],
  "timestamp": "2025-10-12T14:30:00Z"
}
```

---

### 3.4 General Projection Features

#### FR-GP-001: URL Projection
**Priority:** LOW
**Description:** Project any web URL to the projection window.

**Acceptance Criteria:**
- Accept any valid HTTP/HTTPS URL
- Auto-add https:// if protocol missing
- Validate URL format before projection
- Support localhost URLs for development
- Handle page load errors gracefully

**Supported URLs:**
- google.com → https://google.com
- https://youtube.com/watch?v=...
- localhost:3000
- 192.168.1.100:8080

---

#### FR-GP-002: Projection Toggle (Show/Hide)
**Priority:** HIGH
**Description:** Toggle projection window visibility without stopping projection.

**Acceptance Criteria:**
- Show/Hide button for each projection type
- Hide: minimize projection window or blank screen (native background)
- Show: restore projection window to full-screen
- Maintain projection state when hidden
- Visual indicator of current state (button label/color)

---

#### FR-GP-003: Keyboard Shortcuts
**Priority:** LOW
**Description:** Support keyboard shortcuts for common operations.

**Acceptance Criteria:**
- ESC: Exit full-screen / close projection
- Ctrl+Q / Ctrl+W: Close projection
- F11: Toggle full-screen mode
- Arrow keys: Navigate verses (when Bible is projected)
- Tab: Switch between input fields in control panel

---

### 3.5 Google Meet Integration

#### FR-GM-001: Automated Meeting Join
**Priority:** LOW
**Description:** Automatically join Google Meet and share screen.

**Acceptance Criteria:**
- Button in control panel: "Join Meet & Share Screen"
- Open Google Meet URL in browser
- Detect when meeting page loads
- Automatically click "Join now" button (if possible)
- Automatically click "Share screen" button
- Select projection window for sharing
- Handle authentication (user must be logged into Google)

**Technical Notes:**
- **Implementation:** Manual browser open only (webbrowser.open)
- Browser automation (Playwright) was attempted but removed due to unreliability
- Google Meet detects and blocks automation attempts
- Users must manually join meetings and share screen

---

#### FR-GM-002: Meeting URL Configuration
**Priority:** LOW
**Description:** Configure Google Meet URL in settings.

**Acceptance Criteria:**
- Settings dialog with Google Meet URL input
- Validate Google Meet URL format
- Persist URL in configuration
- Quick join button uses configured URL

---

## 4. User Interface Specifications

### 4.1 Main Control Panel Window (Hybrid Architecture)

#### 4.1.1 Window Properties
- **Native Window** (wxPython wx.Frame):
  - **Title:** "Webpage Projector - Control Panel"
  - **Size:** 800px × 900px (fixed size, not resizable)
  - **Position:** Center of primary display on startup
  - **Always on top:** Optional (user preference)
  - **Contains:** wx.html2.WebView (fills entire window)

- **Web UI** (HTML/CSS/JavaScript inside WebView):
  - **Technology:** Modern web technologies (HTML5, CSS3, ES6+)
  - **Styling:** Inspired by ncfnj.org/bible (clean, modern, responsive)
  - **Layout:** Vertical sections with proper spacing and visual hierarchy
  - **Communication:** JavaScript ↔ Python bridge for all interactions

#### 4.1.2 Layout Sections

**Section 1: URL Projection**
```
┌─────────────────────────────────────────────────────┐
│  URL Projection                                     │
├─────────────────────────────────────────────────────┤
│  URL: [________________________] [Project] [Hide]   │
│  Examples: google.com, youtube.com, localhost:3000  │
└─────────────────────────────────────────────────────┘
```

**Section 2: Google Slides Projection**
```
┌─────────────────────────────────────────────────────┐
│  Google Slides Presentation                         │
├─────────────────────────────────────────────────────┤
│  Hymn/Slides ID: [__________] [🎵] [Present] [Hide]│
│  Status: Enter hymn ID or Google Slides URL         │
└─────────────────────────────────────────────────────┘
```
- 🎵 button: Opens hymn dropdown menu

**Section 3: Bible Verses**
```
┌─────────────────────────────────────────────────────┐
│  Bible Verses                                       │
├─────────────────────────────────────────────────────┤
│  Verse: [__________] [×] [👁] [📜] [Project] [◀] [▶]│
│                                                     │
│  Versions: ☑ 和合本  ☐ KJV  ☐ NAS  ☐ NIV  ☐ Darby │
│                                                     │
│  Font Size - Chinese: [24 ▼]  English: [22 ▼]     │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  Chapter Preview: (empty)       [◀][▶]       │ │
│  │  ─────────────────────────────────────────── │ │
│  │  Click 👁 to load chapter preview            │ │
│  │  ↕ Scrollable area ↕                         │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```
- × button: Clear verse input
- 👁 button: Load chapter preview
- 📜 button: Show projection history
- ◀ ▶ buttons: Navigate verses (when projecting)

**Section 4: Google Meet (Optional)**
```
┌─────────────────────────────────────────────────────┐
│  Google Meet (Optional)                             │
├─────────────────────────────────────────────────────┤
│  [Join Meeting & Share Screen]                      │
└─────────────────────────────────────────────────────┘
```

**Section 5: Status Bar**
```
┌─────────────────────────────────────────────────────┐
│  Status: Ready to project                           │
│  Displays: 2 monitors detected - Ready for projection│
└─────────────────────────────────────────────────────┘
```

### 4.2 Projection Window

#### 4.2.1 Window Properties
- **Title:** "Webpage Projector - Projection"
- **Size:** Full-screen on target display
- **Style:** Borderless, no title bar, always on top
- **Background:** System desktop background (when not projecting)

#### 4.2.2 Content Rendering
- **Google Slides:** WebView rendering presentation in /present mode
- **Bible Verses:** HTML rendering with custom styling
- **Web URLs:** WebView rendering web page

---

## 5. Data Models

### 5.1 Bible Book Metadata

**File:** `books.csv`

**Format:**
```csv
'BookName':[book_id, chapter_count],
```

**Example:**
```csv
'Genesis创世记':[1, 50],
'Exodus出埃及记':[2, 40],
'John约翰福音':[43, 21],
```

**Fields:**
- `BookName`: English + Chinese name (used for lookup)
- `book_id`: Integer ID for file path (vol{book_id:02d})
- `chapter_count`: Number of chapters in book

### 5.2 Hymn Mapping

**File:** `hymns.csv`

**Format:**
```csv
HymnID,GoogleSlidesID
```

**Example:**
```csv
A01,1saIavtk49GG2zSinkdAgWltEba0xiRv7Cf5KbksYKwk
C002,1O6uLRuKGDsgkgtHSYw2HVfmYvEHDqziz_MiGaDKRsVg
```

### 5.3 Application Configuration

**File:** `config.json`

**Schema:**
```json
{
  "window": {
    "control_panel": {
      "width": 800,
      "height": 900,
      "x": null,
      "y": null
    }
  },
  "display": {
    "preferred_display_index": 1,
    "auto_detect": true
  },
  "bible": {
    "default_versions": ["cuv"],
    "font_size_chinese": 24,
    "font_size_english": 22
  },
  "history": {
    "bible_projections": [],
    "max_history_size": 20
  },
  "google_meet": {
    "meeting_url": ""
  }
}
```

---

## 6. Technical Requirements

### 6.1 Technology Stack

**Core Technologies:**
- **Python:** 3.12+
- **UI Framework:** wxPython 4.2+
- **Web Rendering:** wxPython WebView (uses platform WebView: WebKit on macOS, Edge on Windows)
- **Package Manager:** uv (for dependency management)
- **Display Detection:** screeninfo library

**Optional/Enhancement Technologies:**
- **Testing:** pytest
- **Packaging:** PyInstaller or cx_Freeze (for distribution)

### 6.2 Performance Requirements

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Application Startup | < 3 seconds | < 5 seconds |
| Projection Window Render | < 500ms | < 1 second |
| Bible Chapter Load | < 200ms | < 500ms |
| Memory Usage (Idle) | < 150MB | < 250MB |
| Memory Usage (Active) | < 300MB | < 500MB |
| CPU Usage (Idle) | < 2% | < 5% |

### 6.3 Platform Compatibility

**Primary Platform:** macOS 12+ (Monterey and later)

**Secondary Platforms:** Windows 10+, Linux (Ubuntu 20.04+)

**Platform-Specific Notes:**
- macOS: Use native WebKit for WebView
- Windows: Use Edge WebView2 (requires Edge WebView2 Runtime)
- Linux: Use WebKitGTK

### 6.4 Dependencies

**Core Dependencies:**
```toml
[project]
name = "webpage-projector"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "wxPython>=4.2.0",
    "screeninfo>=0.8.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

---

## 7. API & Integration

### 7.1 Bible File API

**Load Chapter:**
```python
def load_chapter(version: str, book_id: int, chapter: int) -> list[str]:
    """
    Load chapter verses from file.

    Args:
        version: Bible version code (cuv, kjv, nas, niv, dby)
        book_id: Book ID from books.csv
        chapter: Chapter number (1-indexed)

    Returns:
        List of verses (strings), one per line

    Raises:
        FileNotFoundError: If chapter file doesn't exist
        UnicodeDecodeError: If encoding is incorrect
    """
```

**Get Book Metadata:**
```python
def get_book_info(book_name: str) -> dict:
    """
    Get book metadata from books.csv.

    Args:
        book_name: Book name (case-insensitive, English or Chinese)

    Returns:
        {
            'book_id': int,
            'chapter_count': int,
            'name': str
        }

    Raises:
        KeyError: If book not found
    """
```

### 7.2 Google Slides API

**Convert to Presentation URL:**
```python
def get_presentation_url(slides_id: str) -> str:
    """
    Convert slides ID to presentation mode URL.

    Args:
        slides_id: Google Slides presentation ID

    Returns:
        Full presentation URL (https://docs.google.com/presentation/d/{ID}/present)
    """
```

**Lookup Hymn:**
```python
def lookup_hymn(hymn_id: str) -> str:
    """
    Lookup hymn ID in hymns.csv.

    Args:
        hymn_id: Hymn ID (case-insensitive)

    Returns:
        Google Slides ID for the hymn

    Raises:
        KeyError: If hymn ID not found
    """
```

---

## 8. Testing Strategy

### 8.1 Unit Testing

**Coverage Target:** 80% minimum

**Test Categories:**
- Bible parser (verse reference parsing)
- Book metadata loading
- Hymn ID lookup
- URL validation
- Configuration loading/saving

### 8.2 Integration Testing

**Test Scenarios:**
- Load Bible chapter and render to HTML
- Project Google Slides to secondary display
- Navigate between Bible verses
- History management (add, retrieve, clear)

### 8.3 Manual Testing

**Test Cases:**
- Multi-monitor setup (2+ displays)
- Single monitor fallback
- Display hot-plug (connect/disconnect during runtime)
- All keyboard shortcuts
- Font size changes
- Bible version selection combinations

---

## 9. Deployment & Distribution

### 9.1 Packaging

**Tool:** PyInstaller

**Output:**
- macOS: `.app` bundle
- Windows: `.exe` installer
- Linux: AppImage or .deb package

**Bundled Assets:**
- `books/` directory (all Bible text files)
- `hymns.csv`
- `books.csv`
- `config.json` (default configuration)

### 9.2 Installation Requirements

**macOS:**
- macOS 12+ (Monterey or later)
- No additional dependencies

**Windows:**
- Windows 10 or later
- Edge WebView2 Runtime (auto-installed if missing)

**Linux:**
- Ubuntu 20.04+ or equivalent
- WebKitGTK 2.0+

### 9.3 First Launch Setup

1. Application launches and creates default `config.json`
2. Detects available displays
3. If `books/` directory is missing, show warning
4. If `hymns.csv` is missing, disable hymn features
5. Load default settings

---

## 10. Future Enhancements

### 10.1 Planned Features (v2.0)
- [ ] Slide preview thumbnails
- [ ] Custom background images for Bible projection
- [ ] Text animations (fade in/out)
- [ ] Remote control via mobile app
- [ ] Cloud sync for history and settings
- [ ] PowerPoint presentation support
- [ ] Video projection support

### 10.2 Potential Integrations
- [ ] Planning Center Online integration
- [ ] ProPresenter compatibility
- [ ] OBS Studio integration (virtual camera)
- [ ] NDI output for video streaming

---

## Appendices

### A. File Structure

```
webpage_projector/
├── src/
│   ├── main.py                 # Application entry point
│   ├── ui/
│   │   ├── web/                # Web-based control panel (Hybrid Architecture)
│   │   │   ├── index.html      # Main HTML structure
│   │   │   ├── styles.css      # Modern CSS styling (inspired by ncfnj.org/bible)
│   │   │   ├── app.js          # Main JavaScript controller
│   │   │   ├── components/     # JavaScript modules
│   │   │   │   ├── bridge.js   # JavaScript ↔ Python communication
│   │   │   │   ├── url_controller.js     # URL projection UI
│   │   │   │   ├── slides_controller.js  # Google Slides UI
│   │   │   │   └── bible_controller.js   # Bible selection UI
│   │   │   └── assets/         # Images, icons, fonts
│   │   ├── main_window.py      # wxPython window with wx.html2.WebView
│   │   ├── web_controller.py   # WebView manager and message handlers
│   │   ├── projection_window.py # Native borderless projection window
│   │   └── dialogs.py          # Settings, history dialogs
│   ├── core/
│   │   ├── bible_engine.py     # Bible text loading and parsing
│   │   ├── display_manager.py  # Monitor detection and management
│   │   ├── content_renderer.py # HTML rendering for projection content
│   │   └── history_manager.py  # Projection history
│   ├── data/
│   │   ├── bible_repository.py # Bible file I/O
│   │   ├── slides_repository.py # Hymn lookup
│   │   └── config_manager.py   # Configuration persistence
│   └── utils/
│       ├── parsers.py          # Verse reference parsing
│       └── validators.py       # Input validation
├── books/                      # Bible text files (cuv, kjv, nas, niv, dby)
├── hymns.csv                   # Hymn to Slides ID mapping
├── books.csv                   # Bible book metadata
├── config.json                 # Application configuration
├── pyproject.toml              # Python project configuration
├── README.md                   # User documentation
└── tests/                      # Test suite
    ├── unit/
    │   ├── test_bible_engine.py
    │   ├── test_parsers.py
    │   └── ...
    ├── integration/
    │   ├── test_web_bridge.py  # Test JavaScript ↔ Python communication
    │   └── ...
    └── e2e/
        └── test_projection.py  # End-to-end projection tests
```

### B. Glossary

- **Control Panel:** Main application window with user controls
- **Projection Window:** Full-screen window displaying content on secondary display
- **Hymn ID:** Short identifier for hymn that maps to Google Slides presentation
- **Bible Version:** Translation of the Bible (e.g., KJV, NIV, CUV)
- **Chapter Preview:** Panel showing all verses in a chapter for selection
- **Projection History:** List of previously projected Bible verses

---

**End of Specification Document**