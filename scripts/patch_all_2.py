import os
import re

# 1 & 7. Create Test Script & n8n JSON
with open('test_webhook.py', 'w', encoding='utf-8') as f:
    f.write('''import urllib.request, json
url = "https://n8n.yourdomain.com/webhook/contact"
data = json.dumps({"name": "Test User", "phone": "0912345678", "service": "測試服務", "qty": "10", "msg": "這是一封測試訊息", "time": "2026-05-27T00:00:00Z"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    urllib.request.urlopen(req)
    print("Webhook test successful")
except Exception as e:
    print("Webhook test failed:", e)
''')

with open('n8n_line_notify_workflow.json', 'w', encoding='utf-8') as f:
    f.write('''{
  "name": "SAN-TSAIR Form to LINE Notify",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "contact",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [ 250, 300 ]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://notify-api.line.me/api/notify",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": true,
        "contentType": "form-urlencoded",
        "bodyParameters": {
          "parameters": [
            {
              "name": "message",
              "value": "=\\n【三才實業 詢價單】\\n姓名: {{$json[\"body\"][\"name\"]}}\\n電話: {{$json[\"body\"][\"phone\"]}}\\n項目: {{$json[\"body\"][\"service\"]}}\\n數量: {{$json[\"body\"][\"qty\"]}}\\n說明: {{$json[\"body\"][\"msg\"]}}\\n時間: {{$json[\"body\"][\"time\"]}}"
            }
          ]
        }
      },
      "name": "LINE Notify",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [ 450, 300 ],
      "credentials": {
        "httpHeaderAuth": {
          "id": "YOUR_LINE_NOTIFY_CREDENTIAL_ID",
          "name": "Line Notify Auth"
        }
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [ { "node": "LINE Notify", "type": "main", "index": 0 } ]
      ]
    }
  }
}''')

# 2. Update temple-gifts.html OG & Schema
if os.path.exists('temple-gifts.html'):
    with open('temple-gifts.html', 'r', encoding='utf-8') as f:
        html = f.read()
    html = re.sub(r'<meta property="og:image" content="[^"]+">', '<meta property="og:image" content="https://chendmjc-ui.github.io/SAN-TSAIR/assets/images/temple-og.png">', html)
    html = html.replace('"name": "三才實業"', '"name": "三才實業宮廟客製中心"')
    with open('temple-gifts.html', 'w', encoding='utf-8') as f:
        f.write(html)

# 3, 5, 9. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    index = f.read()

# Add Theme Toggle Button
if 'id="themeToggle"' not in index:
    index = index.replace('<ul class="nav-links"', '<button id="themeToggle" class="theme-toggle" aria-label="切換夜間模式">🌓</button>\n    <ul class="nav-links"')

# Static Map Replace
if '<iframe src="https://www.google.com/maps/embed' in index:
    static_map = '<a href="https://goo.gl/maps/YOUR_LINK" target="_blank"><img src="https://maps.googleapis.com/maps/api/staticmap?center=23.9712176,120.4024368&zoom=14&size=600x200&key=YOUR_API_KEY_HERE&markers=color:red%7C23.9712176,120.4024368" alt="地圖位置" style="width:100%; border-radius:8px; margin-top:10px;"></a>'
    index = re.sub(r'<iframe src="https://www.google.com/maps/embed[^>]+></iframe>', static_map, index)

# Product Filter
if 'class="product-filter"' not in index:
    filter_html = '''
    <div class="product-filter" style="display:flex; gap:10px; margin-bottom: 24px; justify-content:center; flex-wrap:wrap;">
      <button class="filter-btn active" data-filter="all">全部作品</button>
      <button class="filter-btn" data-filter="匾額製作">匾額獎牌</button>
      <button class="filter-btn" data-filter="團體制服">團體制服</button>
      <button class="filter-btn" data-filter="宮廟宗教禮品">宮廟禮品</button>
    </div>
    <div class="products-grid">'''
    index = index.replace('<div class="products-grid">', filter_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index)

# 4, 5, 9. Update main.js
with open('assets/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

if 'themeToggle' not in js:
    js += '''
// --- Dark Mode Toggle ---
const themeBtn = document.getElementById('themeToggle');
if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const target = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', target);
    localStorage.setItem('theme', target);
  });
  if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
}

// --- Product Filter ---
const filterBtns = document.querySelectorAll('.filter-btn');
const productCards = document.querySelectorAll('.product-card');
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    productCards.forEach(card => {
      if (filter === 'all' || card.querySelector('h3').innerText.includes(filter) || card.querySelector('.product-icon').innerText.includes(filter)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  });
});
'''
with open('assets/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 6. sw.js Image Cache
with open('sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

if 'image-cache' not in sw:
    sw += '''
self.addEventListener('fetch', event => {
  if (event.request.url.match(/\\.(png|jpg|jpeg|webp|svg)$/)) {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request).then(fetchRes => {
          return caches.open('image-cache-v1').then(cache => {
            cache.put(event.request.url, fetchRes.clone());
            return fetchRes;
          });
        });
      })
    );
  }
});
'''
with open('sw.js', 'w', encoding='utf-8') as f:
    f.write(sw)

# Update CSS for dark mode attribute and filters
with open('assets/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

if '[data-theme="dark"]' not in css:
    dark_css = '''
[data-theme="dark"] {
  --cream: #121212;
  --cream2: #1E1E1E;
  --cream3: #2D2D2D;
  --ink: #F5F5F5;
  --ink2: #E0E0E0;
  --ink3: #A0A0A0;
  --white: #181818;
  --border: 1px solid rgba(255,255,255,0.1);
}
.theme-toggle { background: transparent; border: none; font-size: 1.4rem; cursor: pointer; padding: 5px; margin-right: 10px; }
.filter-btn { padding: 8px 16px; border: var(--border); border-radius: 20px; background: var(--white); color: var(--ink); cursor: pointer; transition: 0.3s; }
.filter-btn.active, .filter-btn:hover { background: var(--ink); color: var(--cream); }
'''
    css += dark_css

css_min = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
css_min = re.sub(r'\s+', ' ', css_min).replace('{ ', '{').replace(' }', '}').replace(': ', ':').replace('; ', ';')

with open('assets/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
with open('assets/css/style.min.css', 'w', encoding='utf-8') as f:
    f.write(css_min.strip())

# 8. WebP Script
with open('convert_to_webp.py', 'w', encoding='utf-8') as f:
    f.write('''import os
try:
    from PIL import Image
    import glob
    files = glob.glob('assets/images/**/*.{png,jpg,jpeg}', recursive=True)
    count = 0
    for f in files:
        if not f.endswith('.webp'):
            img = Image.open(f)
            img.save(f.rsplit('.', 1)[0] + '.webp', 'webp')
            count += 1
    print(f"Converted {count} images to WebP.")
except ImportError:
    print("Pillow not installed. Please run `pip install Pillow` to convert images.")
''')

print("All patches applied successfully.")
