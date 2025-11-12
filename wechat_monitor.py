import requests
import os
import feedparser
from datetime import datetime
import time

print("🚀 开始监控公众号...")

class WeChatMonitor:
    def __init__(self):
        self.corp_id = os.getenv('CORP_ID')
        self.agent_id = os.getenv('AGENT_ID')
        self.secret = os.getenv('APP_SECRET')
        self.user_id = os.getenv('USER_ID')
        print(f"✅ 配置加载完成: 企业{self.corp_id[:10]}..., 应用{self.agent_id}, 用户{self.user_id}")
        
    def get_access_token(self):
        """获取企业微信access_token"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.secret}"
        try:
            response = requests.get(url, timeout=10)
            result = response.json()
            if 'access_token' in result:
                print("✅ AccessToken获取成功")
                return result['access_token']
            else:
                print(f"❌ 获取token失败: {result}")
                return None
        except Exception as e:
            print(f"❌ 获取access_token失败: {e}")
            return None
    
    def send_message(self, content):
        """发送企业微信消息"""
        print("📤 准备发送消息...")
        access_token = self.get_access_token()
        if not access_token:
            return False
            
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": self.user_id,
            "msgtype": "text",
            "agentid": int(self.agent_id),
            "text": {
                "content": content
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 消息发送成功！请检查企业微信")
                return True
            else:
                print(f"❌ 消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False
    
    def check_public_account(self, rss_url, account_name):
        """检查单个公众号更新"""
        try:
            print(f"🔍 正在检查 {account_name}...")
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print(f"   {account_name} 没有找到文章")
                return []
            
            # 取最新的一篇文章
            latest_article = feed.entries[0]
            article_info = {
                'title': latest_article.title,
                'link': latest_article.link,
                'source': account_name
            }
            
            print(f"✅ 找到文章: {latest_article.title[:20]}...")
            return [article_info]
            
        except Exception as e:
            print(f"❌ 检查{account_name}失败: {e}")
            return []

def main():
    # 创建监控器
    monitor = WeChatMonitor()
    
    # 配置要监控的公众号（这里先放2个示例，您可以后续添加）
    accounts = [
        {
            'name': '人民日报', 
            'rss_url': 'https://rsshub.app/wechat/werss/MzIwMDM4NDMxMA=='
        },
        {
            'name': '央视新闻',
            'rss_url': 'https://rsshub.app/wechat/werss/MjM5MDE0MjM2MA=='
        }
    ]
    
    print(f"📰 开始检查 {len(accounts)} 个公众号...")
    
    all_articles = []
    
    # 检查每个公众号
    for account in accounts:
        articles = monitor.check_public_account(account['rss_url'], account['name'])
        all_articles.extend(articles)
        time.sleep(1)  # 等待1秒，避免请求太快
    
    # 发送汇总消息
    if all_articles:
        message_lines = ["🎯 今日公众号更新", ""]
        for article in all_articles:
            message_lines.append(f"📰 {article['source']}")
            message_lines.append(f"{article['title']}")
            message_lines.append(f"{article['link']}")
            message_lines.append("")  # 空行
        
        message = "\n".join(message_lines)
        print("📨 准备发送汇总消息...")
        success = monitor.send_message(message)
    else:
        print("📭 没有找到文章，发送空更新通知")
        success = monitor.send_message("📭 今日暂无公众号更新")
    
    if success:
        print("🎉 监控任务完成！")
    else:
        print("💥 监控任务失败")

# 运行主程序
if __name__ == "__main__":
    main()
