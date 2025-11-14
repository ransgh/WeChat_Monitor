import requests
import os
import feedparser
from datetime import datetime
import time
import json

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        feed = feedparser.parse(rss_url)
        
        if feed.entries:
            articles = []
            for entry in feed.entries[:3]:  # 取最近3篇
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source_name,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:100] if entry.get('summary') else ''
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
    """获取公众号文章 - 优化版"""
    print("📰 开始检查公众号更新...")
    
    all_articles = []
    
    # 稳定的资讯源（确保有内容）
    reliable_sources = [
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
            'name': '36氪',
            'url': 'https://rsshub.app/36kr/newsflashes'
        },
        {
            'name': '界面新闻',
            'url': 'https://rsshub.app/jiemian/news'
        },
        {
            'name': '澎湃新闻',
            'url': 'https://rsshub.app/thepaper/featured'
        },
        {
            'name': '今日热榜',
            'url': 'https://rsshub.app/tophub/Om4ejxvxEN'
        }
    ]
    
    # 尝试一些公众号（可能不稳定）
    wechat_sources = [
        {
            'name': '人民日报',
            'url': 'https://rsshub.app/wechat/rmrb'
        },
        {
            'name': '央视新闻',
            'url': 'https://rsshub.app/wechat/cctvnews'
        },
        {
            'name': '新华网',
            'url': 'https://rsshub.app/wechat/xinhuanet'
        }
    ]
    
    print("📊 检查稳定的资讯源...")
    for source in reliable_sources:
        articles = get_articles_from_rss(source['url'], source['name'])
        all_articles.extend(articles)
        time.sleep(1)
    
    print("📊 尝试检查公众号...")
    for source in wechat_sources:
        articles = get_articles_from_rss(source['url'], source['name'])
        all_articles.extend(articles)
        time.sleep(1)
    
    return all_articles

def format_message(articles):
    """格式化消息内容"""
    if not articles:
        return """📭 今日暂无更新
        
可能是RSS服务暂时不可用。
但机器人功能正常！"""
    
    # 按来源分组
    source_groups = {}
    for article in articles:
        source = article['source']
        if source not in source_groups:
            source_groups[source] = []
        source_groups[source].append(article)
    
    message_lines = [
        "🎯 每日资讯推送",
        "=" * 30
    ]
    
    total_count = 0
    for source, source_articles in source_groups.items():
        if total_count >= 10:  # 最多显示10条
            break
            
        message_lines.append(f"\n📰 {source}")
        for i, article in enumerate(source_articles[:2]):  # 每个来源最多2条
            if total_count >= 10:
                break
                
            clean_title = article['title'].replace('\n', ' ').replace('\r', '')
            # 缩短过长的标题
            if len(clean_title) > 40:
                clean_title = clean_title[:40] + '...'
                
            message_lines.append(f"   {i+1}. {clean_title}")
            if article['link']:
                # 缩短链接显示
                short_link = article['link'][:50] + '...' if len(article['link']) > 50 else article['link']
                message_lines.append(f"      🔗 {short_link}")
            message_lines.append("")
            
            total_count += 1
    
    message_lines.append("=" * 30)
    message_lines.append(f"📊 共推送 {total_count} 条热门内容")
    message_lines.append(f"⏰ 更新时间: {datetime.now().strftime('%m-%d %H:%M')}")
    message_lines.append("💡 资讯来源于各大平台热榜")
    
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

# if __name__ == "__main__":
#     main()
