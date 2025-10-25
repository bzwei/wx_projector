#!/usr/bin/env python3
"""
Verse Reference Parsers
Parses Bible verse references in various formats
"""

import re
from typing import Optional, Dict, Tuple


class VerseReference:
    """Represents a parsed verse reference"""

    def __init__(self, book: Optional[str] = None, chapter: Optional[int] = None,
                 verse_start: Optional[int] = None, verse_end: Optional[int] = None):
        self.book = book
        self.chapter = chapter
        self.verse_start = verse_start
        self.verse_end = verse_end

    def is_single_verse(self) -> bool:
        """Check if this is a single verse reference"""
        return self.verse_start is not None and self.verse_end is None

    def is_verse_range(self) -> bool:
        """Check if this is a verse range"""
        return self.verse_start is not None and self.verse_end is not None

    def is_entire_chapter(self) -> bool:
        """Check if this is an entire chapter"""
        return self.chapter is not None and self.verse_start is None

    def __repr__(self):
        parts = []
        if self.book:
            parts.append(self.book)
        if self.chapter:
            parts.append(str(self.chapter))
        if self.verse_start:
            if self.verse_end:
                parts.append(f"{self.verse_start}-{self.verse_end}")
            else:
                parts.append(str(self.verse_start))
        return f"VerseReference({':'.join(parts)})"


def parse_verse_reference(reference: str, current_book: Optional[str] = None) -> Optional[VerseReference]:
    """
    Parse a verse reference string into components

    Supported formats:
    - "John 3:16" - full reference with book
    - "3:16" - chapter:verse (requires current_book)
    - "3 16" - chapter verse with space (requires current_book)
    - "1:1-5" - verse range
    - "13" - entire chapter (requires current_book)

    Args:
        reference: Verse reference string
        current_book: Current book context (for references without book name)

    Returns:
        VerseReference object, or None if parsing fails
    """
    reference = reference.strip()

    if not reference:
        return None

    # Pattern 1: "Book Chapter:Verse" or "Book Chapter:Verse-Verse"
    # e.g., "John 3:16" or "John 3:16-18"
    match = re.match(r'^([A-Za-z0-9\u4e00-\u9fff]+)\s+(\d+):(\d+)(?:-(\d+))?$', reference)
    if match:
        book = match.group(1)
        chapter = int(match.group(2))
        verse_start = int(match.group(3))
        verse_end = int(match.group(4)) if match.group(4) else None
        return VerseReference(book=book, chapter=chapter, verse_start=verse_start, verse_end=verse_end)

    # Pattern 2: "Chapter:Verse" or "Chapter:Verse-Verse" (requires current_book)
    # e.g., "3:16" or "3:16-18"
    match = re.match(r'^(\d+):(\d+)(?:-(\d+))?$', reference)
    if match:
        if not current_book:
            return None
        chapter = int(match.group(1))
        verse_start = int(match.group(2))
        verse_end = int(match.group(3)) if match.group(3) else None
        return VerseReference(book=current_book, chapter=chapter, verse_start=verse_start, verse_end=verse_end)

    # Pattern 3: "Chapter Verse" or "Chapter Verse-Verse" with space (requires current_book)
    # e.g., "3 16" or "3 2-7"
    match = re.match(r'^(\d+)\s+(\d+)(?:-(\d+))?$', reference)
    if match:
        if not current_book:
            return None
        chapter = int(match.group(1))
        verse_start = int(match.group(2))
        verse_end = int(match.group(3)) if match.group(3) else None
        return VerseReference(book=current_book, chapter=chapter, verse_start=verse_start, verse_end=verse_end)

    # Pattern 4: Just chapter number - entire chapter (requires current_book)
    # e.g., "13"
    match = re.match(r'^(\d+)$', reference)
    if match:
        if not current_book:
            return None
        chapter = int(match.group(1))
        return VerseReference(book=current_book, chapter=chapter)

    # No pattern matched
    return None


def load_books_metadata(books_csv_path: str = "books.csv") -> Dict[str, Tuple[int, int]]:
    """
    Load book metadata from books.csv

    Args:
        books_csv_path: Path to books.csv file

    Returns:
        Dict mapping book name to (book_id, chapter_count)
    """
    books = {}

    try:
        with open(books_csv_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse format: 'BookName':[book_id, chapter_count],
        # book_id can be "39+4" which needs to be evaluated
        pattern = r"'([^']+)':\s*\[([\d+\s]+),\s*(\d+)\]"
        matches = re.findall(pattern, content)

        for match in matches:
            book_name = match[0]
            # Evaluate book_id expression (e.g., "39+4" -> 43)
            book_id_expr = match[1].strip()
            book_id = eval(book_id_expr)  # Safe because we control the CSV format
            chapter_count = int(match[2])
            books[book_name] = (book_id, chapter_count)

    except FileNotFoundError:
        print(f"Warning: {books_csv_path} not found")

    return books


def get_book_id(book_name: str, books_metadata: Dict[str, Tuple[int, int]]) -> Optional[int]:
    """
    Get book ID from book name

    Args:
        book_name: Book name (English or Chinese, case-insensitive)
        books_metadata: Book metadata dict from load_books_metadata()

    Returns:
        Book ID, or None if not found
    """
    # Try exact match first (case-insensitive)
    for name, (book_id, _) in books_metadata.items():
        if name.lower() == book_name.lower():
            return book_id

    # Try partial match (English part or Chinese part)
    # Prioritize longer matches to avoid "John" matching "John1约翰一书" instead of "John约翰福音"
    book_name_lower = book_name.lower()
    matches = []

    for name, (book_id, _) in books_metadata.items():
        name_lower = name.lower()
        # Check if book_name matches at start of this book name
        if name_lower.startswith(book_name_lower):
            matches.append((name, book_id))

    # Sort by name length (shortest first) - prefer exact-like matches
    if matches:
        matches.sort(key=lambda x: len(x[0]))
        return matches[0][1]

    return None


def get_chapter_count(book_name: str, books_metadata: Dict[str, Tuple[int, int]]) -> Optional[int]:
    """
    Get chapter count for a book

    Args:
        book_name: Book name
        books_metadata: Book metadata dict

    Returns:
        Chapter count, or None if not found
    """
    for name, (_, chapter_count) in books_metadata.items():
        if name.lower() == book_name.lower():
            return chapter_count
    return None
