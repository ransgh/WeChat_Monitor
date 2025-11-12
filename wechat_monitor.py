import requests
import os
import feedparser
from datetime import datetime
import time
import random

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

def get_articles_from_rss(rss_url, source_name):
    """从RSS源获取文章"""
    try:
        print(f"🔍 尝试从 {source_name} 获取内容...")
        feed = feedparser.parse(rss_url)
        
        if feed.entries:
            articles = []
            for entry in feed.entries[:2]:  # 取最近2篇
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source_name,
                    'published': entry.get('published', '')
                })
            print(f"✅ 从 {source_name} 找到 {len(articles)} 篇文章")
            return articles
        else:
            print(f"❌ {source_name} 没有找到文章")
            return []
            
    except Exception as e:
        print(f"❌ {source_name} 获取失败: {e}")
        return []

def get_public_account_articles():
    """获取公众号文章 - 使用多种RSS源"""
    print("📰 开始检查公众号更新...")
    
    all_articles = []
    
    # 方法1: 使用其他RSS服务（更稳定）
    rss_sources = [
        {
            'name': '知乎热榜',
            'url': 'https://rsshub.app/zhihu/hotlist'
        },
        {
            'name': '微博热搜',
            'url': 'https://rsshub.app/weibo/search/hot'
        },
        {
            'name': 'GitHub Trending',
            'url': 'https://rsshub.app/github/trending'
        },
        {
            'name': '少数派',
            'url': 'https://sspai.com/feed'
        },
        {
            'name': '36氪',
            'url': 'https://rsshub.app/36kr/newsflashes'
        }
    ]
    
    for source in rss_sources:
        articles = get_articles_from_rss(source['url'], source['name'])
        all_articles.extend(articles)
        time.sleep(1)  # 避免请求过快
    
    # 方法2: 尝试一些已知可用的公众号（备用）
    wechat_backup_sources = [
        {
            'name': '腾讯新闻',
            'url': 'https://rsshub.app/tencent/news/rank'
        }
    ]
    
    for source in wechat_backup_sources:
        articles = get_articles_from_rss(source['url'], source['name'])
        all_articles.extend(articles)
        time.sleep(1)
    
    return all_articles

def format_message(articles):
    """格式化消息内容"""
    if not articles:
        return """📭 今日暂无更新

可能是RSS服务暂时不可用。
建议：
1. 稍后重试
2. 更换其他RSS源
3. 使用其他内容源替代"""
    
    message_lines = [
        "🎯 最新内容更新",
        "=" * 30
    ]
    
    for i, article in enumerate(articles[:8], 1):  # 最多显示8条
        # 清理标题中的换行符
        clean_title = article['title'].replace('\n', ' ').replace('\r', '')
        message_lines.append(f"{i}. {article['source']}")
        message_lines.append(f"   📝 {clean_title[:50]}{'...' if len(clean_title) > 50 else ''}")
        if article['link']:
            message_lines.append(f"   🔗 {article['link']}")
        message_lines.append("")
    
    message_lines.append(f"📊 共找到 {len(articles)} 条内容")
    message_lines.append(f"⏰ 更新时间: {datetime.now().strftime('%m-%d %H:%M')}")
    
    message = "\n".join(message_lines)
    
    # 如果消息太长，截断
    if len(message) > 4000:
        message = message[:4000] + "\n\n...（内容过多已截断）"
    
    return message

def main():
    bot = WeChatBot()
    
    print("开始获取内容...")
    articles = get_public_account_articles()
    
    print(f"总共找到 {len(articles)} 篇文章")
    
    message = format_message(articles)
    
    print("准备发送消息...")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    success = bot.send_message(message)
    
    if success:
        print("🎉 监控任务完成！")
        if articles:
            print(f"✅ 成功推送 {len(articles)} 条内容")
        else:
            print("⚠️ 未找到内容，但推送成功")
    else:
        print("💥 监控任务失败")

if __name__ == "__main__":
    main()
