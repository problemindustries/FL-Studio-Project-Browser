# DAW Project Browser

![screenshot](screenshot.png)

A local app that displays all your DAW projects on a draggable whiteboard. Tag projects by colour, write notes, rate them, and open them directly in your DAW — all from a standalone desktop window.

Supports **FL Studio** (`.flp`) and **Ableton Live** (`.als`).

GitHub: [github.com/problemindustries/DAW-Project-Browser](https://github.com/problemindustries/DAW-Project-Browser)

---

## Requirements

- **Python 3.8 or later** — [download here](https://www.python.org/downloads/)
- **FL Studio** or **Ableton Live** installed, with projects saved somewhere on your machine

---

## Running from source

### macOS

1. Open Terminal and navigate to the project folder:
   ```bash
   cd path/to/DAW-Project-Browser
   ```
2. Make the run script executable (first time only):
   ```bash
   chmod +x run.sh
   ```
3. Run the app:
   ```bash
   ./run.sh
   ```

The first time you run it, the script automatically creates a Python virtual environment and installs dependencies. After that it starts up instantly.

---

### Windows

1. Open File Explorer and navigate to the project folder
2. Double-click **`run.bat`**

   Or from Command Prompt:
   ```cmd
   cd path\to\DAW-Project-Browser
   run.bat
   ```

> **Note:** If Python isn't recognised, make sure you checked "Add Python to PATH" during installation.

---

## Building a standalone executable

To build a native `.app` (macOS) or `.exe` (Windows):

```bash
# macOS
./build.sh

# Windows
build.bat
```

Output is placed in the `dist/` folder. The app bundles everything — no Python or browser installation needed to run it.

---

## First-time setup

When you open the app for the first time, a setup screen will appear:

1. **Select your DAW** — FL Studio or Ableton Live
2. **Choose your projects folder** — click **Browse…** to open a native folder picker, or paste the path directly
3. Click **Open Browser**

Your DAW and folder are remembered on every subsequent launch. To change either, click **⚙ Settings** in the header at any time.

---

## Features

| Feature | How to use |
|---|---|
| **View all projects** | All project folders appear as cards on the board — arrange them however you like |
| **Open in your DAW** | Click a project card → click **Open in FL Studio** / **Open in Ableton Live** |
| **Colour tag** | Click a card → pick a colour (organise by genre, status, anything) |
| **Star rating** | Rate each project 0–5 stars |
| **Notes** | Write a note for each project (auto-saves) |
| **Sticky notes** | Free-floating notes on the canvas for extra organisation |
| **Hide a project** | Click a card → **Hide from project browser** |
| **Show hidden** | Click **Show Hidden** in the header to reveal hidden projects |
| **Search** | Type in the search box to filter cards by name |
| **Reset layout** | Click **Reset Layout** to snap all cards back to a grid |
| **Settings** | Click **⚙ Settings** to change DAW or projects folder |
| **Load data backup** | Click **📂 Load Data** to restore a saved `data.json` |
| **Light/dark mode** | Click the 🌙/☀️ button in the top-right corner |

---

## Data & Privacy

All project metadata — ratings, notes, colours, card positions — is saved locally in `data.json` in your user data folder (`~/Library/Application Support/DAW Project Browser/` on macOS). Nothing ever leaves your machine.

---

## Acknowledgement

Built by [Problem Industries](https://problem-industries.com). Open source under the [GNU General Public License v3](LICENSE).
