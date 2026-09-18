import os
import re

# 1. Update main.js for n8n Webhook and Number Counter
with open('assets/js/main.js', 'r', encoding='utf-8') as f:
    main_js = f.read()

main_js = main_js.replace("const N8N_WEBHOOK = '';", "const N8N_WEBHOOK = 'https://n8n.yourdomain.com/webhook/contact';")

counter_code = """
  // --- Number Counter Animation ---
  const countObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const target = e.target;
        const finalNum = parseInt(target.innerText.replace(/\D/g, ''));
        let start = 0;
        const duration = 2000;
        const step = Math.max(1, Math.floor(finalNum / (duration / 16)));
        const timer = setInterval(() => {
          start += step;
          if (start >= finalNum) {
            target.innerText = finalNum + (target.dataset.suffix || '');
            clearInterval(timer);
          } else {
            target.innerText = start + (target.dataset.suffix || '');
          }
        }, 16);
        countObserver.unobserve(target);
      }
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('.stat-num').forEach(el => {
    if(el.innerText.includes('+')) el.dataset.suffix = '+';
    if(el.innerText.includes('%')) el.dataset.suffix = '%';
    countObserver.observe(el);
  });
"""
if 'Number Counter Animation' not in main_js:
    main_js = main_js.replace('// --- Scroll reveal ---', counter_code + '\n  // --- Scroll reveal ---')

with open('assets/js/main.js', 'w', encoding='utf-8') as f:
    f.write(main_js)

# 2. Update sw.js for PDF Cache
with open('sw.js', 'r', encoding='utf-8') as f:
    sw_js = f.read()
if 'pdf-cache' not in sw_js:
    pdf_cache_code = """
self.addEventListener('fetch', event => {
  if (event.request.url.endsWith('.pdf')) {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request).then(fetchRes => {
          return caches.open('pdf-cache-v1').then(cache => {
            cache.put(event.request.url, fetchRes.clone());
            return fetchRes;
          });
        });
      })
    );
  }
});
"""
    sw_js += pdf_cache_code
with open('sw.js', 'w', encoding='utf-8') as f:
    f.write(sw_js)

# 3. Add Google Maps & FAQ to index.html
with open('index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

faq_html = """
<!-- ===== FAQ ===== -->
<section class="faq" id="faq">
  <div class="container">
    <div class="section-label">FAQ</div>
    <h2 class="section-title">常見<span class="accent-text">問題</span></h2>
    <div class="faq-list">
      <details>
        <summary>客製化制服最少需要幾件？</summary>
        <p>一般來說，我們的基本訂製量為 30 件起。若有特殊需求或較小數量，歡迎與我們聯繫討論。</p>
      </details>
      <details>
        <summary>從下單到交貨需要多久時間？</summary>
        <p>確認設計稿並支付訂金後，一般約需 7-14 個工作天完成製作並出貨。如遇旺季，交期可能有所調整，請提早下單。</p>
      </details>
      <details>
        <summary>可以開立統一發票嗎？</summary>
        <p>可以，我們是合法立案公司，可開立二聯式或三聯式統一發票，請於下單時提供抬頭與統編。</p>
      </details>
    </div>
  </div>
</section>
"""
if 'id="faq"' not in index_html:
    index_html = index_html.replace('<!-- ===== CONTACT ===== -->', faq_html + '\n<!-- ===== CONTACT ===== -->')

map_html = """<div class="info-item"><span class="info-icon">📍</span><div><strong>地圖位置</strong>
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d116347.11942127824!2d120.4024368!3d23.9712176!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x346934c56abebf61%3A0xc36720e53a27f6e3!2z5b2w5YyW5Y6_5rqq5rmW6Y6u!5e0!3m2!1szh-TW!2stw!4v1700000000000!5m2!1szh-TW!2stw" width="100%" height="200" style="border:0; border-radius:8px; margin-top:10px;" allowfullscreen="" loading="lazy"></iframe>
</div></div>"""
if 'google.com/maps/embed' not in index_html:
    index_html = index_html.replace('<div class="info-item"><span class="info-icon">📍</span><div><strong>地址</strong><p>彰化縣溪湖鎮（詳細地址請電洽）</p></div></div>', '<div class="info-item"><span class="info-icon">📍</span><div><strong>地址</strong><p>彰化縣溪湖鎮（詳細地址請電洽）</p></div></div>\n        ' + map_html)

# Add FAQ Schema JSON-LD
faq_schema = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{
      "@type": "Question",
      "name": "客製化制服最少需要幾件？",
      "acceptedAnswer": { "@type": "Answer", "text": "一般來說，我們的基本訂製量為 30 件起。若有特殊需求或較小數量，歡迎與我們聯繫討論。" }
    }, {
      "@type": "Question",
      "name": "從下單到交貨需要多久時間？",
      "acceptedAnswer": { "@type": "Answer", "text": "確認設計稿並支付訂金後，一般約需 7-14 個工作天完成製作並出貨。如遇旺季，交期可能有所調整，請提早下單。" }
    }, {
      "@type": "Question",
      "name": "可以開立統一發票嗎？",
      "acceptedAnswer": { "@type": "Answer", "text": "可以，我們是合法立案公司，可開立二聯式或三聯式統一發票，請於下單時提供抬頭與統編。" }
    }]
  }
  </script>
"""
if '"@type": "FAQPage"' not in index_html:
    index_html = index_html.replace('</head>', faq_schema + '</head>')

index_html = index_html.replace('assets/css/style.css', 'assets/css/style.min.css')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# 4. CSS Minify & Dark Mode
with open('assets/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()
if '--dark-bg' not in css:
    dark_vars = """
@media (prefers-color-scheme: dark) {
  :root {
    --cream: #121212;
    --cream2: #1E1E1E;
    --cream3: #2D2D2D;
    --ink: #F5F5F5;
    --ink2: #E0E0E0;
    --ink3: #A0A0A0;
    --white: #181818;
    --border: 1px solid rgba(255,255,255,0.1);
  }
}
"""
    css += dark_vars

css += """
/* FAQ Styles */
.faq{background:var(--white)}
.faq-list details{background:var(--cream);border:var(--border);border-radius:8px;padding:15px;margin-bottom:10px;cursor:pointer}
.faq-list summary{font-weight:bold;font-size:1.05rem;color:var(--ink);outline:none}
.faq-list p{margin-top:10px;color:var(--ink2);font-size:0.95rem;line-height:1.6}
"""

# Minify logic
css_min = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL) # remove comments
css_min = re.sub(r'\s+', ' ', css_min) # collapse spaces
css_min = css_min.replace('{ ', '{').replace(' }', '}').replace(': ', ':').replace('; ', ';').replace(', ', ',')

with open('assets/css/style.min.css', 'w', encoding='utf-8') as f:
    f.write(css_min.strip())

print('Assets updated successfully!')
