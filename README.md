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
- 핫 **Hotkeys**:
  - `Ctrl+Shift+T`: Toggle "Always on Top" mode.
  - `Ctrl+O`: Open a new chat window.

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
- [x] ~~Keyboard shortcuts~~ ✅ **Completed!**
- [ ] Custom theme support for the entire interface
- [ ] Cross-platform builds (Mac/Linux)
- [ ] System tray integration

## Customization & Contributing 🎨
This application is designed to be customizable. Power users can modify the `injection/inject.js` file to add their own CSS or JavaScript enhancements. If you create a cool or useful feature, feel free to open a pull request and contribute back to the project!

## Connect with Me 👋
- [YouTube](https://youtube.com/@LousyBook01)
- [GitHub](https://github.com/LousyBook94)

## Cool Guys
- [vanja-san](https://github.com/vanja-san)

## Attribution
- Icons by [Icons8](https://icons8.com)
- Powered by [DeepSeek](https://deepseek.com)
