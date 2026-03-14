import glob
import json
import os
import platform
import subprocess
import threading
import time
import webbrowser

from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

DEFAULT_PROJECTS_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Projects")
DATA_FILE = os.path.join(BASE_DIR, "data.json")
SKIP_NAMES = {"Backup", "Templates"}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_projects_dir():
    return load_data().get("_projects_dir", None)


def get_flps(folder):
    """Return .flp files in the project root (not Backup), newest first."""
    flps = glob.glob(os.path.join(folder, "*.flp"))
    flps.sort(key=os.path.getmtime, reverse=True)
    return flps


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def api_get_config():
    projects_dir = get_projects_dir()
    return jsonify({
        "projects_dir": projects_dir,
        "is_configured": projects_dir is not None,
        "default_dir": DEFAULT_PROJECTS_DIR,
    })


@app.route("/api/config", methods=["POST"])
def api_set_config():
    projects_dir = request.json.get("projects_dir", "").strip()
    if not projects_dir or not os.path.isdir(projects_dir):
        return jsonify({"error": "Invalid or missing folder path"}), 400
    data = load_data()
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
    projects_dir = get_projects_dir()
    if not projects_dir or not os.path.exists(projects_dir):
        return jsonify([])

    projects = []
    for name in sorted(os.listdir(projects_dir)):
        if name in SKIP_NAMES or name.startswith("."):
            continue
        folder = os.path.join(projects_dir, name)
        if not os.path.isdir(folder):
            continue

        flps = get_flps(folder)
        main_flp = flps[0] if flps else None
        mtime = os.path.getmtime(main_flp) if main_flp else None

        projects.append({
            "name": name,
            "main_flp": main_flp,
            "flps": flps,
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
    def open_browser():
        time.sleep(0.8)
        webbrowser.open("http://localhost:8765")

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=True, port=8765, use_reloader=False)
