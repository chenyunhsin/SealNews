import feedparser
import datetime
import requests
import os

def build_site():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. 抓取 NASA (穩定版) ---
    nasa_data = {"url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", "title": "探索宇宙", "desc": "正在觀測中..."}
    try:
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True", timeout=5).json()
        nasa_data["url"] = resp.get("url") if resp.get("media_type") != "video" else resp.get("thumbnail_url")
        nasa_data["title"] = resp.get("title", "NASA APOD")
        nasa_data["desc"] = resp.get("explanation", "")[:100] + "..."
    except: pass

    # --- 2. 抓取新聞 (包含台灣、日本、美國) ---
    sources = [
        {"r": "台灣", "u": "https://feeds.feedburner.com/cnaFirstNews", "f": "🇹🇼"},
        {"r": "日本", "u": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "f": "🇯🇵"},
        {"r": "美國", "u": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "f": "🇺🇸"}
    ]
    news_html = ""
    for s in sources:
        try:
            feed = feedparser.parse(s["u"])
            news_html += f'<h2 class="text-2xl font-bold mt-10 mb-4">{s["f"]} {s["r"]}焦點</h2>'
            news_html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">'
            for e in feed.entries[:3]:
                news_html += f'<a href="{e.link}" target="_blank" class="bg-white p-4 rounded-xl shadow-sm border hover:bg-slate-50 transition"><h3 class="font-bold text-sm">{e.title}</h3></a>'
            news_html += '</div>'
        except: continue

    # --- 3. HTML 模板 (使用純字串替換，最安全) ---
    template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <title>SealNews</title>
</head>
<body class="bg-slate-50 p-6 text-slate-900">
    <div class="max-w-6xl mx-auto">
        <header class="text-center mb-10"><h1 class="text-4xl font-black">SEAL NEWS</h1><p>[DATE]</p></header>

        <section class="rounded-3xl overflow-hidden shadow-lg bg-black text-white mb-10">
            <img src="[NASA_URL]" class="w-full h-64 object-cover opacity-80">
            <div class="p-6"><h2 class="text-xl font-bold">[NASA_TITLE]</h2><p class="text-sm opacity-70">[NASA_DESC]</p></div>
        </section>

        [NEWS_CONTENT]

        <section class="mt-20 border-t pt-10 text-center">
            <h2 class="text-2xl font-bold mb-2">狗狗的矛盾藝術 0.0</h2>
            <p class="text-sm text-slate-500 mb-6">看著腳印慢慢繞圈...（滑鼠是項圈）</p>
            <div id="canvas-wrap" class="w-full h-[400px] bg-white rounded-3xl shadow-inner border relative overflow-hidden"></div>
        </section>
    </div>

    <script>
    let dog;
    function setup() {
        let c = document.getElementById('canvas-wrap');
        let cnv = createCanvas(c.offsetWidth, 400);
        cnv.parent('canvas-wrap');
        dog = { pos: createVector(width/2, height/2), ang: 0, rot: 0 };
        background(255);
    }
    function draw() {
        background(255, 30); // 增加殘影感
        let t = createVector(mouseX, mouseY);
        // 自動漫遊
        if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {
            t = createVector(width/2 + sin(frameCount*0.005)*width/3, height/2 + cos(frameCount*0.01)*100);
        }

        let d = dist(dog.pos.x, dog.pos.y, t.x, t.y);
        if (d < 120) {
            dog.ang += 0.05; // 慢速旋轉
            dog.pos.x = t.x + cos(dog.ang) * 80;
            dog.pos.y = t.y + sin(dog.ang) * 80;
            dog.rot = dog.ang + PI/2;
        } else {
            let v = p5.Vector.sub(t, dog.pos);
            dog.rot = v.heading() + PI/2;
            v.setMag(1.2); // 慢速移動
            dog.pos.add(v);
        }

        // 畫出腳印 (用程式畫肉球)
        if (frameCount % 40 == 0) {
            noStroke(); fill(180, 160, 140, 150);
            push(); translate(dog.pos.x, dog.pos.y); rotate(dog.rot);
            ellipse(0, 0, 10, 8); // 大墊
            ellipse(-5, -5, 4, 4); ellipse(0, -7, 4, 4); ellipse(5, -5, 4, 4); // 腳趾
            pop();
        }
        
        // 畫出狗狗（現在用一個溫暖的深灰色圓點代替，像是一顆小石子或影子的感覺）
        fill(80); noStroke();
        ellipse(dog.pos.x, dog.pos.y, 12, 12);
    }
    function windowResized() {
        let c = document.getElementById('canvas-wrap');
        if(c) resizeCanvas(c.offsetWidth, 400);
    }
    </script>
</body>
</html>
"""

    # --- 4. 取代並輸出 ---
    final_html = template.replace("[DATE]", today_str)\
                         .replace("[NASA_URL]", nasa_data["url"])\
                         .replace("[NASA_TITLE]", nasa_data["title"])\
                         .replace("[NASA_DESC]", nasa_data["desc"])\
                         .replace("[NEWS_CONTENT]", news_html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    build_site()
