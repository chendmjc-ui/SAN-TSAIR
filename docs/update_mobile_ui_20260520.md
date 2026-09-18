# 三才實業專案 — 手機版 UI 優化更新紀錄
> 建立日期：2026-05-20 15:51

## 🔄 更新摘要
本次更動主要針對手機版介面（Mobile UI）進行細節優化，提升在小螢幕設備上的閱讀性與操作體驗，並確保跑馬燈、標題與懸浮按鈕的視覺正確性。

## 🛠️ 修正數量與位置 (總計 3 處)

1. **`assets/css/style.css` (跑馬燈漸層遮罩與標題斷詞)**
   * **位置**：`.marquee-bar` 與 `.section-title`。
   * **修正內容**：為跑馬燈外層增加左右邊緣的漸層消失遮罩（`::before` / `::after`），使其滾動時視覺更柔和。並為區塊標題加入 `word-break: keep-all;`，避免中文字元在邊緣被不自然截斷。

2. **`assets/css/style.css` (懸浮按鈕與防遮擋 Padding)**
   * **位置**：`@media(max-width:768px)` 媒體查詢中的 `body` 與 `.floating-btn`。
   * **修正內容**：調整了 `.floating-btn` 的 `bottom` 與 `right` 距離至 16px，並在 `body` 底部加上 `padding-bottom: 80px`，徹底解決了手機版懸浮「免費詢價」按鈕可能遮擋頁尾或內容的問題。

3. **`assets/css/style.css` (Hero 區塊按鈕滿版)**
   * **位置**：`@media(max-width:480px)` 與 `@media(max-width:375px)`。
   * **修正內容**：整理並統一按鈕的排版，在 480px 以下即套用 `width: 100%` 與 `flex-direction: column` 加 `gap: 12px`，讓按鈕具備一致的滿版寬度且不再擁擠。

---

## 📈 AEOSCAN.tw 檢測結果
*   **檢測時間**：2026-05-20 15:51
*   **總得分**：55 / 55 分 (100.0%)
*   **結論**：UI 修改未破壞原有的 AEO 架構與 PWA 設定，滿分通過，可放心發布。
