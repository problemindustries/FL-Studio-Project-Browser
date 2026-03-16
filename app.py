import glob
import json
import os
import platform
import subprocess
import sys
import threading
import time

from flask import Flask, jsonify, render_template, request

# Resource directory — works both in dev and when frozen by PyInstaller
if getattr(sys, "frozen", False):
    RESOURCES_DIR = sys._MEIPASS
else:
    RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))

# User data directory — persists across app updates
_system = platform.system()
if _system == "Darwin":
    _data_base = os.path.expanduser("~/Library/Application Support")
elif _system == "Windows":
    _data_base = os.environ.get("APPDATA", os.path.expanduser("~"))
else:
    _data_base = os.path.expanduser("~/.config")

DATA_DIR = os.path.join(_data_base, "DAW Project Browser")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(RESOURCES_DIR, "templates"),
    static_folder=os.path.join(RESOURCES_DIR, "static"),
)

DATA_FILE = os.path.join(DATA_DIR, "data.json")

_sys = platform.system()
DAW_CONFIGS = {
    "fl_studio": {
        "label": "FL Studio",
        "ext": "*.flp",
        "skip": {"Backup", "Templates"},
        "default_dir": os.path.expanduser("~/Documents/Image-Line/FL Studio/Projects"),
    },
    "ableton": {
        "label": "Ableton Live",
        "ext": "*.als",
        "skip": {"Backup", "Templates", "Samples"},
        "default_dir": os.path.expanduser(
            "~/Music/Ableton/Projects" if _sys == "Darwin"
            else "~/Documents/Ableton/Projects"
        ),
    },
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_daw():
    return load_data().get("_daw", "fl_studio")


def get_project_files(folder, daw):
    """Return project files (.flp or .als) in the folder, newest first."""
    ext = DAW_CONFIGS.get(daw, DAW_CONFIGS["fl_studio"])["ext"]
    files = glob.glob(os.path.join(folder, ext))
    files.sort(key=os.path.getmtime, reverse=True)
    return files


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def api_get_config():
    data = load_data()
    daw = data.get("_daw", None)
    projects_dir = data.get("_projects_dir", None)
    return jsonify({
        "daw": daw,
        "projects_dir": projects_dir,
        "is_configured": daw is not None and projects_dir is not None,
        "default_dirs": {k: v["default_dir"] for k, v in DAW_CONFIGS.items()},
    })


@app.route("/api/config", methods=["POST"])
def api_set_config():
    daw = request.json.get("daw", "").strip()
    projects_dir = request.json.get("projects_dir", "").strip()
    if daw not in DAW_CONFIGS:
        return jsonify({"error": "Invalid DAW selection"}), 400
    if not projects_dir or not os.path.isdir(projects_dir):
        return jsonify({"error": "Invalid or missing folder path"}), 400
    data = load_data()
    data["_daw"] = daw
    data["_projects_dir"] = projects_dir
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/browse", methods=["POST"])
def api_browse():
    """Open a native folder picker and return the selected path."""
    system = platform.system()
    try:
        if system == "Darwin":
            result = subprocess.run(
                ["osascript", "-e",
                 'POSIX path of (choose folder with prompt "Select your FL Studio Projects folder")'],
                capture_output=True, text=True, timeout=60,
            )
            path = result.stdout.strip().rstrip("/")
        elif system == "Windows":
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$d = New-Object System.Windows.Forms.FolderBrowserDialog;"
                "$d.Description = 'Select your FL Studio Projects folder';"
                "if ($d.ShowDialog() -eq 'OK') { Write-Output $d.SelectedPath }"
            )
            result = subprocess.run(
                ["powershell", "-Command", ps],
                capture_output=True, text=True, timeout=60,
            )
            path = result.stdout.strip()
        else:
            return jsonify({"error": "Unsupported platform for native picker"}), 400

        if path and os.path.isdir(path):
            return jsonify({"path": path})
        return jsonify({"error": "No folder selected"}), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Picker timed out"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects")
def api_projects():
    store = load_data()
    projects_dir = store.get("_projects_dir")
    daw = store.get("_daw", "fl_studio")
    if not projects_dir or not os.path.exists(projects_dir):
        return jsonify([])

    skip = DAW_CONFIGS.get(daw, DAW_CONFIGS["fl_studio"])["skip"]
    projects = []
    for name in sorted(os.listdir(projects_dir)):
        if name in skip or name.startswith("."):
            continue
        folder = os.path.join(projects_dir, name)
        if not os.path.isdir(folder):
            continue

        files = get_project_files(folder, daw)
        main_file = files[0] if files else None
        mtime = os.path.getmtime(main_file) if main_file else None

        projects.append({
            "name": name,
            "main_flp": main_file,
            "flps": files,
            "mtime": mtime,
        })

    return jsonify(projects)


@app.route("/api/metadata", methods=["GET"])
def api_get_metadata():
    return jsonify(load_data())


@app.route("/api/metadata", methods=["POST"])
def api_set_metadata():
    save_data(request.json)
    return jsonify({"ok": True})


@app.route("/api/load-data", methods=["POST"])
def api_load_data():
    """Open a native file picker, read the selected JSON, save it as current metadata."""
    system = platform.system()
    try:
        if system == "Darwin":
            result = subprocess.run(
                ["osascript", "-e",
                 'POSIX path of (choose file with prompt "Select your data.json backup")'],
                capture_output=True, text=True, timeout=60,
            )
            path = result.stdout.strip()
        elif system == "Windows":
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$d = New-Object System.Windows.Forms.OpenFileDialog;"
                "$d.Filter = 'JSON files (*.json)|*.json|All files (*.*)|*.*';"
                "$d.Title = 'Select your data.json backup';"
                "if ($d.ShowDialog() -eq 'OK') { Write-Output $d.FileName }"
            )
            result = subprocess.run(
                ["powershell", "-Command", ps],
                capture_output=True, text=True, timeout=60,
            )
            path = result.stdout.strip()
        else:
            return jsonify({"error": "Unsupported platform for native picker"}), 400

        if not path or not os.path.isfile(path):
            return jsonify({"error": "No file selected"}), 400

        with open(path) as f:
            data = json.load(f)

        save_data(data)
        return jsonify({"ok": True, "data": data})

    except json.JSONDecodeError:
        return jsonify({"error": "Selected file is not valid JSON"}), 400
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Picker timed out"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/open", methods=["POST"])
def api_open():
    path = request.json.get("path")
    if not path or not os.path.isfile(path):
        return jsonify({"error": "File not found"}), 404
    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", path])
    elif system == "Windows":
        os.startfile(path)
    else:
        subprocess.Popen(["xdg-open", path])
    return jsonify({"ok": True})


if __name__ == "__main__":
    import webview

    # Flask runs in a background thread; pywebview owns the main thread
    flask_thread = threading.Thread(
        target=lambda: app.run(debug=False, port=8765, use_reloader=False),
        daemon=True,
    )
    flask_thread.start()
    time.sleep(0.6)  # Give Flask a moment to start

    window = webview.create_window(
        "DAW Project Browser",
        "http://localhost:8765",
        width=1400,
        height=900,
        min_size=(900, 600),
    )
    webview.start()
