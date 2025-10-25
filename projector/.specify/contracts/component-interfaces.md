# Component Interfaces & Contracts

**Date**: 2025-10-12
**Phase**: 1
**Related**: [data-model.md](../data-model.md), [plan.md](../plan.md)

## Overview

This document defines the interfaces (contracts) for all major UI components in the Webpage Projector application. These interfaces specify:
- What data each component accepts
- What events each component emits
- What methods each component exposes
- How components interact with each other

---

## 1. Window Components

### 1.1 IMainWindow

**Purpose**: Main control panel window interface

```python
from abc import ABC, abstractmethod
from typing import Optional, Callable

class IMainWindow(ABC):
    """Main control panel window interface"""

    @abstractmethod
    def __init__(self, app_state: AppState):
        """
        Initialize main window

        Args:
            app_state: Application state container
        """
        pass

    @abstractmethod
    def show(self):
        """Display the main window"""
        pass

    @abstractmethod
    def close(self):
        """Close the main window"""
        pass

    @abstractmethod
    def update_status(self, message: str):
        """
        Update status bar message

        Args:
            message: Status message to display
        """
        pass

    @abstractmethod
    def update_display_info(self, displays: list[DisplayInfo]):
        """
        Update display information in status bar

        Args:
            displays: List of detected displays
        """
        pass

    # Event callbacks
    @abstractmethod
    def on_url_project(self, callback: Callable[[str], None]):
        """Register callback for URL projection button"""
        pass

    @abstractmethod
    def on_slides_project(self, callback: Callable[[str], None]):
        """Register callback for Slides projection button"""
        pass

    @abstractmethod
    def on_bible_project(self, callback: Callable[[BibleSelection], None]):
        """Register callback for Bible projection button"""
        pass

    @abstractmethod
    def on_projection_hide(self, callback: Callable[[], None]):
        """Register callback for hide projection button"""
        pass
```

---

### 1.2 IProjectionWindow

**Purpose**: Full-screen projection window interface

```python
class IProjectionWindow(ABC):
    """Projection window interface"""

    @abstractmethod
    def __init__(self, display_config: DisplayConfig):
        """
        Initialize projection window

        Args:
            display_config: Display configuration
        """
        pass

    @abstractmethod
    def show_content(self, content: ProjectionContent):
        """
        Display content in projection window

        Args:
            content: Content to project (Bible/URL/Slides)
        """
        pass

    @abstractmethod
    def show_blank(self):
        """Display blank screen (system background)"""
        pass

    @abstractmethod
    def show(self):
        """Show projection window"""
        pass

    @abstractmethod
    def hide(self):
        """Hide projection window (minimize or blank)"""
        pass

    @abstractmethod
    def close(self):
        """Close projection window"""
        pass

    @abstractmethod
    def set_fullscreen(self, fullscreen: bool):
        """
        Toggle fullscreen mode

        Args:
            fullscreen: True for fullscreen, False for windowed
        """
        pass

    @abstractmethod
    def move_to_display(self, display: DisplayInfo):
        """
        Move window to specific display

        Args:
            display: Target display
        """
        pass
```

---

## 2. Panel Components (Control Panel Sections)

### 2.1 IURLPanel

**Purpose**: URL projection section interface

```python
class IURLPanel(ABC):
    """URL projection panel interface"""

    @abstractmethod
    def __init__(self, parent: wx.Window):
        """
        Initialize URL panel

        Args:
            parent: Parent window
        """
        pass

    @abstractmethod
    def get_url(self) -> str:
        """Get current URL input value"""
        pass

    @abstractmethod
    def set_url(self, url: str):
        """Set URL input value"""
        pass

    @abstractmethod
    def clear_url(self):
        """Clear URL input"""
        pass

    @abstractmethod
    def show_error(self, message: str):
        """Show inline error message"""
        pass

    @abstractmethod
    def clear_error(self):
        """Clear error message"""
        pass

    # Event callbacks
    @abstractmethod
    def on_project_clicked(self, callback: Callable[[str], None]):
        """Register callback for Project button"""
        pass

    @abstractmethod
    def on_hide_clicked(self, callback: Callable[[], None]):
        """Register callback for Hide button"""
        pass
```

---

### 2.2 ISlidesPanel

**Purpose**: Google Slides projection section interface

```python
class ISlidesPanel(ABC):
    """Google Slides projection panel interface"""

    @abstractmethod
    def __init__(self, parent: wx.Window, hymns: dict[str, HymnInfo]):
        """
        Initialize Slides panel

        Args:
            parent: Parent window
            hymns: Dictionary of hymn ID -> HymnInfo
        """
        pass

    @abstractmethod
    def get_input(self) -> str:
        """Get current hymn/slides input value"""
        pass

    @abstractmethod
    def set_input(self, value: str):
        """Set hymn/slides input value"""
        pass

    @abstractmethod
    def clear_input(self):
        """Clear input"""
        pass

    @abstractmethod
    def show_error(self, message: str):
        """Show inline error message"""
        pass

    @abstractmethod
    def clear_error(self):
        """Clear error message"""
        pass

    @abstractmethod
    def show_hymn_dropdown(self):
        """Show dropdown menu with hymn list"""
        pass

    # Event callbacks
    @abstractmethod
    def on_project_clicked(self, callback: Callable[[str], None]):
        """Register callback for Present button"""
        pass

    @abstractmethod
    def on_hide_clicked(self, callback: Callable[[], None]):
        """Register callback for Hide button"""
        pass

    @abstractmethod
    def on_hymn_selected(self, callback: Callable[[str], None]):
        """Register callback for hymn selection from dropdown"""
        pass
```

---

### 2.3 IBiblePanel

**Purpose**: Bible verses section interface

```python
class IBiblePanel(ABC):
    """Bible verses panel interface"""

    @abstractmethod
    def __init__(self, parent: wx.Window, books: dict[str, BookInfo]):
        """
        Initialize Bible panel

        Args:
            parent: Parent window
            books: Dictionary of book name -> BookInfo
        """
        pass

    @abstractmethod
    def get_book(self) -> Optional[str]:
        """Get selected book name"""
        pass

    @abstractmethod
    def set_book(self, book: str):
        """Set selected book"""
        pass

    @abstractmethod
    def get_verse_input(self) -> str:
        """Get chapter+verse input value"""
        pass

    @abstractmethod
    def set_verse_input(self, value: str):
        """Set chapter+verse input value"""
        pass

    @abstractmethod
    def get_selected_versions(self) -> list[str]:
        """Get list of selected Bible versions"""
        pass

    @abstractmethod
    def set_selected_versions(self, versions: list[str]):
        """Set selected Bible versions"""
        pass

    @abstractmethod
    def get_font_sizes(self) -> FontConfig:
        """Get current font size configuration"""
        pass

    @abstractmethod
    def set_font_sizes(self, config: FontConfig):
        """Set font size configuration"""
        pass

    @abstractmethod
    def show_error(self, message: str):
        """Show inline error message"""
        pass

    @abstractmethod
    def clear_error(self):
        """Clear error message"""
        pass

    @abstractmethod
    def set_chapter_preview(self, preview: ChapterPreviewState):
        """Update chapter preview panel"""
        pass

    @abstractmethod
    def set_history_entries(self, entries: list[HistoryEntry]):
        """Update history dropdown"""
        pass

    # Event callbacks
    @abstractmethod
    def on_project_clicked(self, callback: Callable[[], None]):
        """Register callback for Project button"""
        pass

    @abstractmethod
    def on_clear_clicked(self, callback: Callable[[], None]):
        """Register callback for Clear button"""
        pass

    @abstractmethod
    def on_preview_clicked(self, callback: Callable[[], None]):
        """Register callback for Preview (👁) button"""
        pass

    @abstractmethod
    def on_history_clicked(self, callback: Callable[[], None]):
        """Register callback for History (📜) button"""
        pass

    @abstractmethod
    def on_prev_verse_clicked(self, callback: Callable[[], None]):
        """Register callback for Previous Verse (◀) button"""
        pass

    @abstractmethod
    def on_next_verse_clicked(self, callback: Callable[[], None]):
        """Register callback for Next Verse (▶) button"""
        pass

    @abstractmethod
    def on_version_changed(self, callback: Callable[[list[str]], None]):
        """Register callback for version selection change"""
        pass

    @abstractmethod
    def on_font_size_changed(self, callback: Callable[[FontConfig], None]):
        """Register callback for font size change"""
        pass
```

---

## 3. Sub-Components

### 3.1 IChapterPreview

**Purpose**: Chapter preview panel (embedded in Bible panel)

```python
class IChapterPreview(ABC):
    """Chapter preview panel interface"""

    @abstractmethod
    def __init__(self, parent: wx.Window):
        """Initialize chapter preview panel"""
        pass

    @abstractmethod
    def load_chapter(self, state: ChapterPreviewState):
        """
        Load chapter preview

        Args:
            state: Chapter preview state with verse texts
        """
        pass

    @abstractmethod
    def clear(self):
        """Clear chapter preview"""
        pass

    @abstractmethod
    def set_selected_verse(self, verse_number: int):
        """
        Highlight selected verse

        Args:
            verse_number: Verse number to highlight
        """
        pass

    @abstractmethod
    def get_selected_verse(self) -> Optional[int]:
        """Get currently selected verse number"""
        pass

    @abstractmethod
    def enable_prev_chapter(self, enabled: bool):
        """Enable/disable previous chapter button"""
        pass

    @abstractmethod
    def enable_next_chapter(self, enabled: bool):
        """Enable/disable next chapter button"""
        pass

    # Event callbacks
    @abstractmethod
    def on_verse_selected(self, callback: Callable[[int], None]):
        """Register callback for verse selection (double-click)"""
        pass

    @abstractmethod
    def on_prev_chapter_clicked(self, callback: Callable[[], None]):
        """Register callback for previous chapter button"""
        pass

    @abstractmethod
    def on_next_chapter_clicked(self, callback: Callable[[], None]):
        """Register callback for next chapter button"""
        pass
```

---

### 3.2 IHistoryPanel

**Purpose**: History dropdown/menu interface

```python
class IHistoryPanel(ABC):
    """Projection history panel interface"""

    @abstractmethod
    def __init__(self, parent: wx.Window):
        """Initialize history panel"""
        pass

    @abstractmethod
    def update_history(self, entries: list[HistoryEntry]):
        """
        Update history entries

        Args:
            entries: List of history entries (most recent first)
        """
        pass

    @abstractmethod
    def show_dropdown(self):
        """Show history dropdown menu"""
        pass

    @abstractmethod
    def clear_history(self):
        """Clear all history entries"""
        pass

    # Event callbacks
    @abstractmethod
    def on_history_selected(self, callback: Callable[[HistoryEntry], None]):
        """Register callback for history item selection"""
        pass

    @abstractmethod
    def on_clear_clicked(self, callback: Callable[[], None]):
        """Register callback for clear history"""
        pass
```

---

## 4. Content Rendering Components

### 4.1 IBibleRenderer

**Purpose**: Renders Bible verses to HTML for projection window

```python
class IBibleRenderer(ABC):
    """Bible content renderer interface"""

    @abstractmethod
    def render(
        self,
        verses: list[BibleVerse],
        reference: str,
        versions: list[str],
        font_config: FontConfig
    ) -> str:
        """
        Render Bible verses to HTML

        Args:
            verses: List of Bible verses with translations
            reference: Reference string (e.g., "John 3:16-17")
            versions: List of version codes to display
            font_config: Font size configuration

        Returns:
            HTML string for projection window
        """
        pass

    @abstractmethod
    def render_blank(self) -> str:
        """Render blank screen HTML"""
        pass
```

---

## 5. Backend Service Interfaces

### 5.1 IBibleEngine

**Purpose**: Loads and manages Bible text data

```python
class IBibleEngine(ABC):
    """Bible text loading and management interface"""

    @abstractmethod
    def __init__(self, books_dir: str, books_metadata: dict[str, BookInfo]):
        """
        Initialize Bible engine

        Args:
            books_dir: Path to books/ directory
            books_metadata: Dictionary of book metadata
        """
        pass

    @abstractmethod
    def load_chapter(
        self,
        book_id: int,
        chapter: int,
        versions: list[str]
    ) -> BibleChapter:
        """
        Load complete chapter with specified versions

        Args:
            book_id: Book ID (e.g., 43 for John)
            chapter: Chapter number
            versions: List of version codes (e.g., ["cuv", "kjv"])

        Returns:
            BibleChapter with all verses and translations

        Raises:
            FileNotFoundError: If chapter file doesn't exist
            ValueError: If version is invalid
        """
        pass

    @abstractmethod
    def load_verses(
        self,
        book_id: int,
        chapter: int,
        verse_start: int,
        verse_end: int,
        versions: list[str]
    ) -> list[BibleVerse]:
        """
        Load specific verse range

        Args:
            book_id: Book ID
            chapter: Chapter number
            verse_start: Starting verse number
            verse_end: Ending verse number
            versions: List of version codes

        Returns:
            List of BibleVerse objects

        Raises:
            FileNotFoundError: If chapter file doesn't exist
            IndexError: If verse number out of range
        """
        pass

    @abstractmethod
    def get_chapter_preview(
        self,
        book_id: int,
        chapter: int,
        preview_version: str = "kjv"
    ) -> list[str]:
        """
        Get chapter preview text for display in preview panel

        Args:
            book_id: Book ID
            chapter: Chapter number
            preview_version: Version to use for preview

        Returns:
            List of formatted verse strings (e.g., ["1. In the beginning...", ...])
        """
        pass

    @abstractmethod
    def validate_reference(
        self,
        book_id: int,
        chapter: int,
        verse: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate Bible reference

        Args:
            book_id: Book ID
            chapter: Chapter number
            verse: Verse number (optional)

        Returns:
            ValidationResult with error message if invalid
        """
        pass
```

---

### 5.2 IDisplayManager

**Purpose**: Manages display detection and window placement

```python
class IDisplayManager(ABC):
    """Display detection and management interface"""

    @abstractmethod
    def __init__(self):
        """Initialize display manager"""
        pass

    @abstractmethod
    def detect_displays(self) -> list[DisplayInfo]:
        """
        Detect all connected displays

        Returns:
            List of DisplayInfo objects
        """
        pass

    @abstractmethod
    def get_primary_display(self) -> DisplayInfo:
        """Get primary display info"""
        pass

    @abstractmethod
    def get_secondary_display(self) -> Optional[DisplayInfo]:
        """Get secondary display info (None if only 1 display)"""
        pass

    @abstractmethod
    def get_recommended_projection_display(self) -> DisplayInfo:
        """
        Get recommended display for projection

        Returns:
            Secondary display if available, otherwise primary
        """
        pass

    @abstractmethod
    def should_use_fullscreen(self) -> bool:
        """
        Determine if fullscreen should be used

        Returns:
            True if 2+ displays, False if 1 display
        """
        pass
```

---

### 5.3 IHistoryManager

**Purpose**: Manages projection history

```python
class IHistoryManager(ABC):
    """Projection history manager interface"""

    @abstractmethod
    def __init__(self, max_size: int = 30):
        """
        Initialize history manager

        Args:
            max_size: Maximum number of history entries (default 30)
        """
        pass

    @abstractmethod
    def add_entry(self, entry: HistoryEntry):
        """
        Add entry to history

        Args:
            entry: History entry to add
        """
        pass

    @abstractmethod
    def get_history(self) -> list[HistoryEntry]:
        """
        Get all history entries

        Returns:
            List of entries (most recent first)
        """
        pass

    @abstractmethod
    def clear_history(self):
        """Clear all history entries"""
        pass

    @abstractmethod
    def get_recent(self, count: int) -> list[HistoryEntry]:
        """
        Get N most recent entries

        Args:
            count: Number of entries to retrieve

        Returns:
            List of recent entries
        """
        pass
```

---

### 5.4 IConfigManager

**Purpose**: Manages application configuration persistence

```python
class IConfigManager(ABC):
    """Configuration persistence manager interface"""

    @abstractmethod
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize config manager

        Args:
            config_path: Path to config file
        """
        pass

    @abstractmethod
    def load_config(self) -> AppState:
        """
        Load configuration from file

        Returns:
            AppState loaded from config file (or default if not exists)
        """
        pass

    @abstractmethod
    def save_config(self, state: AppState):
        """
        Save configuration to file

        Args:
            state: AppState to save
        """
        pass

    @abstractmethod
    def get_default_config(self) -> AppState:
        """
        Get default configuration

        Returns:
            AppState with default values
        """
        pass
```

---

## 6. Repository Interfaces

### 6.1 IBibleRepository

**Purpose**: Low-level Bible file I/O

```python
class IBibleRepository(ABC):
    """Bible file repository interface"""

    @abstractmethod
    def __init__(self, books_dir: str):
        """
        Initialize repository

        Args:
            books_dir: Path to books/ directory
        """
        pass

    @abstractmethod
    def read_chapter_file(
        self,
        version: str,
        book_id: int,
        chapter: int
    ) -> list[str]:
        """
        Read chapter file and return verses

        Args:
            version: Version code (cuv, kjv, etc.)
            book_id: Book ID
            chapter: Chapter number

        Returns:
            List of verse strings (one per line)

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If encoding is wrong
        """
        pass

    @abstractmethod
    def chapter_exists(
        self,
        version: str,
        book_id: int,
        chapter: int
    ) -> bool:
        """Check if chapter file exists"""
        pass
```

---

### 6.2 ISlidesRepository

**Purpose**: Hymn and Google Slides lookup

```python
class ISlidesRepository(ABC):
    """Hymn/Slides repository interface"""

    @abstractmethod
    def __init__(self, hymns_csv_path: str):
        """
        Initialize repository

        Args:
            hymns_csv_path: Path to hymns.csv
        """
        pass

    @abstractmethod
    def load_hymns(self) -> dict[str, HymnInfo]:
        """
        Load all hymns from CSV

        Returns:
            Dictionary of hymn ID (uppercase) -> HymnInfo
        """
        pass

    @abstractmethod
    def get_hymn(self, hymn_id: str) -> Optional[HymnInfo]:
        """
        Get hymn by ID (case-insensitive)

        Args:
            hymn_id: Hymn ID (e.g., "A01", "a01")

        Returns:
            HymnInfo or None if not found
        """
        pass

    @abstractmethod
    def hymn_exists(self, hymn_id: str) -> bool:
        """Check if hymn ID exists"""
        pass
```

---

## 7. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        MainWindow                            │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │  URLPanel    │  │ SlidesPanel │  │  BiblePanel     │   │
│  └──────┬───────┘  └──────┬──────┘  └────────┬────────┘   │
│         │                  │                  │             │
│         │ on_project       │ on_project       │ on_project  │
│         ▼                  ▼                  ▼             │
│    ┌──────────────────────────────────────────────┐        │
│    │          Event Handlers (in MainWindow)      │        │
│    └────────────────────┬─────────────────────────┘        │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │      Backend Services               │
        │  ┌────────────────────────────┐    │
        │  │    BibleEngine             │    │
        │  │  - load_verses()           │    │
        │  │  - load_chapter()          │    │
        │  └────────────────────────────┘    │
        │  ┌────────────────────────────┐    │
        │  │    DisplayManager          │    │
        │  │  - detect_displays()       │    │
        │  └────────────────────────────┘    │
        │  ┌────────────────────────────┐    │
        │  │    HistoryManager          │    │
        │  │  - add_entry()             │    │
        │  └────────────────────────────┘    │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   ProjectionWindow          │
        │  - show_content()           │
        │  - set_fullscreen()         │
        └─────────────────────────────┘
```

---

## 8. Contract Summary

### Phase 2 (UI with Mocks)
- Implement: `IMainWindow`, `IURLPanel`, `ISlidesPanel`, `IBiblePanel`
- Mock: All backend services return hardcoded data

### Phase 3 (More UI)
- Implement: `IProjectionWindow`, `IChapterPreview`, `IHistoryPanel`, `IBibleRenderer`
- Mock: Still using mock Bible data

### Phase 4 (Display & Validation)
- Implement: `IDisplayManager`, validators, parsers
- Mock: `IBibleEngine` still returns mock data

### Phase 5 (Bible Backend)
- Implement: `IBibleEngine`, `IBibleRepository`
- Real: Bible text loading from files

### Phase 6 (Slides & Web)
- Implement: WebView integration in `IProjectionWindow`
- Implement: `ISlidesRepository`

### Phase 7 (Config & History)
- Implement: `IHistoryManager`, `IConfigManager`
- Real: Persistence layer

---

**Next**: Create quickstart.md for development setup