#!/usr/bin/env python3
from flask import Flask, request, jsonify
import pyautogui
import subprocess
import threading
import time
import tkinter as tk

app = Flask(__name__)
highlight_running = False

def start_cursor_highlight():
    """Show a red circle that follows the mouse until stopped."""
    def _run():
        global highlight_running
        highlight_running = True

        root = tk.Tk()
        root.overrideredirect(True)               # No window border
        root.attributes('-topmost', True)         # Always on top

        # Try per-pixel transparency; if unsupported, fall back to alpha
        try:
            root.attributes('-transparentcolor', 'white')
        except tk.TclError:
            root.attributes('-alpha', 0.3)

        canvas = tk.Canvas(root, width=50, height=50, bg='white', highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 45, 45, outline='red', width=4)

        while highlight_running:
            x, y = pyautogui.position()
            root.geometry(f"+{x-25}+{y-25}")
            root.update()
            time.sleep(0.01)

        root.destroy()

    threading.Thread(target=_run, daemon=True).start()

@app.route('/api/v1/start_highlight', methods=['POST'])
def start_highlight_endpoint():
    start_cursor_highlight()
    return jsonify(status='highlighting started')

@app.route('/api/v1/stop_highlight', methods=['POST'])
def stop_highlight_endpoint():
    global highlight_running
    highlight_running = False
    return jsonify(status='highlighting stopped')

@app.route('/api/v1/open_url', methods=['POST'])
def open_url():
    url = request.json.get('url')
    ua = ("Mozilla/5.0 (X11; Linux x86_64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/120.0.0.0 Safari/537.36")
    cmd = [
        "chromium-browser",
        "--new-window",
        f"--user-agent={ua}",
        "--disable-infobars",
        "--disable-gpu",
        "--no-first-run",
        url
    ]
    threading.Thread(target=lambda: subprocess.Popen(cmd), daemon=True).start()
    return jsonify(status='ok')

@app.route('/api/v1/draw_curve', methods=['POST'])
def draw_curve():
    def _draw():
        points = [(400, 200), (800, 200), (500, 600), (900, 600), (400, 200)]
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            pyautogui.moveTo(x0, y0, duration=0.2)
            pyautogui.dragTo(x1, y1, duration=0.5)
        time.sleep(0.5)
    threading.Thread(target=_draw, daemon=True).start()
    return jsonify(status='ok')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
