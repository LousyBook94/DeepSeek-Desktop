# Implementation Plan

[Overview]
Fix Unicode encoding errors that occur when the auto-updater runs in the built executable, preventing crashes from Unicode characters in GitHub API responses.

The issue occurs because the updater subprocess doesn't properly inherit UTF-8 encoding environment when launched from the built executable, causing Unicode characters from GitHub API responses to crash with the charmap codec error. The main app works correctly but the updater subprocess fails when processing Unicode characters in release information.

[Types]
No new types are required for this implementation.

[Files]
- main.py: Modified launch_auto_updater() function to ensure proper UTF-8 environment inheritance
- utils/auto_update.py: Enhanced API response processing and console initialization for Unicode safety
- utils/build-updater.py: Updated build configuration to include UTF-8 encoding support

[Functions]
- launch_auto_updater() in main.py: Add explicit UTF-8 environment variables to subprocess
- fetch_latest_version_with_retry() in auto_update.py: Add immediate Unicode sanitization for API responses
- sanitize_release_notes() in auto_update.py: Enhanced to handle all Unicode fields
- setup_logging() in auto_update.py: Strengthen UTF-8 logging configuration

[Classes]
- SafeConsole in auto_update.py: Enhanced Unicode safety for all console operations
- UpdateChecker in auto_update.py: Improved Unicode handling in release info processing

[Dependencies]
No new dependencies required. Existing packages (rich, requests) support Unicode properly.

[Testing]
Test the updater in both development mode and built executable to ensure:
- No charmap codec errors
- Unicode characters are properly sanitized
- Console displays correctly
- Update process completes successfully

[Implementation Order]
1. Modify launch_auto_updater() in main.py to fix subprocess encoding
2. Enhance Unicode sanitization in auto_update.py API processing
3. Strengthen console initialization and logging in auto_update.py
4. Update build configuration if needed
5. Test the complete fix in built executable
