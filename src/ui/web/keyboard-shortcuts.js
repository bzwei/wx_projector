/**
 * Keyboard Shortcuts
 * Handle Enter key for quick projection
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enter key on hymn/URL input -> trigger Project or Reload button
    const universalInput = document.getElementById('universal-input');
    if (universalInput) {
        universalInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();

                // Check if hymn/URL is already projected (reload button visible)
                const reloadBtn = document.getElementById('universal-reload-btn');
                const projectBtn = document.getElementById('universal-toggle-btn');

                if (reloadBtn && reloadBtn.style.display !== 'none') {
                    // Reload button is visible, click it to reload
                    reloadBtn.click();
                } else if (projectBtn) {
                    // Otherwise click the project/hide toggle
                    projectBtn.click();
                }
            }
        });
    }

    // Enter key on book select -> trigger Project or Reload button
    const bookSelect = document.getElementById('book-select');
    if (bookSelect) {
        bookSelect.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();

                // Check if Bible is already projected (reload button visible)
                const reloadBtn = document.getElementById('bible-reload-btn');
                const bibleToggleBtn = document.getElementById('bible-toggle-btn');

                if (reloadBtn && reloadBtn.style.display !== 'none') {
                    // Reload button is visible, click it
                    reloadBtn.click();
                } else if (bibleToggleBtn) {
                    // Otherwise click the project/hide toggle
                    bibleToggleBtn.click();
                }
            }
        });
    }

    // Enter key on verse input -> trigger Project or Reload button
    const verseInput = document.getElementById('verse-input');
    if (verseInput) {
        verseInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();

                // Check if Bible is already projected (reload button visible)
                const reloadBtn = document.getElementById('bible-reload-btn');
                const bibleToggleBtn = document.getElementById('bible-toggle-btn');

                if (reloadBtn && reloadBtn.style.display !== 'none') {
                    // Reload button is visible, click it
                    reloadBtn.click();
                } else if (bibleToggleBtn) {
                    // Otherwise click the project/hide toggle
                    bibleToggleBtn.click();
                }
            }
        });
    }

    console.log('[KeyboardShortcuts] Enter key handlers initialized');

    // Custom error notification function (no Python logo, no "Message" text)
    window.showErrorNotification = function(message) {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        // Create error box
        const errorBox = document.createElement('div');
        errorBox.style.cssText = `
            background: white;
            padding: 30px 40px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            text-align: center;
        `;

        // Error icon
        const icon = document.createElement('div');
        icon.textContent = '⚠️';
        icon.style.cssText = 'font-size: 48px; margin-bottom: 15px;';

        // Error message
        const msg = document.createElement('div');
        msg.textContent = message;
        msg.style.cssText = `
            font-size: 16px;
            color: #333;
            margin-bottom: 20px;
            line-height: 1.5;
        `;

        // OK button
        const okBtn = document.createElement('button');
        okBtn.textContent = 'OK';
        okBtn.className = 'btn btn-primary';
        okBtn.style.cssText = 'padding: 10px 30px;';
        okBtn.onclick = function() {
            document.body.removeChild(overlay);
        };

        errorBox.appendChild(icon);
        errorBox.appendChild(msg);
        errorBox.appendChild(okBtn);
        overlay.appendChild(errorBox);
        document.body.appendChild(overlay);

        // Focus OK button
        okBtn.focus();
    };
});
