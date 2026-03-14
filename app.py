import glob
import json
import os
import subprocess
import threading
import time
import webbrowser

from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

PROJECTS_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Projects")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
SKIP_NAMES = {"Backup", "Templates"}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_flps(folder):
    """Return .flp files in the project root (not Backup), newest first."""
    flps = glob.glob(os.path.join(folder, "*.flp"))
    flps.sort(key=os.path.getmtime, reverse=True)
    return flps


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/projects")
def api_projects():
    if not os.path.exists(PROJECTS_DIR):
        return jsonify([])

    projects = []
    for name in sorted(os.listdir(PROJECTS_DIR)):
        if name in SKIP_NAMES or name.startswith("."):
            continue
        folder = os.path.join(PROJECTS_DIR, name)
        if not os.path.isdir(folder):
            continue

        flps = get_flps(folder)
        main_flp = flps[0] if flps else None
        mtime = os.path.getmtime(main_flp) if main_flp else None

        projects.append(
            {
                "name": name,
                "main_flp": main_flp,
                "flps": flps,
                "mtime": mtime,
            }
        )

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
    subprocess.Popen(["open", path])
    return jsonify({"ok": True})


if __name__ == "__main__":
    def open_browser():
        time.sleep(0.8)
        webbrowser.open("http://localhost:8765")

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=True, port=8765, use_reloader=False)
