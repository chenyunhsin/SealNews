import feedparser
from googletrans import Translator
import datetime
import requests
from textblob import TextBlob  # <--- 確保這行有加！

def build_site():
    translator = Translator()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. 抓取 NASA 每日天文圖 ---
    nasa_data = {"url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", "title": "探索宇宙", "explanation": ""}
    try:
        api_url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True"
        resp = requests.get(api_url, timeout=10).json()
        
        # 處理圖片網址
        if resp.get("media_type") == "video":
            nasa_data["url"] = resp.get("thumbnail_url", nasa_data["url"])
        else:
            nasa_data["url"] = resp.get("url", nasa_data["url"])
        
        # 翻譯標題 (分開處理，失敗也不影響圖片)
        raw_title = resp.get("title", "NASA APOD")
        try:
            nasa_data["title"] = translator.translate(raw_title, dest='zh-tw').text
        except:
            nasa_data["title"] = raw_title
            
        raw_exp = resp.get("explanation", "")
        try:
            nasa_data["explanation"] = translator.translate(raw_exp, dest='zh-tw').text[:150] + "..."
        except:
            nasa_data["explanation"] = raw_exp[:150] + "..."
    except Exception as e:
        print(f"NASA Error: {e}")

    # --- 2. 抓取每日貓貓 ---
    cat_url = "https://cataas.com/cat"

    # --- 3. 新聞與情緒分析 ---
    sources = [
        {"region": "台灣", "url": "https://feeds.feedburner.com/cnaFirstNews", "lang": "zh-tw", "flag": "🇹🇼"},
        {"region": "日本", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "lang": "ja", "flag": "🇯🇵"},
        {"region": "美國", "url": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "lang": "en", "flag": "🇺🇸"}
    ]

    news_html = ""
    us_titles = [] # 用來存美國新聞原文做分析
    
    for s in sources:
        feed = feedparser.parse(s["url"])
        news_html += f'<section class="mb-12"><h2 class="text-2xl font-bold mb-6 flex items-center">{s["flag"]} {s["region"]}焦點</h2><div class="grid grid-cols-1 md:grid-cols-3 gap-6">'
        for entry in feed.entries[:3]:
            title = entry.title
            if s["region"] == "美國": us_titles.append(title)
            if s["lang"] != "zh-tw":
                try: title = translator.translate(title, dest='zh-tw').text
                except: pass
            news_html += f'<a href="{entry.link}" target="_blank" class="bg-white p-6 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 group"><h3 class="font-bold text-gray-800 group-hover:text-blue-600 mb-2 leading-relaxed">{title}</h3><span class="text-blue-500 text-sm font-medium">閱讀更多 →</span></a>'
        news_html += '</div></section>'

    # --- 情緒換膚邏輯 ---
    sentiment_color = "bg-slate-50"
    mood_text = "平穩的一天"
    try:
        analysis = TextBlob(" ".join(us_titles))
        score = analysis.sentiment.polarity
        if score > 0.1:
            sentiment_color = "bg-amber-50" # 溫暖金
            mood_text = "今日世界氣氛：充滿希望"
        elif score < -0.1:
            sentiment_color = "bg-rose-50" # 警戒紅
            mood_text = "今日世界氣氛：略顯緊張"
    except: pass

    # --- 4. 生成 HTML (保持你之前的漂亮模板) ---
    full_html = f'''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>SealNews</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Noto Sans TC', sans-serif; transition: background-color 1s ease; }}</style>
    </head>
    <body class="{sentiment_color} text-slate-900 pb-20">
        <header class="bg-white/80 backdrop-blur-md border-b px-6 py-8 text-center shadow-sm sticky top-0 z-50">
            <h1 class="text-4xl font-black text-slate-800">世界局勢晨報</h1>
            <p class="text-slate-500 mt-2 font-medium">{today_str} · {mood_text}</p>
        </header>
        <main class="max-w-6xl mx-auto px-6 py-10">
            <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank" class="block mb-16">
                <section class="relative rounded-3xl overflow-hidden shadow-2xl aspect-[16/9] md:aspect-[21/9] group">
                    <img src="{nasa_data['url']}" class="w-full h-full object-cover transition duration-700 group-hover:scale-105">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 p-8 flex flex-col justify-end text-white">
                        <span class="bg-orange-500 text-xs font-bold px-3 py-1 rounded-full w-max mb-3">NASA 每日天文圖片</span>
                        <h2 class="text-2xl md:text-4xl font-bold mb-2 underline-offset-4 group-hover:underline">{nasa_data['title']}</h2>
                        <p class="text-gray-200 text-sm line-clamp-2">{nasa_data['explanation']}</p>
                    </div>
                </section>
            </a>
            {news_html}
            <section class="mt-20 text-center border-t pt-12">
                <h2 class="text-2xl font-bold mb-6">今日療癒貓貓 🐈</h2>
                <div class="max-w-md mx-auto rounded-3xl overflow-hidden shadow-lg border-4 border-white"><img src="{cat_url}" class="w-full"></div>
            </section>
        </main>
    </body>
    </html>
    '''
    with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)

if __name__ == "__main__":
    build_site()
