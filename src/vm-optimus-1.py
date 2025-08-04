#!/usr/bin/env python3
from flask import Flask, request, jsonify
import pyautogui
import subprocess
import threading
import time

app = Flask(__name__)

# 1) Open a URL in a new Chromium window with a Chrome-like UA and stealth flags
@app.route('/api/v1/open_url', methods=['POST'])
def open_url():
    url = request.json.get('url')
    ua = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    cmd = [
        "chromium-browser",
        "--new-window",
        f"--user-agent={ua}",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-gpu",
        "--no-first-run",
        url
    ]
    # Launch in background so we can return immediately
    threading.Thread(target=lambda: subprocess.Popen(cmd)).start()
    return jsonify(status='ok')

# 2) Draw a Bézier-style “star” on the screen
@app.route('/api/v1/draw_curve', methods=['POST'])
def draw_curve():
    def _draw():
        points = [(400, 200), (800, 200), (500, 600), (900, 600), (400, 200)]
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            pyautogui.moveTo(x0, y0, duration=0.2)
            pyautogui.dragTo(x1, y1, duration=0.5)
        time.sleep(0.5)

    threading.Thread(target=_draw).start()
    return jsonify(status='ok')

if __name__ == '__main__':
    # Listen on all interfaces so your host can reach it via port-forward
    app.run(host='0.0.0.0', port=5000)
