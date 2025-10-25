"""
Google Meet Automation using macOS AppleScript and Accessibility APIs.

This module provides automated Google Meet joining and screen sharing
using macOS-native automation (AppleScript + System Events).

IMPORTANT: macOS only - will not work on Windows/Linux.
"""

import subprocess
import time
import platform
from pathlib import Path


class GoogleMeetAutomation:
    """
    Handles automated Google Meet joining and screen sharing using macOS automation.

    Uses AppleScript and macOS Accessibility APIs to control Chrome browser.
    This avoids browser automation detection by Google Meet.
    """

    def __init__(self):
        """Initialize the automation handler."""
        if platform.system() != "Darwin":
            raise RuntimeError("Google Meet automation only supports macOS")

        self.chrome_app = "Google Chrome"
        self.meet_tab_title = None

    def join_meeting(self, meet_url):
        """
        Join a Google Meet and share the second monitor.

        Args:
            meet_url: The Google Meet URL to join

        Returns:
            bool: True if automation was initiated successfully
        """
        try:
            print(f"[GoogleMeet] Starting macOS automation for: {meet_url}")

            # Step 1: Open URL in Chrome
            self._open_url_in_chrome(meet_url)
            time.sleep(3)  # Wait for page to load

            # Step 2: Check if already in meeting (detect "Switch here" vs "Join now")
            # Step 3: Click "Join now" button (or handle other states)
            self._click_join_button()
            time.sleep(3)  # Wait for meeting to load

            # Step 4: Start presenting (share second monitor)
            print(f"[GoogleMeet] Starting screen share automation...")
            self._start_presenting()

            print(f"[GoogleMeet] ✅ Automation completed")
            return True

        except Exception as e:
            print(f"[GoogleMeet] ❌ Automation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop_sharing(self):
        """
        Stop screen sharing in the active Google Meet.

        Returns:
            bool: True if successful
        """
        try:
            print(f"[GoogleMeet] Stopping screen share via macOS automation")

            # Click "Stop sharing" button using AppleScript
            script = '''
            tell application "Google Chrome"
                activate
                tell application "System Events"
                    tell process "Google Chrome"
                        -- Look for "Stop sharing" button
                        -- This is typically at the bottom of the screen
                        set frontmost to true
                        delay 0.5

                        -- Try to click the stop sharing button
                        -- Google Meet shows it as a floating bar at the bottom
                        try
                            click (first button whose description contains "Stop" or name contains "Stop")
                        on error
                            -- Button might be in different location
                            keystroke "p" using {command down, shift down}
                        end try
                    end tell
                end tell
            end tell
            '''

            self._run_applescript(script)
            print(f"[GoogleMeet] ✅ Stop sharing command sent")
            return True

        except Exception as e:
            print(f"[GoogleMeet] ❌ Failed to stop sharing: {e}")
            return False

    def _open_url_in_chrome(self, url):
        """Open URL in Chrome using AppleScript."""
        script = f'''
        tell application "Google Chrome"
            activate

            -- Check if there's already a window open
            if (count of windows) = 0 then
                make new window
            end if

            -- Open URL in new tab
            tell front window
                make new tab with properties {{URL:"{url}"}}
            end tell
        end tell
        '''

        self._run_applescript(script)
        print(f"[GoogleMeet] Opened URL in Chrome")

    def _click_join_button(self):
        """
        Click the join button using JavaScript injection, with mouse click fallback.

        First tries JavaScript injection (requires Chrome setting enabled).
        Falls back to simulated mouse click if JavaScript is disabled.
        """
        # Try JavaScript first
        script_js = '''
        tell application "Google Chrome"
            activate
            delay 3

            try
                -- Execute JavaScript to click the join button
                tell active tab of front window
                    set jsResult to execute javascript "(() => { const btns = Array.from(document.querySelectorAll('button, div[role=button]')); const join = btns.find(b => (b.innerText || '').match(/Join|join/)); if (join) { join.click(); return 'SUCCESS'; } return 'NOT_FOUND'; })()"
                    log "JavaScript result: " & jsResult
                    return jsResult
                end tell
            on error errMsg
                log "JavaScript error: " & errMsg
                return "JS_DISABLED"
            end try
        end tell
        '''

        try:
            result = self._run_applescript(script_js)
            if "SUCCESS" in result:
                print(f"[GoogleMeet] ✅ Clicked join button via JavaScript")
                return
            elif "JS_DISABLED" in result:
                print(f"[GoogleMeet] ⚠️  JavaScript from AppleScript is disabled in Chrome")
                print(f"[GoogleMeet] 💡 Enable it: View > Developer > Allow JavaScript from Apple Events")
                print(f"[GoogleMeet] 🔄 Falling back to keyboard method...")
                self._click_join_button_keyboard()
                return
        except Exception as e:
            print(f"[GoogleMeet] JavaScript method failed: {e}")
            print(f"[GoogleMeet] Trying keyboard fallback...")
            self._click_join_button_keyboard()

    def _click_join_button_keyboard(self):
        """
        Fallback method: Use keyboard shortcuts to join.
        Simpler and works without JavaScript permission.
        """
        script = '''
        tell application "Google Chrome"
            activate
            delay 3
        end tell

        tell application "System Events"
            tell process "Google Chrome"
                set frontmost to true
                delay 1

                -- Press Return key (Enter) to join
                -- Google Meet auto-focuses the Join button on page load
                keystroke return

                log "Pressed Enter to join"
            end tell
        end tell
        '''

        self._run_applescript(script)
        print(f"[GoogleMeet] Pressed Enter key to join (keyboard fallback)")

    def _start_presenting(self):
        """
        Start presenting by clicking 'Present now' and selecting second monitor.

        Google Meet presentation flow:
        1. Click "Present now" button (bottom toolbar) via JavaScript
        2. Wait for screen picker dialog (macOS native dialog)
        3. Use keyboard navigation to select second monitor
        4. Click "Share" button
        """
        # Step 1: Click "Present now" button using JavaScript
        print(f"[GoogleMeet] Step 1: Clicking 'Present now' button...")
        script_present = '''
        tell application "Google Chrome"
            activate
            delay 2

            try
                -- Click the "Share screen" button via JavaScript
                tell active tab of front window
                    set jsResult to execute javascript "(() => { const btns = Array.from(document.querySelectorAll('button, div[role=button]')); const present = btns.find(b => { const label = b.getAttribute('aria-label') || ''; const text = (b.innerText || b.textContent || ''); return label.includes('Share screen') || label.includes('Present') || text.includes('Present now'); }); if (present) { console.log('Clicking Share screen button'); present.click(); return 'CLICKED_PRESENT'; } return 'NOT_FOUND'; })()"
                    log "Present button result: " & jsResult
                    return jsResult
                end tell
            on error errMsg
                log "JavaScript error: " & errMsg
                return "JS_DISABLED"
            end try
        end tell
        '''

        try:
            result = self._run_applescript(script_present)
            if "CLICKED_PRESENT" in result:
                print(f"[GoogleMeet] ✅ Clicked 'Present now' button")
            else:
                print(f"[GoogleMeet] ⚠️  Could not find Present button, trying keyboard fallback...")
                self._click_present_keyboard()
                return
        except Exception as e:
            print(f"[GoogleMeet] Error clicking present: {e}")
            return

        # Step 2: Wait for screen picker dialog to appear
        time.sleep(2)
        print(f"[GoogleMeet] Step 2: Screen picker dialog should be open...")

        # Step 3: Use keyboard to navigate and select second monitor
        print(f"[GoogleMeet] Step 3: Selecting screen to share...")
        self._select_screen_to_share()

    def _click_present_keyboard(self):
        """Fallback: Try to click present using keyboard shortcuts."""
        script = '''
        tell application "Google Chrome"
            activate
        end tell

        tell application "System Events"
            tell process "Google Chrome"
                -- Try Cmd+E (sometimes works for present)
                keystroke "e" using {command down}
                delay 1
            end tell
        end tell
        '''
        self._run_applescript(script)

    def _select_screen_to_share(self):
        """
        Navigate the Chrome native share dialog using COORDINATE-BASED MOUSE CLICKS.

        The Chrome share dialog:
        - Cannot be accessed via JavaScript (outside the DOM)
        - Has no accessible element names (all "missing value")
        - Requires clicking at specific screen coordinates

        This is fragile and may need adjustment based on screen resolution and dialog position.
        """
        print(f"[GoogleMeet] Using coordinate-based clicking for share dialog...")
        print(f"[GoogleMeet] ⚠️  Please manually complete if automation fails")

        script = '''
        tell application "System Events"
            tell process "Google Chrome"
                set frontmost to true
                delay 1.5

                -- Get the share dialog window
                set shareWindow to window "Choose what to share with meet.google.com"

                -- Get dialog position and size
                set dialogPosition to position of shareWindow
                set dialogSize to size of shareWindow
                set dialogX to item 1 of dialogPosition
                set dialogY to item 2 of dialogPosition
                set dialogWidth to item 1 of dialogSize
                set dialogHeight to item 2 of dialogSize

                log "Dialog at: " & dialogX & "," & dialogY & " size: " & dialogWidth & "x" & dialogHeight

                -- Calculate click positions relative to dialog
                -- Coordinates measured from actual dialog:
                -- "Entire screen" tab: 10/13 width, 9/50 height
                set entireScreenX to dialogX + (dialogWidth * 10 / 13)
                set entireScreenY to dialogY + (dialogHeight * 9 / 50)

                -- Click "Entire screen" tab
                click at {entireScreenX, entireScreenY}
                log "Clicked at Entire screen tab (10/13, 9/50)"
                delay 1

                -- Screen 2 thumbnail: 10/13 width, 20/50 height
                set screen2X to dialogX + (dialogWidth * 10 / 13)
                set screen2Y to dialogY + (dialogHeight * 20 / 50)

                -- Click Screen 2
                click at {screen2X, screen2Y}
                log "Clicked at Screen 2 (10/13, 20/50)"
                delay 1

                -- Share button: 11/13 width, 48/50 height
                set shareButtonX to dialogX + (dialogWidth * 11 / 13)
                set shareButtonY to dialogY + (dialogHeight * 48 / 50)

                -- Click Share button
                click at {shareButtonX, shareButtonY}
                log "Clicked at Share button (11/13, 48/50)"

            end tell
        end tell
        '''

        self._run_applescript(script)
        print(f"[GoogleMeet] ✅ Clicked at estimated positions")
        print(f"[GoogleMeet] 💡 If incorrect, manually click: Entire screen → Screen 2 → Share")

    def _run_applescript(self, script):
        """
        Execute an AppleScript and return the result.

        Args:
            script: AppleScript code to execute

        Returns:
            str: Script output

        Raises:
            RuntimeError: If script execution fails
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"AppleScript failed: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("AppleScript execution timed out")
        except FileNotFoundError:
            raise RuntimeError("osascript not found - are you on macOS?")