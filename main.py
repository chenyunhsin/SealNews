import feedparser
from googletrans import Translator
import datetime
import requests

def build_site():
    translator = Translator()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. 抓取 NASA 每日天文圖 (APOD) ---
    nasa_data = {"url": "", "title": "", "explanation": ""}
    try:
        # 使用 NASA 免費 API (demo key)
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY").json()
        nasa_data["url"] = resp.get("url", "")
        nasa_data["title"] = translator.translate(resp.get("title", ""), dest='zh-tw').text
        nasa_data["explanation"] = translator.translate(resp.get("explanation", ""), dest='zh-tw').text[:150] + "..."
    except:
        nasa_data["title"] = "探索宇宙"

    # --- 2. 抓取每日貓貓 ---
    cat_url = "https://cataas.com/cat" # 簡單好用的貓貓 API

    # --- 3. 新聞來源設定 ---
    sources = [
        {"region": "台灣", "url": "https://feeds.feedburner.com/cnaFirstNews", "lang": "zh-tw", "flag": "🇹🇼"},
        {"region": "日本", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "lang": "ja", "flag": "🇯🇵"},
        {"region": "美國", "url": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "lang": "en", "flag": "🇺🇸"}
    ]

    news_html = ""
    for s in sources:
        feed = feedparser.parse(s["url"])
        news_html += f'<section class="mb-12"><h2 class="text-2xl font-bold mb-6 flex items-center">{s["flag"]} {s["region"]}焦點</h2>'
        news_html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-6">'
        
        for entry in feed.entries[:3]:
            title = entry.title
            if s["lang"] != "zh-tw":
                try: title = translator.translate(title, dest='zh-tw').text
                except: pass
            
            news_html += f'''
                <a href="{entry.link}" target="_blank" class="bg-white p-6 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 group">
                    <h3 class="font-bold text-gray-800 group-hover:text-blue-600 mb-2 leading-relaxed">{title}</h3>
                    <span class="text-blue-500 text-sm font-medium">閱讀更多 →</span>
                </a>'''
        news_html += '</div></section>'

    # --- 4. 組合最終 HTML ---
    full_html = f'''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>世界局勢晨報 x NASA x 貓貓</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Noto Sans TC', sans-serif; }}</style>
    </head>
    <body class="bg-slate-50 text-slate-900">
        <header class="bg-white border-b px-6 py-8 text-center shadow-sm">
            <h1 class="text-4xl font-black text-slate-800 tracking-tight">世界局勢晨報</h1>
            <p class="text-slate-500 mt-2 font-medium">{today_str} · 全球資訊同步更新</p>
        </header>

        <main class="max-w-6xl mx-auto px-6 py-10">
            <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank" class="block">
                <section class="relative rounded-3xl overflow-hidden mb-16 shadow-2xl aspect-[16/9] md:aspect-[21/9] group cursor-pointer">
                    <img src="{nasa_data['url']}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" alt="NASA APOD">
                    
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-end p-8 text-white">
                        <span class="bg-orange-500 text-white text-xs font-bold px-3 py-1 rounded-full w-max mb-3">NASA 每日天文圖片</span>
                        <h2 class="text-2xl md:text-4xl font-bold mb-2 group-hover:underline">{nasa_data['title']}</h2>
                        <p class="text-gray-200 text-sm md:text-base line-clamp-2 max-w-2xl">{nasa_data['explanation']}</p>
                    </div>
                </section>
            </a>

            {news_html}

            <section class="mt-20 text-center border-t pt-12">
                <h2 class="text-2xl font-bold mb-6 text-slate-800">今日療癒貓貓 🐈</h2>
                <div class="max-w-md mx-auto rounded-3xl overflow-hidden shadow-lg border-4 border-white">
                    <img src="{cat_url}" class="w-full h-64 object-cover" alt="Daily Cat">
                </div>
                <p class="mt-4 text-slate-500 italic text-sm">「不管局勢多緊張，總有一隻貓在等你。」</p>
            </section>
        </main>

        <footer class="text-center py-12 text-slate-400 text-sm font-light">
            &copy; {today_str} SealNews · 每天早上 8:00 自動更新
        </footer>
    </body>
    </html>
    '''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    build_site()
