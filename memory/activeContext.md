# SAN-TSAIR — 目前工作狀態

> 每次任務開始時更新

## 2026-09-18 型錄架構重建（服飾已完成一段落，禮品部分待決）

### 已完成
- **架構分析**：盤點現有靜態站架構（GitHub Pages + PWA + n8n webhook），發現 `assets/images/` 空資料夾（PWA icon / og:image 404）、`style.min.css` 手動同步易脫鉤兩個風險，`style.min.css` 已補上重新同步機制。
- **詢價表單改用 Google Apps Script**：取代不穩定的自架 n8n（GCP VM 曾出現連線被拒事故）。程式碼 `config/google-apps-script/Code.gs`，前端 `assets/js/main.js` 的 `FORM_WEBHOOK` 常數待填入實際部署網址（部署步驟見 `docs/apps_script_form_setup.md`），**這步還沒完成**，需要 user 本人操作 Google/LINE 帳號後把 `/exec` 網址回填。
- **型錄資料源**：`P:\@三才WEB\@三才WEB.xlsx` 是廠商同意使用資料的正式追蹤表，對應實體資料夾（1-同意/2-需先看網站/3-不同意/@詢問中）。發現原網站「品牌型錄」內容是**完全虛構的假資料**（大嘉衣業四品牌 + weiwi/goorik 假商品），且大嘉衣業同意狀態其實還在「詢問中」，已修正。
- **型錄改分類架構**：`#catalog` 區塊拆成「服飾・制服系列」「企業禮贈品系列」兩組（index.html + temple-gifts.html 同步）。
- **大嘉衣業開關機制**：`main.js` 的 `VENDOR_ENABLED.daijia = false`，目前隱藏；取得書面同意後改 `true` 即可上架，不用動 HTML。
- **服飾類全部上架**：富雷克（Diaox No.3/no.17 UK/no.33百達，38+30+54頁）、瑋瑋服飾（2025秋冬68頁/2026春夏64頁）、萬宇（2026夏季上27頁/下19頁）——原始 PDF 共177MB，用 `scripts/extract_catalog_pdfs.py` 整頁渲染+webp壓縮（1100px寬/quality72）降到19MB（含丹露/創冠），型錄 modal 加了多頁瀏覽器（上一頁/下一頁+鍵盤左右鍵+頁碼），已用 Playwright 實測翻頁功能與畫面正常。
- **禮贈品類已上架**：丹露實業（4款）、創冠UNAVI（1款，無線充電器）。

### 待決事項（下次接續／需 user 決定）
1. **Google Apps Script 部署未完成**：需 user 操作 Google Sheet + Apps Script 部署 + LINE Channel Token，見 `docs/apps_script_form_setup.md`，完成後把 `/exec` 網址回填 `main.js` 的 `FORM_WEBHOOK`。
2. **Maktar Qubii Duo**：廠商狀態「已同意但要先看三才網站再決定」，素材齊全（型錄/Sales Kit/5張照片/報價單），可考慮先做好但關閉（比照大嘉衣業開關模式），等對方看過網站回覆同意後開啟——**需 user 決定要不要先做**。
3. **DAQI Concept／善良 Kindmade**：都還沒同意，素材不齊（DAQI 只有詢價信、善良有報價單+3張照片），**不用主動處理**，等對方明確同意再回來做。
4. **光榮工藝社**：資料夾完全空的，連分類都看不出來（制服還是禮品），**需 user 說明這家的用途／類別**，可能是匾額/獎牌原料供應商而非要公開展示的品牌型錄。
5. **創冠 UNAVI 可選擴充**：還有一支產品影片 + 一張較大張產品圖沒用到（非必要，user 未要求）。

### 重要規則（已存 auto-memory）
**網站任何內容嚴禁出現物件價格，尤其廠商批發報價**（MOQ分級價/樣品價等）。創冠UNAVI的報價單PDF因含批發定價已刻意不採用。詳見 auto-memory `feedback_no_pricing_public.md`。

### 尚未 commit
本次所有異動（含之前搬移的目錄整理）都還沒 commit，git status 顯示大量 modified/untracked，下次接續前建議先 review diff 再一次性 commit。
