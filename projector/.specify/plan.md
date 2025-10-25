# Implementation Plan: Webpage Projector - Hybrid Architecture (v2.0)

**Branch**: `main` | **Date**: 2025-10-12 | **Spec**: [specification.md](./specification.md)
**Architecture**: Hybrid (Web UI + Native Projection)

## Summary

Webpage Projector is a hybrid desktop application for worship services that projects Google Slides and Bible verses to a secondary display. The application uses a **web-based control panel** (HTML/CSS/JavaScript inside wx.html2.WebView) for a modern, beautiful UI inspired by ncfnj.org/bible, while using **native borderless windows** for true fullscreen projection with multi-monitor support.

**Key Innovation**: Combines the best of both worlds - modern web UI development with native OS-level window control.

## Technical Context

**Language/Version**: Python 3.12 (backend), HTML5/CSS3/ES6+ (frontend)
**Primary Dependencies**: wxPython 4.2+ (wx.html2.WebView), screeninfo (monitor detection), uv (package manager)
**Frontend**: HTML/CSS/JavaScript (no frameworks - vanilla for simplicity)
**Backend**: Python with wxPython native components
**Communication**: JavaScript ↔ Python bridge via wx.html2 message handlers
**Storage**: Local files (CSV for lookups, text files for Bible verses, JSON for config)
**Testing**: pytest (Python), Jest (JavaScript), pytest-qt (integration)
**Target Platform**: macOS 12+ (primary), Windows 10+, Linux (Ubuntu 20.04+) secondary
**Project Type**: Hybrid desktop application (web control + native projection)
**Performance Goals**: <3s startup, <500ms projection render, <200ms Bible chapter load, <100ms bridge communication
**Constraints**: <250MB memory idle, <5% CPU idle, must work offline
**Scale/Scope**: 2 windows (hybrid control + native projection), 5 Bible versions, ~1200 Bible chapters, 400+ hymns

## Constitution Check

**Status**: ✅ Constitution file is a template - no specific constraints defined yet

*This project follows standard desktop application patterns. No constitution violations detected.*

## Project Structure

### Documentation (this feature)

```
projector/.specify/
├── specification.md        # Complete feature specification
├── plan.md                 # This file - implementation plan
├── research.md             # Phase 0 output - UX research and decisions
├── data-model.md           # Phase 1 output - UI state models
├── quickstart.md           # Phase 1 output - development setup guide
└── contracts/              # Phase 1 output - component interfaces
```

### Source Code (repository root)

```
webpage_projector/
├── projector/
│   └── .specify/           # Planning and specification artifacts
├── src/
│   ├── main.py             # Application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── web/                        # Web-based control panel (Phase 1-2)
│   │   │   ├── index.html              # Main HTML structure (Phase 1)
│   │   │   ├── styles.css              # Modern CSS (Phase 1)
│   │   │   ├── app.js                  # Main JavaScript controller (Phase 2)
│   │   │   ├── components/             # JavaScript modules (Phase 2)
│   │   │   │   ├── bridge.js           # JS ↔ Python communication
│   │   │   │   ├── url_controller.js   # URL projection UI logic
│   │   │   │   ├── slides_controller.js # Google Slides UI logic
│   │   │   │   └── bible_controller.js # Bible selection UI logic
│   │   │   └── assets/                 # Images, icons (Phase 1)
│   │   ├── main_window.py              # wxPython window with WebView (Phase 2)
│   │   ├── web_controller.py           # WebView manager + message handlers (Phase 2)
│   │   └── projection_window.py        # Native borderless projection (Phase 3)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── display_manager.py          # Monitor detection (Phase 3)
│   │   ├── bible_engine.py             # Bible text loader (Phase 4)
│   │   ├── content_renderer.py         # HTML rendering for projection (Phase 4)
│   │   └── history_manager.py          # Projection history (Phase 5)
│   ├── data/
│   │   ├── __init__.py
│   │   ├── bible_repository.py         # Bible file I/O (Phase 4)
│   │   ├── slides_repository.py        # Hymn CSV lookup (Phase 4)
│   │   └── config_manager.py           # Settings persistence (Phase 5)
│   └── utils/
│       ├── __init__.py
│       ├── parsers.py                  # Verse reference parsing (Phase 4)
│       └── validators.py               # Input validation (Phase 3)
├── books/                              # Bible text files (existing data)
├── hymns.csv                           # Hymn mappings (existing data)
├── books.csv                           # Bible metadata (existing data)
├── tests/
│   ├── __init__.py
│   ├── web/
│   │   └── test_bridge.js              # JavaScript ↔ Python bridge tests (Phase 2)
│   ├── ui/
│   │   └── test_web_controller.py      # WebView integration tests (Phase 2)
│   ├── core/
│   │   ├── test_bible_engine.py        # Engine tests (Phase 4)
│   │   └── test_display_manager.py     # Display tests (Phase 3)
│   └── integration/
│       └── test_projection_flow.py     # End-to-end tests (Phase 6)
├── pyproject.toml                      # Project configuration
├── uv.lock                             # Dependency lock file
└── README.md                           # User documentation
```

**Structure Decision**: Hybrid architecture selected with web-based control panel inside native wxPython window. Frontend web files in `src/ui/web/`, Python backend in `src/core/`, native UI wrappers in `src/ui/`. This structure enables modern web UI development while maintaining native OS capabilities for borderless projection.

## Phased Implementation Plan (Hybrid Architecture)

### Phase 0: Research & Foundation ✅ **COMPLETED**
**Goal**: Research hybrid architecture approach and establish technical feasibility

**Completed Outputs**:
- ✅ `research.md`: Hybrid architecture research, wx.html2.WebView capabilities
- ✅ `HYBRID_ARCHITECTURE_ANALYSIS.md`: Technical implementation guide
- ✅ Development environment validated (Python 3.12 + uv + wxPython)
- ✅ Analyzed ncfnj.org/bible web UI for design inspiration

**Research Findings**:
1. ✅ wx.html2.WebView provides excellent cross-platform HTML/CSS/JS support
2. ✅ JavaScript ↔ Python bridge via message handlers is reliable
3. ✅ Native borderless windows work independently from WebView
4. ✅ Web UI provides superior styling and layout capabilities vs native wxPython
5. ✅ Hybrid approach maintains multi-monitor native capabilities

**Key Technical Decisions**:
- Control panel: HTML/CSS/JS inside wx.html2.WebView for modern UI
- Projection window: Native wxPython borderless fullscreen for OS-level control
- Communication: JSON-based message passing via wx.html2 handlers
- No web frameworks: Vanilla HTML/CSS/JS for simplicity and performance

---

### Phase 1: Web UI Design & Static HTML ⭐ **NEXT - UX VALIDATION POINT**
**Goal**: Create beautiful web-based control panel UI with HTML/CSS (no JavaScript yet)

**What You'll See**:
- Modern, clean web UI inspired by ncfnj.org/bible
- Complete control panel with all sections (URL, Slides, Bible)
- Professional styling with proper spacing, colors, typography
- Responsive layout (even though window is fixed 800×900px)
- All form elements styled but non-functional (pure HTML/CSS)

**Implementation Tasks**:
1. Create `src/ui/web/index.html` with semantic HTML structure
   - URL projection section
   - Google Slides section
   - Bible verses section (book dropdown, chapter/verse input, version checkboxes)
   - Chapter preview area (scrollable)
   - Status bar
2. Create `src/ui/web/styles.css` with modern CSS
   - Clean color palette (inspired by ncfnj.org/bible)
   - Typography system (font families, sizes, weights)
   - Spacing system (consistent padding/margins)
   - Form element styling (inputs, buttons, checkboxes)
   - Section cards with subtle shadows
3. Add static mock content for visual validation
4. Create simple wxPython window to display HTML (just WebView.LoadURL)

**Success Criteria**:
- ✅ HTML structure is semantic and accessible
- ✅ CSS provides clean, modern look matching inspiration
- ✅ All UI elements are visible and properly styled
- ✅ Layout is clean with good visual hierarchy
- ✅ Can open HTML file in browser OR in wxPython WebView
- ✅ **User can validate the visual design**

**Deliverables**:
- [ ] `src/ui/web/index.html` - Complete HTML structure
- [ ] `src/ui/web/styles.css` - Professional CSS styling
- [ ] Simple `src/main.py` to display in WebView
- [ ] Screenshot for documentation

---

### Phase 2: JavaScript Interactivity & Python Bridge ⭐ **FUNCTIONAL VALIDATION**
**Goal**: Add JavaScript functionality and establish communication with Python backend

**What Works**:
- Button clicks trigger JavaScript functions
- Form input validation in JavaScript
- JavaScript sends messages to Python backend
- Python receives messages and logs them
- Python sends data back to JavaScript
- JavaScript updates UI with Python data
- Mock data flows through the bridge

**Implementation Tasks**:
1. Create `src/ui/web/components/bridge.js` - JavaScript ↔ Python communication layer
   ```javascript
   // Send to Python
   window.bridge.sendToPython({ action: 'project_url', data: { url: '...' } })

   // Receive from Python
   window.bridge.onMessageFromPython((message) => { ... })
   ```

2. Create `src/ui/main_window.py` - wxPython window with wx.html2.WebView
   - Create wx.Frame (800×900px)
   - Embed wx.html2.WebView
   - Load `src/ui/web/index.html`

3. Create `src/ui/web_controller.py` - Message handler system
   ```python
   def on_message_received(self, message):
       data = json.loads(message)
       if data['action'] == 'project_url':
           self.handle_project_url(data['data'])
   ```

4. Add JavaScript controllers:
   - `url_controller.js`: Handle URL projection button clicks
   - `slides_controller.js`: Handle Slides projection button clicks
   - `bible_controller.js`: Handle Bible selection and projection

5. Implement `app.js`: Main JavaScript initialization
   - Set up event listeners on all buttons
   - Initialize controllers
   - Set up bridge communication

6. Test bidirectional communication with mock data:
   - JavaScript → Python: Send projection requests
   - Python → JavaScript: Send Bible chapter data for preview

**Success Criteria**:
- ✅ Buttons trigger JavaScript functions
- ✅ JavaScript messages reach Python handler
- ✅ Python can send data back to JavaScript
- ✅ UI updates when receiving Python data
- ✅ Console logs show successful message flow
- ✅ **Bridge communication is reliable and fast (<100ms)**

**Deliverables**:
- [ ] `bridge.js` - Communication layer working
- [ ] `main_window.py` - WebView integration complete
- [ ] `web_controller.py` - Message handlers implemented
- [ ] JavaScript controllers for each section
- [ ] Bidirectional communication demo working

---

### Phase 3: Native Projection Window & Display Management
**Goal**: Implement native borderless projection window with multi-monitor support

**What Works**:
- Clicking "Project" button opens native borderless window
- Window appears on secondary display (if available)
- Window is borderless fullscreen (no title bar, no borders)
- Can project simple content (text, web URLs)
- Display manager detects all connected monitors
- Status bar shows real display information

**Implementation Tasks**:
1. Implement `src/core/display_manager.py` using `screeninfo` library
   - Detect all connected displays
   - Identify primary vs secondary displays
   - Get display resolutions and positions
   - Provide API for window placement

2. Create `src/ui/projection_window.py` - Native borderless window
   - wx.Frame with wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP
   - Borderless styling (no title bar)
   - Fullscreen on target display
   - Contains wx.html2.WebView for content rendering

3. Connect web UI to projection window via bridge:
   ```javascript
   // JavaScript sends projection request
   bridge.sendToPython({ action: 'project_url', data: { url: 'https://google.com' } })
   ```
   ```python
   # Python opens projection window and loads URL
   def handle_project_url(self, data):
       self.projection_window.show()
       self.projection_window.load_url(data['url'])
   ```

4. Implement display selection logic:
   - If 2+ displays: Use secondary display, fullscreen
   - If 1 display: Use primary display, windowed mode (for development)

5. Add "Hide" button functionality:
   - Hide projection window (minimize or close)
   - Maintain state for quick re-show

**Success Criteria**:
- ✅ Projection window opens on secondary display
- ✅ Window is truly borderless (no title bar, no borders)
- ✅ Can project web URLs in fullscreen
- ✅ Display manager correctly detects monitors
- ✅ Status bar shows "2 monitors detected - Projecting to Display 2"
- ✅ **Multi-monitor projection works end-to-end**

**Deliverables**:
- [ ] `display_manager.py` - Monitor detection complete
- [ ] `projection_window.py` - Borderless fullscreen working
- [ ] Bridge integration for projection commands
- [ ] URL projection working (end-to-end test)

---

### Phase 4: Bible Engine & Content Rendering
**Goal**: Load real Bible text and render multi-version verses to projection window

**What Works**:
- Selecting book + chapter:verse loads real Bible text from files
- Chapter preview in web UI shows real verses
- Clicking verse in preview projects it to projection window
- Multi-version display works (verse 1 all versions, verse 2 all versions, etc.)
- Font size controls adjust projection text size
- "Load Previous/Remaining Verses" buttons work

**Implementation Tasks**:
1. Implement `src/data/bible_repository.py` - Bible file I/O
   - Load chapter files: `books/{version}/vol{book_id}/chap{chapter}.txt`
   - Handle encoding: UTF-8 (English), GB2312 (Chinese CUV)
   - Parse one verse per line
   - Cache loaded chapters for performance

2. Implement `src/core/bible_engine.py` - Bible text loader
   - Parse verse references (use existing parsers)
   - Load verses from multiple versions simultaneously
   - Format verses for row-based display
   - Handle verse ranges (e.g., 1-5)
   - Handle entire chapters (e.g., just "13")

3. Implement `src/core/content_renderer.py` - HTML rendering
   - Generate HTML for multi-version verse display
   - Row-based layout: all versions of verse 1, then verse 2, etc.
   - Apply font size settings (Chinese vs English)
   - Styling for readability (spacing, colors)

4. Implement `src/utils/parsers.py` - Verse reference parsing
   - Parse "John 3:16" → {book: "John", chapter: 3, verse: 16}
   - Parse "3:16" → {chapter: 3, verse: 16} (requires current book context)
   - Parse "1:1-5" → {chapter: 1, verse_start: 1, verse_end: 5}
   - Parse "13" → {chapter: 13, verse: null} (entire chapter)

5. Load `books.csv` and `hymns.csv` for metadata:
   - Book names, IDs, chapter counts
   - Hymn ID to Google Slides ID mapping

6. Connect web UI to Bible engine:
   ```javascript
   // Load chapter preview
   bridge.sendToPython({ action: 'load_chapter', data: { book: 'John', chapter: 3 } })

   // Project verse
   bridge.sendToPython({ action: 'project_bible', data: {
       book: 'John', chapter: 3, verse: 16, versions: ['cuv', 'kjv']
   }})
   ```

**Success Criteria**:
- ✅ Chapter preview loads real Bible text
- ✅ Verse projection displays correct multi-version text
- ✅ Row-based layout works correctly
- ✅ Font sizes apply properly (Chinese vs English)
- ✅ Can project verse ranges (e.g., 1-5)
- ✅ Can project entire chapters
- ✅ **Real Bible content end-to-end**

**Deliverables**:
- [ ] `bible_repository.py` - File loading complete
- [ ] `bible_engine.py` - Verse loading logic working
- [ ] `content_renderer.py` - HTML generation working
- [ ] `parsers.py` - Verse parsing complete
- [ ] Bible projection working end-to-end

---

### Phase 5: Google Slides & Hymn Projection
**Goal**: Implement Google Slides projection with hymn ID lookup

**What Works**:
- Entering Google Slides URL projects presentation in /present mode
- Entering hymn ID looks up and projects corresponding Slides
- Slides projection works in fullscreen on secondary display
- Show/Hide toggle works for projection window
- Slides keyboard navigation works (arrow keys)

**Implementation Tasks**:
1. Implement `src/data/slides_repository.py` - Hymn CSV loader
   - Load `hymns.csv` on startup
   - Case-insensitive hymn ID lookup
   - Return Google Slides ID

2. Implement Google Slides URL conversion:
   ```python
   def convert_to_presentation_url(slides_id):
       return f"https://docs.google.com/presentation/d/{slides_id}/present"
   ```

3. Add Slides projection logic to web controller:
   ```python
   def handle_project_slides(self, data):
       slides_id = data.get('slides_id')
       if self.is_hymn_id(slides_id):
           slides_id = self.hymns_repo.lookup(slides_id)
       url = self.convert_to_presentation_url(slides_id)
       self.projection_window.load_url(url)
   ```

4. Update web UI JavaScript controller:
   - Extract Slides ID from URL if full URL provided
   - Send hymn ID or Slides ID to Python
   - Show error if invalid

5. Implement Show/Hide toggle functionality

**Success Criteria**:
- ✅ Hymn ID "A01" projects correct Google Slides
- ✅ Full Google Slides URLs work
- ✅ Slides appear in /present mode (not /edit)
- ✅ Fullscreen projection works
- ✅ Show/Hide toggle functional
- ✅ **Slides projection complete**

**Deliverables**:
- [ ] `slides_repository.py` - Hymn lookup working
- [ ] Slides URL conversion working
- [ ] End-to-end Slides projection working

---

### Phase 6: History, Settings & Polish
**Goal**: Implement projection history, settings persistence, and final polish

**What Works**:
- Last 30 Bible projections tracked in current session
- History dropdown populated with real entries
- Clicking history re-projects with original settings
- Font sizes and version selections persist across sessions
- Preferred display preference saved
- All keyboard shortcuts work

**Implementation Tasks**:
1. Implement `history_manager.py` - in-memory history (session only)
2. Wire Bible projections to add history entries
3. Populate history dropdown with real data
4. Implement history click handler to re-project
5. Implement `config_manager.py` - JSON config persistence
6. Save/load Bible version selections
7. Save/load font size preferences
8. Save/load display preferences
9. Implement keyboard shortcuts (ESC, F11, arrows)
10. Add "Clear History" button
11. Final UI polish and bug fixes

**Success Criteria**:
- ✅ History tracks last 30 Bible projections
- ✅ Settings persist between application restarts
- ✅ Keyboard shortcuts functional
- ✅ Clear history works
- ✅ **Application feature-complete per specification**

**Deliverables**:
- [ ] History tracking functional
- [ ] Settings persistence working
- [ ] All keyboard shortcuts implemented
- [ ] Final bug fixes and polish

---

### Phase 7: Testing, Documentation & Optional Features
**Goal**: Comprehensive testing, documentation, and optional enhancements

**Implementation Tasks**:
1. Write unit tests:
   - `test_parsers.py` - Verse reference parsing
   - `test_bible_engine.py` - Bible text loading
   - `test_display_manager.py` - Monitor detection

2. Write integration tests:
   - `test_web_bridge.py` - JavaScript ↔ Python communication
   - `test_projection_flow.py` - End-to-end projection flows

3. Documentation:
   - Update `README.md` with user guide and screenshots
   - Add inline code documentation (docstrings)
   - Create troubleshooting guide

4. Optional features (if time permits):
   - Google Meet integration (manual browser open - automation removed due to unreliability)
   - Custom background images for Bible verses
   - Text animations (fade in/out)
   - Remote control via mobile browser

**Success Criteria**:
- ✅ Core functionality has test coverage
- ✅ README.md is complete and helpful
- ✅ Code is well-documented
- ✅ Application is stable and bug-free

**Deliverables**:
- [ ] Test suite with reasonable coverage
- [ ] Complete README.md with screenshots
- [ ] Optional features (if implemented)

---

## Implementation Summary

### Hybrid Architecture Benefits
1. **Modern Web UI**: HTML/CSS/JS provides superior styling and layout capabilities
2. **Native Projection**: Borderless fullscreen windows with true multi-monitor support
3. **Fast Development**: Web UI is easier and faster to iterate on than native wxPython
4. **Cross-Platform**: wx.html2.WebView works consistently across macOS/Windows/Linux
5. **Maintainability**: Clear separation between UI (web) and backend (Python)

### Phased Approach Benefits
1. **Phase 1**: Visual validation before any logic (just HTML/CSS)
2. **Phase 2**: Communication layer validation (bridge working)
3. **Phase 3**: Projection capability validation (borderless fullscreen)
4. **Phase 4**: Core feature complete (Bible projection end-to-end)
5. **Phases 5-6**: Additional features and polish
6. **Phase 7**: Testing and documentation

### Key Technical Decisions
- ✅ Hybrid architecture over pure native or pure web
- ✅ Vanilla JavaScript over frameworks (simplicity, performance)
- ✅ wx.html2.WebView over Electron (smaller footprint, better OS integration)
- ✅ Native projection window over web-based (true borderless fullscreen)

## Next Steps

**Immediate**: Begin Phase 1 - Create HTML/CSS control panel UI
2. **Run `/speckit.plan` Phase 1**: Generate `data-model.md` and `contracts/`
3. **Begin Phase 2**: Start building control panel UI with mock data
4. **Validate UX**: Review control panel before moving to Phase 3

---

**Plan Version**: 1.0.0
**Last Updated**: 2025-10-12
**Status**: Ready for Phase 0 Research