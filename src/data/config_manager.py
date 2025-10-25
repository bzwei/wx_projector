#!/usr/bin/env python3
"""
Configuration Manager - Handles application settings persistence
"""

import json
import os
import copy
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration and settings"""

    DEFAULT_CONFIG = {
        "window": {
            "control_panel": {
                "width": 1200,
                "height": 900,
                "x": None,  # Will be centered on first run
                "y": None   # Will be centered on first run
            }
        },
        "display": {
            "preferred_display_index": 1,
            "auto_detect": True
        },
        "bible": {
            "default_versions": ["cuv"],
            "font_size_chinese": 28,
            "font_size_english": 24
        },
        "agenda": {
            "slides_id": ""  # Google Slides ID for agenda
        },
        "history": {
            # Note: bible_projections are NOT persisted to config file
            # History is session-only and cleared on app restart
            "max_history_size": 30  # Maximum number of history items to keep in session
        },
        "google_meet": {
            "meeting_url": ""
        }
    }

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from file, create default if doesn't exist"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = self._merge_with_defaults(loaded_config)
                    print(f"[ConfigManager] Loaded configuration from {self.config_path}")
            except json.JSONDecodeError as e:
                print(f"[ConfigManager] Error parsing config file: {e}")
                print(f"[ConfigManager] Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
            except Exception as e:
                print(f"[ConfigManager] Error loading config: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            print(f"[ConfigManager] Config file not found, creating default at {self.config_path}")
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()

    def _merge_with_defaults(self, loaded_config: Dict) -> Dict:
        """
        Merge loaded config with defaults to ensure all keys exist

        Args:
            loaded_config: Configuration loaded from file

        Returns:
            Merged configuration with all default keys
        """
        def merge_dicts(default: Dict, loaded: Dict) -> Dict:
            """Recursively merge dictionaries"""
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result

        return merge_dicts(self.DEFAULT_CONFIG, loaded_config)

    def save(self):
        """Save configuration to file (excludes session-only data like history)"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a deep copy of config for saving
            config_to_save = copy.deepcopy(self.config)

            # Remove bible_projections from history before saving (session-only)
            if 'history' in config_to_save and 'bible_projections' in config_to_save['history']:
                # Keep max_history_size but remove actual projection history
                config_to_save['history'] = {
                    'max_history_size': config_to_save['history'].get('max_history_size', 30)
                }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            print(f"[ConfigManager] Saved configuration to {self.config_path}")
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path

        Args:
            key_path: Dot-separated path (e.g., "bible.font_size_chinese")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set configuration value by dot-separated path

        Args:
            key_path: Dot-separated path (e.g., "bible.font_size_chinese")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def get_window_position(self) -> Optional[tuple[int, int]]:
        """
        Get saved window position

        Returns:
            (x, y) tuple or None if not saved
        """
        x = self.get('window.control_panel.x')
        y = self.get('window.control_panel.y')

        if x is not None and y is not None:
            return (x, y)
        return None

    def save_window_position(self, x: int, y: int):
        """
        Save window position

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.set('window.control_panel.x', x)
        self.set('window.control_panel.y', y)

    def get_window_size(self) -> tuple[int, int]:
        """
        Get saved window size

        Returns:
            (width, height) tuple
        """
        width = self.get('window.control_panel.width', 1200)
        height = self.get('window.control_panel.height', 900)
        return (width, height)

    def save_window_size(self, width: int, height: int):
        """
        Save window size

        Args:
            width: Window width
            height: Window height
        """
        self.set('window.control_panel.width', width)
        self.set('window.control_panel.height', height)

    def get_font_sizes(self) -> tuple[int, int]:
        """
        Get font sizes for Chinese and English

        Returns:
            (chinese_size, english_size) tuple
        """
        chinese = self.get('bible.font_size_chinese', 28)
        english = self.get('bible.font_size_english', 24)
        return (chinese, english)

    def save_font_sizes(self, chinese_size: int, english_size: int):
        """
        Save font sizes

        Args:
            chinese_size: Font size for Chinese text
            english_size: Font size for English text
        """
        self.set('bible.font_size_chinese', chinese_size)
        self.set('bible.font_size_english', english_size)

    def get_agenda_slides_id(self) -> str:
        """
        Get agenda Google Slides ID

        Returns:
            Google Slides ID for agenda
        """
        return self.get('agenda.slides_id', '')

    def save_agenda_slides_id(self, slides_id: str):
        """
        Save agenda Google Slides ID

        Args:
            slides_id: Google Slides ID
        """
        self.set('agenda.slides_id', slides_id)

    def get_google_meet_url(self) -> str:
        """
        Get default Google Meet URL

        Returns:
            Google Meet URL from config
        """
        return self.get('google_meet.meeting_url', '')
