# Data Models - UI State Management

**Date**: 2025-10-12
**Phase**: 1
**Related**: [plan.md](./plan.md), [research.md](./research.md)

## Overview

This document defines all data models for the Webpage Projector application, focusing on UI state management. These models represent the data structures that flow through the application and determine what is displayed in the UI.

---

## 1. Core Application State

### 1.1 AppState

**Purpose**: Central state container for entire application

```python
from typing import Optional, Literal
from dataclasses import dataclass, field

@dataclass
class AppState:
    """Main application state container"""

    # Current projection mode
    current_projection: Optional[Literal["url", "slides", "bible"]] = None

    # Bible selection state
    bible_selection: 'BibleSelection' = field(default_factory=lambda: BibleSelection())

    # Font configuration
    font_config: 'FontConfig' = field(default_factory=lambda: FontConfig())

    # Display configuration
    display_config: 'DisplayConfig' = field(default_factory=lambda: DisplayConfig())

    # Projection history
    history: list['HistoryEntry'] = field(default_factory=list)

    # Window states
    projection_window_visible: bool = False
    control_panel_position: Optional[tuple[int, int]] = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON config persistence"""
        return {
            "bible_selection": self.bible_selection.to_dict(),
            "font_config": self.font_config.to_dict(),
            "display_config": self.display_config.to_dict(),
            "control_panel_position": self.control_panel_position,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppState':
        """Deserialize from JSON config"""
        state = cls()
        if "bible_selection" in data:
            state.bible_selection = BibleSelection.from_dict(data["bible_selection"])
        if "font_config" in data:
            state.font_config = FontConfig.from_dict(data["font_config"])
        if "display_config" in data:
            state.display_config = DisplayConfig.from_dict(data["display_config"])
        if "control_panel_position" in data:
            state.control_panel_position = tuple(data["control_panel_position"])
        return state
```

---

## 2. Bible-Related Models

### 2.1 BibleSelection

**Purpose**: Represents current Bible verse selection and preferences

```python
@dataclass
class BibleSelection:
    """Current Bible verse selection state"""

    book: Optional[str] = None  # e.g., "John约翰福音"
    book_id: Optional[int] = None  # e.g., 43 (for file path)
    chapter: Optional[int] = None  # e.g., 3
    verse_start: Optional[int] = None  # e.g., 16
    verse_end: Optional[int] = None  # e.g., 17 (None = single verse)

    # Selected Bible versions
    versions: list[str] = field(default_factory=lambda: ["cuv"])

    # Progressive loading state
    loaded_verse_start: Optional[int] = None  # First loaded verse
    loaded_verse_end: Optional[int] = None  # Last loaded verse

    def to_dict(self) -> dict:
        return {
            "book": self.book,
            "book_id": self.book_id,
            "chapter": self.chapter,
            "verse_start": self.verse_start,
            "verse_end": self.verse_end,
            "versions": self.versions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BibleSelection':
        return cls(
            book=data.get("book"),
            book_id=data.get("book_id"),
            chapter=data.get("chapter"),
            verse_start=data.get("verse_start"),
            verse_end=data.get("verse_end"),
            versions=data.get("versions", ["cuv"]),
        )

    def get_reference_string(self) -> str:
        """Get human-readable reference (e.g., 'John 3:16-17')"""
        if not self.book or not self.chapter:
            return ""

        # Extract English book name (before Chinese)
        book_english = self.book.split('约')[0].split('创')[0].split('出')[0].strip()
        if not book_english:
            book_english = self.book  # Fallback to full name

        if self.verse_start is None:
            return f"{book_english} {self.chapter}"  # Entire chapter
        elif self.verse_end is None or self.verse_end == self.verse_start:
            return f"{book_english} {self.chapter}:{self.verse_start}"  # Single verse
        else:
            return f"{book_english} {self.chapter}:{self.verse_start}-{self.verse_end}"  # Range
```

---

### 2.2 BibleVerseRequest

**Purpose**: Request object for loading Bible verses

```python
@dataclass
class BibleVerseRequest:
    """Request to load Bible verses from files"""

    version: str  # e.g., "cuv", "kjv", "niv"
    book_id: int  # e.g., 43 (John)
    chapter: int  # e.g., 3
    verse_start: int  # e.g., 16
    verse_end: int  # e.g., 17

    def get_file_path(self) -> str:
        """Get file path for this chapter"""
        return f"books/{self.version}/vol{self.book_id:02d}/chap{self.chapter:03d}.txt"
```

---

### 2.3 BibleVerse

**Purpose**: Represents a single verse with multiple version translations

```python
@dataclass
class BibleVerse:
    """A single Bible verse with multiple version translations"""

    verse_number: int  # e.g., 16
    translations: dict[str, str]  # e.g., {"cuv": "神爱世人...", "kjv": "For God so loved..."}

    def get_translation(self, version: str) -> Optional[str]:
        """Get translation for specific version"""
        return self.translations.get(version)

    def has_version(self, version: str) -> bool:
        """Check if verse has translation for version"""
        return version in self.translations
```

---

### 2.4 BibleChapter

**Purpose**: Represents a complete chapter with all verses

```python
@dataclass
class BibleChapter:
    """Complete Bible chapter data"""

    book: str  # e.g., "John约翰福音"
    book_id: int  # e.g., 43
    chapter: int  # e.g., 3
    verses: list[BibleVerse]  # List of verses in order

    def get_verse(self, verse_number: int) -> Optional[BibleVerse]:
        """Get specific verse by number"""
        for verse in self.verses:
            if verse.verse_number == verse_number:
                return verse
        return None

    def get_verse_range(self, start: int, end: int) -> list[BibleVerse]:
        """Get range of verses"""
        return [v for v in self.verses if start <= v.verse_number <= end]

    def verse_count(self) -> int:
        """Total number of verses in chapter"""
        return len(self.verses)
```

---

### 2.5 ChapterPreviewState

**Purpose**: State for chapter preview panel in control panel

```python
@dataclass
class ChapterPreviewState:
    """State for chapter preview panel"""

    book: Optional[str] = None
    book_id: Optional[int] = None
    chapter: Optional[int] = None
    max_chapter: Optional[int] = None  # Total chapters in book

    # Loaded verse preview texts (formatted for display)
    verse_previews: list[str] = field(default_factory=list)  # e.g., ["1. In the beginning...", "2. And the earth..."]

    # Currently selected verse in preview
    selected_verse: Optional[int] = None

    # Version to use for preview (default: first selected version)
    preview_version: str = "kjv"

    def can_go_previous_chapter(self) -> bool:
        """Check if can navigate to previous chapter"""
        return self.chapter is not None and self.chapter > 1

    def can_go_next_chapter(self) -> bool:
        """Check if can navigate to next chapter"""
        return self.chapter is not None and self.max_chapter is not None and self.chapter < self.max_chapter

    def get_preview_title(self) -> str:
        """Get preview panel title"""
        if not self.book or not self.chapter:
            return "Chapter Preview"

        book_english = self.book.split('约')[0].split('创')[0].split('出')[0].strip()
        if not book_english:
            book_english = self.book

        return f"{book_english} {self.chapter}"
```

---

## 3. Display & Projection Models

### 3.1 DisplayConfig

**Purpose**: Display and projection window configuration

```python
@dataclass
class DisplayConfig:
    """Display and projection configuration"""

    # Target display index (0 = primary, 1 = secondary, etc.)
    target_display_index: int = 1

    # Auto-detect best display
    auto_detect: bool = True

    # Fullscreen mode
    fullscreen: bool = True

    # Detected displays (populated at runtime)
    available_displays: list['DisplayInfo'] = field(default_factory=list)

    def get_target_display(self) -> Optional['DisplayInfo']:
        """Get target display info"""
        if self.target_display_index < len(self.available_displays):
            return self.available_displays[self.target_display_index]
        return None

    def should_use_fullscreen(self) -> bool:
        """Determine if fullscreen should be used"""
        # Only fullscreen if 2+ displays available
        return self.fullscreen and len(self.available_displays) >= 2

    def to_dict(self) -> dict:
        return {
            "target_display_index": self.target_display_index,
            "auto_detect": self.auto_detect,
            "fullscreen": self.fullscreen,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DisplayConfig':
        return cls(
            target_display_index=data.get("target_display_index", 1),
            auto_detect=data.get("auto_detect", True),
            fullscreen=data.get("fullscreen", True),
        )
```

---

### 3.2 DisplayInfo

**Purpose**: Information about a single display/monitor

```python
@dataclass
class DisplayInfo:
    """Information about a physical display"""

    index: int  # Display index (0, 1, 2, ...)
    name: str  # e.g., "Display 1", "Built-in Retina Display"
    width: int  # Resolution width
    height: int  # Resolution height
    x: int  # Position X
    y: int  # Position Y
    is_primary: bool  # Is this the primary display?

    def get_resolution_string(self) -> str:
        """Get resolution as string"""
        return f"{self.width}×{self.height}"

    def get_position_string(self) -> str:
        """Get position as string"""
        return f"({self.x}, {self.y})"

    def get_display_label(self) -> str:
        """Get user-friendly display label"""
        primary_tag = " (Primary)" if self.is_primary else ""
        return f"{self.name} - {self.get_resolution_string()}{primary_tag}"
```

---

### 3.3 ProjectionContent

**Purpose**: Content to be displayed in projection window

```python
from typing import Union

@dataclass
class ProjectionContent:
    """Content for projection window"""

    content_type: Literal["url", "slides", "bible", "blank"]

    # URL/Slides content
    url: Optional[str] = None

    # Bible content
    bible_verses: Optional[list[BibleVerse]] = None
    bible_reference: Optional[str] = None  # e.g., "John 3:16-17"
    bible_versions: Optional[list[str]] = None  # e.g., ["cuv", "kjv"]
    font_config: Optional['FontConfig'] = None

    def is_bible(self) -> bool:
        return self.content_type == "bible"

    def is_web(self) -> bool:
        return self.content_type in ["url", "slides"]

    def is_blank(self) -> bool:
        return self.content_type == "blank"
```

---

## 4. History Models

### 4.1 HistoryEntry

**Purpose**: Single entry in projection history

```python
from datetime import datetime

@dataclass
class HistoryEntry:
    """Single projection history entry"""

    # Type of projection
    projection_type: Literal["url", "slides", "bible"]

    # Bible-specific fields
    bible_reference: Optional[str] = None  # e.g., "John 3:16"
    bible_versions: Optional[list[str]] = None  # e.g., ["cuv", "kjv"]

    # Slides-specific fields
    hymn_id: Optional[str] = None  # e.g., "A01"
    slides_id: Optional[str] = None

    # URL-specific fields
    url: Optional[str] = None

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    def get_display_string(self) -> str:
        """Get human-readable display string for history dropdown"""
        time_str = self.timestamp.strftime("%H:%M")

        if self.projection_type == "bible":
            versions_str = ", ".join(self.bible_versions) if self.bible_versions else ""
            return f"{self.bible_reference} ({versions_str}) - {time_str}"

        elif self.projection_type == "slides":
            return f"Hymn {self.hymn_id} - {time_str}"

        elif self.projection_type == "url":
            # Truncate long URLs
            url_display = self.url[:40] + "..." if len(self.url) > 40 else self.url
            return f"{url_display} - {time_str}"

        return f"Unknown - {time_str}"

    def to_dict(self) -> dict:
        return {
            "projection_type": self.projection_type,
            "bible_reference": self.bible_reference,
            "bible_versions": self.bible_versions,
            "hymn_id": self.hymn_id,
            "slides_id": self.slides_id,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryEntry':
        return cls(
            projection_type=data["projection_type"],
            bible_reference=data.get("bible_reference"),
            bible_versions=data.get("bible_versions"),
            hymn_id=data.get("hymn_id"),
            slides_id=data.get("slides_id"),
            url=data.get("url"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
```

---

## 5. Font & Styling Models

### 5.1 FontConfig

**Purpose**: Font size configuration for Bible projection

```python
@dataclass
class FontConfig:
    """Font configuration for Bible text projection"""

    chinese_size: int = 24  # Font size for Chinese text (px)
    english_size: int = 22  # Font size for English text (px)

    # Font size constraints
    MIN_SIZE: int = 16
    MAX_SIZE: int = 40

    def validate_sizes(self):
        """Ensure font sizes are within valid range"""
        self.chinese_size = max(self.MIN_SIZE, min(self.MAX_SIZE, self.chinese_size))
        self.english_size = max(self.MIN_SIZE, min(self.MAX_SIZE, self.english_size))

    def to_dict(self) -> dict:
        return {
            "chinese_size": self.chinese_size,
            "english_size": self.english_size,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FontConfig':
        config = cls(
            chinese_size=data.get("chinese_size", 24),
            english_size=data.get("english_size", 22),
        )
        config.validate_sizes()
        return config
```

---

## 6. Input Parsing Models

### 6.1 VerseReferenceInput

**Purpose**: Parsed verse reference input from user

```python
@dataclass
class VerseReferenceInput:
    """Parsed verse reference from chapter+verse input field"""

    raw_input: str  # Original input string
    chapter: Optional[int] = None
    verse_start: Optional[int] = None
    verse_end: Optional[int] = None
    is_valid: bool = False
    error_message: Optional[str] = None

    @classmethod
    def parse(cls, input_str: str) -> 'VerseReferenceInput':
        """Parse chapter+verse input like '3:16', '3:16-17', '13', '1:1-3'"""
        import re

        result = cls(raw_input=input_str.strip())

        if not result.raw_input:
            result.error_message = "Please enter chapter and verse"
            return result

        # Pattern 1: "chapter:verse-verse" or "chapter:verse"
        match = re.match(r'^(\d+):(\d+)(?:-(\d+))?$', result.raw_input)
        if match:
            result.chapter = int(match.group(1))
            result.verse_start = int(match.group(2))
            result.verse_end = int(match.group(3)) if match.group(3) else result.verse_start
            result.is_valid = True
            return result

        # Pattern 2: "chapter verse-verse" or "chapter verse" (space separator)
        match = re.match(r'^(\d+)\s+(\d+)(?:-(\d+))?$', result.raw_input)
        if match:
            result.chapter = int(match.group(1))
            result.verse_start = int(match.group(2))
            result.verse_end = int(match.group(3)) if match.group(3) else result.verse_start
            result.is_valid = True
            return result

        # Pattern 3: "chapter" only (entire chapter)
        match = re.match(r'^(\d+)$', result.raw_input)
        if match:
            result.chapter = int(match.group(1))
            result.verse_start = None  # None means entire chapter
            result.verse_end = None
            result.is_valid = True
            return result

        # Invalid format
        result.error_message = "Invalid format. Use: '3:16', '3:16-17', or '13'"
        return result
```

---

## 7. Lookup Models

### 7.1 BookInfo

**Purpose**: Bible book metadata from books.csv

```python
@dataclass
class BookInfo:
    """Bible book metadata"""

    name: str  # e.g., "John约翰福音"
    book_id: int  # e.g., 43
    chapter_count: int  # e.g., 21

    def get_english_name(self) -> str:
        """Extract English book name"""
        # Simple heuristic: take text before first Chinese character
        for i, char in enumerate(self.name):
            if '\u4e00' <= char <= '\u9fff':  # Chinese Unicode range
                return self.name[:i].strip()
        return self.name

    def get_chinese_name(self) -> str:
        """Extract Chinese book name"""
        for i, char in enumerate(self.name):
            if '\u4e00' <= char <= '\u9fff':
                return self.name[i:].strip()
        return ""
```

---

### 7.2 HymnInfo

**Purpose**: Hymn lookup data from hymns.csv

```python
@dataclass
class HymnInfo:
    """Hymn metadata"""

    hymn_id: str  # e.g., "A01", "C002"
    slides_id: str  # Google Slides presentation ID
    name: Optional[str] = None  # Optional hymn name

    def get_presentation_url(self) -> str:
        """Get Google Slides presentation URL"""
        return f"https://docs.google.com/presentation/d/{self.slides_id}/present"
```

---

## 8. Validation Models

### 8.1 ValidationResult

**Purpose**: Generic validation result

```python
@dataclass
class ValidationResult:
    """Result of input validation"""

    is_valid: bool
    error_message: Optional[str] = None
    value: Optional[any] = None  # Validated/parsed value

    @classmethod
    def success(cls, value: any = None) -> 'ValidationResult':
        return cls(is_valid=True, value=value)

    @classmethod
    def error(cls, message: str) -> 'ValidationResult':
        return cls(is_valid=False, error_message=message)
```

---

## 9. Model Usage Examples

### Example 1: Creating Bible Selection
```python
# User selects "John 3:16-17" with CUV and KJV
selection = BibleSelection(
    book="John约翰福音",
    book_id=43,
    chapter=3,
    verse_start=16,
    verse_end=17,
    versions=["cuv", "kjv"]
)

print(selection.get_reference_string())  # "John 3:16-17"
```

### Example 2: Parsing Verse Input
```python
# User enters "3:16" in chapter+verse field
parsed = VerseReferenceInput.parse("3:16")
if parsed.is_valid:
    print(f"Chapter: {parsed.chapter}, Verse: {parsed.verse_start}")
else:
    print(f"Error: {parsed.error_message}")
```

### Example 3: Creating History Entry
```python
# User projects John 3:16
entry = HistoryEntry(
    projection_type="bible",
    bible_reference="John 3:16",
    bible_versions=["cuv", "kjv"]
)

print(entry.get_display_string())  # "John 3:16 (cuv, kjv) - 14:30"
```

### Example 4: Display Detection
```python
# System detects displays
displays = [
    DisplayInfo(index=0, name="Built-in Display", width=1920, height=1080,
                x=0, y=0, is_primary=True),
    DisplayInfo(index=1, name="External Display", width=1920, height=1080,
                x=1920, y=0, is_primary=False),
]

config = DisplayConfig(available_displays=displays)
target = config.get_target_display()  # Returns Display 1 (external)
print(config.should_use_fullscreen())  # True (2 displays)
```

---

## 10. State Transitions

### Application State Flow

```
┌──────────────────┐
│   App Startup    │
│ (Load config.json)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  AppState Init   │◄──────────┐
│ - No projection  │            │
│ - Default fonts  │            │
│ - Detect displays│            │
└────────┬─────────┘            │
         │                      │
         ▼                      │
┌──────────────────┐            │
│  User Selects    │            │
│  Content Type    │            │
│ (URL/Slides/Bible)│            │
└────────┬─────────┘            │
         │                      │
         ▼                      │
┌──────────────────┐            │
│  Validate Input  │            │
│ (Parsers/Validators)          │
└────────┬─────────┘            │
         │                      │
         ├─ Invalid ────────────┘
         │
         ▼ Valid
┌──────────────────┐
│  Load Content    │
│ (Bible/Slides/URL)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Update AppState  │
│ - current_projection │
│ - Add to history │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Render Projection│
│    Window        │
└──────────────────┘
```

---

## Summary

This data model provides:

✅ **Clear state management** with `AppState` as single source of truth
✅ **Type-safe models** using Python dataclasses
✅ **JSON serialization** for config persistence
✅ **Validation support** with `ValidationResult`
✅ **UI-friendly methods** for display strings and formatting
✅ **Separation of concerns** between data, logic, and UI

**Next**: Create component contracts defining how these models are used by UI components.