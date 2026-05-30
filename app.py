import logging
from flask import Flask, Response, render_template
import keyboard
from PIL import ImageGrab
from pyzbar.pyzbar import decode, ZBarSymbol
import base64
import threading
import queue
import json
import winsound
import webbrowser
import sys

# 屏蔽 Flask 默认日志，运行更清爽
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)
data_queue = queue.Queue()

# =========================================================================
# Python 异步高性能解码系统
# =========================================================================
last_scanned_text = ""
monitoring_active = True
scan_event = threading.Event()

def scanner_worker():
    """常驻后台的异步解码线程，依靠 Event 锁进行高响应低开销挂起"""
    global last_scanned_text
    while True:
        scan_event.wait()
        scan_event.clear()
        
        if not monitoring_active:
            continue
            
        data_queue.put({"status": "scanning"})
        
        try:
            # 灰度截屏，大幅提升 ZBar 寻点定位速度
            img = ImageGrab.grab().convert('L')
            decoded_objects = decode(img, symbols=[ZBarSymbol.QRCODE])

            if decoded_objects:
                raw_data = decoded_objects[0].data.decode('utf-8')
                
                # 如果原始数据与上次相同则判定为重复
                if raw_data == last_scanned_text:
                    data_queue.put({"status": "duplicate"})
                    continue
                    
                last_scanned_text = raw_data
                data_queue.put({"status": "success", "text": raw_data})
                winsound.Beep(2000, 100)  # 听觉反馈：成功短哔
            else:
                data_queue.put({"status": "not_found"})
                winsound.Beep(500, 200)  # 听觉反馈：失败长哔
                
        except Exception as e:
            data_queue.put({"status": "error", "message": str(e)})

def on_f8_pressed():
    """轻量级按键捕获，瞬间唤醒后台 Event 锁，绝不阻塞键盘响应"""
    if monitoring_active:
        scan_event.set()

def hotkey_listener():
    """全局热键驻留线程"""
    keyboard.add_hotkey('f8', on_f8_pressed)
    keyboard.wait()

# =========================================================================
# 路由通信机制
# =========================================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle', methods=['POST'])
def toggle_monitoring():
    global monitoring_active
    monitoring_active = not monitoring_active
    state = "active" if monitoring_active else "paused"
    return {"state": state}

@app.route('/reset', methods=['POST'])
def reset_history():
    global last_scanned_text
    last_scanned_text = ""
    return "ok"

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            data = data_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    print("=====================================================")
    print("🚀 内网数据传输服务器已就绪！")
    print("👉 全局热键 [F8] 已安全挂载 (如果无法接收热键请使用管理员提权运行)")
    print("=====================================================")
    
    # 启动后台守护异步解码与键盘热键拦截线程
    threading.Thread(target=scanner_worker, daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000)