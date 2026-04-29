import feedparser
import datetime
import requests
import os

def build_site():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. NASA 數據 ---
    nasa_data = {"url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", "title": "探索宇宙"}
    try:
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True", timeout=5).json()
        nasa_data["url"] = resp.get("url") if resp.get("media_type") != "video" else resp.get("thumbnail_url")
        nasa_data["title"] = resp.get("title", "NASA APOD")
    except: pass

    # --- 2. 新聞數據 (日、台、美 三方並列) ---
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
            <div>
                <h2 class="text-xl font-black mb-4 flex items-center gap-2 border-b-2 border-slate-900 pb-2">
                    <span>{s["f"]}</span> {s["r"]}焦點
                </h2>
                <div class="space-y-3">'''
            for e in feed.entries[:5]:
                news_html += f'''
                    <a href="{e.link}" target="_blank" class="block bg-white p-3 rounded-xl shadow-sm border border-slate-100 hover:border-slate-400 transition-all group">
                        <h3 class="text-sm font-bold text-slate-800 line-clamp-2">{e.title}</h3>
                    </a>'''
            news_html += '</div></div>'
        except: continue

    # --- 3. HTML 模板 ---
    template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <title>SealNews | Real-time Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;900&display=swap');
        body { font-family: 'Noto Sans TC', sans-serif; background-color: #f8fafc; }
    </style>
</head>
<body class="p-4 md:p-10 text-slate-900">
    <div class="max-w-6xl mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-5xl font-black tracking-tighter">SEAL NEWS</h1>
            <p class="text-slate-400 text-xs mt-2 font-bold uppercase tracking-widest">[DATE]</p>
        </header>

        <section class="rounded-[2.5rem] overflow-hidden shadow-2xl bg-black text-white relative h-64 md:h-80 mb-10 group">
            <img src="[NASA_URL]" class="w-full h-full object-cover opacity-70 group-hover:scale-105 transition duration-1000">
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 flex flex-col justify-end p-6 md:p-10">
                <h2 class="text-2xl md:text-3xl font-black tracking-tight">[NASA_TITLE]</h2>
            </div>
        </section>

        <section class="mb-12">
            <h2 class="text-2xl font-black mb-6 text-center">🦭 海豹即時觀測站</h2>
            <div class="aspect-video rounded-[2rem] overflow-hidden shadow-2xl border-4 border-white bg-black">
                <iframe class="w-full h-full" src="https://www.youtube.com/embed/videoseries?list=PLK8X9hH2pG7ajG0hYh8mI0h1S8L6e5N6S&autoplay=1&mute=1" title="Seal Cam" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
            <p class="text-center text-xs text-slate-400 mt-4 italic font-bold">即時觀測海豹的矛盾生活 0.0</p>
        </section>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            [NEWS_CONTENT]
        </div>

        <section class="mb-20 text-center border-t border-slate-200 pt-16">
            <h2 class="text-2xl font-bold mb-6 text-slate-800">今日份的療癒 🐈</h2>
            <div class="max-w-md mx-auto rounded-[2.5rem] overflow-hidden shadow-lg border-4 border-white">
                <img src="https://cataas.com/cat" class="w-full h-64 object-cover" alt="Daily Cat">
            </div>
            <p class="mt-4 text-slate-500 italic text-sm">「不管世界局勢如何變幻，總有一隻貓在默默陪著你。」</p>
        </section>

        <section class="mt-20 border-t border-slate-200 pt-10 text-center relative">
            <h2 class="text-3xl font-black text-slate-900 mb-2 font-mono">Footprint Art 0.0</h2>
            <div id="canvas-wrap" class="w-full h-[500px] bg-white rounded-[3rem] shadow-inner border border-slate-100 relative overflow-hidden mt-8">
                <button onclick="clearCanvas()" class="absolute bottom-6 right-6 bg-slate-900 text-white px-6 py-2 rounded-full text-[10px] font-black shadow-lg hover:bg-black transition z-10 uppercase tracking-widest">
                    Clear Canvas
                </button>
            </div>
        </section>
    </div>

    <footer class="text-center py-20 text-slate-300 text-[10px] font-black tracking-[0.3em] uppercase">
        [DATE] • SealNews Hub
    </footer>

    <script>
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
        // 腳印留存超久 (0.005)
        fill(0, 0, 100, 0.005); 
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

        if (frameCount % 10 == 0) {
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
        fill(h, 60, 85, 0.5); scale(random(0.8, 1.1));
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

    # --- 4. 輸出 ---
    final_html = template.replace("[DATE]", today_str)\
                         .replace("[NASA_URL]", nasa_data["url"])\
                         .replace("[NASA_TITLE]", nasa_data["title"])\
                         .replace("[NEWS_CONTENT]", news_html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    build_site()
