from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import time
import threading
from collections import defaultdict
import json
import os
import psutil

app = Flask(__name__)
socketio = SocketIO(app)

class DDoSMONITOR:
    def __init__(self, port=7787, threshold=100):
        self.port = port
        self.threshold = threshold
        self.traffic = defaultdict(int)
        self.banned_ips = set()
        self.stats = {
            'current_ips': [],
            'banned_ips': [],
            'traffic_data': [],
            'threshold': threshold
        }

    def start_monitor(self):
        # 启动监控线程
        threading.Thread(target=self.monitor_traffic, daemon=True).start()
        # 启动网络统计线程
        threading.Thread(target=self.update_stats, daemon=True).start()
        
        # 主监听循环
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                
                if ip in self.banned_ips:
                    continue
                
                self.traffic[ip] += 1
                self.update_current_ips(ip)
                
        except KeyboardInterrupt:
            print("\n停止监控")
        finally:
            sock.close()

    def monitor_traffic(self):
        while True:
            time.sleep(1)
            current_time = time.time()
            
            for ip, count in list(self.traffic.items()):
                if count > self.threshold:
                    self.ban_ip(ip)
            
            self.traffic.clear()
            self.send_stats()

    def ban_ip(self, ip):
        self.banned_ips.add(ip)
        self.stats['banned_ips'] = list(self.banned_ips)
        socketio.emit('ip_banned', {'ip': ip, 'time': time.ctime()})

    def update_current_ips(self, ip):
        if ip not in self.stats['current_ips']:
            self.stats['current_ips'].append(ip)
            socketio.emit('new_ip', {'ip': ip})

    def update_stats(self):
        while True:
            time.sleep(2)
            # 获取网络流量数据
            net_io = psutil.net_io_counters()
            self.stats['traffic_data'].append({
                'time': time.time(),
                'bytes_recv': net_io.bytes_recv,
                'bytes_sent': net_io.bytes_sent
            })
            # 保持最近60个数据点
            self.stats['traffic_data'] = self.stats['traffic_data'][-60:]
            self.send_stats()

    def send_stats(self):
        socketio.emit('stats_update', self.stats)

@socketio.on('set_threshold')
def handle_set_threshold(data):
    monitor.threshold = data['threshold']
    monitor.stats['threshold'] = data['threshold']
    print(f"更新流量阈值为: {data['threshold']}")

@app.route('/')
def dashboard():
    return render_template('index.html')

if __name__ == "__main__":
    monitor = DDoSMONITOR()
    threading.Thread(target=monitor.start_monitor, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
