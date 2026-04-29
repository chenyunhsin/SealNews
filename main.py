import feedparser
from googletrans import Translator
import datetime
import requests
import os

def build_site():
    translator = Translator()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. 抓取 NASA 每日天文圖 ---
    nasa_data = {"url": "", "title": "", "explanation": ""}
    try:
        api_url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True"
        resp = requests.get(api_url).json()
        if resp.get("media_type") == "video":
            nasa_data["url"] = resp.get("thumbnail_url", "https://images.nasa.gov/images/as11-40-5874_orig.jpg")
        else:
            nasa_data["url"] = resp.get("url", "https://images.nasa.gov/images/as11-40-5874_orig.jpg")
            
        nasa_data["title"] = translator.translate(resp.get("title", "探索宇宙"), dest='zh-tw').text
        explanation = resp.get("explanation", "")
        nasa_data["explanation"] = translator.translate(explanation, dest='zh-tw').text[:150] + "..."
    except Exception as e:
        print(f"NASA 抓取錯誤: {e}")
        nasa_data["title"] = "探索宇宙"
        nasa_data["url"] = "https://images.nasa.gov/images/as11-40-5874_orig.jpg"

    # --- 2. 抓取每日貓貓 ---
    cat_url = "https://cataas.com/cat"

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

    sentiment_color = "bg-slate-50"
    mood_text = "今日世界氣氛：充滿希望"
    
    # --- 5. 組合最終 HTML (使用 {{ }} 轉義 JavaScript 的大括號) ---
    full_html = f'''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
        <title>SealNews | 狗狗矛盾藝術</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Noto Sans TC', sans-serif; scroll-behavior: smooth; }}</style>
    </head>
    <body class="{sentiment_color} text-slate-900 transition-colors duration-1000">
        <header class="bg-white/80 backdrop-blur-md border-b px-6 py-8 text-center shadow-sm sticky top-0 z-50">
            <h1 class="text-4xl font-black text-slate-800 tracking-tight">SEAL NEWS</h1>
            <p class="text-slate-500 mt-2 font-medium">{today_str} · {mood_text}</p>
        </header>

        <main class="max-w-6xl mx-auto px-6 py-10">
            <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank" class="block">
                <section class="relative rounded-3xl overflow-hidden mb-16 shadow-2xl aspect-[16/9] md:aspect-[21/9] group cursor-pointer">
                    <img src="{nasa_data['url']}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" alt="NASA APOD">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-end p-8 text-white">
                        <span class="bg-orange-500 text-white text-xs font-bold px-3 py-1 rounded-full w-max mb-3">NASA Daily Exploration</span>
                        <h2 class="text-2xl md:text-4xl font-bold mb-2 group-hover:underline">{nasa_data['title']}</h2>
                        <p class="text-gray-200 text-sm md:text-base line-clamp-2 max-w-2xl">{nasa_data['explanation']}</p>
                    </div>
                </section>
            </a>

            {news_html}

            <section class="mt-20 text-center border-t pt-12">
                <h2 class="text-2xl font-bold mb-6 text-slate-800">今日份的療癒 🐈</h2>
                <div class="max-w-md mx-auto rounded-3xl overflow-hidden shadow-lg border-4 border-white">
                    <img src="{cat_url}" class="w-full h-64 object-cover" alt="Daily Cat">
                </div>
            </section>

            <section class="mt-20 border-t pt-10 text-center">
                <h2 class="text-2xl font-bold text-slate-800 mb-2">狗狗的矛盾藝術 0.0</h2>
                <p class="text-sm text-slate-500 mb-6">當你拿著項圈（滑鼠）靠近，牠會興奮地繞著你轉圈圈</p>
                <div id="dog-canvas-container" class="w-full h-[350px] bg-white/50 rounded-3xl shadow-inner relative overflow-hidden"></div>
            </section>
        </main>

        <footer class="text-center py-12 text-slate-400 text-sm font-light">
            &copy; {today_str} SealNews Automation
        </footer>

        <script>
        let dogImg, collarImg;
        let dog;

        function preload() {{
            dogImg = loadImage('https://img.icons8.com/color/96/dog--v1.png'); 
            collarImg = 'https://img.icons8.com/color/48/dog-collar.png';
        }}

        function setup() {{
            let container = document.getElementById('dog-canvas-container');
            let canvas = createCanvas(container.offsetWidth, 350);
            canvas.parent('dog-canvas-container');
            container.style.cursor = `url('${{collarImg}}') 24 24, auto`;

            dog = {{
                pos: createVector(width/2, height/2),
                angle: 0,
                rotation: 0,
                display: function() {{
                    push();
                    translate(this.pos.x, this.pos.y);
                    rotate(this.rotation);
                    imageMode(CENTER);
                    if (dogImg) image(dogImg, 0, 0, 80, 80);
                    pop();
                }}
            }};
            background(255);
        }}

        function draw() {{
            background(255, 40); 
            let target = createVector(mouseX, mouseY);
            
            if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {{
                target = createVector(
                    width/2 + sin(frameCount * 0.01) * (width/3),
                    height/2 + cos(frameCount * 0.02) * 100
                );
            }}

            let d = p5.Vector.dist(dog.pos, target);
            if (d < 130) {{
                dog.angle += 0.18;
                dog.pos.x = target.x + cos(dog.angle) * 90;
                dog.pos.y = target.y + sin(dog.angle) * 90;
                dog.rotation = dog.angle + PI/2;
                
                if (frameCount % 4 == 0) {{
                    noStroke();
                    fill(255, 150, 150, 100);
                    ellipse(dog.pos.x, dog.pos.y, 6, 6);
                }}
            }} else {{
                let vel = p5.Vector.sub(target, dog.pos);
                dog.rotation = vel.heading() + PI/2;
                vel.setMag(4);
                dog.pos.add(vel);
            }}
            dog.display();
        }}

        function windowResized() {{
            let container = document.getElementById('dog-canvas-container');
            resizeCanvas(container.offsetWidth, 350);
        }}
        </script>
    </body>
    </html>
    '''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    build_site()
