```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.1] - 2025-12-27

### Fixed
- Corrected indentation error in `run_script` method for scrollbar creation, resolving a syntax issue.
- Fixed `NameError` in `run_script` when attempting to reuse existing tabs by properly handling frame and text retrieval.
- Enabled tab reuse for repeated script executions, appending new logs to the existing tab instead of creating duplicates.
- Converted theme toggle button to an instance attribute (`self.dark_btn`) for consistent reference in the `toggle_dark_mode` method.

## [1.6.0] - 2025-12-27

### Added
- Implemented script cancellation mechanism:
  - Added a "Cancel Current Script" button to terminate the running script in the selected tab.
  - Tracked subprocesses in a new `processes` dict for safe termination.
  - Updated tab change handler to enable/disable the cancel button based on tab type and running status.
  - Enhanced application close handler to terminate all running scripts if user confirms.

## [1.5.0] - 2025-12-27

### Improved
- Adapted tooltips to dynamically change background and foreground colors based on the current dark/light theme for improved visibility and consistency.

## [1.4.0] - 2025-12-27

### Improved
- Enhanced the sudo password dialog with better usability and validation:
  - "OK" button is now the default button (visually highlighted and triggered by Enter/Numpad Enter regardless of focus).
  - Added support for Enter, Numpad Enter, and Escape keys for submission/cancellation.
  - Implemented validation to prevent submission of empty passwords, displaying a clear warning message while keeping the dialog open and focused on the entry field.
  - Minor layout improvements (consistent sizing, resizable disabled, better padding).

## [1.3.0] - 2025-12-27

### Fixed
- Resolved a critical bug in tab management where closing script tabs or clearing finished tabs could cause a `TclError` due to reliance on a hardcoded widget path (`.!notebook.!frame`) that becomes invalid after tab reordering or removal.
- Stored a direct reference to the Console tab frame during setup and updated `close_current_tab` and `close_finished_tabs` to select it reliably, ensuring robustness with drag-to-reorder functionality.

## [1.2.0] - 2025-12-27

### Changed
- Updated script paths in `scripts.json` to be relative to the application directory.
- Modified `runner.py` to resolve script paths using `os.path.join(os.path.dirname(__file__), path)` for improved portability and easier deployment across different environments.

## [1.1.0] - 2025-12-27

### Changed
- Refactored code for improved maintainability:
  - Modularized the script into smaller functions and a main `ScriptRunnerApp` class to encapsulate logic.
  - Separated script configurations into an external `scripts.json` file for easier editing and extensibility without modifying code.
  - Defined constants for magic numbers and strings at the top of the file.
  - Added type hints and docstrings for better readability and IDE support.
  - Improved error handling with more robust try-except blocks and logging.
  - Ensured code style compliance with PEP8, including consistent spacing and shorter lines.
  - Enabled dynamic loading of scripts from JSON at runtime.
  - Simplified theme handling and UI setup.

## [1.0.0] - 2025-12-27

### Added
- Initial release of the Bash Script Runner GUI application.
- Modern dark/light theming using sv-ttk (Sun Valley ttk theme).
- Predefined bash scripts with tagging, filtering, and search functionality.
- Concurrent script execution with configurable limits.
- Tabbed interface for console logs, scratchpad, and individual script outputs.
- Secure sudo password dialog for elevated privilege scripts.
- Tooltips for script descriptions and controls.
- Tab management features: save, close, reorder, and auto-clear finished tabs.
- Dynamic button grid with responsive layout.
```