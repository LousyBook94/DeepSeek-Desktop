// --- Hotkey Functionality ---
document.addEventListener('keydown', async (e) => {
    // Ctrl+Shift+T: Toggle Always on Top
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        try {
            await window.pywebview.api.toggle_always_on_top();
        } catch (err) {
            console.error("Failed to toggle always on top:", err);
        }
    }

    // Ctrl+O: Open New Window
    if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        try {
            await window.pywebview.api.open_new_window();
        } catch (err) {
            console.error("Failed to open new window:", err);
        }
    }
});
