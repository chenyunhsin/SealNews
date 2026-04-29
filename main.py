import feedparser
import datetime
import requests
import os

def build_site():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 1. 抓取 NASA ---
    nasa_data = {
        "url": "https://images.nasa.gov/images/as11-40-5874_orig.jpg",
        "title": "探索宇宙",
        "explanation": "今日的宇宙美景正在加載中..."
    }
    try:
        resp = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=True", timeout=10).json()
        if resp.get("media_type") == "video":
            nasa_data["url"] = resp.get("thumbnail_url")
        else:
            nasa_data["url"] = resp.get("url")
        nasa_data["title"] = resp.get("title", "NASA Astronomy Picture")
        nasa_data["explanation"] = resp.get("explanation", "")[:150] + "..."
    except:
        pass

    # --- 2. 抓取新聞 ---
    sources = [
        {"region": "台灣", "url": "https://feeds.feedburner.com/cnaFirstNews", "flag": "🇹🇼"},
        {"region": "日本", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "flag": "🇯🇵"},
        {"region": "美國", "url": "https://news.google.com/rss/search?q=when:1d+source:Associated_Press", "flag": "🇺🇸"}
    ]
    news_html = ""
    for s in sources:
        try:
            feed = feedparser.parse(s["url"])
            news_html += f'<h2 class="text-2xl font-bold mt-10 mb-4">{s["flag"]} {s["region"]}焦點</h2>'
            news_html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">'
            for entry in feed.entries[:3]:
                news_html += f'''
                    <a href="{entry.link}" target="_blank" class="bg-white p-4 rounded-xl shadow-sm border hover:shadow-md transition">
                        <h3 class="font-bold text-sm">{entry.title}</h3>
                    </a>'''
            news_html += '</div>'
        except:
            continue

    # --- 3. HTML 模板 ---
    template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    <title>SealNews | 柴犬藝術</title>
</head>
<body class="bg-slate-50 text-slate-900">
    <header class="bg-white border-b py-6 text-center shadow-sm sticky top-0 z-50">
        <h1 class="text-3xl font-black">SEAL NEWS</h1>
        <p class="text-gray-500 text-sm">[DATE]</p>
    </header>
    <main class="max-w-6xl mx-auto px-6 py-10">
        <section class="rounded-3xl overflow-hidden shadow-xl mb-10 bg-black aspect-video relative">
            <img src="[NASA_URL]" class="w-full h-full object-cover opacity-80">
            <div class="absolute bottom-0 p-6 bg-gradient-to-t from-black text-white w-full">
                <h2 class="text-xl font-bold">[NASA_TITLE]</h2>
                <p class="text-sm opacity-80">[NASA_DESC]</p>
            </div>
        </section>
        [NEWS_CONTENT]
        <section class="mt-20 border-t pt-10 text-center">
            <h2 class="text-2xl font-bold mb-2">柴犬的矛盾藝術 0.0</h2>
            <p class="text-sm text-slate-500 mb-6">點擊柴犬可以套上項圈喔！</p>
            <div id="dog-canvas-container" class="w-full h-[350px] bg-white rounded-3xl shadow-inner relative overflow-hidden"></div>
        </section>
    </main>
    <footer class="text-center py-10 text-gray-400 text-xs border-t mt-10">
        © [DATE] SealNews Automation
    </footer>
    <script>
    [JS_CODE]
    </script>
</body>
</html>
"""

    # --- 4. JavaScript 程式碼 ---
    js_code = """
let dogImg, pawImg;
let dog;
let isCaught = false;

function preload() {
    dogImg = loadImage('https://img.icons8.com/color/96/shiba-inu.png'); 
    pawImg = loadImage('https://img.icons8.com/color/48/dog-paw.png');
}

function setup() {
    let container = document.getElementById('dog-canvas-container');
    let canvas = createCanvas(container.offsetWidth, 350);
    canvas.parent('dog-canvas-container');
    container.style.cursor = "url('https://img.icons8.com/color/32/dog-collar.png') 16 16, auto";
    dog = { pos: createVector(width/2, height/2), angle: 0, rotation: 0 };
}

function draw() {
    background(255, isCaught ? 15 : 45);
    let target = createVector(mouseX, mouseY);
    if (mouseX <= 0 || mouseX >= width || mouseY <= 0 || mouseY >= height) {
        target = createVector(width/2 + sin(frameCount*0.01)*200, height/2 + cos(frameCount*0.015)*100);
    }
    if (!isCaught) {
        let d = dist(dog.pos.x, dog.pos.y, target.x, target.y);
        if (d < 120) {
            dog.angle += 0.08;
            dog.pos.x = target.x + cos(dog.angle) * 85;
            dog.pos.y = target.y + sin(dog.angle) * 85;
            dog.rotation = dog.angle + PI/2;
        } else {
            let v = p5.Vector.sub(target, dog.pos);
            dog.rotation = v.heading() + PI/2;
            v.setMag(2.2);
            dog.pos.add(v);
        }
        if (frameCount % 25 == 0) {
            push(); translate(dog.pos.x, dog.pos.y); rotate(dog.rotation);
            tint(255, 60); image(pawImg, 10, 10, 15, 15); pop();
        }
    }
    push();
    translate(dog.pos.x, dog.pos.y);
    rotate(isCaught ? sin(frameCount*0.1)*0.1 : dog.rotation);
    imageMode(CENTER);
    image(dogImg, 0, 0, 80, 80);
    if (isCaught) {
        textSize(24); textAlign(CENTER); text('❤️', 0, -45);
    }
    pop();
}

function mousePressed() {
    let d = dist(mouseX, mouseY, dog.pos.x, dog.pos.y);
    if (d < 50) {
        isCaught = true;
        setTimeout(() => { isCaught = false; }, 3000);
    }
}

function windowResized() {
    let container = document.getElementById('dog-canvas-container');
    if(container) resizeCanvas(container.offsetWidth, 350);
}
"""

    # --- 5. 組合與輸出 ---
    final_html = template.replace("[DATE]", today_str)\
                         .replace("[NASA_URL]", nasa_data["url"])\
                         .replace("[NASA_TITLE]", nasa_data["title"])\
                         .replace("[NASA_DESC]", nasa
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    build_site()
