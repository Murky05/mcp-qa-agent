# Troubleshooting: every error from the setup, and the fix

| Symptom | Cause | Fix |
|---|---|---|
| `pip : The term 'pip' is not recognized` | Python's `Scripts` folder isn't on PATH | Use `py -m pip ...` or the full path to `python.exe` |
| `Could not find platform independent libraries` / `No module named pip` (Python 3.15) | Broken/too-new Python install, plus the Python Install Manager taking over `py` | Uninstall Python 3.15 **and** the Python Install Manager, install **Python 3.13** with "Add to PATH" |
| `python` opens the Microsoft Store | Windows App Execution Alias | Settings → Apps → Advanced app settings → App execution aliases → turn off `python.exe` / `python3.exe` |
| `Stop-Service MySQL80 ... Cannot open MySQL80 service` | PowerShell not elevated | Open PowerShell with **Run as administrator** (title bar says *Administrator*) |
| `Access to the path 'C:\mysql-init.txt' is denied` | Same: not admin | Same fix |
| Forgot MySQL root password | — | [`scripts/reset-mysql-root-password.ps1`](../scripts/reset-mysql-root-password.ps1) |
| Config script ran but no "Updated" line | Config wasn't at `%APPDATA%\Claude` | It was at `%LOCALAPPDATA%\Claude-Data\<profile>\claude_desktop_config.json`. Open it via **Settings → Developer → Edit Config** |
| MCP server doesn't appear after editing config | Claude still running in the tray | Right-click the tray icon → **Quit**, then reopen |
| Whole config fails to load | Curly quotes `“ ”` pasted from a doc/slide | Replace them with straight quotes `" "` |
| `uv` not found by Claude | `uv` isn't on PATH | Use the full path: `...\Python313\Scripts\uv.exe` (backslashes doubled in JSON) |
| `filesystem` server fails | The folder in its args doesn't exist | Create `C:\Users\<you>\files_claude` first |
| First restart slow / a server shows "failed" | `npx` is downloading packages | Restart Claude once more |
| Registration says email already exists | Record was registered in an earlier run | Use a new email suffix, or skip the record |
