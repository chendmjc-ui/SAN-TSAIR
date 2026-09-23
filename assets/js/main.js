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
      const unitPrice = document.getElementById('unitPrice')?.value || '';
      const totalBudget = document.getElementById('totalBudget')?.value || '';
      const deadline = document.getElementById('deadline')?.value || '';
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
          body: JSON.stringify({ name, phone, service, qty, unitPrice, totalBudget, deadline, msg, time: new Date().toISOString() })
        });
        sent = res.ok;
      } catch (err) {
        console.error('詢價單傳送失敗:', err);
      }

      // 本機備用記錄（無論是否送達都保留，方便排查）
      const records = JSON.parse(localStorage.getItem('santsair_inquiries') || '[]');
      records.push({ name, phone, service, qty, unitPrice, totalBudget, deadline, msg, time: new Date().toISOString(), sent });
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
  // BIGHOME：同意狀態確認中（詳見 P:\@三才WEB\@三才WEB.xlsx），暫時下架；
  // Maktar：已同意但要先看三才網站再決定，先做好素材保持關閉；
  // 獎牌：尚未取得廠商同意、無實際素材，先放類別示意圖佔位保持關閉；
  // DANRO：2026-09-21 緊急下架——型錄圖（Oichan/Danro/HAPADO/KUKKAR）印有實際
  //   售價與「N只/箱」批發包裝量，違反網站嚴禁公開物件價格規則，待去識別化/改用
  //   無價格版素材後才能重新開啟；
  // 取得書面同意（或素材修正）後把對應開關改成 true 即可重新上架，不用改 HTML 結構
  const VENDOR_ENABLED = {
    daijia: false,
    maktar: false,
    guangrong: false,
    danlu: true
  };
  document.querySelectorAll('[data-vendor-toggle]').forEach(el => {
    if (VENDOR_ENABLED[el.dataset.vendorToggle] === false) el.style.display = 'none';
  });

  // --- PDF Catalog Modal（單一檔案：BIGHOME外部 PDF、DANRO/UNAVI單張型錄圖）---
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

  // --- 多頁型錄瀏覽（PADER PHALIPE/Paul Sailing/Pro Dormy：PDF 拆頁壓縮成的 webp 圖片組）---
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

  // --- LINE 直接呼叫 App（桌面/手機皆先試 line:// 協定，1.2秒沒反應才退回網頁版QR code）---
  window.openLineApp = function(e, lineId) {
    if (e) e.preventDefault();
    const appUrl = `line://ti/p/${lineId}`;
    const webUrl = `https://line.me/R/ti/p/${lineId}`;
    const leftAt = Date.now();
    window.location.href = appUrl;
    setTimeout(() => {
      if (!document.hidden && Date.now() - leftAt < 2000) {
        window.open(webUrl, '_blank');
      }
    }, 1200);
    return false;
  };

  // --- 「立即詢價」icon：把目前頁面資訊即時帶入 LINE OA 訊息框，小編一眼看出客戶在看哪一頁、附上該頁連結 ---
  window.sendLineInquiry = function(e, lineId) {
    if (e) e.preventDefault();
    const pageLabel = document.title;
    const msg = `您好，我正在看「${pageLabel}」\n${location.href}\n想了解更多資訊，麻煩幫我介紹`;
    const encoded = encodeURIComponent(msg);
    const appUrl = `line://oaMessage/${lineId}/?${encoded}`;
    const webUrl = `https://line.me/R/oaMessage/${lineId}/?${encoded}`;
    const leftAt = Date.now();
    window.location.href = appUrl;
    setTimeout(() => {
      if (!document.hidden && Date.now() - leftAt < 2000) {
        window.open(webUrl, '_blank');
      }
    }, 1200);
    return false;
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

// --- Product Filter（比對 data-category，不比對文字，避免標題改字就篩不到）---
const filterBtns = document.querySelectorAll('.filter-btn');
const productCards = document.querySelectorAll('.product-card');
function applyProductFilter(category) {
  filterBtns.forEach(b => b.classList.toggle('active', b.dataset.filter === category));
  productCards.forEach(card => {
    card.style.display = (category === 'all' || card.dataset.category === category) ? 'block' : 'none';
  });
  updateCatalogHint(category);
}
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => applyProductFilter(btn.dataset.filter));
});

// --- 篩到某分類時，在示意卡上方提示「往下有合作廠商的真實型錄」並直接錨到該系列 ---
// #products 六張卡只是服務項目說明（CTA 都是詢價表單），真正上架的廠商商品在 #catalog；
// LINE 圖文選單 ?cat= 導流進來的客戶若只看到示意卡，不會知道下面還有型錄。
// id 對照 index.html 的 .catalog-category-title；award 目前沒有上架廠商（獎牌關閉中）會自動不顯示
const CATALOG_SECTIONS = {
  gift:    { id: 'catalog-gift',    label: '企業禮贈品系列' },
  uniform: { id: 'catalog-uniform', label: '服飾・制服系列' },
  award:   { id: 'catalog-award',   label: '匾額・獎牌系列' }
};
function updateCatalogHint(category) {
  const hint = document.getElementById('catalogHint');
  if (!hint) return;
  const target = CATALOG_SECTIONS[category];
  const title = target ? document.getElementById(target.id) : null;
  const group = title ? title.nextElementSibling : null;
  // 該系列底下至少要有一個沒被 VENDOR_ENABLED 關掉的廠商區塊，否則提示連過去是空的
  const hasVisible = !!group && Array.from(group.querySelectorAll('.supplier-block'))
    .some(block => block.style.display !== 'none');
  if (!hasVisible) { hint.hidden = true; return; }
  hint.querySelector('a').href = '#' + target.id;
  hint.querySelector('.catalog-hint-label').textContent = target.label;
  hint.hidden = false;
}

// --- 首頁三大 icon 選單：直接篩到對應分類並捲動到商品區，客戶不用逛整頁 ---
window.goToCategory = function(e, category) {
  if (e) e.preventDefault();
  applyProductFilter(category);
  document.getElementById('products')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  return false;
};

// --- 網址帶 ?cat= 參數時，頁面一載入就自動篩選並捲動（給LINE圖文選單/外部廣告連結導流用）---
// item/unitPrice/qty/deadline 對應 LINE Rich Menu 規劃中的細項/單價/數量/交期深連結，
// 有帶這些參數代表客戶在 LINE 端已經選完，直接預填表單並捲到聯絡表單，不用再逛一次型錄
const CATEGORY_ITEM_TO_SERVICE = {
  'gift:corporate': '企業禮贈品',
  'gift:temple': '宮廟宗教禮品',
  'uniform:group': '團體制服',
  'uniform:custom': '訂製服裝',
  'award:plaque': '匾額製作',
  'award:trophy': '獎牌・獎座'
};
(function () {
  // temple-gifts.html 也載這支檔但沒有篩選按鈕、卡片沒有 data-category，跑下去會把卡片全藏掉，直接略過
  if (!filterBtns.length) return;
  const params = new URLSearchParams(location.search);
  const cat = params.get('cat');
  if (!['gift', 'uniform', 'award'].includes(cat)) return;

  const item = params.get('item');
  const serviceValue = CATEGORY_ITEM_TO_SERVICE[`${cat}:${item}`];
  const unitPrice = params.get('unitPrice');
  const totalBudget = params.get('totalBudget');
  const qty = params.get('qty');
  const deadline = params.get('deadline');
  const hasDeepLinkDetail = serviceValue || unitPrice || totalBudget || qty || deadline;

  window.addEventListener('load', () => {
    goToCategory(null, cat);
    if (!hasDeepLinkDetail) return;

    const setIfPresent = (id, value) => {
      const el = document.getElementById(id);
      if (el && value) el.value = value;
    };
    setIfPresent('service', serviceValue);
    setIfPresent('unitPrice', unitPrice);
    setIfPresent('totalBudget', totalBudget);
    setIfPresent('qty', qty);
    setIfPresent('deadline', deadline);

    setTimeout(() => {
      document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 500);
  });
})();
