#!/usr/bin/env python3
"""
Simplified JavaScript-Python Bridge
Uses a polling approach - JavaScript writes commands to the page title, Python reads them
"""

import wx
import json


def setup_simple_bridge(main_window):
    """
    Set up simple bidirectional communication between JavaScript and Python

    Args:
        main_window: MainWindow instance with webview and projection_window
    """

    # Inject JavaScript that exposes Python functions
    script = """
    (function() {
        // Simple bridge using document title as message passing
        window.pythonBridge = {
            showURL: function(url) {
                console.log('[Bridge] showURL:', url);
                // Call Python directly via title
                document.title = 'CMD:showURL:' + url;
            },

            reloadURL: function(url) {
                console.log('[Bridge] reloadURL:', url);
                // Call Python directly via title with reload command
                document.title = 'CMD:reloadURL:' + url;
            },

            showBible: function(text, chineseSize, englishSize) {
                console.log('[Bridge] showBible:', text.substring(0, 50) + '...');
                var data = JSON.stringify({
                    text: text,
                    chineseSize: parseInt(chineseSize) || 26,
                    englishSize: parseInt(englishSize) || 24
                });
                document.title = 'CMD:showBible:' + data;
            },

            showAgenda: function(html) {
                console.log('[Bridge] showAgenda');
                document.title = 'CMD:showAgenda:' + html;
            },

            hideProjection: function() {
                console.log('[Bridge] hideProjection');
                document.title = 'CMD:hideProjection:';
            },

            showBibleWindow: function() {
                console.log('[Bridge] showBibleWindow (without reload)');
                document.title = 'CMD:showBibleWindow:';
            },

            hideBibleWindow: function() {
                console.log('[Bridge] hideBibleWindow');
                document.title = 'CMD:hideBibleWindow:';
            },

            hideHymnWindow: function() {
                console.log('[Bridge] hideHymnWindow');
                document.title = 'CMD:hideHymnWindow:';
            },

            hideAgenda: function() {
                console.log('[Bridge] hideAgenda');
                document.title = 'CMD:hideAgenda:';
            },

            saveFontSizes: function(chineseSize, englishSize) {
                console.log('[Bridge] saveFontSizes:', chineseSize, englishSize);
                var data = JSON.stringify({
                    chineseSize: parseInt(chineseSize),
                    englishSize: parseInt(englishSize)
                });
                document.title = 'CMD:saveFontSizes:' + data;
            },

            projectBibleVerse: function(book, verse, versions, chineseSize, englishSize, preserveScroll) {
                console.log('[Bridge] projectBibleVerse:', book, verse, versions, 'preserveScroll:', preserveScroll);
                var data = JSON.stringify({
                    book: book,
                    verse: verse,
                    versions: versions,
                    chineseSize: parseInt(chineseSize) || 28,
                    englishSize: parseInt(englishSize) || 24,
                    preserveScroll: preserveScroll || false
                });
                document.title = 'CMD:projectBibleVerse:' + data;
            },

            loadMoreBibleVerses: function(book, chapter, startVerse, endVerse, versions) {
                console.log('[Bridge] loadMoreBibleVerses:', book, chapter, startVerse, '-', endVerse);
                var data = JSON.stringify({
                    book: book,
                    chapter: chapter,
                    startVerse: startVerse,
                    endVerse: endVerse,
                    versions: versions
                });
                document.title = 'CMD:loadMoreBibleVerses:' + data;
            },

            showError: function(message) {
                console.log('[Bridge] showError:', message);
                // Show custom error notification
                if (window.showErrorNotification) {
                    window.showErrorNotification(message);
                } else {
                    alert(message);
                }
            },

            loadChapterPreview: function(book, chapter, versions) {
                console.log('[Bridge] loadChapterPreview:', book, chapter, versions);
                var data = JSON.stringify({
                    book: book,
                    chapter: parseInt(chapter),
                    versions: versions || ['kjv']
                });
                document.title = 'CMD:loadChapterPreview:' + data;
            },

            updateDisplayStatus: function(text) {
                var elem = document.getElementById('monitor-status');
                if (elem) {
                    var textElem = elem.querySelector('.status-text');
                    if (textElem) {
                        textElem.textContent = text;
                    }
                }
            }
        };

        console.log('[Bridge] Python bridge initialized');
    })();
    """

    def on_loaded(event):
        """Called when page finishes loading"""
        if event.GetURL().startswith('file://'):
            main_window.webview.RunScript(script)
            print("[Bridge] JavaScript bridge injected")

            # Update display status
            display_count = len(main_window.displays)
            if display_count > 1:
                status_script = f"pythonBridge.updateDisplayStatus('{display_count} displays detected');"
            else:
                status_script = "pythonBridge.updateDisplayStatus('1 display (no secondary)');"

            main_window.webview.RunScript(status_script)

            # Load and apply saved font sizes
            chinese_size, english_size = main_window.config.get_font_sizes()
            font_script = f"""
            (function() {{
                // Set font size dropdowns if they exist (correct IDs: chinese-size, english-size)
                var chineseSelect = document.getElementById('chinese-size');
                var englishSelect = document.getElementById('english-size');
                if (chineseSelect) {{
                    chineseSelect.value = {chinese_size};
                    console.log('[Bridge] Set Chinese font size to:', {chinese_size});
                }}
                if (englishSelect) {{
                    englishSelect.value = {english_size};
                    console.log('[Bridge] Set English font size to:', {english_size});
                }}

                // Add event listeners to save when font sizes change
                if (chineseSelect && englishSelect) {{
                    var saveFontSizes = function() {{
                        var chSize = parseInt(chineseSelect.value);
                        var enSize = parseInt(englishSelect.value);
                        console.log('[Bridge] Font sizes changed, saving:', chSize, enSize);
                        window.pythonBridge.saveFontSizes(chSize, enSize);
                    }};

                    chineseSelect.addEventListener('change', saveFontSizes);
                    englishSelect.addEventListener('change', saveFontSizes);
                    console.log('[Bridge] Added font size change listeners');
                }}

                console.log('[Bridge] Loaded font sizes from config: Chinese={chinese_size}px, English={english_size}px');
            }})();
            """
            main_window.webview.RunScript(font_script)
            print(f"[Bridge] Loaded saved font sizes: Chinese={chinese_size}px, English={english_size}px")

            # Populate book datalist
            try:
                books = main_window.bible_engine.get_book_list()
                books_json = json.dumps(books)
                populate_script = f"""
                var bookList = document.getElementById('book-list');
                if (bookList) {{
                    var books = {books_json};
                    bookList.innerHTML = '';
                    books.forEach(function(book) {{
                        var option = document.createElement('option');
                        option.value = book;
                        bookList.appendChild(option);
                    }});
                    console.log('[Bridge] Populated', books.length, 'books in datalist');
                }}
                """
                main_window.webview.RunScript(populate_script)
                print(f"[Bridge] Populated {len(books)} books in datalist")
            except Exception as e:
                print(f"[Bridge] Error populating books: {e}")

            # Load and set Google Meet URL
            meet_url = main_window.config.get_google_meet_url()
            if meet_url:
                meet_script = f"""
                var meetInput = document.getElementById('meet-url-input');
                if (meetInput) {{
                    meetInput.value = '{meet_url}';
                    console.log('[Bridge] Set Google Meet URL from config');
                }}
                """
                main_window.webview.RunScript(meet_script)
                print(f"[Bridge] Loaded Google Meet URL from config: {meet_url}")

    def on_title_changed(event):
        """Monitor title changes for commands from JavaScript"""
        title = event.GetString()

        # Handle console logs from projection window
        if title.startswith('LOG:'):
            print(f"[ProjectionWindow JS] {title[4:]}")
            return
        elif title.startswith('ERROR:'):
            print(f"[ProjectionWindow JS ERROR] {title[6:]}")
            return

        # Check if this is a command
        if title.startswith('CMD:'):
            try:
                # Parse command
                parts = title.split(':', 2)  # CMD:command:data
                command = parts[1] if len(parts) > 1 else ''
                data = parts[2] if len(parts) > 2 else ''

                print(f"[Bridge] Received command: {command}")

                if command == 'showURL' or command == 'reloadURL':
                    url = data
                    force_reload = (command == 'reloadURL')

                    # Hide all other windows when showing hymn/URL content
                    main_window.bible_window.hide_projection()
                    main_window.agenda_window.hide_projection()

                    # Check if this is a hymn ID
                    if main_window.hymn_repository.is_hymn_id(url):
                        slides_url = main_window.hymn_repository.get_slides_url(url)
                        if slides_url:
                            print(f"[Bridge] Hymn ID '{url}' -> {slides_url}")
                            main_window.hymn_window.show_url(slides_url, force_reload=force_reload)
                        else:
                            print(f"[Bridge] Hymn ID '{url}' not found in hymns.csv")
                    else:
                        # Regular URL
                        print(f"[Bridge] {'Reloading' if force_reload else 'Showing'} URL: {url}")
                        main_window.hymn_window.show_url(url, force_reload=force_reload)

                elif command == 'showBible':
                    try:
                        bible_data = json.loads(data)
                        text = bible_data.get('text', '')
                        chinese_size = int(bible_data.get('chineseSize', 26))
                        english_size = int(bible_data.get('englishSize', 24))
                        print(f"[Bridge] Showing Bible (CN:{chinese_size}px, EN:{english_size}px)")

                        # Hide all other windows when showing Bible content
                        main_window.hymn_window.hide_projection()
                        main_window.agenda_window.hide_projection()

                        main_window.bible_window.show_bible(text, chinese_size, english_size)
                    except json.JSONDecodeError as e:
                        print(f"[Bridge] Error parsing Bible data: {e}")

                elif command == 'showAgenda':
                    # Show agenda in separate agenda window, not the main projection window
                    # Hide all other windows when showing Agenda
                    main_window.bible_window.hide_projection()
                    main_window.hymn_window.hide_projection()

                    # First check if we have an agenda slides ID in config
                    agenda_slides_id = main_window.config.get_agenda_slides_id()

                    if agenda_slides_id:
                        # Show Google Slides agenda
                        slides_url = f"https://docs.google.com/presentation/d/{agenda_slides_id}/present"
                        print(f"[Bridge] Showing Agenda from config: {slides_url}")
                        main_window.agenda_window.show_url(slides_url)
                    elif data:
                        # Show custom HTML agenda if provided
                        print(f"[Bridge] Showing custom HTML Agenda")
                        main_window.agenda_window.show_html(data)
                    else:
                        print(f"[Bridge] No agenda slides ID in config and no HTML provided")
                        # Show error to user
                        error_msg = "No agenda configured. Please set agenda slides ID in config.json"
                        error_script = f"if (window.pythonBridge) {{ window.pythonBridge.showError('{error_msg}'); }}"
                        wx.CallAfter(lambda: main_window.webview.RunScript(error_script))

                elif command == 'hideProjection':
                    print(f"[Bridge] Hiding projection windows")
                    # Hide both Bible and Hymn windows (whichever is showing)
                    main_window.bible_window.hide_projection()
                    main_window.hymn_window.hide_projection()

                elif command == 'showBibleWindow':
                    print(f"[Bridge] Showing Bible window (without reload)")
                    # Just show the Bible window without reloading content
                    # Hide all other windows first
                    main_window.hymn_window.hide_projection()
                    main_window.agenda_window.hide_projection()
                    # Show Bible window (will preserve existing content and scroll position)
                    main_window.bible_window._show_window()

                elif command == 'hideBibleWindow':
                    print(f"[Bridge] Hiding Bible window only")
                    main_window.bible_window.hide_projection()

                elif command == 'hideHymnWindow':
                    print(f"[Bridge] Hiding Hymn window only")
                    main_window.hymn_window.hide_projection()

                elif command == 'hideAgenda':
                    print(f"[Bridge] Hiding agenda")
                    main_window.agenda_window.hide_projection()

                elif command == 'saveFontSizes':
                    try:
                        font_data = json.loads(data)
                        chinese_size = int(font_data.get('chineseSize', 28))
                        english_size = int(font_data.get('englishSize', 24))
                        main_window.config.save_font_sizes(chinese_size, english_size)
                        main_window.config.save()
                        print(f"[Bridge] Saved font sizes: Chinese={chinese_size}px, English={english_size}px")
                    except json.JSONDecodeError as e:
                        print(f"[Bridge] Error parsing font size data: {e}")
                    except Exception as e:
                        print(f"[Bridge] Error saving font sizes: {e}")

                elif command == 'projectBibleVerse':
                    try:
                        from core.content_renderer import render_bible_verses
                        verse_req = json.loads(data)
                        book = verse_req.get('book', '')
                        verse_ref = verse_req.get('verse', '')
                        versions = verse_req.get('versions', ['cuv', 'kjv'])
                        chinese_size = int(verse_req.get('chineseSize', 28))
                        english_size = int(verse_req.get('englishSize', 24))
                        preserve_scroll = verse_req.get('preserveScroll', False)

                        print(f"[Bridge] Projecting Bible: {book} {verse_ref}")
                        print(f"[Bridge] Versions: {versions}, Sizes: CN={chinese_size}px, EN={english_size}px")

                        # Normalize verse reference: convert spaces to colons
                        # Handle formats like "3 8" -> "3:8", "3 8-10" -> "3:8-10"
                        verse_ref_normalized = verse_ref.strip()
                        # Replace first space with colon (chapter verse separator)
                        if ' ' in verse_ref_normalized and ':' not in verse_ref_normalized:
                            parts = verse_ref_normalized.split(' ', 1)
                            if len(parts) == 2:
                                # Also remove any spaces in the verse part (e.g., "8 -10" -> "8-10")
                                verse_part = parts[1].replace(' ', '')
                                verse_ref_normalized = parts[0] + ':' + verse_part
                                print(f"[Bridge] Normalized verse ref: '{verse_ref}' -> '{verse_ref_normalized}'")

                        # Parse and get verse data
                        book_name, chapter, verse_data = main_window.bible_engine.parse_and_get_verses(
                            verse_ref_normalized, book, versions
                        )

                        if verse_data:
                            # Get actual verse range after backend processing
                            actual_start = verse_data[0]['verse']
                            actual_end = verse_data[-1]['verse']
                            actual_range = f"{chapter}:{actual_start}-{actual_end}" if actual_start != actual_end else f"{chapter}:{actual_start}"

                            # Render HTML
                            html = render_bible_verses(book_name, chapter, verse_data, chinese_size, english_size)
                            # Show in Bible projection window (not agenda!)
                            print(f"[Bridge] Projecting {len(verse_data)} verse(s) (preserve_scroll={preserve_scroll})")

                            # Hide all other windows when showing Bible content
                            main_window.hymn_window.hide_projection()
                            main_window.agenda_window.hide_projection()

                            main_window.bible_window.show_bible(html, preserve_scroll=preserve_scroll)
                            print(f"[Bridge] Projected {len(verse_data)} verse(s)")

                            # Update the input field with actual range (not 999)
                            # Also update lastBibleProjection to match the actual range
                            # And add to history if this was a "999" request (entire chapter)
                            book_name_escaped = book_name.replace("'", "\\'")
                            update_script = f"""
                            (function() {{
                                var verseInput = document.getElementById('verse-input');
                                if (verseInput) {{
                                    verseInput.value = '{actual_range}';
                                    console.log('[Bridge] Updated verse input to:', '{actual_range}');
                                }}

                                // Update projection state with actual max verse
                                if (window.currentProjection) {{
                                    window.currentProjection.endVerse = {actual_end};
                                    window.currentProjection.maxVerse = {actual_end};
                                    console.log('[Bridge] Updated projection state:', window.currentProjection);
                                }}

                                // Update lastBibleProjection with actual range to prevent unnecessary reloads
                                if (window.lastBibleProjection) {{
                                    window.lastBibleProjection.verse = '{actual_range}';
                                    console.log('[Bridge] Updated lastBibleProjection.verse to:', '{actual_range}');
                                }}

                                // Add to history if this was entire chapter request (had 999)
                                if ('{verse_ref_normalized}'.includes('999')) {{
                                    if (typeof addToHistory === 'function') {{
                                        addToHistory('{book_name_escaped}', '{actual_range}');
                                        console.log('[Bridge] Added to history:', '{book_name_escaped}', '{actual_range}');
                                    }}
                                }}
                            }})();
                            """
                            wx.CallAfter(lambda: main_window.webview.RunScript(update_script))
                        else:
                            # No verse data - show error to user
                            error_msg = f"Invalid verse reference: {book} {verse_ref}. Please check the book name, chapter, and verse number."
                            print(f"[Bridge] {error_msg}")
                            # Send error back to JavaScript using custom error display
                            error_script = f"if (window.pythonBridge) {{ window.pythonBridge.showError('{error_msg}'); }}"
                            wx.CallAfter(lambda: main_window.webview.RunScript(error_script))

                    except json.JSONDecodeError as e:
                        print(f"[Bridge] Error parsing Bible verse request: {e}")
                    except Exception as e:
                        print(f"[Bridge] Error projecting Bible verse: {e}")
                        import traceback
                        traceback.print_exc()

                elif command == 'loadMoreBibleVerses':
                    try:
                        from core.content_renderer import render_verses_html_only
                        load_req = json.loads(data)
                        book = load_req.get('book', '')
                        chapter = int(load_req.get('chapter', 1))
                        start_verse = int(load_req.get('startVerse', 1))
                        end_verse = int(load_req.get('endVerse', 1))
                        versions = load_req.get('versions', ['cuv', 'kjv'])
                        current_row_count = int(load_req.get('currentRowCount', 0))

                        print(f"[Bridge] Loading more verses: {book} {chapter}:{start_verse}-{end_verse}, current rows: {current_row_count}")

                        # Build verse reference
                        verse_ref = f"{chapter}:{start_verse}-{end_verse}"

                        # Get verse data
                        book_name, chapter_num, verse_data = main_window.bible_engine.parse_and_get_verses(
                            verse_ref, book, versions
                        )

                        # Filter out empty verses (verses with no actual text, only 'verse' key)
                        if verse_data:
                            verse_data = [v for v in verse_data if any(k in v for k in versions)]

                        # If no verses found in current chapter, try next chapter
                        if not verse_data:
                            print(f"[Bridge] No verses in {book} {chapter}:{start_verse}-{end_verse}, trying next chapter")
                            next_chapter = chapter + 1
                            verse_ref = f"{next_chapter}:1-10"  # Load first 10 verses of next chapter
                            print(f"[Bridge] Attempting to load {book} {verse_ref}")
                            book_name, chapter_num, verse_data = main_window.bible_engine.parse_and_get_verses(
                                verse_ref, book, versions
                            )
                            # Filter out empty verses from next chapter too
                            if verse_data:
                                verse_data = [v for v in verse_data if any(k in v for k in versions)]
                            # Update chapter for the response
                            if verse_data:
                                print(f"[Bridge] Successfully loaded {len(verse_data)} verses from chapter {next_chapter}")
                                chapter = next_chapter
                                start_verse = 1
                            else:
                                print(f"[Bridge] No verses found in chapter {next_chapter} either - end of book")

                        if verse_data:
                            # Use actual row count from JavaScript (not verse numbers!)
                            # This is critical for color continuity when multiple versions are displayed
                            color_start_index = current_row_count

                            # Use the chapter variable (which may have been updated to next chapter)
                            # instead of chapter_num from parse result
                            verses_html = render_verses_html_only(chapter, verse_data, versions, color_start_index)

                            # Get last verse number
                            last_verse = verse_data[-1]['verse']

                            print(f"[Bridge] Appending {len(verse_data)} verses (up to verse {last_verse})")

                            # Use JSON encoding to safely pass HTML to JavaScript
                            verses_html_json = json.dumps(verses_html)

                            # Send to projection window to append
                            append_script = f"""
                            (function() {{
                                console.log('[Bridge] Attempting to append verses');
                                if (window.appendBibleVerses) {{
                                    var versesHTML = {verses_html_json};
                                    console.log('[Bridge] Calling appendBibleVerses with chapter', {chapter}, 'verse', {last_verse}, 'HTML length:', versesHTML.length);
                                    window.appendBibleVerses(versesHTML, {last_verse}, {chapter});
                                }} else {{
                                    console.error('[Bridge] appendBibleVerses function not found!');
                                }}
                            }})();
                            """
                            # Run script in Bible projection window
                            def run_append():
                                try:
                                    result = main_window.bible_window.webview.RunScript(append_script)
                                    print(f"[Bridge] Append script executed, result: {result}")
                                except Exception as e:
                                    print(f"[Bridge] Error running append script: {e}")
                                    import traceback
                                    traceback.print_exc()

                            wx.CallAfter(run_append)
                        else:
                            print(f"[Bridge] No more verses found - reached end of book")
                            # Notify that we've reached the end of the book
                            end_script = """
                            if (window.bibleState) {
                                window.bibleState.reachedEnd = true;
                                window.bibleState.loading = false;
                                document.getElementById('loading-indicator').style.display = 'none';
                                console.log('[Scroll] Reached end of book - no more chapters available');
                            }
                            """
                            wx.CallAfter(lambda: main_window.bible_window.webview.RunScript(end_script))

                    except Exception as e:
                        print(f"[Bridge] Error loading more verses: {e}")
                        import traceback
                        traceback.print_exc()

                elif command == 'loadPreviousBibleVerses':
                    try:
                        from core.content_renderer import render_verses_html_only
                        load_req = json.loads(data)
                        book = load_req.get('book', '')
                        chapter = int(load_req.get('chapter', 1))
                        start_verse = int(load_req.get('startVerse', 1))
                        end_verse = int(load_req.get('endVerse', 1))
                        versions = load_req.get('versions', ['cuv', 'kjv'])
                        first_row_is_red = load_req.get('firstRowIsRed', True)
                        batch_size = int(load_req.get('batchSize', 10))  # Get actual batch size from JavaScript

                        print(f"[Bridge] Loading previous verses: {book} {chapter}:{start_verse}-{end_verse}, batchSize: {batch_size}, firstRowIsRed: {first_row_is_red}")

                        # Build verse reference
                        verse_ref = f"{chapter}:{start_verse}-{end_verse}"

                        # Get verse data
                        book_name, chapter_num, verse_data = main_window.bible_engine.parse_and_get_verses(
                            verse_ref, book, versions
                        )

                        # Filter out empty verses
                        if verse_data:
                            verse_data = [v for v in verse_data if any(k in v for k in versions)]

                        # If no verses found and we're at verse 1, try previous chapter
                        if not verse_data and start_verse == 1 and chapter > 1:
                            print(f"[Bridge] At beginning of chapter {chapter}, trying previous chapter {chapter - 1}")
                            prev_chapter = chapter - 1
                            # Load entire previous chapter first to determine how many verses to load
                            verse_ref = f"{prev_chapter}:1-999"  # Get entire previous chapter first
                            book_name, chapter_num, temp_data = main_window.bible_engine.parse_and_get_verses(
                                verse_ref, book, versions
                            )
                            if temp_data:
                                temp_data = [v for v in temp_data if any(k in v for k in versions)]
                                # Use the batch_size from JavaScript to determine how many verses to load
                                # Get the last 'batch_size' verses from the end of the previous chapter
                                verse_data = temp_data[-batch_size:] if len(temp_data) >= batch_size else temp_data
                                chapter = prev_chapter
                                if verse_data:
                                    start_verse = verse_data[0]['verse']
                                    print(f"[Bridge] Successfully loaded {len(verse_data)} verses from end of chapter {prev_chapter} (batch_size={batch_size})")
                            else:
                                print(f"[Bridge] No verses found in previous chapter {prev_chapter} either")

                        if verse_data:
                            # Calculate color index for prepending
                            # We need to calculate backwards from the first row's color
                            # Count how many rows we're about to prepend
                            num_rows_to_prepend = len(verse_data) * len(versions)

                            # If first current row is red (index 0), we work backwards
                            # The last row we prepend should be blue (odd index)
                            # So the first row we prepend depends on total rows being prepended
                            if first_row_is_red:
                                # Current first row is index 0 (red)
                                # So last prepended row should be index -1 equivalent (blue)
                                # First prepended row will be at index -(num_rows_to_prepend)
                                color_start_index = -num_rows_to_prepend
                            else:
                                # Current first row is index 1 (blue)
                                # So last prepended row should be index 0 (red)
                                # First prepended row will be at index -(num_rows_to_prepend-1)
                                color_start_index = -(num_rows_to_prepend - 1)

                            # Convert negative to positive modulo
                            color_start_index = color_start_index % 2

                            print(f"[Bridge] Prepending {len(verse_data)} verses ({num_rows_to_prepend} rows), color_start_index: {color_start_index}")

                            # Use the chapter variable (which may have been updated to prev chapter)
                            verses_html = render_verses_html_only(chapter, verse_data, versions, color_start_index)

                            # Get first verse number
                            first_verse = verse_data[0]['verse']

                            print(f"[Bridge] Prepending {len(verse_data)} verses (starting from verse {first_verse})")

                            # Use JSON encoding to safely pass HTML to JavaScript
                            verses_html_json = json.dumps(verses_html)

                            # Send to projection window to prepend
                            prepend_script = f"""
                            (function() {{
                                console.log('[Bridge] Attempting to prepend verses');
                                if (window.prependBibleVerses) {{
                                    var versesHTML = {verses_html_json};
                                    console.log('[Bridge] Calling prependBibleVerses with chapter', {chapter}, 'verse', {first_verse}, 'HTML length:', versesHTML.length);
                                    window.prependBibleVerses(versesHTML, {first_verse}, {chapter});
                                }} else {{
                                    console.error('[Bridge] prependBibleVerses function not found!');
                                }}
                            }})();
                            """
                            # Run script in Bible projection window
                            def run_prepend():
                                try:
                                    result = main_window.bible_window.webview.RunScript(prepend_script)
                                    print(f"[Bridge] Prepend script executed, result: {result}")
                                except Exception as e:
                                    print(f"[Bridge] Error running prepend script: {e}")
                                    import traceback
                                    traceback.print_exc()

                            wx.CallAfter(run_prepend)
                        else:
                            print(f"[Bridge] No more previous verses found - reached beginning of book")
                            # Notify that we've reached the beginning of the book
                            start_script = """
                            if (window.bibleState) {
                                window.bibleState.reachedStart = true;
                                window.bibleState.loading = false;
                                document.getElementById('loading-indicator').style.display = 'none';
                                console.log('[Scroll] Reached beginning of book');
                            }
                            """
                            wx.CallAfter(lambda: main_window.bible_window.webview.RunScript(start_script))

                    except Exception as e:
                        print(f"[Bridge] Error loading previous verses: {e}")
                        import traceback
                        traceback.print_exc()

                elif command == 'joinGoogleMeet':
                    try:
                        meet_req = json.loads(data)
                        meet_url = meet_req.get('url', '')

                        print(f"[Bridge] Auto-joining Google Meet: {meet_url}")

                        # Import and use Google Meet automation (macOS only)
                        from services.google_meet_automation import GoogleMeetAutomation

                        if not hasattr(main_window, 'meet_automation'):
                            main_window.meet_automation = GoogleMeetAutomation()

                        success = main_window.meet_automation.join_meeting(meet_url)

                        if not success:
                            error_script = "alert('Failed to join Google Meet. Check console for details.');"
                            wx.CallAfter(lambda: main_window.webview.RunScript(error_script))

                    except json.JSONDecodeError as e:
                        print(f"[Bridge] Error parsing Google Meet request: {e}")
                    except Exception as e:
                        print(f"[Bridge] Error auto-joining Google Meet: {e}")
                        import traceback
                        traceback.print_exc()

                elif command == 'openMeetManually':
                    try:
                        meet_req = json.loads(data)
                        meet_url = meet_req.get('url', '')

                        print(f"[Bridge] Opening Google Meet manually: {meet_url}")

                        # Simply open the URL in default browser
                        import webbrowser
                        webbrowser.open(meet_url)

                    except json.JSONDecodeError as e:
                        print(f"[Bridge] Error parsing Meet URL: {e}")
                    except Exception as e:
                        print(f"[Bridge] Error opening Meet URL: {e}")

                elif command == 'loadChapterPreview':
                    try:
                        from utils.parsers import get_chapter_count

                        preview_req = json.loads(data)
                        book = preview_req.get('book', '')
                        chapter = int(preview_req.get('chapter', 1))
                        versions = preview_req.get('versions', ['kjv'])

                        print(f"[Bridge] Loading chapter preview: {book} {chapter} ({', '.join(versions)})")

                        # Get chapter data with all selected versions
                        chapter_data = main_window.bible_engine.get_chapter_data(book, chapter, versions)

                        if chapter_data:
                            # Get total chapter count for this book
                            chapter_count = get_chapter_count(book, main_window.bible_engine.books_metadata)

                            # Send preview data back to JavaScript
                            preview_data = {
                                'book': book,
                                'chapter': chapter,
                                'versions': versions,
                                'chapterCount': chapter_count,
                                'verses': chapter_data  # Already in correct format from get_chapter_data
                            }
                            preview_json = json.dumps(preview_data).replace("'", "\\'")
                            script = f"if (window.updateChapterPreview) {{ window.updateChapterPreview({preview_json}); }}"
                            wx.CallAfter(lambda: main_window.webview.RunScript(script))
                            print(f"[Bridge] Sent {len(chapter_data)} verses for preview (book has {chapter_count} chapters)")
                        else:
                            print(f"[Bridge] No preview verses found")

                    except json.JSONDecodeError as e:
                        print(f"[Bridge] Error parsing chapter preview request: {e}")
                    except Exception as e:
                        print(f"[Bridge] Error loading chapter preview: {e}")
                        import traceback
                        traceback.print_exc()

                # Reset title after processing
                wx.CallAfter(lambda: main_window.webview.RunScript("document.title = 'NCF Bible and Hymn Projector';"))

            except Exception as e:
                print(f"[Bridge] Error processing command: {e}")
                import traceback
                traceback.print_exc()

    # Bind events
    main_window.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, on_loaded)
    main_window.webview.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, on_title_changed)

    print("[Bridge] Setup complete")
