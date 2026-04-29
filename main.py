import feedparser
import datetime
import requests
import os

def build_site():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. NASA 數據 ---
    nasa_data = {"url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", "title": "探索宇宙", "explanation": "正在觀測中..."}
    try:
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True", timeout=10).json()
        nasa_data["url"] = resp.get("url") if resp.get("media_type") != "video" else resp.get("thumbnail_url")
        nasa_data["title"] = resp.get("title", "NASA Astronomy Picture")
        nasa_data["explanation"] = resp.get("explanation", "")[:120] + "..."
    except: pass

    # --- 2. 每日貓貓 (直接寫死 URL 防止 API 失效) ---
    cat_url = "https://cataas.com/cat"

    # --- 3. 新聞數據 ---
    sources = [
        {"region": "台灣焦點", "url": "https://feeds.feedburner.com/cnaFirstNews", "flag": "🇹🇼"},
        {"region": "日本焦點", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "flag": "🇯🇵"}
    ]
    news_html = ""
    for s in sources:
        try:
            feed = feedparser.parse(s["url"])
            news_html += f'<h2 class="text-2xl font-bold mt-10 mb-4">{s["flag"]} {s["region"]}</h2>'
            news_html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">'
            for entry in feed.entries[:3]:
                news_html += f'''
                    <a href="{entry.link}" target="_blank" class="bg-white p-4 rounded-xl shadow-sm border hover:shadow-md transition">
                        <h3 class="font-bold text-sm text-gray-800">{entry.title}</h3>
                    </a>'''
            news_html += '</div>'
        except: continue

    # --- 4. HTML 模板 (JS 代碼處使用兩個括號轉義 Python f-string) ---
    full_html = f'''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
        <title>SealNews | 貓貓與柴犬矛盾藝術 0.0</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Noto Sans TC', sans-serif; scroll-behavior: smooth; }}</style>
    </head>
    <body class="bg-slate-50 text-slate-900 p-6 md:p-10">
        <header class="text-center mb-10 pb-6 border-b border-gray-100">
            <h1 class="text-5xl font-black text-gray-900 tracking-tighter">SEAL NEWS</h1>
            <p class="text-gray-500 mt-2 font-medium">{today_str} · 今日世界：充滿希望</p>
        </header>

        <main class="max-w-6xl mx-auto">
            <section class="rounded-3xl overflow-hidden shadow-2xl bg-black text-white aspect-[16/9] md:aspect-[21/9] relative group">
                <img src="{nasa_data['url']}" class="w-full h-full object-cover opacity-80 transition duration-700 group-hover:scale-105">
                <div class="absolute inset-0 bg-gradient-to-t from-black text-white flex flex-col justify-end p-6">
                    <h2 class="text-3xl font-bold">{nasa_data['title']}</h2>
                    <p class="text-gray-200 text-sm opacity-80 mt-1 line-clamp-2">{nasa_data['explanation']}</p>
                </div>
            </section>

            {news_html}

            <section class="mt-20 text-center border-t border-gray-100 pt-16">
                <h2 class="text-3xl font-bold mb-8 text-gray-900">今日份的療癒 🐈</h2>
                <div class="max-w-md mx-auto rounded-3xl overflow-hidden shadow-lg border-4 border-white">
                    <img src="{cat_url}" class="w-full h-64 object-cover" alt="Daily Cat">
                </div>
                <p class="mt-4 text-gray-500 italic text-sm">「不管世界局勢如何變幻，總有一隻貓在默默陪著你。」</p>
            </section>

            <section class="mt-20 border-t border-gray-100 pt-10 text-center">
                <h2 class="text-3xl font-bold text-gray-900 mb-2">柴犬的矛盾藝術 0.0</h2>
                <p class="text-sm text-gray-500 mb-6">點擊柴犬試著套上項圈，給牠一個 ❤️ 吧！</p>
                <div id="dog-art-container" class="w-full h-[400px] bg-white rounded-3xl shadow-inner relative overflow-hidden">
                </div>
            </section>
        </main>

        <footer class="text-center py-10 text-gray-400 text-xs border-t border-gray-100 mt-16">
            &copy; {today_str} SealNews Automation
        </footer>

        <script>
        let dogImg, pawImg, caughtCollarImg;
        let dog;
        let isCaught = false;

        function preload() {{
            // 這裡所有的圖片載入都加上了 loadImage
            dogImg = loadImage('https://img.icons8.com/color/96/shiba-inu.png'); 
            caughtCollarImg = loadImage('https://img.icons8.com/color/48/dog-collar.png'); 
            pawImg = loadImage('https://img.icons8.com/color/48/dog-paw.png');
        }}

        function setup() {{
            let container = document.getElementById('dog-art-container');
            if(!container) return; // 預防畫布容器不存在
            let canvas = createCanvas(container.offsetWidth, 400);
            canvas.parent('dog-art-container');
            
            // 項圈游標直接使用字串路徑，不由 preload 載入
            container.style.cursor = `url('https://img.icons8.com/color/48/dog-collar.png') 24 24, auto`;

            dog = {{
                pos: createVector(width/2, height/2),
                angle: 0,
                rotation: 0,
                speed: 2.2,
                display: function() {{
                    push();
                    translate(this.pos.x, this.pos.y);
                    rotate(isCaught ? sin(frameCount * 0.1) * 0.1 : this.rotation);
                    imageMode(CENTER);
                    
                    // 如果被點擊到，縮小並戴上項圈
                    if (isCaught) {{
                        image(dogImg, 0, 0, 70, 70);
                        image(caughtCollarImg, 0, 15, 30, 30); // 這裡使用了 preload 載入的圖片
                    }} else {{
                        image(dogImg, 0, 0, 90, 90);
                    }}
                    
                    if (isCaught) {{
                        textSize(32); textAlign(CENTER); text('❤️', 0, -50);
                    }}
                    pop();
                }}
            }};
            background(255);
        }}

        function draw() {{
            // 簡化邏輯：如果是空白，請確認是否 preload() 有圖片載入失敗
            background(255, isCaught ? 10 : 35); 
            let target = createVector(mouseX, mouseY);
            
            if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {{
                target = createVector(
                    width/2 + sin(frameCount * 0.01) * (width/3),
                    height/2 + cos(frameCount * 0.015) * 100
                );
            }}

            if (!isCaught) {{
                let d = p5.Vector.dist(dog.pos, target);
                if (d < 120) {{
                    dog.angle += 0.1;
                    dog.pos.x = target.x + cos(dog.angle) * 85;
                    dog.pos.y = target.y + sin(dog.angle) * 85;
                    dog.rotation = dog.angle + PI/2;
                }} else {{
                    let vel = p5.Vector.sub(target, dog.pos);
                    dog.rotation = vel.heading() + PI/2;
                    vel.setMag(dog.speed);
                    dog.pos.add(vel);
                }}
                
                // 畫腳印
                if (frameCount % 18 == 0) {{
                    push(); translate(dog.pos.x, dog.pos.y); rotate(dog.rotation);
                    tint(255, 60); // 腳印顏色
                    image(pawImg, 10, 10, 15, 15);
                    pop();
                }}
            }}
            dog.display();
        }}

        function mousePressed() {{
            let d = dist(mouseX, mouseY, dog.pos.x, dog.pos.y);
            if (d < 55) {{
                isCaught = true;
                setTimeout(() => {{ isCaught = false; }}, 3000);
            }}
        }}

        function windowResized() {{
            let container = document.getElementById('dog-art-container');
            if(container) resizeCanvas(container.offsetWidth, 400);
        }}
        </script>
    </body>
    </html>
    '''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    build_site()
