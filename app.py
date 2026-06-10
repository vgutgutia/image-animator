"""
Image Animator (educational)
Brings a still image to life with a chosen motion preset using a
first-order motion model running on the club's RTX 5080 worker.
Built to teach how image-to-video synthesis works and why media
literacy matters; the ethics gate in the UI is mandatory.
"""
from flask import Flask, render_template, request, jsonify
import requests as http

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

NECRON          = "http://100.72.210.90:15100"
CONNECT_TIMEOUT = 4
READ_TIMEOUT    = 300

MOTIONS = [
    {"id": "talk",  "name": "Talking",     "desc": "Drives the face with a short speech clip. Works best on front-facing portraits."},
    {"id": "nod",   "name": "Nod and Look","desc": "Subtle head motion: a nod, a glance left and right."},
    {"id": "smile", "name": "Smile",       "desc": "Animates a neutral expression into a smile and back."},
    {"id": "pan",   "name": "Cinematic Pan","desc": "Classic documentary zoom and pan. Works on any image, not just faces."},
]


@app.route("/")
def index():
    return render_template("index.html", motions=MOTIONS)


@app.route("/api/status")
def status():
    """Whether the GPU worker is reachable and advertises the animate task."""
    try:
        r = http.get(f"{NECRON}/status", timeout=(CONNECT_TIMEOUT, 6))
        return jsonify({"available": r.ok})
    except http.exceptions.RequestException:
        return jsonify({"available": False})


@app.route("/api/animate", methods=["POST"])
def animate():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    motion = request.form.get("motion", "pan")
    if motion not in {m["id"] for m in MOTIONS}:
        return jsonify({"error": "Unknown motion preset"}), 400

    file = request.files["image"]
    raw  = file.read()
    try:
        resp = http.post(
            f"{NECRON}/animate",
            files={"image": (file.filename, raw, file.content_type)},
            data={"motion": motion},
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
        )
        return (resp.content, resp.status_code,
                {"Content-Type": resp.headers.get("Content-Type", "application/json")})
    except http.exceptions.RequestException:
        return jsonify({
            "error": "The GPU worker is offline. Animation requires the club's RTX 5080 machine.",
            "gpu_offline": True,
        }), 503


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5010)
