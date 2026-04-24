import feedparser
from googletrans import Translator
import datetime
import requests
from textblob import TextBlob

def build_site():
    translator = Translator()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. 抓取 NASA 每日天文圖 (三層保險版) ---
    nasa_data = {
        "url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", 
        "title": "探索宇宙", 
        "explanation": "今日 NASA 提供精彩的天文資訊，點擊圖片了解更多宇宙奧秘。"
    }
    try:
        # 使用 thumbs=True 確保影片時有縮圖
        api_url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True"
        resp = requests.get(api_url, timeout=15).json()
        
        # 邏輯：優先找縮圖 -> 再找原圖 -> 最後用保底圖
        img_url = resp.get("thumbnail_url") or resp.get("url")
        if img_url:
            nasa_data["url"] = img_url
        
        # 翻譯標題與說明 (個別 Try，互不干擾)
        try:
            raw_title = resp.get("title", "NASA APOD")
            nasa_data["title"] = translator.translate(raw_title, dest='zh-tw').text
        except: pass
            
        try:
            raw_exp = resp.get("explanation", "")
            if raw_exp:
                nasa_data["explanation"] = translator.translate(raw_exp, dest='zh-tw').text[:150] + "..."
        except: pass
    except Exception as e:
        print(f"NASA Error: {e}")

    # --- 2. 抓取每日貓貓 (換一個更快的 API) ---
    # 使用 The Cat API，速度通常更穩定
    cat_url = "https://api.thecatapi.com/v1/images/search"
    try:
        cat_resp = requests.get(cat_url, timeout=5).json()
        final_cat_url = cat_resp[0]['url']
    except:
        final_cat_url = "https://cataas.com/cat" # 備用

    # --- 3. 新聞與情緒分析 ---
    sources = [
        {"region": "台灣", "url": "https://feeds.feedburner.com/cnaFirstNews", "lang": "zh-tw", "flag": "🇹🇼"},
        {"region": "日本", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "lang": "ja", "flag": "🇯🇵"},
        {"region": "美國", "url": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "lang": "en", "flag": "🇺🇸"}
    ]

    news_html = ""
    us_titles = []
    
    for s in sources:
        feed = feedparser.parse(s["url"])
        news_html += f'<section class="mb-12"><h2 class="text-2xl font-bold mb-6 flex items-center">{s["flag"]} {s["region"]}焦點</h2><div class="grid grid-cols-1 md:grid-cols-3 gap-6">'
        
        # 如果沒抓到東西，顯示一個友善提醒
        entries = feed.entries[:3]
        if not entries:
            news_html += '<p class="text-slate-400 italic">暫時無法取得該地區新聞...</p>'
        
        for entry in entries:
            title = entry.title
            if s["region"] == "美國": us_titles.append(title)
            if s["lang"] != "zh-tw":
                try: title = translator.translate(title, dest='zh-tw').text
                except: pass
            news_html += f'''
                <a href="{entry.link}" target="_blank" class="bg-white p-6 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 group">
                    <h3 class="font-bold text-gray-800 group-hover:text-blue-600 mb-2 leading-relaxed">{title}</h3>
                    <span class="text-blue-500 text-sm font-medium italic">閱讀更多 →</span>
                </a>'''
        news_html += '</div></section>'

    # --- 情緒分析 ---
    sentiment_color = "bg-slate-50"
    mood_text = "平穩的一天"
    try:
        score = TextBlob(" ".join(us_titles)).sentiment.polarity
        if score > 0.1:
            sentiment_color = "bg-amber-50"
            mood_text = "今日世界氣味：充滿希望"
        elif score < -0.1:
            sentiment_color = "bg-rose-50"
            mood_text = "今日世界氣味：略顯緊張"
    except: pass

    # --- 4. 生成 HTML ---
    full_html = f'''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>SealNews | 世界局勢</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');
            body {{ font-family: 'Noto Sans TC', sans-serif; transition: background-color 1s ease; }}
            .nasa-gradient {{ background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 50%, transparent 100%); }}
        </style>
    </head>
    <body class="{sentiment_color} text-slate-900 pb-20">
        <header class="bg-white/80 backdrop-blur-md border-b px-6 py-8 text-center shadow-sm sticky top-0 z-50">
            <h1 class="text-4xl font-black text-slate-800 tracking-tighter italic">SEAL NEWS</h1>
            <p class="text-slate-500 mt-2 font-medium tracking-widest">{today_str} · {mood_text}</p>
        </header>

        <main class="max-w-6xl mx-auto px-6 py-10">
            <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank" class="block mb-16">
                <section class="relative rounded-[2rem] overflow-hidden shadow-2xl aspect-[16/9] md:aspect-[21/9] group bg-black">
                    <img src="{nasa_data['url']}" loading="lazy" class="w-full h-full object-cover transition duration-1000 group-hover:scale-110 opacity-90 group-hover:opacity-100">
                    <div class="absolute inset-0 nasa-gradient p-8 flex flex-col justify-end text-white">
                        <span class="bg-blue-600 text-[10px] uppercase tracking-widest font-bold px-3 py-1 rounded-full w-max mb-4">NASA Daily Exploration</span>
                        <h2 class="text-2xl md:text-5xl font-black mb-3 group-hover:text-blue-300 transition">{nasa_data['title']}</h2>
                        <p class="text-gray-300 text-sm md:text-base line-clamp-2 max-w-3xl font-light">{nasa_data['explanation']}</p>
                    </div>
                </section>
            </a>

            {news_html}

            <section class="mt-24 text-center border-t border-slate-200 pt-16">
                <h2 class="text-3xl font-black mb-8 text-slate-800 tracking-tighter">今日份的療癒 🐈</h2>
                <div class="max-w-lg mx-auto rounded-[2rem] overflow-hidden shadow-2xl border-[12px] border-white bg-white">
                    <img src="{final_cat_url}" loading="lazy" class="w-full h-auto min-h-[300px] object-cover" alt="Daily Cat">
                </div>
                <p class="mt-8 text-slate-400 italic font-medium tracking-wide">「不管世界局勢如何變幻，總有一隻貓在默默陪著你。」</p>
            </section>
        </main>

        <footer class="text-center py-12 text-slate-300 text-xs tracking-widest uppercase font-bold">
            &copy; {today_str} SealNews Automation
        </footer>
    </body>
    </html>
    '''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    build_site()
