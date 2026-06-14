import logging
import os
import sys
import threading
import webbrowser

from flask import Flask, render_template


# 屏蔽 Flask 默认日志，运行更清爽
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *x: None

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    """消除浏览器默认的 favicon.ico 404 请求噪声"""
    return "", 204


def open_browser(url):
    try:
        if sys.platform.startswith("win"):
            os.startfile(url)
            return
    except OSError:
        pass

    webbrowser.open(url, new=2)


if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    print("=====================================================")
    print("内网数据传输接收端已就绪")
    print("接收通道：Ctrl+V/拖拽图片 + 天眼屏幕监控")
    print(f"浏览器地址：{url}")
    print("=====================================================")

    threading.Timer(1.0, open_browser, args=(url,)).start()
    app.run(host="127.0.0.1", port=5000)
