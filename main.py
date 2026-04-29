import feedparser
import datetime
import requests
import os

def build_site():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. NASA 每日影像 (最醒目的即時科學資訊) ---
    nasa_data = {"url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", "title": "探索宇宙"}
    try:
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True", timeout=5).json()
        nasa_data["url"] = resp.get("url") if resp.get("media_type") != "video" else resp.get("thumbnail_url")
        nasa_data["title"] = resp.get("title", "NASA APOD")
    except: pass

    # --- 2. 雙重療癒 API (海豹與貓咪) ---
    seal_url = "https://images.unsplash.com/photo-1590273466070-40c466b4432c?q=80&w=1000"
    try:
        r = requests.get("https://api.seals.dog/img", timeout=3)
        seal_url = r.url
    except: pass
    cat_url = "https://cataas.com/cat"

    # --- 3. 即時新聞 (日、台、美) ---
    sources = [
        {"r": "日本", "u": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "f": "🇯🇵"},
        {"r": "台灣", "u": "https://feeds.feedburner.com/cnaFirstNews", "f": "🇹🇼"},
        {"r": "美國", "u": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "f": "🇺🇸"}
    ]
    news_html = ""
    for s in sources:
        try:
            feed = feedparser.parse(s["u"])
            news_html += f'''
            <section class="mb-10">
                <h2 class="text-2xl font-black mb-6 flex items-center gap-2 border-l-4 border-slate-900 pl-4">
                    <span>{s["f"]}</span> {s["r"]}即時新聞
                </h2>
                <div class="space-y-4">'''
            for e in feed.entries[:5]: # 增加到 5 則
                news_html += f'''
                    <a href="{e.link}" target="_blank" class="block bg-white p-5 rounded-2xl shadow-sm border border-slate-100 hover:border-slate-900 transition-all group">
                        <div class="flex justify-between items-center">
                            <h3 class="font-bold text-slate-800 group-hover:text-black leading-tight">{e.title}</h3>
                            <span class="text-slate-300 group-hover:text-slate-900">→</span>
                        </div>
                    </a>'''
            news_html += '</div></section>'
        except: continue

    # --- 4. HTML 模板 ---
    template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <title>SealNews | Real-time Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;900&family=Noto+Sans+TC:wght@400;900&display=swap');
        body { font-family: 'Inter', 'Noto Sans TC', sans-serif; background-color: #f4f4f5; }
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-5xl mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
            <div>
                <h1 class="text-6xl font-black tracking-tighter text-slate-900">SEAL NEWS</h1>
                <p class="text-slate-500 font-bold uppercase tracking-widest text-xs mt-2">Information Hub / [DATE]</p>
            </div>
            <div id="realtime-clock" class="text-right font-black text-2xl text-slate-900 tabular-nums"></div>
        </header>

        <section class="rounded-[2.5rem] overflow-hidden shadow-2xl bg-black text-white relative h-[400px] mb-12 group">
            <img src="[NASA_URL]" class="w-full h-full object-cover opacity-70 group-hover:scale-105 transition duration-1000">
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-10">
                <span class="text-xs font-black tracking-widest uppercase opacity-60 mb-2 font-mono">NASA Daily Discovery</span>
                <h2 class="text-4xl font-black tracking-tight">[NASA_TITLE]</h2>
            </div>
        </section>

        <div class="grid grid-cols-2 gap-6 mb-16">
            <div class="rounded-3xl overflow-hidden shadow-xl aspect-video border-4 border-white bg-slate-200">
                <img src="[SEAL_URL]" class="w-full h-full object-cover" title="Random Seal">
            </div>
            <div class="rounded-3xl overflow-hidden shadow-xl aspect-video border-4 border-white bg-slate-200">
                <img src="https://cataas.com/cat" class="w-full h-full object-cover" title="Random Cat">
            </div>
        </div>

        <div class="grid grid-cols-1 gap-12">
            [NEWS_CONTENT]
        </div>

        <section class="mt-24 border-t-2 border-slate-200 pt-16">
            <div class="flex justify-between items-end mb-8">
                <div>
                    <h2 class="text-3xl font-black text-slate-900">Footprint Art</h2>
                    <p class="text-slate-500 text-sm font-bold uppercase tracking-widest">Generative Expression 0.0</p>
                </div>
                <button onclick="clearCanvas()" class="bg-slate-900 text-white px-8 py-3 rounded-2xl text-xs font-black shadow-lg hover:bg-black transition active:scale-95 uppercase tracking-widest">
                    Clear Canvas
                </button>
            </div>
            <div id="canvas-wrap" class="w-full h-[500px] bg-white rounded-[3rem] shadow-inner border border-slate-200 relative overflow-hidden"></div>
        </section>
    </div>

    <footer class="text-center py-20 text-slate-300 text-[10px] font-black tracking-[0.4em] uppercase">
        [DATE] • Automated by SealNews
    </footer>

    <script>
    // 即時時鐘
    function updateClock() {
        const now = new Date();
        document.getElementById('realtime-clock').innerText = now.toLocaleTimeString('zh-TW', { hour12: false });
    }
    setInterval(updateClock, 1000);
    updateClock();

    // 腳印藝術
    let dog;
    let currentHue = 0;

    function setup() {
        let c = document.getElementById('canvas-wrap');
        let cnv = createCanvas(c.offsetWidth, 500);
        cnv.parent('canvas-wrap');
        colorMode(HSB, 360, 100, 100, 1);
        dog = { pos: createVector(width/2, height/2), ang: 0, rot: 0, stepCounter: 0, noiseOffset: 0 };
        background(0, 0, 100); 
    }

    function clearCanvas() { background(0, 0, 100); }

    function draw() {
        fill(0, 0, 100, 0.007); 
        rect(0, 0, width, height);

        let t = createVector(mouseX, mouseY);
        if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {
            t = createVector(width/2 + sin(frameCount*0.005)*width/3, height/2 + cos(frameCount*0.01)*120);
        }

        let d = dist(dog.pos.x, dog.pos.y, t.x, t.y);
        if (d < 160) {
            dog.ang += 0.045; 
            let j = map(noise(dog.noiseOffset), 0, 1, -12, 12);
            dog.pos.x = t.x + cos(dog.ang) * (100 + j);
            dog.pos.y = t.y + sin(dog.ang) * (100 + j);
            dog.rot = -atan2(t.x - dog.pos.x, t.y - dog.pos.y);
        } else {
            let v = p5.Vector.sub(t, dog.pos);
            dog.rot = v.heading() + PI/2;
            v.setMag(1.8);
            dog.pos.add(v);
        }
        dog.noiseOffset += 0.04;

        if (frameCount % floor(random(8, 14)) == 0) {
            currentHue = (currentHue + 7) % 360;
            dog.stepCounter++;
            let isFirst = (dog.stepCounter % 2 == 0);
            let rx = random(-4, 4), ry = random(-6, 6);
            if (isFirst) {
                drawPaw(dog.pos.x - 14 + rx, dog.pos.y - 15 + ry, dog.rot, currentHue); 
                drawPaw(dog.pos.x + 12 + rx, dog.pos.y + 25 + ry, dog.rot, currentHue); 
            } else {
                drawPaw(dog.pos.x + 14 + rx, dog.pos.y - 15 + ry, dog.rot, currentHue); 
                drawPaw(dog.pos.x - 12 + rx, dog.pos.y + 25 + ry, dog.rot, currentHue); 
            }
        }
    }

    function drawPaw(x, y, r, h) {
        push(); translate(x, y); rotate(r); noStroke();
        fill(h, 60, 85, 0.45); scale(random(0.8, 1.1));
        ellipse(0, 0, 12, 10); ellipse(-6, -7, 5, 5); ellipse(-2, -10, 5, 5); ellipse(2, -10, 5, 5); ellipse(6, -7, 5, 5);
        pop();
    }

    function windowResized() {
        let c = document.getElementById('canvas-wrap');
        if(c) { resizeCanvas(c.offsetWidth, 500); background(0, 0, 100); }
    }
    </script>
</body>
</html>
"""

    # --- 5. 輸出 ---
    final_html = template.replace("[DATE]", today_str)\
                         .replace("[NASA_URL]", nasa_data["url"])\
                         .replace("[NASA_TITLE]", nasa_data["title"])\
                         .replace("[SEAL_URL]", seal_url)\
                         .replace("[NEWS_CONTENT]", news_html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    build_site()
