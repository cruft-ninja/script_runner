<DOCUMENT filename="changelog.md">
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
</DOCUMENT>