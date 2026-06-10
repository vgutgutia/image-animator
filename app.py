"""
Image Animator (educational)
Brings a still image to life from a text prompt using the LTX-Video
image-to-video diffusion model running on the club's GPU servers.
Built to teach how video synthesis works and why media literacy
matters; the ethics gate in the UI is mandatory.
"""
from flask import Flask, render_template, request, jsonify
import requests as http

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

NECRON          = "http://100.72.210.90:15100"
CONNECT_TIMEOUT = 4
READ_TIMEOUT    = 420

PROMPT_IDEAS = [
    "The squirrel turns its head and chatters, tail flicking",
    "Gentle wind moves through the trees as clouds drift by",
    "The statue slowly turns to look at the camera",
    "Waves roll onto the beach in slow motion",
    "The cat blinks and yawns, then settles back to sleep",
    "Snow begins to fall softly over the scene",
]


@app.route("/")
def index():
    return render_template("index.html", ideas=PROMPT_IDEAS)


@app.route("/api/status")
def status():
    """Whether the GPU worker is reachable."""
    try:
        r = http.get(f"{NECRON}/status", timeout=(CONNECT_TIMEOUT, 6))
        return jsonify({"available": r.ok})
    except http.exceptions.RequestException:
        return jsonify({"available": False})


@app.route("/api/animate", methods=["POST"])
def animate():
    """Submit a render job to the GPU queue; returns a job id to poll."""
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    prompt = (request.form.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Describe the motion you want first."}), 400
    if len(prompt) > 400:
        return jsonify({"error": "Prompt too long (max 400 characters)."}), 400

    file = request.files["image"]
    try:
        resp = http.post(
            f"{NECRON}/jobs/animate",
            files={"image": (file.filename, file.read(), file.content_type)},
            data={"prompt": prompt},
            timeout=(CONNECT_TIMEOUT, 30),
        )
        return (resp.content, resp.status_code, {"Content-Type": "application/json"})
    except http.exceptions.RequestException:
        return jsonify({
            "error": "The club's GPU servers are offline right now. Try again later.",
            "gpu_offline": True,
        }), 503


@app.route("/api/job/<jid>")
def job_status(jid):
    try:
        resp = http.get(f"{NECRON}/jobs/{jid}", timeout=(CONNECT_TIMEOUT, 15))
        return (resp.content, resp.status_code, {"Content-Type": "application/json"})
    except http.exceptions.RequestException:
        return jsonify({"error": "GPU server unreachable", "gpu_offline": True}), 503


@app.route("/api/job/<jid>/result")
def job_result(jid):
    try:
        resp = http.get(f"{NECRON}/jobs/{jid}/result", timeout=(CONNECT_TIMEOUT, 60))
        return (resp.content, resp.status_code,
                {"Content-Type": resp.headers.get("Content-Type", "application/octet-stream")})
    except http.exceptions.RequestException:
        return jsonify({"error": "GPU server unreachable"}), 503


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5010)
