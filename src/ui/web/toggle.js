// Toggle button functionality with mutual exclusivity
document.addEventListener('DOMContentLoaded', function() {
    // Get all toggle buttons
    const toggleButtons = document.querySelectorAll('.btn-toggle');

    // Helper function to hide a button (set to Project mode)
    function hideButton(button) {
        button.setAttribute('data-state', 'hidden');
        const icon = button.querySelector('.btn-icon');
        const text = button.querySelector('.btn-text');
        icon.textContent = '▶';

        // Set appropriate text based on button type
        const windowType = button.getAttribute('data-window');
        if (windowType === 'agenda') {
            text.textContent = 'Agenda';
        } else {
            text.textContent = 'Project';
        }

        // Hide reload button for Bible or Universal
        if (windowType === 'bible') {
            const reloadBtn = document.getElementById('bible-reload-btn');
            if (reloadBtn) {
                reloadBtn.style.display = 'none';
            }
        } else if (windowType === 'universal') {
            const reloadBtn = document.getElementById('universal-reload-btn');
            if (reloadBtn) {
                reloadBtn.style.display = 'none';
            }
        }
    }

    // Helper function to show a button (set to Hide mode)
    function showButton(button) {
        button.setAttribute('data-state', 'visible');
        const icon = button.querySelector('.btn-icon');
        const text = button.querySelector('.btn-text');
        icon.textContent = '◼';
        text.textContent = 'Hide';

        // Show reload button for Bible or Universal
        const windowType = button.getAttribute('data-window');
        if (windowType === 'bible') {
            const reloadBtn = document.getElementById('bible-reload-btn');
            if (reloadBtn) {
                reloadBtn.style.display = 'inline-flex';
            }
        } else if (windowType === 'universal') {
            const reloadBtn = document.getElementById('universal-reload-btn');
            if (reloadBtn) {
                reloadBtn.style.display = 'inline-flex';
            }
        }
    }

    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentState = this.getAttribute('data-state');
            const currentWindow = this.getAttribute('data-window');

            if (currentState === 'hidden') {
                // User wants to show this window
                // First, hide all other windows (mutual exclusivity)
                toggleButtons.forEach(otherButton => {
                    if (otherButton !== this) {
                        const otherState = otherButton.getAttribute('data-state');
                        const otherWindow = otherButton.getAttribute('data-window');

                        // Only hide if currently visible
                        if (otherState === 'visible') {
                            hideButton(otherButton);

                            // Actually hide the Python window
                            if (window.pythonBridge) {
                                if (otherWindow === 'agenda') {
                                    window.pythonBridge.hideAgenda();
                                } else {
                                    window.pythonBridge.hideProjection();
                                }
                            }
                        }
                    }
                });

                // Then show this window
                showButton(this);

                // Call Python bridge to show the appropriate content
                if (window.pythonBridge) {
                    if (currentWindow === 'universal') {
                        const url = document.getElementById('universal-input').value.trim();
                        if (url) {
                            window.pythonBridge.showURL(url);
                        } else {
                            alert('Please enter a URL, hymn ID, or Google Slides link');
                            hideButton(this);
                        }
                    } else if (currentWindow === 'agenda') {
                        // Show agenda using slides ID from config
                        window.pythonBridge.showAgenda();
                    } else if (currentWindow === 'bible') {
                        // Get current book and verse from inputs (RAW, don't normalize yet)
                        const book = document.getElementById('book-select').value;
                        const verse = document.getElementById('verse-input').value.trim();

                        if (!book || !verse) {
                            alert('Please select a book and enter chapter:verse');
                            hideButton(this);
                            return;
                        }

                        // Check if input has changed from last projection
                        const inputChanged = !window.lastBibleProjection ||
                                           window.lastBibleProjection.book !== book ||
                                           window.lastBibleProjection.verse !== verse;

                        if (inputChanged) {
                            // Input has changed, need to project new verses
                            console.log('[Bible Toggle] Input changed, projecting new verses');

                            // Get selected versions (checkboxes)
                            const versionCheckboxes = document.querySelectorAll('input[name="version"]:checked');
                            const versions = Array.from(versionCheckboxes).map(cb => cb.value);

                            if (versions.length === 0) {
                                alert('Please select at least one Bible version');
                                hideButton(this);
                                return;
                            }

                            // Get font sizes
                            const chineseSize = document.getElementById('chinese-size').value;
                            const englishSize = document.getElementById('english-size').value;

                            // Call real Bible projection (send RAW verse input, let Python normalize)
                            // Python will handle normalization and update the input field with actual range
                            window.pythonBridge.projectBibleVerse(book, verse, versions, chineseSize, englishSize);

                            // Mark that Bible window now has content (use RAW verse for tracking)
                            // Python will update this to actual range after processing
                            window.lastBibleProjection = {book: book, verse: verse};
                        } else {
                            // Input hasn't changed, just show existing Bible window without reloading
                            console.log('[Bible Toggle] Input unchanged, showing existing Bible window without reload');
                            window.pythonBridge.showBibleWindow();
                        }
                    }
                }
            } else {
                // User wants to hide this window
                // Just hide it (showing native background)
                hideButton(this);

                // Call Python bridge to hide the appropriate window
                if (window.pythonBridge) {
                    if (currentWindow === 'agenda') {
                        window.pythonBridge.hideAgenda();
                    } else if (currentWindow === 'bible') {
                        window.pythonBridge.hideBibleWindow();
                    } else if (currentWindow === 'universal') {
                        window.pythonBridge.hideHymnWindow();
                    }
                }
            }
        });
    });

    // Handle Universal Reload button
    const universalReloadBtn = document.getElementById('universal-reload-btn');
    if (universalReloadBtn) {
        universalReloadBtn.addEventListener('click', function() {
            const url = document.getElementById('universal-input').value.trim();
            if (url && window.pythonBridge) {
                window.pythonBridge.reloadURL(url);
            } else {
                alert('Please enter a URL, hymn ID, or Google Slides link');
            }
        });
    }

    // Handle Bible Reload button
    const bibleReloadBtn = document.getElementById('bible-reload-btn');
    if (bibleReloadBtn) {
        bibleReloadBtn.addEventListener('click', function() {
            // Get current Bible settings and re-project
            const book = document.getElementById('book-select').value;
            const verse = document.getElementById('verse-input').value.trim();

            if (book && verse) {
                const versionCheckboxes = document.querySelectorAll('input[name="version"]:checked');
                const versions = Array.from(versionCheckboxes).map(cb => cb.value);

                if (versions.length === 0) {
                    alert('Please select at least one Bible version');
                    return;
                }

                const chineseSize = document.getElementById('chinese-size').value;
                const englishSize = document.getElementById('english-size').value;

                // Add to history
                addToHistory(book, verse);

                if (window.pythonBridge) {
                    window.pythonBridge.projectBibleVerse(book, verse, versions, chineseSize, englishSize);
                    // Mark that Bible window now has content
                    window.lastBibleProjection = {book: book, verse: verse};
                }
            } else {
                alert('Please select a book and enter chapter:verse');
            }
        });
    }

    // Handle Verse Clear button
    const verseClearBtn = document.getElementById('verse-clear-btn');
    if (verseClearBtn) {
        verseClearBtn.addEventListener('click', function() {
            // Clear the verse input
            const verseInput = document.getElementById('verse-input');
            if (verseInput) {
                verseInput.value = '';
            }

            // Reset the book dropdown to empty
            const bookSelect = document.getElementById('book-select');
            if (bookSelect) {
                bookSelect.value = '';
            }

            // Focus on the verse input for convenience
            if (verseInput) {
                verseInput.focus();
            }
        });
    }

    // Handle Verse Preview button (Load chapter)
    const versePreviewBtn = document.getElementById('verse-preview-btn');
    if (versePreviewBtn) {
        versePreviewBtn.addEventListener('click', function() {
            const book = document.getElementById('book-select').value.trim();
            const verseInput = document.getElementById('verse-input').value.trim();

            if (!book) {
                alert('Please select a book first');
                return;
            }

            // Extract chapter number from verse input (e.g., "3:16" -> 3)
            let chapter = 1;
            if (verseInput) {
                const parts = verseInput.split(':');
                chapter = parseInt(parts[0]) || 1;
            }

            // Get all selected versions for preview
            const versionCheckboxes = document.querySelectorAll('input[name="version"]:checked');
            const versions = Array.from(versionCheckboxes).map(cb => cb.value);

            // Default to kjv if no versions selected
            if (versions.length === 0) {
                versions.push('kjv');
            }

            // Call Python bridge to load chapter preview
            if (window.pythonBridge) {
                window.pythonBridge.loadChapterPreview(book, chapter, versions);
            }
        });
    }
    // Track currently projected Bible verse state
    window.currentProjection = null; // { book: "John", chapter: 3, startVerse: 16, endVerse: 16, maxVerse: 21 }

    // Helper function to normalize verse reference (handle spaces)
    function normalizeVerseRef(verseRef) {
        // Convert "1 4-9" or "1 4" to "1:4-9" or "1:4"
        let normalized = verseRef.trim();

        // Replace first space with colon if no colon exists
        if (!normalized.includes(':') && normalized.includes(' ')) {
            const parts = normalized.split(' ');
            if (parts.length >= 2) {
                // Join chapter and verse parts, removing extra spaces
                normalized = parts[0] + ':' + parts.slice(1).join('').replace(/\s+/g, '');
            }
        }

        return normalized;
    }

    // Helper function to parse verse reference into components
    function parseVerseRef(verseRef) {
        const normalized = normalizeVerseRef(verseRef);
        const parts = normalized.split(':');

        // If only chapter number provided (e.g., "119"), project entire chapter
        if (parts.length === 1) {
            const chapter = parseInt(parts[0]);
            if (isNaN(chapter)) {
                return null;
            }
            // Use 1-999 as temporary placeholder to signal "entire chapter"
            // Backend will replace this with actual verse count (e.g., 3:1-31)
            return {
                chapter,
                startVerse: 1,
                endVerse: 999,
                normalized: chapter + ':1-999'
            };
        }

        if (parts.length < 2) {
            return null;
        }

        const chapter = parseInt(parts[0]);
        const versePart = parts[1];

        let startVerse, endVerse;
        if (versePart.includes('-')) {
            const rangeParts = versePart.split('-');
            startVerse = parseInt(rangeParts[0]);
            endVerse = parseInt(rangeParts[1]);
        } else {
            startVerse = endVerse = parseInt(versePart);
        }

        return { chapter, startVerse, endVerse, normalized };
    }

    // Bible verse history management
    const verseHistory = [];
    const MAX_HISTORY = 20;

    function addToHistory(book, verse) {
        // Normalize verse reference: convert spaces to colons
        // "3 8" -> "3:8", "3 8-10" -> "3:8-10"
        let normalizedVerse = verse.trim();
        if (normalizedVerse.includes(' ') && !normalizedVerse.includes(':')) {
            // Replace first space with colon and remove remaining spaces
            const parts = normalizedVerse.split(' ');
            if (parts.length >= 2) {
                normalizedVerse = parts[0] + ':' + parts.slice(1).join('').replace(/\s+/g, '');
            }
        }

        const entry = book + ' ' + normalizedVerse;
        // Remove if already exists
        const index = verseHistory.indexOf(entry);
        if (index > -1) {
            verseHistory.splice(index, 1);
        }
        // Add to beginning
        verseHistory.unshift(entry);
        // Limit size
        if (verseHistory.length > MAX_HISTORY) {
            verseHistory.pop();
        }
        // Update dropdown
        updateHistoryDropdown();
    }

    function updateHistoryDropdown() {
        const historySelect = document.getElementById('verse-history-select');
        if (!historySelect) return;

        // Clear existing options except the first placeholder
        historySelect.innerHTML = '<option value="">History...</option>';

        // Add history entries
        verseHistory.forEach(function(entry) {
            const option = document.createElement('option');
            option.value = entry;
            option.textContent = entry;
            historySelect.appendChild(option);
        });
    }

    // Handle Verse History dropdown selection
    const verseHistorySelect = document.getElementById('verse-history-select');
    if (verseHistorySelect) {
        verseHistorySelect.addEventListener('change', function() {
            const selectedValue = this.value;
            if (!selectedValue) return;

            // Parse book and verse
            const parts = selectedValue.split(' ');
            if (parts.length >= 2) {
                const verse = parts[parts.length - 1];
                const book = parts.slice(0, -1).join(' ');

                // Update inputs
                document.getElementById('book-select').value = book;
                document.getElementById('verse-input').value = verse;

                // Auto-project the verse
                const versionCheckboxes = document.querySelectorAll('input[name="version"]:checked');
                const versions = Array.from(versionCheckboxes).map(cb => cb.value);

                if (versions.length === 0) {
                    alert('Please select at least one Bible version');
                    this.value = ''; // Reset dropdown
                    return;
                }

                const chineseSize = document.getElementById('chinese-size').value;
                const englishSize = document.getElementById('english-size').value;

                if (window.pythonBridge) {
                    window.pythonBridge.projectBibleVerse(book, verse, versions, chineseSize, englishSize);
                    // Mark that Bible window now has content
                    window.lastBibleProjection = {book: book, verse: verse};
                }

                // Reset dropdown to placeholder
                this.value = '';
            }
        });
    }

    // Helper function to get currently selected versions
    function getCurrentlySelectedVersions() {
        const versionCheckboxes = document.querySelectorAll('input[name="version"]:checked');
        const versions = Array.from(versionCheckboxes).map(cb => cb.value);

        // Default to kjv if no versions selected
        if (versions.length === 0) {
            versions.push('kjv');
        }

        return versions;
    }

    // Handle Previous Chapter button
    const prevChapterBtn = document.getElementById('prev-chapter-btn');
    if (prevChapterBtn) {
        prevChapterBtn.addEventListener('click', function() {
            if (window.currentPreviewState) {
                const state = window.currentPreviewState;
                const newChapter = state.chapter - 1;

                if (newChapter >= 1) {
                    // Read current version selection (don't use stored state)
                    const currentVersions = getCurrentlySelectedVersions();

                    // Load previous chapter with current version selection
                    if (window.pythonBridge) {
                        window.pythonBridge.loadChapterPreview(state.book, newChapter, currentVersions);
                    }
                }
            }
        });
    }

    // Handle Next Chapter button
    const nextChapterBtn = document.getElementById('next-chapter-btn');
    if (nextChapterBtn) {
        nextChapterBtn.addEventListener('click', function() {
            if (window.currentPreviewState) {
                const state = window.currentPreviewState;
                const newChapter = state.chapter + 1;

                if (state.chapterCount && newChapter <= state.chapterCount) {
                    // Read current version selection (don't use stored state)
                    const currentVersions = getCurrentlySelectedVersions();

                    // Load next chapter with current version selection
                    if (window.pythonBridge) {
                        window.pythonBridge.loadChapterPreview(state.book, newChapter, currentVersions);
                    }
                }
            }
        });
    }

    // Handle Google Meet Auto Join & Share button
    const meetAutoJoinBtn = document.getElementById('meet-auto-join-btn');
    if (meetAutoJoinBtn) {
        meetAutoJoinBtn.addEventListener('click', function() {
            const meetUrl = document.getElementById('meet-url-input').value.trim();

            if (!meetUrl) {
                alert('Please enter a Google Meet URL');
                return;
            }

            // Send command to Python to auto join meeting and share screen
            if (window.pythonBridge) {
                const data = JSON.stringify({
                    url: meetUrl
                });
                document.title = 'CMD:joinGoogleMeet:' + data;
            }
        });
    }

    // Handle Google Meet Manual Join button
    const meetManualJoinBtn = document.getElementById('meet-manual-join-btn');
    if (meetManualJoinBtn) {
        meetManualJoinBtn.addEventListener('click', function() {
            const meetUrl = document.getElementById('meet-url-input').value.trim();

            if (!meetUrl) {
                alert('Please enter a Google Meet URL');
                return;
            }

            // Simply open URL in default browser (no automation)
            if (window.pythonBridge) {
                const data = JSON.stringify({
                    url: meetUrl,
                    manual: true
                });
                document.title = 'CMD:openMeetManually:' + data;
            }
        });
    }
});

// Global state for current preview
window.currentPreviewState = null;

// Global function to update chapter preview (called from Python)
window.updateChapterPreview = function(previewData) {
    const previewContainer = document.getElementById('chapter-preview');
    const chapterInfo = document.getElementById('chapter-info');

    if (!previewContainer || !previewData || !previewData.verses) {
        return;
    }

    // Store current state for navigation
    window.currentPreviewState = {
        book: previewData.book,
        chapter: previewData.chapter,
        versions: previewData.versions,
        chapterCount: previewData.chapterCount || null
    };

    // Update header info
    if (chapterInfo) {
        chapterInfo.textContent = previewData.book + ' ' + previewData.chapter;
    }

    // Enable/disable navigation buttons based on chapter bounds
    const prevBtn = document.getElementById('prev-chapter-btn');
    const nextBtn = document.getElementById('next-chapter-btn');

    if (prevBtn) {
        prevBtn.disabled = (previewData.chapter <= 1);
    }
    if (nextBtn) {
        nextBtn.disabled = (previewData.chapterCount && previewData.chapter >= previewData.chapterCount);
    }

    // Get version labels
    const versionLabels = {
        'cuv': '和合本',
        'kjv': 'KJV',
        'nas': 'NASB',
        'niv': 'NIV',
        'dby': 'Darby'
    };

    // Build verse list HTML with multiple versions
    let html = '<div class="verse-list">';
    previewData.verses.forEach(function(verseData) {
        const verseNum = verseData.verse;
        html += '<div class="verse-item" data-verse="' + verseNum + '">';
        html += '<span class="verse-number">' + verseNum + '</span>';
        html += '<div class="verse-content">';

        // Display each version
        previewData.versions.forEach(function(version) {
            if (verseData[version]) {
                html += '<div class="verse-version">';
                html += '<span class="version-label">' + (versionLabels[version] || version.toUpperCase()) + ':</span> ';
                html += '<span class="verse-text">' + verseData[version] + '</span>';
                html += '</div>';
            }
        });

        html += '</div></div>';
    });
    html += '</div>';

    // Update preview container
    previewContainer.innerHTML = html;

    // Scroll to top of preview when chapter changes
    previewContainer.scrollTop = 0;

    // Add click handlers to verses
    const verseItems = previewContainer.querySelectorAll('.verse-item');
    verseItems.forEach(function(item) {
        item.addEventListener('click', function(event) {
            // Find the verse item even if user clicked on a child element
            const verseItem = event.target.closest('.verse-item');
            if (!verseItem) return;

            const verseNum = verseItem.getAttribute('data-verse');
            const chapter = previewData.chapter;
            const book = previewData.book;

            // Update verse input with clicked verse
            const verseInput = document.getElementById('verse-input');
            const verseRef = chapter + ':' + verseNum;
            if (verseInput) {
                verseInput.value = verseRef;
            }

            // Update book input
            const bookInput = document.getElementById('book-select');
            if (bookInput) {
                bookInput.value = book;
            }

            // Get selected versions
            const versionCheckboxes = document.querySelectorAll('input[name="version"]:checked');
            const versions = Array.from(versionCheckboxes).map(cb => cb.value);

            if (versions.length === 0) {
                alert('Please select at least one Bible version');
                return;
            }

            // Get font sizes
            const chineseSize = document.getElementById('chinese-size').value;
            const englishSize = document.getElementById('english-size').value;

            // Add to history
            if (typeof addToHistory === 'function') {
                addToHistory(book, verseRef);
            }

            // Project the verse
            if (window.pythonBridge && typeof window.pythonBridge.projectBibleVerse === 'function') {
                window.pythonBridge.projectBibleVerse(book, verseRef, versions, chineseSize, englishSize);
                // Mark that Bible window now has content
                window.lastBibleProjection = {book: book, verse: verseRef};
            } else {
                console.error('[Preview Click] pythonBridge not available');
                return;
            }

            // Update toggle button to show as active
            const bibleToggleBtn = document.getElementById('bible-toggle-btn');
            if (bibleToggleBtn) {
                bibleToggleBtn.setAttribute('data-state', 'visible');
                const icon = bibleToggleBtn.querySelector('.btn-icon');
                const text = bibleToggleBtn.querySelector('.btn-text');
                if (icon) icon.textContent = '◼';
                if (text) text.textContent = 'Hide';

                // Show reload button
                const reloadBtn = document.getElementById('bible-reload-btn');
                if (reloadBtn) {
                    reloadBtn.style.display = 'inline-flex';
                }
            }

            // Hide other windows (mutual exclusivity)
            const universalToggleBtn = document.getElementById('universal-toggle-btn');
            const agendaToggleBtn = document.getElementById('agenda-toggle-btn');

            if (universalToggleBtn && universalToggleBtn.getAttribute('data-state') === 'visible') {
                universalToggleBtn.setAttribute('data-state', 'hidden');
                const icon = universalToggleBtn.querySelector('.btn-icon');
                const text = universalToggleBtn.querySelector('.btn-text');
                if (icon) icon.textContent = '▶';
                if (text) text.textContent = 'Project';
                const reloadBtn = document.getElementById('universal-reload-btn');
                if (reloadBtn) reloadBtn.style.display = 'none';
                if (window.pythonBridge) window.pythonBridge.hideProjection();
            }

            if (agendaToggleBtn && agendaToggleBtn.getAttribute('data-state') === 'visible') {
                agendaToggleBtn.setAttribute('data-state', 'hidden');
                const icon = agendaToggleBtn.querySelector('.btn-icon');
                const text = agendaToggleBtn.querySelector('.btn-text');
                if (icon) icon.textContent = '▶';
                if (text) text.textContent = 'Agenda';
                if (window.pythonBridge) window.pythonBridge.hideAgenda();
            }
        });
    });
};
