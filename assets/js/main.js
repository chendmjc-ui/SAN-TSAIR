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

  // --- 詢價表單 → Google Apps Script（寫入 Google Sheet + LINE Messaging API 通知）---
  // 部署步驟見 docs/apps_script_form_setup.md，部署完成後把下面網址換成實際的 /exec 網址
  const FORM_WEBHOOK = 'PASTE_APPS_SCRIPT_EXEC_URL_HERE';

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

      let sent = false;
      try {
        // Content-Type 故意用 text/plain：Apps Script Web App 不處理 CORS 預檢請求（OPTIONS），
        // 用 application/json 會觸發預檢而失敗；body 仍是 JSON 字串，Apps Script 端照樣 JSON.parse 解析
        const res = await fetch(FORM_WEBHOOK, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify({ name, phone, service, qty, msg, time: new Date().toISOString() })
        });
        sent = res.ok;
      } catch (err) {
        console.error('詢價單傳送失敗:', err);
      }

      // 本機備用記錄（無論是否送達都保留，方便排查）
      const records = JSON.parse(localStorage.getItem('santsair_inquiries') || '[]');
      records.push({ name, phone, service, qty, msg, time: new Date().toISOString(), sent });
      localStorage.setItem('santsair_inquiries', JSON.stringify(records));

      if (sent) {
        btn.textContent = '✅ 詢價單已送出！我們將於1個工作天內回覆';
        btn.style.background = '#16a34a';
        btn.style.color = '#fff';
        form.reset();
      } else {
        btn.textContent = '⚠️ 傳送失敗，請改用 LINE 或電話聯絡我們';
        btn.style.background = '#dc2626';
        btn.style.color = '#fff';
      }
      btn.style.opacity = '1';

      setTimeout(() => {
        btn.textContent = '送出詢價';
        btn.style.background = '';
        btn.style.color = '';
        btn.disabled = false;
      }, 5000);
    });
  }

  // --- 廠商上下架開關 ---
  // 大嘉衣業：同意狀態確認中（詳見 P:\@三才WEB\@三才WEB.xlsx），暫時下架；
  // 取得書面同意後把 daijia 改成 true 即可重新上架，不用改 HTML 結構
  const VENDOR_ENABLED = {
    daijia: false
  };
  document.querySelectorAll('[data-vendor-toggle]').forEach(el => {
    if (VENDOR_ENABLED[el.dataset.vendorToggle] === false) el.style.display = 'none';
  });

  // --- PDF Catalog Modal（單一檔案：大嘉衣業外部 PDF、丹露/創冠單張型錄圖）---
  window.openPdfCatalog = function(url, title) {
    const modal = document.getElementById('catalogPdfModal');
    const frame = document.getElementById('pdfFrame');
    const titleEl = document.getElementById('pdfModalTitle');
    const dlLink = document.getElementById('pdfDownloadLink');
    const fallbackLink = document.getElementById('pdfFallbackLink');
    const fallback = document.getElementById('pdfFallback');

    document.getElementById('galleryViewer').style.display = 'none';
    frame.style.display = 'block';
    dlLink.style.display = '';

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

  // --- 多頁型錄瀏覽（富雷克/瑋瑋服飾/萬宇：PDF 拆頁壓縮成的 webp 圖片組）---
  // basePath 底下依 scripts/extract_catalog_pdfs.py 的輸出命名規則排好 page-01.webp ~ page-NN.webp
  window.catalogPages = function(basePath, count) {
    const list = [];
    for (let i = 1; i <= count; i++) {
      list.push(basePath + '/page-' + String(i).padStart(2, '0') + '.webp');
    }
    return list;
  };

  let galleryPages = [];
  let galleryIndex = 0;

  function renderGalleryPage() {
    document.getElementById('galleryImg').src = galleryPages[galleryIndex];
    document.getElementById('galleryCounter').textContent = (galleryIndex + 1) + ' / ' + galleryPages.length;
    document.getElementById('galleryPrev').disabled = galleryIndex === 0;
    document.getElementById('galleryNext').disabled = galleryIndex === galleryPages.length - 1;
  }

  window.openGalleryCatalog = function(pages, title) {
    const modal = document.getElementById('catalogPdfModal');
    const titleEl = document.getElementById('pdfModalTitle');
    const dlLink = document.getElementById('pdfDownloadLink');

    document.getElementById('pdfFrame').style.display = 'none';
    document.getElementById('pdfFallback').style.display = 'none';
    document.getElementById('galleryViewer').style.display = 'flex';
    dlLink.style.display = 'none';

    titleEl.textContent = title;
    galleryPages = pages;
    galleryIndex = 0;
    renderGalleryPage();
    modal.classList.add('open');
  };

  document.getElementById('galleryPrev')?.addEventListener('click', () => {
    if (galleryIndex > 0) { galleryIndex--; renderGalleryPage(); }
  });
  document.getElementById('galleryNext')?.addEventListener('click', () => {
    if (galleryIndex < galleryPages.length - 1) { galleryIndex++; renderGalleryPage(); }
  });
  document.addEventListener('keydown', (e) => {
    if (!galleryPages.length || !document.getElementById('catalogPdfModal').classList.contains('open')) return;
    if (e.key === 'ArrowLeft') document.getElementById('galleryPrev').click();
    if (e.key === 'ArrowRight') document.getElementById('galleryNext').click();
  });

  window.closePdfCatalog = function() {
    const modal = document.getElementById('catalogPdfModal');
    modal.classList.remove('open');
    document.getElementById('pdfFrame').src = '';
    galleryPages = [];
  };

  document.getElementById('catalogPdfModal')?.addEventListener('click', function(e) {
    if (e.target === this) closePdfCatalog();
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
