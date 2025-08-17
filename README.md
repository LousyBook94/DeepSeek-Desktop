# DeepSeek Desktop 🚀
- This project is still in development with more features coming soon
- Please report any bugs or suggestions in [issues](https://github.com/LousyBook94/DeepSeek-Desktop/issues)

![DeepSeek Desktop Preview](assets/preview.png)

## Installation
1. Visit the [Releases page](https://github.com/LousyBook94/DeepSeek-Desktop/releases)
2. Download the `DeepSeekChat-windows.zip` file
3. Extract the zip file
4. Run `DeepSeekChat.exe`
5. Run `auto-update.bat` to update the app

## Features ✨
This desktop application enhances your DeepSeek chat experience with:

- 🎨 **Custom UI Elements**:
  - Custom footer text
  - Forced "Inter" font throughout the interface
- ⏰ **Dynamic Greetings**:
  - Time-based messages (Good Morning/Afternoon/Evening)
  - Smooth fade transitions between messages
- ✨ **Animations**:
  - Typing animation with sphere cursor
  - Self-healing UI components via MutationObservers
- 🧹 **Clean Interface**:
  - Removed unnecessary UI elements
  - Persistent styling across navigation
- 🌙 **Dark Titlebar Support**:
  - Automatically matches Windows system theme
  - Manual override options available
- 🔃 **Auto Updater**
- 📝 **Enhanced Markdown Rendering**
  - Full markdown content rendering in user messages
  - System theme detection for code blocks (light/dark mode)
  - JetBrains Mono font for improved code readability
  - Security sanitization with DOMPurify to prevent XSS attacks
  - Fixed spacing issues after headings and other elements
  - Proper handling for code blocks and inline code elements

## Advanced Usage 🔧
For advanced users, you can customize the application behavior:

```bash
# Force dark titlebar regardless of system theme
DeepSeekChat.exe --dark-titlebar

# Force light titlebar regardless of system theme
DeepSeekChat.exe --light-titlebar

# Run in release mode (disable debug tools)
DeepSeekChat.exe --release
```

The titlebar will automatically match your Windows system theme by default. If you have Windows set to dark mode, the titlebar will be dark. If you have Windows set to light mode, the titlebar will be light.

## Future Plans 🔮
- [x] ~~Dark titlebar support~~ ✅ **Completed!**
- [ ] Custom theme support for the entire interface
- [ ] Keyboard shortcuts
- [ ] Cross-platform builds (Mac/Linux)
- [ ] System tray integration

## Connect with Me 👋
- [YouTube](https://youtube.com/@LousyBook01)
- [GitHub](https://github.com/LousyBook94)

## Cool Guys
- [vanja-san](https://github.com/vanja-san)

## Attribution
- Icons by [Icons8](https://icons8.com)
- Powered by [DeepSeek](https://deepseek.com)
