#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Squad礼物CDK发放脚本
功能：
1. 监控本地礼物JSON文件
2. 礼物消息显示在Squad公屏 
3. 特定礼物触发CDK发放
"""

import json
import squad_rcon
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class GiftHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        if event.src_path.endswith('gifts.json'):
            self.callback()

class SquadGiftBridge:
    def __init__(self):
        # 配置参数
        self.config = {
            'squad_rcon': {
                'host': '填写Squad服务器IP',
                'port': 填写RCON端口,
                'password': '填写RCON密码'
            },
            'gift_file': 'gifts.json',
            'trigger_gifts': ['火箭', '超级火箭'],
            'cdk_file': 'cdk_list.txt',
            'used_cdk_file': 'used_cdk.txt'
        }
        
        self.squad_client = None
        self.last_processed = 0

    def connect_squad(self):
        """连接Squad服务器"""
        try:
            self.squad_client = squad_rcon.SquadRcon(
                self.config['squad_rcon']['host'],
                self.config['squad_rcon']['port'],
                self.config['squad_rcon']['password']
            )
            print("成功连接到Squad服务器")
        except Exception as e:
            print(f"连接Squad服务器失败: {e}")

    def process_gifts(self):
        """处理礼物数据"""
        try:
            with open(self.config['gift_file'], 'r') as f:
                gifts = json.load(f)
                
            for gift in gifts['gifts']:
                if gift['timestamp'] > self.last_processed:
                    self.handle_gift(gift)
                    self.last_processed = gift['timestamp']
                    
        except Exception as e:
            print(f"处理礼物数据失败: {e}")

    def handle_gift(self, gift):
        """处理单个礼物"""
        gift_name = gift['name']
        user_name = gift['user']['name']
        
        # 公屏显示礼物消息
        self.send_squad_message(f"^3[礼物] {user_name} 送出了 {gift_name}")
        
        # 检查是否触发CDK发放
        if gift_name in self.config['trigger_gifts']:
            self.process_cdk_reward(user_name, gift_name)

    def process_cdk_reward(self, user_name, gift_name):
        """处理CDK奖励发放"""
        try:
            cdk = self.get_available_cdk()
            if cdk:
                print(f"已向{user_name}发放CDK: {cdk} (礼物: {gift_name})")
        except Exception as e:
            print(f"CDK发放失败: {e}")

    def get_available_cdk(self):
        """获取可用CDK"""
        try:
            # 确保文件存在
            if not os.path.exists(self.config['cdk_file']):
                print(f"CDK文件 {self.config['cdk_file']} 不存在")
                return None
                
            # 读取CDK列表
            with open(self.config['cdk_file'], 'r') as f:
                cdks = [line.strip() for line in f if line.strip()]
                
            # 初始化已使用记录
            if not os.path.exists(self.config['used_cdk_file']):
                open(self.config['used_cdk_file'], 'w').close()
                
            # 读取已使用CDK
            with open(self.config['used_cdk_file'], 'r') as f:
                used = set(line.strip() for line in f if line.strip())
                
            # 找到第一个未使用的
            for cdk in cdks:
                if cdk not in used:
                    with open(self.config['used_cdk_file'], 'a') as f:
                        f.write(f"{cdk}\n")
                    return cdk
                    
            print("所有CDK已发放完毕")
            return None
            
        except Exception as e:
            print(f"获取CDK失败: {e}")
            return None

    def send_squad_message(self, message):
        """发送Squad公屏消息"""
        if self.squad_client:
            try:
                self.squad_client.execute(f"AdminBroadcast {message}")
            except Exception as e:
                print(f"发送Squad消息失败: {e}")

    def run(self):
        """启动服务"""
        self.connect_squad()
        
        # 初始化文件监控
        event_handler = GiftHandler(self.process_gifts)
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=False)
        observer.start()
        
        print("开始监控礼物文件...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    bridge = SquadGiftBridge()
    bridge.run()
