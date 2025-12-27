```markdown
# Bash Script Runner GUI

A modern, themed GUI application built with Python and Tkinter for running predefined bash scripts. It features a clean interface with light/dark mode support using the Sun Valley ttk theme (sv-ttk). Ideal for managing routine tasks like system updates, Docker management, AI model updates, and more.

## Features

- **Modern Theming**: Supports dark and light modes with sv-ttk for a sleek, Windows 11-inspired look.

- **Script Management**: Predefined list of bash scripts with tags for easy filtering and searching.

- **Concurrent Execution**: Run multiple scripts simultaneously with a configurable limit (default: 5).

- **Tabbed Logging**: Dedicated tabs for console output, scratchpad, and individual script logs.

- **Sudo Support**: Secure password prompt for scripts requiring elevated privileges.

- **Tooltips and Filtering**: Hover tooltips for script descriptions; search by name or tag.

- **Tab Management**: Save, close, and reorder tabs; auto-close finished script tabs.

- **Scratchpad Mode**: Built-in text editor for notes or quick edits.

## Screenshot

![Screenshot of main window](screenshot.png?raw=true "Main Window")

## Requirements
- Python 3.6+ (tested on 3.12)

- Tkinter (usually included with Python)

- sv-ttk: `pip install sv-ttk`

- tkfilebrowser: `pip install tkfilebrowser`

- Linux environment (due to bash scripts and sudo usage)

- Optional: Dependencies for specific scripts (e.g., Docker, Ollama)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/bash-script-runner-gui.git
   cd bash-script-runner-gui
   ```

2. Install dependencies:

   ```
   pip install sv-ttk tkfilebrowser
   ```

3. Ensure the bash scripts referenced in `scripts.json` exist in the specified paths (e.g., relative to the app directory like `bash/my_script.sh`). Customize paths as needed.

4. Run the application:

   ```
   python runner.py
   ```

## Usage

- Launch the app: `python runner.py`

- **Search and Filter**: Use the search bar for script names or the tag dropdown for categories (e.g., "docker", "ai").

- **Run a Script**: Click a button to execute. Scripts with sudo requirements will prompt for a password.

- **Monitor Output**: Output appears in dedicated tabs. Use the console for general logs.

- **Scratchpad**: Edit plain text in the "Scratchpad" tab.

- **Controls**:

  - Save current tab content to a file.

  - Close individual or finished tabs.

  - Toggle dark/light mode.

  - Set max concurrent scripts (1-20).

- **Clear Log**: Quickly clear the current tab's content.

## Configuration

Customize the scripts in `scripts.json` to add/remove entries. The file should be a JSON array of objects with the following structure:

```json
[
    {
        "label": "Button Label",
        "path": "/path/to/script.sh",
        "needs_sudo": true,
        "tags": ["tag1", "tag2"],
        "description": "Tooltip description"
    },
    // Add more here...
]
```

- `needs_sudo`: Set to `true` for scripts requiring elevated privileges.

- `tags`: Used for filtering (e.g., ["system", "update"]).

- Adjust `BUTTONS_PER_ROW`, `GRID_PAD`, and `LOG_LINES` for layout preferences in `runner.py`.

## Contributing

Contributions are welcome! Fork the repo, make changes, and submit a pull request. Ensure code follows PEP8 and test on Linux.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Tkinter](https://docs.python.org/3/library/tkinter.html) and [sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme).

- Inspired by simple script automation needs for developers and sysadmins.
```