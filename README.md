# FL Studio Project Browser

A local web app that displays all your FL Studio projects on a draggable whiteboard. Tag projects by colour, write notes, rate them, and open them directly in FL Studio — all from your browser.

---

## Requirements

- **Python 3.8 or later** — [download here](https://www.python.org/downloads/)
- **FL Studio** installed with projects saved in the default location:
  - macOS: `~/Documents/Image-Line/FL Studio/Projects`
  - Windows: `Documents\Image-Line\FL Studio\Projects`

---

## Setup & Running

### macOS

1. Open Terminal
2. Navigate to the project folder:
   ```bash
   cd path/to/fl-studio-project-browser
   ```
3. Make the run script executable (first time only):
   ```bash
   chmod +x run.sh
   ```
4. Run the app:
   ```bash
   ./run.sh
   ```

The first time you run it, the script automatically creates a virtual environment and installs dependencies. After that it starts up instantly.

Your browser will open automatically at `http://localhost:8765`.

---

### Windows

1. Open File Explorer and navigate to the project folder
2. Double-click **`run.bat`**

   Or from Command Prompt:
   ```cmd
   cd path\to\fl-studio-project-browser
   run.bat
   ```

The first time you run it, the script automatically creates a virtual environment and installs dependencies. After that it starts up instantly.

Your browser will open automatically at `http://localhost:8765`.

> **Note:** If Python isn't recognised, make sure you checked "Add Python to PATH" during installation. Re-run the Python installer and enable that option if needed.

---

## Features

| Feature | How to use |
|---|---|
| **View projects** | All FL Studio project folders appear as cards on the board |
| **Open in FL Studio** | Click a card → click **Open in FL Studio** |
| **Drag cards** | Click and drag any card to reposition it on the board |
| **Colour tag** | Click a card → pick a colour dot |
| **Star rating** | Click a card → click the stars (0–5) |
| **Notes** | Click a card → type in the Notes box (auto-saves) |
| **Sticky notes** | Click **＋ Sticky Note** in the header to place a free note on the board |
| **Hide a project** | Click a card → **Hide from project browser** at the bottom |
| **Show hidden** | Click **Show Hidden** in the header to reveal hidden projects |
| **Search** | Type in the search box to filter cards by name |
| **Reset layout** | Click **Reset Layout** to snap all cards back to a grid |
| **Light/dark mode** | Click the 🌙/☀️ button in the top-right corner |

---

## Data & Privacy

Your ratings, notes, colours, and card positions are saved locally in `data.json` in the project folder. This file is excluded from git (via `.gitignore`) so your personal data is never committed or shared.

---

## Stopping the app

Go back to the terminal / command prompt and press `Ctrl + C`.
