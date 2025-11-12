import requests
import os
import feedparser
from datetime import datetime
import time

print("🚀 开始监控公众号...")

class WeChatBot:
    def __init__(self):
        self.webhook_url = os.getenv('WEBHOOK_URL')
        print(f"✅ 机器人配置加载完成")
        
    def send_message(self, content):
        """发送企业微信机器人消息"""
        print("📤 准备发送消息...")
        
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
                print("✅ 消息发送成功！")
                return True
            else:
                print(f"❌ 消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False

def get_public_account_articles():
    """获取公众号文章"""
    print("📰 开始检查公众号更新...")
    
    # 这里配置您要监控的公众号
    accounts = [
        {
            'name': '人民日报', 
            'rss_url': 'https://rsshub.app/wechat/werss/MzIwMDM4NDMxMA=='
        },
        {
            'name': '央视新闻',
            'rss_url': 'https://rsshub.app/wechat/werss/MjM5MDE0MjM2MA=='
        },
        {
            'name': '新华社',
            'rss_url': 'https://rsshub.app/wechat/werss/MjM5MzcyMjA0MA=='
        }
    ]
    
    all_articles = []
    
    for account in accounts:
        try:
            print(f"🔍 正在检查 {account['name']}...")
            feed = feedparser.parse(account['rss_url'])
            
            if feed.entries:
                # 取最新的一篇文章
                latest_article = feed.entries[0]
                article_info = {
                    'title': latest_article.title,
                    'link': latest_article.link,
                    'source': account['name'],
                    'time': latest_article.get('published', '最新')
                }
                
                print(f"✅ 找到文章: {latest_article.title[:30]}...")
                all_articles.append(article_info)
            else:
                print(f"❌ {account['name']} 没有找到文章")
                
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            print(f"❌ 检查{account['name']}失败: {e}")
    
    return all_articles

def format_message(articles):
    """格式化消息内容"""
    if not articles:
        return "📭 今日暂无公众号更新"
    
    message_lines = [
        "🎯 公众号最新更新",
        "=" * 20
    ]
    
    for i, article in enumerate(articles, 1):
        message_lines.append(f"{i}. {article['source']}")
        message_lines.append(f"   📝 {article['title']}")
        message_lines.append(f"   🔗 {article['link']}")
        message_lines.append("")  # 空行
    
    message_lines.append(f"📊 共找到 {len(articles)} 篇新文章")
    message_lines.append(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    return "\n".join(message_lines)

def main():
    bot = WeChatBot()
    
    # 获取公众号文章
    articles = get_public_account_articles()
    
    # 格式化消息
    message = format_message(articles)
    
    print("📨 准备发送汇总消息...")
    print("=" * 40)
    print(message)
    print("=" * 40)
    
    # 发送消息
    success = bot.send_message(message)
    
    if success:
        print("🎉 监控任务完成！请检查企业微信")
    else:
        print("💥 监控任务失败")

if __name__ == "__main__":
    main()
