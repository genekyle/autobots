#!/usr/bin/env python3
from flask import Flask, request, jsonify
import pyautogui, subprocess, threading, time
from PyQt5 import QtWidgets, QtCore, QtGui
import sys

app = Flask(__name__)
highlight_app = None
highlight_timer = None
highlight_window = None

# at the top of your file
highlight_app = None
highlight_window = None
highlight_timer = None

def start_cursor_highlight():
    """Launch a click-through translucent overlay that follows the mouse."""
    def _run_qt():
        global highlight_app, highlight_window, highlight_timer

        # If already running, do nothing
        if highlight_app:
            return

        from PyQt5 import QtWidgets, QtCore, QtGui
        import sys

        highlight_app = QtWidgets.QApplication(sys.argv)
        highlight_window = QtWidgets.QWidget(
            None,
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        highlight_window.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        highlight_window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        highlight_window.resize(50, 50)

        # Paint a red circle
        def paint_overlay(event):
            painter = QtGui.QPainter(highlight_window)
            pen = QtGui.QPen(QtCore.Qt.red, 4)
            painter.setPen(pen)
            painter.drawEllipse(2, 2, 46, 46)
        highlight_window.paintEvent = paint_overlay

        highlight_window.show()

        # Timer to follow the cursor
        def tick():
            pos = QtGui.QCursor.pos()
            highlight_window.move(pos.x() - 25, pos.y() - 25)

        highlight_timer = QtCore.QTimer()
        highlight_timer.timeout.connect(tick)
        highlight_timer.start(10)

        highlight_app.exec_()

    threading.Thread(target=_run_qt, daemon=True).start()

@app.route('/api/v1/start_highlight', methods=['POST'])
def start_highlight_endpoint():
    start_cursor_highlight()
    return jsonify(status='highlighting started')

@app.route('/api/v1/stop_highlight', methods=['POST'])
def stop_highlight_endpoint():
    global highlight_app
    if highlight_app:
        highlight_app.quit()
    highlight_app = None
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
