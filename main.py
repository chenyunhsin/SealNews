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
                news_html += f'<a href="{e.link}" target="_blank" class="bg-white p-4 rounded-xl shadow-sm border hover:bg-slate-50 transition"><h3 class="font-bold text-sm text-slate-800">{e.title}</h3></a>'
            news_html += '</div>'
        except: continue

    # --- 3. HTML 模板 ---
    template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <title>SealNews | 腳印藝術</title>
</head>
<body class="bg-slate-50 p-6 text-slate-900">
    <div class="max-w-6xl mx-auto">
        <header class="text-center mb-10"><h1 class="text-4xl font-black">SEAL NEWS</h1><p class="text-slate-500">[DATE]</p></header>

        <section class="rounded-3xl overflow-hidden shadow-lg bg-black text-white mb-10">
            <img src="[NASA_URL]" class="w-full h-64 object-cover opacity-80">
            <div class="p-6"><h2 class="text-xl font-bold">[NASA_TITLE]</h2><p class="text-sm opacity-70">[NASA_DESC]</p></div>
        </section>

        <section class="mb-16 text-center border-b pb-12">
            <h2 class="text-2xl font-bold mb-6 text-slate-800">今日份的療癒 🐈</h2>
            <div class="max-w-md mx-auto rounded-3xl overflow-hidden shadow-lg border-4 border-white">
                <img src="https://cataas.com/cat" class="w-full h-64 object-cover" alt="Daily Cat">
            </div>
            <p class="mt-4 text-slate-500 italic text-sm">「不管世界如何，總有一隻貓在等著你。」</p>
        </section>

        [NEWS_CONTENT]

        <section class="mt-20 border-t pt-10 text-center">
            <h2 class="text-2xl font-bold mb-2">狗狗的腳印藝術 0.0</h2>
            <p class="text-sm text-slate-500 mb-6">看著腳印在畫布上慢慢留下...（滑鼠是項圈）</p>
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
        background(255); // 只在開始時畫一次白背景
    }

    function draw() {
        // 關鍵：不再每一幀都重畫背景，讓腳印留著
        // 只有在非常緩慢的情況下輕微覆蓋，模擬淡化感
        fill(255, 3); 
        rect(0, 0, width, height);

        let t = createVector(mouseX, mouseY);
        if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {
            t = createVector(width/2 + sin(frameCount*0.005)*width/3, height/2 + cos(frameCount*0.01)*100);
        }

        let d = dist(dog.pos.x, dog.pos.y, t.x, t.y);
        if (d < 120) {
            dog.ang += 0.04; 
            dog.pos.x = t.x + cos(dog.ang) * 80;
            dog.pos.y = t.y + sin(dog.ang) * 80;
            dog.rot = dog.ang + PI/2;
        } else {
            let v = p5.Vector.sub(t, dog.pos);
            dog.rot = v.heading() + PI/2;
            v.setMag(1.0); // 慢速移動
            dog.pos.add(v);
        }

        // 繪製腳印
        if (frameCount % 45 == 0) {
            drawPaw(dog.pos.x, dog.pos.y, dog.rot);
        }
    }

    function drawPaw(x, y, r) {
        push();
        translate(x, y);
        rotate(r);
        noStroke();
        fill(100, 80, 60, 150); // 咖啡色腳印
        // 大肉墊
        ellipse(0, 0, 12, 10);
        // 四顆腳趾
        ellipse(-6, -6, 5, 5);
        ellipse(-2, -8, 5, 5);
        ellipse(2, -8, 5, 5);
        ellipse(6, -6, 5, 5);
        pop();
    }

    function windowResized() {
        let c = document.getElementById('canvas-wrap');
        if(c) resizeCanvas(c.offsetWidth, 400);
        background(255);
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
