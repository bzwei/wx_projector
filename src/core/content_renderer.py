#!/usr/bin/env python3
"""
Content Renderer - Generate HTML for projection content
Handles row-based multi-version Bible verse display
"""

from typing import List, Dict


# Version display names
VERSION_NAMES = {
    'cuv': '和合本 (CUV)',
    'kjv': 'King James (KJV)',
    'nas': 'New American Standard (NAS)',
    'niv': 'New International Version (NIV)',
    'dby': 'Darby Translation (DBY)'
}


def render_bible_verses(book_name: str, chapter: int, verse_data: List[Dict[str, str]],
                       chinese_size: int = 26, english_size: int = 24) -> str:
    """
    Render Bible verses in compact layout with labels on left side

    Args:
        book_name: Book name for title
        chapter: Chapter number for title
        verse_data: List of verse dicts with format:
            [{'verse': 16, 'cuv': '...', 'kjv': '...'}, ...]
        chinese_size: Font size for Chinese text (px)
        english_size: Font size for English text (px)

    Returns:
        HTML string for projection
    """
    if not verse_data:
        return _render_empty_bible()

    # Determine verse range for title
    verse_numbers = [v['verse'] for v in verse_data if 'verse' in v]
    if not verse_numbers:
        verse_range = ""
    elif len(verse_numbers) == 1:
        verse_range = f":{verse_numbers[0]}"
    else:
        verse_range = f":{min(verse_numbers)}-{max(verse_numbers)}"

    # Get list of versions present in data
    versions = []
    if verse_data:
        first_verse = verse_data[0]
        for key in first_verse.keys():
            if key != 'verse' and key in VERSION_NAMES:
                versions.append(key)

    # Build HTML with compact layout and infinite scroll support
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 20px 40px;
            background-color: #ffffff;
            color: #000000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            overflow-y: auto;
            height: 100vh;
            box-sizing: border-box;
        }}
        .title {{
            text-align: center;
            font-size: {english_size + 2}px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #000000;
        }}
        #verses-container {{
            /* Container for dynamically loaded verses */
        }}
        .verse-row {{
            display: flex;
            margin-bottom: 0;
            align-items: baseline;
            padding: 4px 0;
            border-bottom: 1px solid #999999;
        }}
        .verse-row.color-red .verse-label {{
            color: #000000;
        }}
        .verse-row.color-red .verse-content {{
            color: #ff0000;
        }}
        .verse-row.color-blue .verse-label {{
            color: #000000;
        }}
        .verse-row.color-blue .verse-content {{
            color: #0000ff;
        }}
        .verse-label {{
            flex-shrink: 0;
            width: auto;
            min-width: fit-content;
            max-width: 300px;
            font-size: {min(english_size - 2, 48)}px;
            font-weight: 600;
            text-align: right;
            padding-right: 20px;
            white-space: nowrap;
        }}
        .verse-content {{
            flex: 1;
            font-size: {english_size}px;
            line-height: 1.5;
        }}
        .verse-content.chinese {{
            font-size: {chinese_size}px;
            line-height: 1.6;
        }}
        .loading {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: {english_size - 4}px;
        }}
    </style>
</head>
<body>
    <div class="title">{book_name} {chapter}{verse_range}</div>
    <div id="verses-container">
"""

    # Render each verse with compact layout
    for verse_idx, verse_dict in enumerate(verse_data):
        verse_num = verse_dict.get('verse', '?')

        # Alternate colors: even verses are red, odd verses are blue
        color_class = 'color-red' if verse_idx % 2 == 0 else 'color-blue'

        # Render each version for this verse
        for idx, version in enumerate(versions):
            if version in verse_dict:
                verse_text = verse_dict[version]
                version_name = VERSION_NAMES.get(version, version.upper())

                # Determine if this is Chinese text
                is_chinese = version == 'cuv'
                text_class = 'verse-content chinese' if is_chinese else 'verse-content'

                # For first version of verse, show chapter:verse; for subsequent versions, show version abbreviation
                if idx == 0:
                    label = f"{chapter}:{verse_num}"
                else:
                    # Extract short version name: "King James (KJV)" -> "KJV"
                    if '(' in version_name:
                        label = version_name.split('(')[1].rstrip(')')
                    else:
                        label = version.upper()

                html += f"""
    <div class="verse-row {color_class}">
        <div class="verse-label">{label}</div>
        <div class="{text_class}">{verse_text}</div>
    </div>
"""

    html += """
    </div>
    <div id="loading-indicator" class="loading" style="display:none;">Loading more verses...</div>

    <script>
        // Redirect console.log to Python via document.title
        (function() {
            const originalLog = console.log;
            const originalError = console.error;

            console.log = function(...args) {
                originalLog.apply(console, args);
                try {
                    document.title = 'LOG:' + args.join(' ');
                } catch(e) {}
            };

            console.error = function(...args) {
                originalError.apply(console, args);
                try {
                    document.title = 'ERROR:' + args.join(' ');
                } catch(e) {}
            };
        })();

        // Infinite scroll state
        window.bibleState = {
            book: """ + f'"{book_name}"' + """,
            startChapter: """ + str(chapter) + """,  // Chapter of first verse
            startVerse: """ + str(min(verse_numbers)) + """,  // First verse number
            endChapter: """ + str(chapter) + """,  // Chapter of last verse
            endVerse: """ + str(max(verse_numbers)) + """,  // Last verse number
            maxVerse: null,  // Will be set by control panel
            versions: """ + str(versions).replace("'", '"') + """,
            loading: false,
            reachedEnd: false,
            reachedStart: false  // Track if we've reached beginning of book
        };

        // Check if we need to load more content
        function checkAndLoadContent() {
            const scrollHeight = document.documentElement.scrollHeight;
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const clientHeight = window.innerHeight;
            const distanceToBottom = scrollHeight - (scrollTop + clientHeight);
            const distanceToTop = scrollTop;

            // Load previous verses when scrolling near top (within 100px)
            if (distanceToTop < 100 && !window.bibleState.loading && !window.bibleState.reachedStart) {
                loadPreviousVerses();
            }
            // Load more verses when scrolling near bottom (within 200px)
            else if (distanceToBottom < 200 && !window.bibleState.loading && !window.bibleState.reachedEnd) {
                loadMoreVerses();
            }
        }

        // Detect scroll near top or bottom
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(checkAndLoadContent, 100);  // Debounce
        });

        // Handle arrow key navigation (especially important when page isn't scrollable yet)
        window.addEventListener('keydown', function(event) {
            // Check if page is not scrollable (content fits in viewport)
            const isNotScrollable = document.documentElement.scrollHeight <= window.innerHeight;

            if (event.key === 'ArrowDown' || event.key === 'Down') {
                if (isNotScrollable && !window.bibleState.loading && !window.bibleState.reachedEnd) {
                    event.preventDefault();
                    loadMoreVerses();
                }
            } else if (event.key === 'ArrowUp' || event.key === 'Up') {
                if (isNotScrollable && !window.bibleState.loading && !window.bibleState.reachedStart) {
                    event.preventDefault();
                    loadPreviousVerses();
                }
            }
        });

        function loadMoreVerses() {
            const state = window.bibleState;

            // Don't check for chapter end here - let Python handle chapter transitions
            // Python will automatically load from next chapter when current chapter ends

            state.loading = true;
            document.getElementById('loading-indicator').style.display = 'block';

            // Determine batch size based on whether page is scrollable
            const isNotScrollable = document.documentElement.scrollHeight <= window.innerHeight;
            const batchSize = isNotScrollable ? 1 : 10;  // Load 1 verse at a time when not scrollable

            // Request next batch from the END of our current range
            const nextStart = state.endVerse + 1;
            const nextEnd = state.maxVerse || (state.endVerse + batchSize);

            // Count current verse rows (for color continuity)
            const currentRowCount = document.querySelectorAll('#verses-container .verse-row').length;

            // Send command to Python via document.title
            const data = JSON.stringify({
                book: state.book,
                chapter: state.endChapter,  // Use the chapter of the last verse
                startVerse: nextStart,
                endVerse: nextEnd,
                versions: state.versions,
                currentRowCount: currentRowCount
            });
            document.title = 'CMD:loadMoreBibleVerses:' + data;
        }

        function loadPreviousVerses() {
            const state = window.bibleState;

            // Don't load if we're at chapter 1, verse 1
            if (state.startChapter === 1 && state.startVerse === 1) {
                console.log('[Scroll] Already at beginning of book');
                state.reachedStart = true;
                return;
            }

            state.loading = true;
            document.getElementById('loading-indicator').style.display = 'block';

            // Determine batch size based on whether page is scrollable
            const isNotScrollable = document.documentElement.scrollHeight <= window.innerHeight;
            const batchSize = isNotScrollable ? 1 : 10;  // Load 1 verse at a time when not scrollable, 10 when scrollable

            // Request previous verses from the START of our current range
            const prevEnd = state.startVerse - 1;
            const prevStart = Math.max(1, prevEnd - (batchSize - 1));

            // Count current first verse row color (for color continuity when prepending)
            const firstRow = document.querySelector('#verses-container .verse-row');
            const firstRowIsRed = firstRow ? firstRow.classList.contains('color-red') : true;

            // Send command to Python via document.title
            const data = JSON.stringify({
                book: state.book,
                chapter: state.startChapter,  // Use the chapter of the first verse
                startVerse: prevStart,
                endVerse: prevEnd,
                versions: state.versions,
                isPrepend: true,  // Signal that this is for prepending
                firstRowIsRed: firstRowIsRed,  // For color continuity
                batchSize: batchSize  // Send the actual batch size to Python
            });
            document.title = 'CMD:loadPreviousBibleVerses:' + data;
        }

        // Function called from Python to append verses
        window.appendBibleVerses = function(versesHTML, lastVerseNum, newChapter) {
            console.log('[appendBibleVerses] Called with chapter:', newChapter, 'lastVerseNum:', lastVerseNum, 'HTML length:', versesHTML ? versesHTML.length : 0);

            const container = document.getElementById('verses-container');
            if (!container) {
                console.error('[appendBibleVerses] verses-container not found!');
                return;
            }

            if (!versesHTML || versesHTML.trim().length === 0) {
                console.error('[appendBibleVerses] Empty HTML provided');
                window.bibleState.loading = false;
                document.getElementById('loading-indicator').style.display = 'none';
                return;
            }

            // Duplicate prevention: check if this verse range is already loaded
            const existingLabels = Array.from(container.querySelectorAll('.verse-label'))
                .map(el => el.textContent.trim());
            const newVerseLabel = newChapter + ':' + lastVerseNum;
            if (existingLabels.includes(newVerseLabel)) {
                console.log('[appendBibleVerses] Duplicate detected - verse', newVerseLabel, 'already exists, skipping');
                window.bibleState.loading = false;
                document.getElementById('loading-indicator').style.display = 'none';
                return;
            }

            try {
                container.insertAdjacentHTML('beforeend', versesHTML);
                console.log('[appendBibleVerses] Successfully appended HTML');
            } catch (e) {
                console.error('[appendBibleVerses] Error inserting HTML:', e);
                console.error('[appendBibleVerses] HTML was:', versesHTML.substring(0, 200));
            }

            // Update the END of our range (chapter and verse)
            window.bibleState.endChapter = newChapter;
            window.bibleState.endVerse = lastVerseNum;
            window.bibleState.loading = false;
            document.getElementById('loading-indicator').style.display = 'none';

            console.log('[Scroll] Appended verses, end now at chapter', newChapter, 'verse', lastVerseNum);

            // Don't check for end anymore - we continue to next chapter automatically
        };

        // Function called from Python to prepend verses (for scroll-up)
        window.prependBibleVerses = function(versesHTML, firstVerseNum, newChapter) {
            console.log('[prependBibleVerses] Called with chapter:', newChapter, 'firstVerseNum:', firstVerseNum, 'HTML length:', versesHTML ? versesHTML.length : 0);

            const container = document.getElementById('verses-container');
            if (!container) {
                console.error('[prependBibleVerses] verses-container not found!');
                return;
            }

            if (!versesHTML || versesHTML.trim().length === 0) {
                console.error('[prependBibleVerses] Empty HTML provided');
                window.bibleState.loading = false;
                document.getElementById('loading-indicator').style.display = 'none';
                return;
            }

            // Duplicate prevention: check if this verse range is already loaded
            const existingLabels = Array.from(container.querySelectorAll('.verse-label'))
                .map(el => el.textContent.trim());
            const newVerseLabel = newChapter + ':' + firstVerseNum;
            if (existingLabels.includes(newVerseLabel)) {
                console.log('[prependBibleVerses] Duplicate detected - verse', newVerseLabel, 'already exists, skipping');
                window.bibleState.loading = false;
                document.getElementById('loading-indicator').style.display = 'none';
                return;
            }

            // Save current scroll position to maintain it after prepending
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;

            try {
                // Prepend HTML at the beginning
                container.insertAdjacentHTML('afterbegin', versesHTML);
                console.log('[prependBibleVerses] Successfully prepended HTML');

                // Restore scroll position (adjust for new content height)
                const newScrollHeight = document.documentElement.scrollHeight;
                const heightDiff = newScrollHeight - scrollHeight;
                window.scrollTo(0, scrollTop + heightDiff);
                console.log('[prependBibleVerses] Adjusted scroll by', heightDiff, 'px');
            } catch (e) {
                console.error('[prependBibleVerses] Error inserting HTML:', e);
                console.error('[prependBibleVerses] HTML was:', versesHTML.substring(0, 200));
            }

            // Update the START of our range (chapter and verse)
            window.bibleState.startChapter = newChapter;
            window.bibleState.startVerse = firstVerseNum;
            window.bibleState.loading = false;
            document.getElementById('loading-indicator').style.display = 'none';

            console.log('[Scroll] Prepended verses, start now at chapter', newChapter, 'verse', firstVerseNum);

            // Check if we've reached the beginning
            if (newChapter === 1 && firstVerseNum === 1) {
                window.bibleState.reachedStart = true;
                console.log('[Scroll] Reached beginning of book');
            }
        };
    </script>
</body>
</html>
"""

    return html


def _render_empty_bible() -> str:
    """Render empty Bible view"""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000000;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        .message {
            text-align: center;
            font-size: 32px;
            color: #888888;
        }
    </style>
</head>
<body>
    <div class="message">No verse selected</div>
</body>
</html>
"""


def render_verses_html_only(chapter: int, verse_data: List[Dict[str, str]],
                            versions: List[str], start_color_index: int = 0) -> str:
    """
    Render just the verse HTML (without page wrapper) for dynamic appending

    Args:
        chapter: Chapter number
        verse_data: List of verse dicts
        versions: List of version codes to render
        start_color_index: Starting index for color alternation (for continuity)

    Returns:
        HTML string of verse rows only
    """
    html = ""

    for verse_idx, verse_dict in enumerate(verse_data):
        verse_num = verse_dict.get('verse', '?')

        # Alternate colors based on global index
        actual_idx = start_color_index + verse_idx
        color_class = 'color-red' if actual_idx % 2 == 0 else 'color-blue'

        # Render each version for this verse
        for idx, version in enumerate(versions):
            if version in verse_dict:
                verse_text = verse_dict[version]
                version_name = VERSION_NAMES.get(version, version.upper())

                # Determine if this is Chinese text
                is_chinese = version == 'cuv'
                text_class = 'verse-content chinese' if is_chinese else 'verse-content'

                # For first version of verse, show chapter:verse; for subsequent versions, show version abbreviation
                if idx == 0:
                    label = f"{chapter}:{verse_num}"
                else:
                    # Extract short version name
                    if '(' in version_name:
                        label = version_name.split('(')[1].rstrip(')')
                    else:
                        label = version.upper()

                html += f"""    <div class="verse-row {color_class}">
        <div class="verse-label">{label}</div>
        <div class="{text_class}">{verse_text}</div>
    </div>
"""

    return html


def render_chapter_preview_item(verse_number: int, verse_text: str, is_selected: bool = False) -> str:
    """
    Render a single verse item for chapter preview (for JavaScript to use)

    Args:
        verse_number: Verse number
        verse_text: Verse text
        is_selected: Whether this verse is currently selected

    Returns:
        HTML string for verse item
    """
    selected_class = ' selected' if is_selected else ''
    # Truncate long verses for preview
    preview_text = verse_text if len(verse_text) <= 120 else verse_text[:117] + '...'

    return f"""
<div class="verse-item{selected_class}" data-verse="{verse_number}">
    <span class="verse-number">{verse_number}</span>
    <span class="verse-text">{preview_text}</span>
</div>
"""
