import requests
import os
import time

print("🚀 开始测试企业微信机器人推送...")

class WeChatBot:
    def __init__(self):
        self.webhook_url = os.getenv('WEBHOOK_URL')
        print(f"✅ 机器人配置加载完成")
        
    def send_message(self, content):
        """发送企业微信机器人消息"""
        print("📤 准备通过机器人发送消息...")
        
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 机器人消息发送成功！请检查企业微信")
                return True
            else:
                print(f"❌ 机器人消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False

def main():
    bot = WeChatBot()
    
    # 发送测试消息
    test_message = """🎉 机器人测试成功！
    
通过企业微信机器人推送！
时间：{}

✅ 这个方案不需要IP白名单
✅ 更稳定可靠
✅ 消息直接推送到群聊

接下来可以配置公众号监控了！
    """.format(time.strftime("%Y-%m-%d %H:%M:%S"))
    
    success = bot.send_message(test_message)
    
    if success:
        print("🎉 机器人测试完成！")
    else:
        print("💥 机器人测试失败")

if __name__ == "__main__":
    main()
