# Agent Instructions for DeepSeek Desktop

This document provides instructions for AI agents working on the DeepSeek Desktop repository.

## Project Overview

DeepSeek Desktop is a Python-based desktop application that acts as a wrapper around the official DeepSeek chat website (`https://chat.deepseek.com`). It uses the `pywebview` library to create a webview container and injects custom JavaScript and CSS to enhance the user experience.

The primary goal of this project is to provide a more feature-rich, customizable, and integrated desktop experience for DeepSeek users.

## Codebase Structure

The repository is structured as follows:

- **`main.py`**: The main entry point of the application. It is responsible for:
  - Parsing command-line arguments.
  - Creating and managing the `pywebview` window.
  - Exposing a Python API to the JavaScript frontend for desktop-specific actions (e.g., toggling "always on top", opening new windows).
  - Injecting the custom JavaScript from `injection/inject.js`.
  - Handling the launch of the auto-updater on Windows.

- **`src/`**: This directory contains auxiliary Python source code.
  - **`src/windows_helpers.py`**: Contains all Windows-specific logic, primarily for enabling and managing the dark mode title bar by interacting with the Windows API (`ctypes`, `winreg`). This keeps the main script clean from OS-specific code.

- **`injection/`**: This directory contains files that are injected into the webview.
  - **`injection/inject.js`**: This is the core of the client-side enhancements. It is responsible for:
    - Injecting the "Inter" font.
    - Replacing the footer with custom attribution.
    - Creating dynamic, time-based greetings with a typing animation.
    - Removing unnecessary UI elements from the original site.
    - Listening for hotkeys (`Ctrl+Shift+T`, `Ctrl+O`) and calling the Python API.

- **`tests/`**: Contains the test suite for the application.
  - **`tests/test_main.py`**: Uses `pytest` to test the application's logic. It heavily relies on mocking (`unittest.mock`) and fixtures to isolate tests and handle platform-specific code.

- **`.github/workflows/`**: Contains GitHub Actions workflows.
  - **`release.yml`**: This workflow automates the process of building and releasing the application for Windows. It uses `pyinstaller` to create a distributable `.exe` file.

- **`build.py`**: A helper script for the `pyinstaller` build process, often used by the release workflow.

- **`requirements.txt`**: Lists the Python dependencies required for the application to run.

- **`requirements-dev.txt`**: Lists the dependencies required for development and testing (e.g., `pytest`).

## How It Works

1.  The user runs the application (`main.py` or the compiled `.exe`).
2.  `main.py` creates a `pywebview` window, loading the DeepSeek chat URL.
3.  An `Api` class instance is exposed to the JavaScript environment, allowing the frontend to call Python functions.
4.  Once the web page loads, `injection/inject.js` is executed within the webview's context.
5.  The JavaScript code manipulates the DOM to apply UI enhancements and sets up event listeners for hotkeys.
6.  On Windows, `main.py` calls functions from `windows_helpers.py` to adjust the title bar theme based on system settings or command-line flags.

## Build and Release Process

The release process is automated via the `release.yml` GitHub Action.

1.  **Code Changes:** Make any necessary changes to the source code (`.py`, `.js` files).
2.  **Version Bump:** Before creating a release, the version number in `.github/workflows/release.yml` should be updated.
3.  **Trigger Workflow:** The workflow is typically triggered by pushing a tag to the repository (e.g., `v0.1.62`).
4.  **Build:** The workflow runs on a Windows runner, installs dependencies, and uses `pyinstaller` (via `build.py`) to package the application into a single executable.
5.  **Create Release:** The workflow then creates a new GitHub Release, attaches the compiled application as a zipped asset, and uses the tag's notes as the release description.

To contribute, a developer would typically make their changes, ensure tests pass, and then create a pull request. The repository owner will then handle the version bump and tagging for a new release.
