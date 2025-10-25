#!/usr/bin/env python3
"""
Hymn Repository - Loads hymn Google Slides IDs from CSV
"""

import csv
import re
from typing import Optional, Dict


class HymnRepository:
    """Manages hymn ID to Google Slides URL mapping"""

    def __init__(self, hymns_csv: str = "hymns.csv"):
        """
        Initialize hymn repository

        Args:
            hymns_csv: Path to hymns CSV file
        """
        self.hymns_csv = hymns_csv
        self.hymns: Dict[str, str] = {}  # hymn_id -> slides_id
        self.load_hymns()

    def load_hymns(self):
        """Load hymns from CSV file"""
        try:
            with open(self.hymns_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        hymn_id = row[0].strip()
                        slides_id = row[1].strip()
                        self.hymns[hymn_id.upper()] = slides_id
            print(f"[HymnRepository] Loaded {len(self.hymns)} hymns")
        except FileNotFoundError:
            print(f"[HymnRepository] Warning: {self.hymns_csv} not found")
        except Exception as e:
            print(f"[HymnRepository] Error loading hymns: {e}")

    def normalize_hymn_id(self, hymn_input: str) -> Optional[str]:
        """
        Normalize hymn input to standard format

        Args:
            hymn_input: User input (e.g., "21", "C21", "C021", "A01")

        Returns:
            Normalized hymn ID (e.g., "C021", "A01") or None if invalid
        """
        hymn_input = hymn_input.strip().upper()

        # Pattern 1: Already in correct format (C021, A01, etc.)
        if re.match(r'^[A-Z]\d{2,3}$', hymn_input):
            # Pad to 3 digits if needed
            match = re.match(r'^([A-Z])(\d+)$', hymn_input)
            if match:
                prefix = match.group(1)
                number = match.group(2).zfill(3)
                return f"{prefix}{number}"

        # Pattern 2: Just a number (e.g., "21" -> "C021")
        if re.match(r'^\d+$', hymn_input):
            number = hymn_input.zfill(3)
            return f"C{number}"

        # Pattern 3: Letter + number without padding (e.g., "C21" -> "C021")
        match = re.match(r'^([A-Z])(\d+)$', hymn_input)
        if match:
            prefix = match.group(1)
            number = match.group(2).zfill(3)
            return f"{prefix}{number}"

        return None

    def get_slides_url(self, hymn_input: str) -> Optional[str]:
        """
        Get Google Slides URL for a hymn

        Args:
            hymn_input: Hymn ID or number (e.g., "21", "C21", "A01")

        Returns:
            Google Slides URL, or None if not found
        """
        hymn_input = hymn_input.strip().upper()

        # Try direct lookup first (exact match)
        slides_id = self.hymns.get(hymn_input)
        if slides_id:
            return f"https://docs.google.com/presentation/d/{slides_id}/present"

        # Try normalized lookup as fallback
        normalized_id = self.normalize_hymn_id(hymn_input)
        if normalized_id:
            slides_id = self.hymns.get(normalized_id)
            if slides_id:
                return f"https://docs.google.com/presentation/d/{slides_id}/present"

        return None

    def is_hymn_id(self, input_str: str) -> bool:
        """
        Check if input string looks like a hymn ID

        Args:
            input_str: Input string

        Returns:
            True if it looks like a hymn ID
        """
        input_str = input_str.strip().upper()

        # Try direct lookup first
        if input_str in self.hymns:
            return True

        # Try normalized lookup as fallback
        if re.match(r'^[A-Z]?\d{1,3}$', input_str):
            normalized = self.normalize_hymn_id(input_str)
            return normalized in self.hymns if normalized else False

        return False
