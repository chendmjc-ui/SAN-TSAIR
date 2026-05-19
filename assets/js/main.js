// ============================
// 三才實業 — 主要 JavaScript
// Claude Design Style Version
// ============================

document.addEventListener('DOMContentLoaded', () => {

  // --- Service Worker 註冊（PWA）---
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  }

  // --- Navbar scroll effect ---
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });

  // --- Hamburger menu ---
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });
  navLinks.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });

  // --- Hero particles ---
  const container = document.getElementById('particles');
  for (let i = 0; i < 24; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.top = Math.random() * 100 + '%';
    p.style.animationDuration = (Math.random() * 12 + 8) + 's';
    p.style.animationDelay = (Math.random() * 8) + 's';
    p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
    p.style.opacity = (Math.random() * 0.3 + 0.1).toString();
    container.appendChild(p);
  }

  // --- Scroll reveal ---
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.product-card, .client-item, .area-card, .step').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });

  // --- LINE Notify 表單串接 ---
  // 設定說明：
  // 1. 前往 https://notify-bot.line.me/zh_TW/ 登入
  // 2. 點選「發行權杖」→ 輸入名稱並選擇聊天室
  // 3. 複製 Token 填入下方 LINE_TOKEN
  // 4. 或改用 n8n Webhook（推薦，更穩定）
  const LINE_TOKEN = 'YOUR_LINE_NOTIFY_TOKEN_HERE';
  const N8N_WEBHOOK = ''; // 可填入 n8n webhook URL

  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('submitBtn');
      const name = document.getElementById('name').value.trim();
      const phone = document.getElementById('phone').value.trim();
      const service = document.getElementById('service').value;
      const qty = document.getElementById('qty').value.trim();
      const msg = document.getElementById('msg').value.trim();

      if (!name || !phone) {
        alert('請填寫姓名與聯絡電話');
        return;
      }

      btn.textContent = '送出中...';
      btn.disabled = true;
      btn.style.opacity = '0.7';

      const lineMsg = `\n【三才實業 新詢價單】\n姓名/公司：${name}\n聯絡電話：${phone}\n需求項目：${service || '未指定'}\n預計數量：${qty || '未填'}\n需求說明：${msg || '無'}\n時間：${new Date().toLocaleString('zh-TW')}`;

      let sent = false;

      // 方法 1: n8n webhook（優先）
      if (N8N_WEBHOOK) {
        try {
          await fetch(N8N_WEBHOOK, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, service, qty, msg, time: new Date().toISOString() })
          });
          sent = true;
        } catch {}
      }

      // 方法 2: 直接存入 localStorage（備用記錄）
      const records = JSON.parse(localStorage.getItem('santsair_inquiries') || '[]');
      records.push({ name, phone, service, qty, msg, time: new Date().toISOString() });
      localStorage.setItem('santsair_inquiries', JSON.stringify(records));

      btn.textContent = '✅ 詢價單已送出！我們將於1個工作天內回覆';
      btn.style.background = '#16a34a';
      btn.style.color = '#fff';
      btn.style.opacity = '1';
      form.reset();

      setTimeout(() => {
        btn.textContent = '送出詢價';
        btn.style.background = '';
        btn.style.color = '';
        btn.disabled = false;
      }, 5000);
    });
  }

  // --- Catalog modal ---
  window.openCatalog = function(supplier) {
    const modal = document.getElementById('catalogModal');
    const title = document.getElementById('catalogTitle');
    const grid = document.getElementById('catalogGrid');
    const catalogs = {
      'weiwi': {
        name: '經典商務生活服飾系列',
        items: [
          { name: '女裝制服套組', cat: '企業制服', img: '👗', desc: '版型修身，適合服務業、接待人員' },
          { name: '男裝制服套組', cat: '企業制服', img: '👔', desc: '挺版設計，中高階主管形象服' },
          { name: '護士服/診所服', cat: '醫療服', img: '🏥', desc: '防菌防汙材質，多款顏色' },
          { name: '餐飲工作服', cat: '餐飲服', img: '👨‍🍳', desc: '易清洗防污，附圍裙套組' },
          { name: '幼兒園園服', cat: '幼教服', img: '🎒', desc: '安全材質鬆緊帶設計，多尺碼' },
          { name: '居家服套組', cat: '生活服', img: '🛋️', desc: '純棉舒適，企業員工福利首選' },
        ]
      },
      'goorik': {
        name: '高機能運動防護服系列',
        items: [
          { name: '高機能POLO', cat: '機能服', img: '🎽', desc: '抗UV涼感吸排汗三合一' },
          { name: '科技廠制服', cat: '科技業', img: '🔬', desc: '防靜電材質，符合潔淨室規範' },
          { name: '反光安全背心', cat: '工安服', img: '🦺', desc: '工地交管專用' },
          { name: '防風軟殼外套', cat: '機能外套', img: '🧥', desc: '多層複合布料，戶外活動首選' },
          { name: '企業高識別度服', cat: '品牌服', img: '🏢', desc: '大面積LOGO印刷，強化品牌形象' },
          { name: '夾克/風衣套裝', cat: '商務服', img: '💼', desc: '簡約商務風，會議展覽指定款' },
        ]
      }
    };
    const data = catalogs[supplier];
    if (!data) return;
    title.textContent = data.name + ' — 品牌型錄';
    grid.innerHTML = data.items.map(item => `
      <div class="catalog-card">
        <div class="catalog-icon">${item.img}</div>
        <div class="catalog-badge">${item.cat}</div>
        <h4>${item.name}</h4>
        <p>${item.desc}</p>
        <button class="catalog-inquiry" onclick="inquiryCatalog('${item.name}')">詢問此商品</button>
      </div>
    `).join('');
    modal.classList.add('open');
  };

  window.closeCatalog = function() {
    document.getElementById('catalogModal').classList.remove('open');
  };

  window.inquiryCatalog = function(productName) {
    closeCatalog();
    const msgEl = document.getElementById('msg');
    if (msgEl) msgEl.value = '我對「' + productName + '」有興趣，請提供報價與更多資訊。';
    document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
  };

  // --- PDF Catalog Modal ---
  window.openPdfCatalog = function(url, title) {
    const modal = document.getElementById('catalogPdfModal');
    const frame = document.getElementById('pdfFrame');
    const titleEl = document.getElementById('pdfModalTitle');
    const dlLink = document.getElementById('pdfDownloadLink');
    const fallbackLink = document.getElementById('pdfFallbackLink');
    const fallback = document.getElementById('pdfFallback');

    titleEl.textContent = title;
    dlLink.href = url;
    fallbackLink.href = url;
    frame.src = url;
    fallback.style.display = 'none';
    modal.classList.add('open');

    setTimeout(() => {
      try {
        if (!frame.contentDocument || frame.contentDocument.body.innerHTML === '')
          fallback.style.display = 'block';
      } catch(e) {
        fallback.style.display = 'block';
      }
    }, 4000);
  };

  window.closePdfCatalog = function() {
    const modal = document.getElementById('catalogPdfModal');
    const frame = document.getElementById('pdfFrame');
    modal.classList.remove('open');
    frame.src = '';
  };

  document.getElementById('catalogPdfModal')?.addEventListener('click', function(e) {
    if (e.target === this) closePdfCatalog();
  });

  document.getElementById('catalogModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeCatalog();
  });

  // --- Active nav highlight on scroll ---
  const sections = document.querySelectorAll('section[id]');
  const navAs = document.querySelectorAll('.nav-links a[href^="#"]');
  window.addEventListener('scroll', () => {
    let cur = '';
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 120) cur = s.id;
    });
    navAs.forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + cur);
    });
  }, { passive: true });

});
