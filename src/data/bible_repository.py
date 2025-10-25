#!/usr/bin/env python3
"""
Bible Repository - Loads Bible chapter files from disk
Handles multiple versions and encodings (UTF-8 for English, GB2312 for Chinese)
"""

import os
from pathlib import Path
from typing import List, Dict, Optional


class BibleRepository:
    """Manages loading Bible text files from disk"""

    def __init__(self, books_dir: str = "books"):
        """
        Initialize Bible repository

        Args:
            books_dir: Base directory containing Bible version folders
        """
        self.books_dir = Path(books_dir)
        self.cache: Dict[str, List[str]] = {}  # Cache loaded chapters

        # Encoding map for different versions
        self.encodings = {
            'cuv': 'gb2312',  # Chinese Union Version uses GB2312
            'kjv': 'utf-8',   # King James Version
            'nas': 'utf-8',   # New American Standard
            'niv': 'utf-8',   # New International Version
            'dby': 'utf-8',   # Darby Translation
        }

    def load_chapter(self, version: str, book_id: int, chapter: int) -> List[str]:
        """
        Load chapter verses from file

        Args:
            version: Bible version code (cuv, kjv, nas, niv, dby)
            book_id: Book ID (1-66)
            chapter: Chapter number (1-indexed)

        Returns:
            List of verses (strings), one per line, 0-indexed

        Raises:
            FileNotFoundError: If chapter file doesn't exist
            UnicodeDecodeError: If encoding is incorrect
        """
        # Check cache first
        cache_key = f"{version}_{book_id}_{chapter}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Build file path: books/{version}/vol{book_id}/chap{chapter}.txt
        version_dir = self.books_dir / version
        book_dir = version_dir / f"vol{book_id:02d}"
        chapter_file = book_dir / f"chap{chapter:03d}.txt"

        if not chapter_file.exists():
            raise FileNotFoundError(f"Chapter file not found: {chapter_file}")

        # Get encoding for this version
        encoding = self.encodings.get(version, 'utf-8')

        # Load file
        try:
            with open(chapter_file, 'r', encoding=encoding) as f:
                verses = [line.rstrip('\n\r') for line in f.readlines()]
        except UnicodeDecodeError as e:
            # Try fallback encoding
            fallback_encoding = 'utf-8' if encoding == 'gb2312' else 'gb2312'
            with open(chapter_file, 'r', encoding=fallback_encoding) as f:
                verses = [line.rstrip('\n\r') for line in f.readlines()]

        # Cache the result
        self.cache[cache_key] = verses

        return verses

    def get_verse(self, version: str, book_id: int, chapter: int, verse: int) -> Optional[str]:
        """
        Get a single verse

        Args:
            version: Bible version code
            book_id: Book ID
            chapter: Chapter number
            verse: Verse number (1-indexed)

        Returns:
            Verse text, or None if verse doesn't exist
        """
        try:
            verses = self.load_chapter(version, book_id, chapter)
            # Verses are 0-indexed in list, but verse parameter is 1-indexed
            if 0 < verse <= len(verses):
                return verses[verse - 1]
            return None
        except (FileNotFoundError, UnicodeDecodeError):
            return None

    def get_verse_range(self, version: str, book_id: int, chapter: int,
                       verse_start: int, verse_end: int) -> List[str]:
        """
        Get a range of verses

        Args:
            version: Bible version code
            book_id: Book ID
            chapter: Chapter number
            verse_start: Starting verse (1-indexed, inclusive)
            verse_end: Ending verse (1-indexed, inclusive)

        Returns:
            List of verses in range
        """
        try:
            verses = self.load_chapter(version, book_id, chapter)
            # Convert to 0-indexed for slicing
            start_idx = verse_start - 1
            end_idx = verse_end  # end is exclusive in slicing, so no -1
            return verses[start_idx:end_idx]
        except (FileNotFoundError, UnicodeDecodeError):
            return []

    def clear_cache(self):
        """Clear the chapter cache"""
        self.cache.clear()

    def get_chapter_verse_count(self, version: str, book_id: int, chapter: int) -> int:
        """
        Get the number of verses in a chapter

        Args:
            version: Bible version code
            book_id: Book ID
            chapter: Chapter number

        Returns:
            Number of verses in chapter, or 0 if chapter doesn't exist
        """
        try:
            verses = self.load_chapter(version, book_id, chapter)
            return len(verses)
        except (FileNotFoundError, UnicodeDecodeError):
            return 0
