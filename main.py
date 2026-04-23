import feedparser
from googletrans import Translator
import datetime

# 1. 設定來源
SOURCES = [
    {"region": "台灣", "url": "https://feeds.feedburner.com/cnaFirstNews", "lang": "zh-tw", "flag": "🇹🇼"},
    {"region": "日本", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "lang": "ja", "flag": "🇯🇵"},
    {"region": "美國", "url": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "lang": "en", "flag": "🇺🇸"}
]

def build_site():
    translator = Translator()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    all_html_content = ""

    for s in SOURCES:
        feed = feedparser.parse(s["url"])
        if not feed.entries:
            print(f"警告：無法從 {s['region']} 獲取資料")
            continue
        region_html = f'<section class="mb-12"><h2 class="text-xl font-bold mb-4 border-l-4 border-blue-500 pl-3">{s["flag"]} {s["region"]}焦點</h2><div class="grid grid-cols-1 md:grid-cols-3 gap-6">'
        for entry in feed.entries[:3]:
            # 優先取 title，如果沒有就取 summary
            title = getattr(entry, 'title', '無標題')
            link = getattr(entry, 'link', '#')
            original_title = ""
    
            if s["lang"] != "zh-tw":
                original_title = title
                try:
                    # 加入 timeout 避免卡死，並指定 src='ja' 給日本來源
                    translated = translator.translate(title, dest='zh-tw')
                    title = translated.text
                except Exception as e:
                    print(f"翻譯失敗: {e}")
                    # 如果翻譯失敗，就直接顯示原文標題，不要讓它是空的
                    title = original_title
       
            
            # 生成卡片 HTML
            region_html += f'''
                <a href="{entry.link}" target="_blank" class="bg-white p-5 rounded-xl shadow-sm hover:shadow-md transition">
                    <h3 class="font-bold text-gray-800 leading-snug">{title}</h3>
                    <p class="text-xs text-gray-400 mt-2 italic">{original_title}</p>
                </a>'''
        
        region_html += "</div></section>"
        all_html_content += region_html

    # 讀取模板並替換內容 (這裡簡單示範直接寫入完整 HTML)
    full_html = f'''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script>
        <title>世界局勢晨報</title>
    </head>
    <body class="bg-gray-50 p-8">
        <header class="text-center mb-10"><h1 class="text-3xl font-bold">世界局勢晨報</h1><p>{today}</p></header>
        <main class="max-w-6xl mx-auto">{all_html_content}</main>
    </body>
    </html>
    '''
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    build_site()
