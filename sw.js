// ============================
// 三才實業 — Service Worker（PWA 離線快取）
// ============================
// 快取版本：改到快取策略、或需要強制所有訪客清掉舊快取時升版。
// v3（2026-09-23）：改為 network-first。舊版 stale-while-revalidate 會讓回頭訪客在每次部署後
//   「第一次載入仍拿到上一版 main.js / index.html」（新版要第二次開才生效），?cat= 這類新功能
//   會被當成沒反應；型錄圖同理——丹露 09-21 下架前含售價的四張圖去識別化後檔名沒換，
//   回頭訪客快取裡仍是舊圖。升版後 activate 會把舊快取整批刪掉。
// 同名換圖（檔名不變、內容改了）時記得同步升 MEDIA_CACHE 版號，否則回頭訪客會先看到舊圖一次。
const CACHE_NAME = 'santsair-v3';
const MEDIA_CACHE = 'santsair-media-v3';
const PRECACHE = [
  './',
  './index.html',
  './temple-gifts.html',
  './assets/css/style.min.css',
  './assets/js/main.js',
  './manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME && k !== MEDIA_CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// 只接手同源 GET；Google Fonts / wikimedia LINE logo 等跨網域請求交給瀏覽器自己處理。
// 舊版三個 fetch listener 對同一個 request 重複呼叫 respondWith 會丟 InvalidStateError，合併成一個。
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  const isMedia = /\.(png|jpe?g|webp|svg|pdf)$/i.test(url.pathname);
  e.respondWith(isMedia ? staleWhileRevalidate(req, MEDIA_CACHE) : networkFirst(req, CACHE_NAME));
});

// HTML / JS / CSS / JSON：先抓網路（部署後立刻生效），斷線才退回快取
async function networkFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const res = await fetch(req);
    if (res && res.status === 200) cache.put(req, res.clone());
    return res;
  } catch (err) {
    // ignoreSearch：離線時 ./?cat=gift 也能對到快取裡的 ./
    const cached = await cache.match(req, { ignoreSearch: true });
    if (cached) return cached;
    if (req.mode === 'navigate') {
      const index = await cache.match('./index.html');
      if (index) return index;
    }
    throw err;
  }
}

// 圖片 / PDF：型錄多頁 webp 量大，先回快取再背景更新
async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const network = fetch(req).then(res => {
    if (res && res.status === 200) cache.put(req, res.clone());
    return res;
  }).catch(() => null);
  return cached || network;
}
