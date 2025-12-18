# 🤖 AGENTS.md: AI Architectural Guide

This document serves as a high-level map for AI agents (and human collaborators) working on the DeepSeek Desktop project. It outlines the core architecture, design patterns, and critical areas of the codebase.

> [!IMPORTANT]
> **Keep this file updated.** If you make significant architectural changes (e.g., refactoring the communication layer, adding major new components, or changing the build pipeline), ensure this document is updated to reflect the new state.

## �️ Core Architecture

The project follows a hybrid architecture where a Python backend ([main.py](main.py)) wraps a Chromium-based webview ([pywebview](https://pywebview.flowrl.com/)) and injects custom behavior via JavaScript ([injection/inject.js](injection/inject.js)).

### 1. Python Backend (`main.py`)
- **DeepSeekApp**: The central lifecycle manager. It handles window creation, internal server startup, and API registration.
- **Local Server**: A lightweight threaded `socketserver` that serves static files and provides environment info (like the active port) to the frontend.
- **API Class**: Exposed to the frontend via `pywebview.api`. This is the bridge for native functions like screenshots and update initiation.

### 2. Frontend Injection (`injection/inject.js`)
- **Modular Managers**: Logic is split into managers:
  - `UIManager`: Handles custom buttons, notifications, and banners.
  - `VersionManager`: Syncs with the backend to check and display versions.
  - `MarkdownManager`: Custom parsing for streaming messages and code blocks.
- **MutationObserver**: Robustly watches the DOM to apply styles and logic as content streams in from the DeepSeek web app.

### 3. Update System (`utils/auto_update.py`)
- **UpdateChecker**: A decoupled class used by the backend to fetch GitHub releases and compare versions.
- **Standalone Updater**: A console-based executable that runs independently once the main app closes, allowing it to overwrite application files.

## 🛠️ Critical Workflows

### Manual Update Check
Press **Ctrl + Shift + U** in the app. In development mode (unfrozen), this forces the update banner to appear for UI testing.

### Native Screenshot
Press **Ctrl + Shift + S** in development mode to capture the client area and save it to `assets/`.

## 📦 Build Pipeline
- `build.py`: Uses PyInstaller to bundle the app.
- `.github/workflows/ci.yml`: Automated testing on every push.
- `.github/workflows/release.yml`: Automated CI/CD for creating GitHub releases.

---

*Initial guide established by Antigravity (Advanced Agentic AI).*
