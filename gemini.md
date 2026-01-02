# Component: Script Runner Core

## Purpose
This directory contains the main source code, configuration, and documentation for the "Bash Script Runner" application. It serves as the entry point for the GUI, managing the loading, display, and execution of automation scripts defined in the configuration.

## Key Files
*   **`runner.py`**: The primary executable file. It initializes the `tk` (Tkinter) GUI, applies the `sv_ttk` theme, builds the interface dynamically based on `scripts.json`, and handles script execution via the `subprocess` module.
*   **`scripts.json`**: The central configuration file. It contains a JSON array of objects, where each object defines a script's label, file path, sudo requirements, tags, and description.
*   **`README.md`**: General documentation for the project.

## Dependencies
*   **Internal**: `bash/` directory (contains the scripts to be executed).
*   **External**:
    *   **Python 3**: The runtime environment.
    *   **`tkinter`**: Standard Python GUI library.
    *   **`sv_ttk`**: A modern Sun Valley theme for Tkinter (must be installed via pip).
    *   **`tkfilebrowser`**: Used for the "Save Current Tab" file dialog.

## Interactions
*   **Configuration Loading**: On startup, `runner.py` reads `scripts.json` to populate the grid of buttons.
*   **Script Execution**: When a button is clicked, `runner.py` spawns a subprocess to execute the corresponding script found in the `bash/` folder.
*   **IO Streaming**: Standard output (stdout) and error (stderr) from the scripts are captured in real-time and displayed in the application's log window (threaded).

## Important Notes
*   **Threading**: Script execution is handled in separate threads to prevent the GUI from freezing during long-running tasks.
*   **Sudo Handling**: The application has built-in logic to detect if a script requires `sudo` (defined in `scripts.json`). It prompts the user for a password via a custom GUI dialog and passes it securely to the subprocess.
*   **"Clear Log"**: This is a special internal command defined in `scripts.json` that clears the text widget rather than running an external file.
