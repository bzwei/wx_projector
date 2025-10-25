/**
 * Book Dropdown Search/Filter
 * Filters book options as user types
 */

(function() {
    let allBooks = []; // Store all book options
    let bookSelect = null;

    // Initialize when DOM is ready
    function init() {
        bookSelect = document.getElementById('book-select');
        if (!bookSelect) {
            console.error('[BookSearch] book-select not found');
            return;
        }

        // Store all original options
        const options = bookSelect.querySelectorAll('option');
        allBooks = Array.from(options).map(opt => ({
            value: opt.value,
            text: opt.textContent
        }));

        console.log('[BookSearch] Initialized with', allBooks.length, 'books');

        // Add event listener for typing
        bookSelect.addEventListener('keyup', handleKeyup);
        bookSelect.addEventListener('input', handleInput);
    }

    function handleKeyup(event) {
        const key = event.key;

        // If user pressed a letter or number, filter the list
        if (key.length === 1 && /[a-zA-Z0-9\u4e00-\u9fff]/.test(key)) {
            filterBooks();
        }
    }

    function handleInput(event) {
        // This handles when user selects from dropdown
        // Reset filter if a valid book was selected
        const selectedValue = bookSelect.value;
        if (selectedValue && allBooks.some(b => b.value === selectedValue)) {
            // Valid selection - do nothing
            return;
        }
    }

    function filterBooks() {
        // Get the currently selected text (what user has typed/selected)
        const selectedIndex = bookSelect.selectedIndex;
        const currentText = selectedIndex >= 0 ? bookSelect.options[selectedIndex].text : '';

        // Get search query from the selected option text
        let searchQuery = currentText.toLowerCase();

        console.log('[BookSearch] Filtering with query:', searchQuery);

        // Filter books that match the query
        const matchingBooks = allBooks.filter(book => {
            const bookText = book.text.toLowerCase();
            return bookText.includes(searchQuery) || bookText.startsWith(searchQuery);
        });

        console.log('[BookSearch] Found', matchingBooks.length, 'matches');

        // Clear current options
        bookSelect.innerHTML = '';

        // Add empty option first
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = 'Select book...';
        bookSelect.appendChild(emptyOption);

        // Add matching options
        matchingBooks.forEach(book => {
            const option = document.createElement('option');
            option.value = book.value;
            option.textContent = book.text;
            bookSelect.appendChild(option);
        });

        // If only one match (plus empty option), select it
        if (matchingBooks.length === 1) {
            bookSelect.selectedIndex = 1; // Select the first real option (after empty)
        }
    }

    // Alternative approach: Use datalist for better browser support
    function convertToDatalist() {
        // This would convert the select to an input with datalist
        // More flexible but requires HTML changes
    }

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose globally for debugging
    window.bookSearch = {
        init,
        filterBooks,
        reset: function() {
            if (bookSelect) {
                bookSelect.innerHTML = '';
                const emptyOption = document.createElement('option');
                emptyOption.value = '';
                emptyOption.textContent = 'Select book...';
                bookSelect.appendChild(emptyOption);

                allBooks.forEach(book => {
                    const option = document.createElement('option');
                    option.value = book.value;
                    option.textContent = book.text;
                    bookSelect.appendChild(option);
                });
            }
        }
    };
})();
