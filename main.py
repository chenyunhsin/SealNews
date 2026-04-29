import feedparser
import datetime
import requests
import os
import random

def build_site():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. NASA 數據 ---
    nasa_data = {"url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg", "title": "探索宇宙"}
    try:
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True", timeout=5).json()
        nasa_data["url"] = resp.get("url") if resp.get("media_type") != "video" else resp.get("thumbnail_url")
        nasa_data["title"] = resp.get("title", "NASA APOD")
    except: pass

    # --- 2. 海豹與貓咪圖片 (療癒 API) ---
    # 海豹圖片使用專屬 API，若失敗則用備用圖
    seal_url = "https://images.unsplash.com/photo-1590273466070-40c466b4432c?auto=format&fit=crop&w=800&q=80"
    try:
        seal_resp = requests.get("https://randomseal.com/api/v1/random", timeout=3).json()
        seal_url = seal_resp['image']
    except: pass
    cat_url = "https://cataas.com/cat"

    # --- 3. 遊戲推薦與 FF14 連結 ---
    games = [
        {"n": "FF14: 曙光之女", "p": "PC / PS5", "d": "最新 7.0 版本，體驗壯闊的黃金鄉冒險。"},
        {"n": "集合啦！動物森友會", "p": "Switch", "d": "永遠的療癒王者，適合在忙碌一天後放空。"},
        {"n": "星露谷物語", "p": "PC / Switch", "d": "1.6 版本更新了大量內容，回歸農場生活。"},
        {"n": "密特羅德 生存恐懼", "p": "Switch", "d": "精準的動作手感，適合想要點挑戰性的你。"}
    ]
    rec_game = random.choice(games)

    # --- 4. 抓取新聞 (台、日、美) ---
    sources = [
        {"r": "日本", "u": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "f": "🇯🇵"},
        {"r": "台灣", "u": "https://feeds.feedburner.com/cnaFirstNews", "f": "🇹🇼"},
        {"r": "美國", "u": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "f": "🇺🇸"}
    ]
    news_html = ""
    for s in sources:
        try:
            feed = feedparser.parse(s["u"])
            news_html += f'<h2 class="text-2xl font-bold mt-10 mb-4">{s["f"]} {s["r"]}焦點</h2><div class="grid grid-cols-1 md:grid-cols-3 gap-4">'
            for e in feed.entries[:3]:
                news_html += f'<a href="{e.link}" target="_blank" class="bg-white p-4 rounded-xl shadow-sm border hover:bg-slate-50 transition"><h3 class="font-bold text-sm text-slate-800 line-clamp-2">{e.title}</h3></a>'
            news_html += '</div>'
        except: continue

    # --- 5. 完整 HTML 模板 ---
    template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <title>SealNews | FF14 & 繽紛足跡</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;900&display=swap');
        body { font-family: 'Noto Sans TC', sans-serif; }
    </style>
</head>
<body class="bg-slate-50 p-6 text-slate-900">
    <div class="max-w-6xl mx-auto">
        <header class="text-center mb-12">
            <h1 class="text-6xl font-black tracking-tighter text-slate-900">SEAL NEWS</h1>
            <p class="text-slate-400 mt-2">[DATE] · 冒險者的每日情報</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
            <section class="lg:col-span-2 rounded-3xl overflow-hidden shadow-lg bg-black text-white relative h-80">
                <img src="[NASA_URL]" class="w-full h-full object-cover opacity-60">
                <div class="absolute bottom-0 p-6">
                    <span class="bg-blue-600 text-xs px-2 py-1 rounded mb-2 inline-block">宇宙焦點</span>
                    <h2 class="text-2xl font-bold">[NASA_TITLE]</h2>
                </div>
            </section>
            <section class="bg-indigo-600 rounded-3xl p-6 text-white shadow-lg flex flex-col justify-between">
                <div>
                    <h2 class="text-xl font-bold mb-4">🎮 遊戲推薦</h2>
                    <h3 class="text-2xl font-black">[G_NAME]</h3>
                    <p class="text-indigo-100 text-sm mt-2">[G_DESC]</p>
                </div>
                <div class="mt-4 pt-4 border-t border-indigo-400 text-xs opacity-80">平台: [G_PLAT]</div>
            </section>
        </div>

        <section class="mb-10 bg-white rounded-3xl p-8 border border-slate-200 shadow-sm">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-black text-slate-800">⚔️ FINAL FANTASY XIV</h2>
                <a href="https://jp.finalfantasyxiv.com/lodestone/" target="_blank" class="text-sm text-blue-600 font-bold hover:underline">查看 Lodestone 日版官網 →</a>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-slate-50 rounded-2xl border border-dashed border-slate-300">
                    <p class="text-xs text-slate-400 uppercase font-bold">伺服器狀態</p>
                    <p class="text-green-600 font-bold">● All Worlds Normal</p>
                </div>
                <div class="p-4 bg-slate-50 rounded-2xl border border-dashed border-slate-300">
                    <p class="text-xs text-slate-400 uppercase font-bold">目前版本</p>
                    <p class="text-slate-700 font-bold">Version 7.0 "Dawntrail"</p>
                </div>
            </div>
        </section>

        <section class="mb-16 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="text-center">
                <h2 class="text-xl font-bold mb-4 text-slate-700">今日海豹 🦭</h2>
                <div class="rounded-3xl overflow-hidden shadow-lg aspect-square border-4 border-white">
                    <img src="[SEAL_URL]" class="w-full h-full object-cover">
                </div>
            </div>
            <div class="text-center">
                <h2 class="text-xl font-bold mb-4 text-slate-700">今日貓貓 🐈</h2>
                <div class="rounded-3xl overflow-hidden shadow-lg aspect-square border-4 border-white">
                    <img src="[CAT_URL]" class="w-full h-full object-cover">
                </div>
            </div>
        </section>

        [NEWS_CONTENT]

        <section class="mt-20 border-t border-gray-200 pt-10 text-center relative">
            <h2 class="text-3xl font-black text-slate-800 mb-2">繽紛足跡 0.0</h2>
            <p class="text-sm text-slate-400 mb-6">這是一場不完美的矛盾演出...</p>
            
            <div id="canvas-wrap" class="w-full h-[500px] bg-white rounded-[2rem] shadow-inner border border-slate-200 relative overflow-hidden">
                <button onclick="clearCanvas()" class="absolute bottom-6 right-6 bg-slate-800 text-white px-4 py-2 rounded-full text-xs font-bold shadow-lg hover:bg-black transition z-10">
                    重置畫布 (Clear)
                </button>
            </div>
        </section>
    </div>

    <footer class="text-center py-12 text-gray-400 text-xs mt-10 border-t border-gray-100 italic">
        "May you have joy in your journey." - FF14 / [DATE] SealNews Automation
    </footer>

    <script>
    let dog;
    let currentHue = 0;
    let pg; // 使用圖層來處理 Clear

    function setup() {
        let c = document.getElementById('canvas-wrap');
        let cnv = createCanvas(c.offsetWidth, 500);
        cnv.parent('canvas-wrap');
        colorMode(HSB, 360, 100, 100, 1);
        dog = { pos: createVector(width/2, height/2), ang: 0, rot: 0, stepCounter: 0, noiseOffset: 0 };
        background(0, 0, 100); 
    }

    function clearCanvas() {
        background(0, 0, 100);
    }

    function draw() {
        // [強化] 殘留更久：刷新率降到極致
        fill(0, 0, 100, 0.005); 
        rect(0, 0, width, height);

        let t = createVector(mouseX, mouseY);
        // 如果滑鼠不在範圍，自動漫遊
        if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {
            t = createVector(width/2 + sin(frameCount*0.005)*width/3, height/2 + cos(frameCount*0.01)*120);
        }

        let d = dist(dog.pos.x, dog.pos.y, t.x, t.y);
        
        if (d < 160) {
            dog.ang += 0.045; 
            let jitter = map(noise(dog.noiseOffset), 0, 1, -12, 12);
            dog.pos.x = t.x + cos(dog.ang) * (100 + jitter);
            dog.pos.y = t.y + sin(dog.ang) * (100 + jitter);
            dog.rot = -atan2(t.x - dog.pos.x, t.y - dog.pos.y);
        } else {
            let v = p5.Vector.sub(t, dog.pos);
            dog.rot = v.heading() + PI/2;
            v.setMag(1.8);
            dog.pos.add(v);
        }
        dog.noiseOffset += 0.04;

        // [強化] 四足步態：模擬不規則真實感
        if (frameCount % floor(random(7, 13)) == 0) {
            currentHue = (currentHue + 8) % 360;
            dog.stepCounter++;

            let isFirstPhase = (dog.stepCounter % 2 == 0);
            let rx = random(-4, 4);
            let ry = random(-6, 6);

            if (isFirstPhase) {
                drawPaw(dog.pos.x - 14 + rx, dog.pos.y - 15 + ry, dog.rot, currentHue); 
                drawPaw(dog.pos.x + 12 + rx, dog.pos.y + 25 + ry, dog.rot, currentHue); 
            } else {
                drawPaw(dog.pos.x + 14 + rx, dog.pos.y - 15 + ry, dog.rot, currentHue); 
                drawPaw(dog.pos.x - 12 + rx, dog.pos.y + 25 + ry, dog.rot, currentHue); 
            }
        }
    }

    function drawPaw(x, y, r, h) {
        push();
        translate(x, y);
        rotate(r);
        noStroke();
        fill(h, 60, 85, 0.45);
        scale(random(0.8, 1.2));
        ellipse(0, 0, 12, 10); 
        ellipse(-6, -7, 5, 5);
        ellipse(-2, -10, 5, 5);
        ellipse(2, -10, 5, 5);
        ellipse(6, -7, 5, 5);
        pop();
    }

    function windowResized() {
        let c = document.getElementById('canvas-wrap');
        if(c) {
            resizeCanvas(c.offsetWidth, 500);
            background(0, 0, 100);
        }
    }
    </script>
</body>
</html>
"""

    # --- 6. 取代內容並儲存 ---
    final_html = template.replace("[DATE]", today_str)\
                         .replace("[NASA_URL]", nasa_data["url"])\
                         .replace("[NASA_TITLE]", nasa_data["title"])\
                         .replace("[SEAL_URL]", seal_url)\
                         .replace("[CAT_URL]", cat_url)\
                         .replace("[NEWS_CONTENT]", news_html)\
                         .replace("[G_NAME]", rec_game["n"])\
                         .replace("[G_PLAT]", rec_game["p"])\
                         .replace("[G_DESC]", rec_game["d"])

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    build_site()
