#!/usr/bin/env python3
"""
Bible Engine - High-level API for loading and formatting Bible verses
Orchestrates repository, parsers, and rendering
"""

from typing import List, Dict, Optional, Tuple
from data.bible_repository import BibleRepository
from utils.parsers import (
    parse_verse_reference,
    load_books_metadata,
    get_book_id,
    get_chapter_count
)


class BibleEngine:
    """High-level interface for Bible verse operations"""

    def __init__(self, books_dir: str = "books", books_csv: str = "books.csv"):
        """
        Initialize Bible engine

        Args:
            books_dir: Directory containing Bible version folders
            books_csv: Path to books metadata CSV
        """
        self.repository = BibleRepository(books_dir)
        self.books_metadata = load_books_metadata(books_csv)

    def get_verse_data(self, book_name: str, chapter: int, verse: int, versions: List[str]) -> Dict[str, str]:
        """
        Get a single verse from multiple versions

        Args:
            book_name: Book name (English or Chinese)
            chapter: Chapter number
            verse: Verse number (1-indexed)
            versions: List of version codes (e.g., ['cuv', 'kjv'])

        Returns:
            Dict mapping version code to verse text
            Example: {'cuv': '神爱世人...', 'kjv': 'For God so loved...'}
        """
        book_id = get_book_id(book_name, self.books_metadata)
        if not book_id:
            return {}

        result = {}
        for version in versions:
            verse_text = self.repository.get_verse(version, book_id, chapter, verse)
            if verse_text:
                result[version] = verse_text

        return result

    def get_verse_range_data(self, book_name: str, chapter: int,
                            verse_start: int, verse_end: int,
                            versions: List[str]) -> List[Dict[str, str]]:
        """
        Get a range of verses from multiple versions

        Args:
            book_name: Book name
            chapter: Chapter number
            verse_start: Starting verse (1-indexed, inclusive)
            verse_end: Ending verse (1-indexed, inclusive)
            versions: List of version codes

        Returns:
            List of dicts, one per verse, each mapping version code to verse text
            Example: [
                {'verse': 16, 'cuv': '...', 'kjv': '...'},
                {'verse': 17, 'cuv': '...', 'kjv': '...'}
            ]
        """
        book_id = get_book_id(book_name, self.books_metadata)
        if not book_id:
            return []

        result = []
        for verse_num in range(verse_start, verse_end + 1):
            verse_data = {'verse': verse_num}
            for version in versions:
                verse_text = self.repository.get_verse(version, book_id, chapter, verse_num)
                if verse_text:
                    verse_data[version] = verse_text
            result.append(verse_data)

        return result

    def get_chapter_data(self, book_name: str, chapter: int, versions: List[str]) -> List[Dict[str, str]]:
        """
        Get entire chapter from multiple versions

        Args:
            book_name: Book name
            chapter: Chapter number
            versions: List of version codes

        Returns:
            List of verse dicts with all versions
        """
        book_id = get_book_id(book_name, self.books_metadata)
        if not book_id:
            return []

        # Get verse count from first version
        verse_count = self.repository.get_chapter_verse_count(versions[0], book_id, chapter)
        if verse_count == 0:
            return []

        return self.get_verse_range_data(book_name, chapter, 1, verse_count, versions)

    def get_chapter_preview(self, book_name: str, chapter: int, version: str = 'kjv') -> List[Tuple[int, str]]:
        """
        Get chapter preview for UI (single version, all verses)

        Args:
            book_name: Book name
            chapter: Chapter number
            version: Version to use for preview (default: kjv)

        Returns:
            List of (verse_number, verse_text) tuples
        """
        book_id = get_book_id(book_name, self.books_metadata)
        if not book_id:
            return []

        try:
            verses = self.repository.load_chapter(version, book_id, chapter)
            return [(i + 1, verse) for i, verse in enumerate(verses)]
        except Exception:
            return []

    def parse_and_get_verses(self, reference: str, current_book: Optional[str],
                            versions: List[str]) -> Tuple[Optional[str], Optional[int], List[Dict[str, str]]]:
        """
        Parse reference and get verse data

        Args:
            reference: Verse reference string (e.g., "John 3:16", "3:16-18", "13")
            current_book: Current book context (for references without book name)
            versions: List of version codes

        Returns:
            Tuple of (book_name, chapter, verse_data_list)
            book_name: Resolved book name
            chapter: Chapter number
            verse_data_list: List of verse dicts
        """
        parsed = parse_verse_reference(reference, current_book)
        if not parsed:
            return None, None, []

        book = parsed.book or current_book
        if not book:
            return None, None, []

        chapter = parsed.chapter

        if parsed.is_entire_chapter():
            # Load entire chapter
            verse_data = self.get_chapter_data(book, chapter, versions)
        elif parsed.is_verse_range():
            # Load verse range
            verse_data = self.get_verse_range_data(book, chapter, parsed.verse_start, parsed.verse_end, versions)
        elif parsed.is_single_verse():
            # Load single verse
            single_verse = self.get_verse_data(book, chapter, parsed.verse_start, versions)
            verse_data = [{'verse': parsed.verse_start, **single_verse}] if single_verse else []
        else:
            verse_data = []

        return book, chapter, verse_data

    def get_book_list(self) -> List[str]:
        """
        Get list of all book names

        Returns:
            List of book names in order
        """
        # Sort by book ID
        sorted_books = sorted(self.books_metadata.items(), key=lambda x: x[1][0])
        return [book_name for book_name, _ in sorted_books]

    def get_book_chapter_count(self, book_name: str) -> int:
        """Get number of chapters in a book"""
        return get_chapter_count(book_name, self.books_metadata) or 0
