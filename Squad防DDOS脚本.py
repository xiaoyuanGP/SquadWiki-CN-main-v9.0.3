import socket
import time
from collections import defaultdict
import threading
import json
import os

class SquadAntiDDoS:
    def __init__(self, port=7787, threshold=100, ban_time=3600):
        self.port = port  # Squad默认UDP端口
        self.threshold = threshold  # 每秒请求阈值
        self.ban_time = ban_time  # 封禁时长(秒)
        self.traffic = defaultdict(int)
        self.banned_ips = {}
        self.load_config()
        
    def load_config(self):
        if os.path.exists('antiddos_config.json'):
            with open('antiddos_config.json') as f:
                config = json.load(f)
                self.threshold = config.get('threshold', self.threshold)
                self.ban_time = config.get('ban_time', self.ban_time)
    
    def save_config(self):
        with open('antiddos_config.json', 'w') as f:
            json.dump({
                'threshold': self.threshold,
                'ban_time': self.ban_time
            }, f)
    
    def start_protection(self):
        print(f"启动Squad服务器防DDOS保护(端口:{self.port})...")
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_traffic)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 启动封禁清理线程
        cleaner_thread = threading.Thread(target=self.clean_banned_ips)
        cleaner_thread.daemon = True
        cleaner_thread.start()
        
        # 主线程处理数据包
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                
                if ip in self.banned_ips:
                    continue  # 忽略被封禁IP的请求
                
                self.traffic[ip] += 1
                
        except KeyboardInterrupt:
            print("\n停止防护")
        finally:
            sock.close()
            self.save_config()
    
    def monitor_traffic(self):
        while True:
            time.sleep(1)  # 每秒检查一次
            current_time = time.time()
            
            for ip, count in list(self.traffic.items()):
                if count > self.threshold:
                    print(f"检测到异常流量: {ip} (请求数: {count}/秒)")
                    self.ban_ip(ip, current_time)
            
            self.traffic.clear()
    
    def ban_ip(self, ip, ban_time):
        self.banned_ips[ip] = ban_time + self.ban_time
        print(f"已封禁IP: {ip} (时长: {self.ban_time}秒)")
        
        # 记录到日志文件
        with open('ddos_protection.log', 'a') as f:
            f.write(f"{time.ctime()} - 封禁IP: {ip}\n")
    
    def clean_banned_ips(self):
        while True:
            time.sleep(60)  # 每分钟清理一次
            current_time = time.time()
            
            for ip, end_time in list(self.banned_ips.items()):
                if current_time > end_time:
                    del self.banned_ips[ip]
                    print(f"已解封IP: {ip}")

if __name__ == "__main__":
    # 默认使用Squad默认UDP端口7787
    protector = SquadAntiDDoS(port=7787)
    protector.start_protection()
