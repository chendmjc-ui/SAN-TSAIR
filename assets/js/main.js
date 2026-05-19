// ============================
// 三才實業 — 主要 JavaScript
// ============================

document.addEventListener('DOMContentLoaded', () => {

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
  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.top = Math.random() * 100 + '%';
    p.style.animationDuration = (Math.random() * 10 + 8) + 's';
    p.style.animationDelay = (Math.random() * 8) + 's';
    p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
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

  // --- Contact form ---
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = document.getElementById('submitBtn');
      btn.textContent = '✅ 已送出！我們將盡快回覆您';
      btn.style.background = '#4CAF50';
      btn.style.color = '#fff';
      btn.disabled = true;
    });
  }

  // --- Catalog modal ---
  window.openCatalog = function(supplier) {
    const modal = document.getElementById('catalogModal');
    const title = document.getElementById('catalogTitle');
    const grid = document.getElementById('catalogGrid');
    const catalogs = {
      'dajia': {
        name: '大嘉衣業',
        desc: '溪湖在地服裝供應商，專業團體服、制服',
        items: [
          { name: 'Polo 衫系列', cat: '企業制服', img: '👔', desc: '吸濕排汗、多色可選，最小起訂12件' },
          { name: '工作背心', cat: '工作服', img: '🦺', desc: '反光條、多口袋設計，耐磨耐洗' },
          { name: '運動外套', cat: '活動服', img: '🧥', desc: '防潑水材質，適合班服、社團服' },
          { name: '班服T恤', cat: '班服', img: '👕', desc: '純棉/混紡，可印製LOGO及文字' },
          { name: '宮廟背心', cat: '宗教服', img: '⛩️', desc: '傳統刺繡工藝，廟會活動指定款' },
          { name: '運動褲組', cat: '運動服', img: '🩲', desc: '學校運動會、社區活動首選' },
        ]
      },
      'weiwi': {
        name: '瑋瑋服飾',
        desc: '埔鹽鄉成衣製造，多年在地供應經驗',
        items: [
          { name: '女裝制服套組', cat: '企業制服', img: '👗', desc: '版型修身，適合服務業、接待人員' },
          { name: '男裝制服套組', cat: '企業制服', img: '👔', desc: '挺版設計，中高階主管形象服' },
          { name: '護士服/診所服', cat: '醫療服', img: '🏥', desc: '防菌、防汙材質，多款顏色' },
          { name: '餐飲工作服', cat: '餐飲服', img: '👨‍🍳', desc: '易清洗、防污，附圍裙套組' },
          { name: '幼兒園園服', cat: '幼教服', img: '🎒', desc: '安全材質、鬆緊帶設計，多尺碼' },
          { name: '居家服套組', cat: '生活服', img: '🛋️', desc: '純棉舒適，企業員工福利首選' },
        ]
      },
      'goorik': {
        name: '富雷克 GOORIK',
        desc: '工廠直營，快速出貨，企業制服專家',
        items: [
          { name: '高機能POLO', cat: '機能服', img: '🎽', desc: '抗UV、涼感、吸排汗三合一機能' },
          { name: '科技廠制服', cat: '科技業', img: '🔬', desc: '防靜電材質，符合潔淨室規範' },
          { name: '反光安全背心', cat: '工安服', img: '🦺', desc: 'EN471認證，工地/交管專用' },
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
    document.getElementById('msg').value = '我對「' + productName + '」有興趣，請提供報價與更多資訊。';
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

    // 若 iframe 載入失敗，顯示 fallback
    frame.onerror = () => { fallback.style.display = 'block'; };
    // timeout fallback（部分 PDF 不支援 iframe）
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

  // close modal on backdrop click
  document.getElementById('catalogModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeCatalog();
  });
});
