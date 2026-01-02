# Component: Bash Scripts Library

## Purpose
This directory serves as the repository for the executable scripts managed by the Script Runner application. It contains a variety of Bash scripts designed to perform system maintenance, application updates, launching of tools, and other utility tasks.

## Key Files
(Examples of scripts found in this directory)
*   **`update_system`**: Performs a full system package update and upgrade (likely requires sudo).
*   **`ollama_update` / `ollama_model_update`**: Scripts for managing the Ollama AI tool and its models.
*   **`docker_image_prune` / `update_docker_images`**: Utilities for maintaining Docker containers and images.
*   **`system_monitor`**: Launches the system monitor GUI.

## Dependencies
*   **System Tools**: Relies heavily on installed system CLI tools such as `apt`, `docker`, `gnome-system-monitor`, `chromium`, etc.
*   **Environment**: Scripts expect a standard Bash environment (`#!/bin/sh` or `#!/bin/bash`).

## Interactions
*   **Invoked By**: These scripts are directly executed by the `runner.py` application located in the parent directory.
*   **Output**: All output (text printed to stdout/stderr) is captured by the runner and displayed in the application's GUI log tabs.

## Important Notes
*   **Permissions**: Scripts intended to run with elevated privileges must be flagged with `"needs_sudo": true` in the parent directory's `scripts.json` file. The scripts themselves generally do not contain `sudo` calls internally; the runner handles the elevation.
*   **Non-Blocking**: Scripts should ideally run linearly. Interactive prompts (other than the initial sudo password handled by the runner) might not be supported or visible in the runner's log window.
