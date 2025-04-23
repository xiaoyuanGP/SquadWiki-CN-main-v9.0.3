#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音直播礼物与Squad服务器集成脚本
功能：
1. 礼物消息显示在Squad公屏
2. 特定礼物触发CDK发放
需要用户填写以下信息：
1. Squad服务器RCON信息
2. 抖音直播间ID和开发者access_token
3. SquadConsole后台API配置
"""

import websocket
import json
import squad_rcon
import requests
import os

class DouyinSquadBridge:
    def __init__(self):
        # ===== 需要用户配置的部分 =====
        # Squad服务器RCON配置
        self.squad_rcon_config = {
            'host': '填写Squad服务器IP',
            'port': 填写RCON端口,
            'password': '填写RCON密码'
        }
        
        # 抖音直播配置
        self.douyin_config = {
            'room_id': '填写抖音直播间ID',
            'access_token': '填写抖音开发者access_token'
        }

        # CDK发放配置
        self.cdk_config = {
            'trigger_gifts': ['棒棒糖', '啤酒'],  # 触发CDK的礼物名称
            'cdk_file': 'cdk_list.txt',  # CDK列表文件
            'used_cdk_file': 'used_cdk.txt'  # 已使用CDK记录文件
        }
        # ===== 配置结束 =====
        
        self.squad_client = None
        self.ws = None
    
    def connect_squad(self):
        """连接Squad服务器"""
        try:
            self.squad_client = squad_rcon.SquadRcon(
                self.squad_rcon_config['host'],
                self.squad_rcon_config['port'],
                self.squad_rcon_config['password']
            )
            print("成功连接到Squad服务器")
        except Exception as e:
            print(f"连接Squad服务器失败: {e}")
    
    def on_douyin_message(self, ws, message):
        """处理抖音WebSocket消息"""
        try:
            data = json.loads(message)
            if data.get('type') == 'gift':
                # 礼物消息处理
                gift_name = data['gift']['name']
                user_name = data['user']['nickname']
                user_id = data['user']['id']  # 抖音用户UID
                
                # 公屏显示礼物消息
                self.send_squad_message(f"^3[抖音礼物] {user_name} 送出了 {gift_name}")
                
                # 检查是否触发CDK发放
                if gift_name in self.cdk_config['trigger_gifts']:
                    self.process_cdk_reward(user_id, user_name, gift_name)
                    
        except Exception as e:
            print(f"处理抖音消息错误: {e}")

    def process_cdk_reward(self, user_id, user_name, gift_name):
        """处理CDK奖励发放"""
        try:
            # 从SquadConsole获取预留CDK
            cdk = self.get_reserved_cdk()
            if cdk:
                # 发送CDK私信给用户
                self.send_private_message(user_id, f"感谢您的{gift_name}！您的CDK兑换码为：{cdk}")
                print(f"已向{user_name}发放CDK: {cdk}")
        except Exception as e:
            print(f"CDK发放失败: {e}")

    def get_reserved_cdk(self):
        """从本地文件获取可用CDK"""
        try:
            # 确保CDK文件存在
            if not os.path.exists(self.cdk_config['cdk_file']):
                print(f"CDK列表文件 {self.cdk_config['cdk_file']} 不存在")
                return None
                
            # 读取未使用的CDK
            with open(self.cdk_config['cdk_file'], 'r') as f:
                cdks = [line.strip() for line in f if line.strip()]
            
            # 初始化已使用CDK文件
            if not os.path.exists(self.cdk_config['used_cdk_file']):
                open(self.cdk_config['used_cdk_file'], 'w').close()
            
            # 读取已使用的CDK
            with open(self.cdk_config['used_cdk_file'], 'r') as f:
                used_cdks = set(line.strip() for line in f if line.strip())
            
            # 找到第一个未使用的CDK
            for cdk in cdks:
                if cdk not in used_cdks:
                    # 标记为已使用
                    with open(self.cdk_config['used_cdk_file'], 'a') as f:
                        f.write(f"{cdk}\n")
                    return cdk
            
            print("所有CDK已发放完毕")
            return None
        except Exception as e:
            print(f"获取CDK失败: {e}")
            return None

    def send_private_message(self, user_id, message):
        """发送抖音私信"""
        # 需要抖音私信API权限
        # 实现取决于抖音开放平台API支持
        print(f"[模拟]发送私信给用户{user_id}: {message}")
    
    def send_squad_message(self, message):
        """发送消息到Squad服务器公屏"""
        if self.squad_client:
            try:
                self.squad_client.execute(f"AdminBroadcast {message}")
            except Exception as e:
                print(f"发送Squad消息失败: {e}")
    
    def start_douyin_listener(self):
        """启动抖音WebSocket监听"""
        ws_url = f"wss://webcast3-ws-web-hl.douyin.com/webcast/im/push/?room_id={self.douyin_config['room_id']}&access_token={self.douyin_config['access_token']}"
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_douyin_message
        )
        
        print("开始监听抖音直播间...")
        self.ws.run_forever()
    
    def run(self):
        """启动桥接服务"""
        self.connect_squad()
        self.start_douyin_listener()

if __name__ == "__main__":
    bridge = DouyinSquadBridge()
    bridge.run()
