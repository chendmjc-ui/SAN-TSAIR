# SAN-TSAIR — 目前工作狀態

> 每次任務開始時更新

## 2026-09-19 23:06 CST C 槽空間危機（唯讀分析中）+ Maktar 驗證卡住未 commit

- **背景**：延續 09-18 的 1-5 待辦，繼續處理時 Maktar Playwright 驗證撞到磁碟寫入失敗，查出 C 槽已逼近滿載，中途插入緊急磁碟盤點，尚未收尾。
- **C 槽危機**：918G/931G 已用（99%），僅剩 13GB。已完成唯讀掃描（**全程沒刪除任何檔案**）：
  - `Documents and Settings` 顯示 685G 其實是指向 `C:\Users` 的系統相容性 junction，`du` 誤跟導致重複計算，非額外佔用，已排除誤判。
  - `C:\Users\pc` 670G 為大宗：`projects/` 278G、`AppData/` 116G、`Videos/` 88G、`Downloads/` 79G、`Documents/` 75G、`Desktop/` 20G。
  - `$Recycle.Bin` 顯示 48G，但使用者自己帳號（SID 尾碼 -1000）的回收筒只有 65KB，那 48G 其實在 **SYSTEM 帳戶**（S-1-5-18）底下，`Clear-RecycleBin` 與 COM Shell 方法都因目前 PowerShell session 非系統管理員身分而清不到，**這條路卡住，需要 user 用系統管理員身分手動處理**。
  - `Downloads/` 79G 已細看：約 4GB 是重複安裝檔（NVMS Lite×2／pdfgear_setup×2／VSCodeUserSetup×2／DiscordSetup×2／印表機驅動程式資料夾+zip重複等），低風險可刪；`Video/`28G、`Compressed/`27G 需 user 自己看內容判斷；東茂易拉展海報.pdf、RT授課檔等業務文件不建議動。
  - `AppData/` 116G 的 Local/Roaming 子資料夾細部排行掃描（背景任務 ID `btanc1eme`）啟動後被 `//save` 指令中斷，**結果尚未讀取**，下次接續先看該任務輸出檔（session 若已結束此暫存路徑可能失效，需要重新跑一次 `du`）。
  - user 目前只拍板「先清空回收筒」，但因權限問題卡住；其餘項目（Downloads 低風險安裝檔、AppData 快取）都還沒問過 user 要不要刪。
- **Maktar 型錄**：HTML/JS/webp 圖檔都已做完但**尚未 commit**（`git status` 顯示 `assets/js/main.js`／`index.html`／`temple-gifts.html` modified + `assets/images/catalog/maktar/`、`scripts/extract_maktar_catalog.py` 未追蹤）。`VENDOR_ENABLED.maktar = false`（關閉狀態）。Playwright **Step 1（預設隱藏）已通過**；**Step 2（開啟後 modal／翻頁／圖片載入）因磁碟空間不足中斷未完成**——main.js 已確認沒有殘留任何測試改動。**建議 C 槽空間問題緩解後重跑 Step 2，通過才 commit**，不要在驗證不完整的狀態下進版控。

### 下次接續順序
1. 重跑或讀取 AppData 掃描結果，彙整完整 C 槽清理清單給 user 逐項拍板（哪些刪、哪些留）
2. C 槽空出足夠空間後，重跑 Maktar Playwright Step 2 驗證（開啟開關→點卡片→查 modal/頁碼/圖片載入→改回關閉）
3. Step 2 通過後才 commit Maktar 型錄異動
4. 光榮工藝社持續等 user 補素材（型錄/照片/報價單），資料夾目前完全是空的
5. Google Apps Script 部署仍等 user 本人操作（見 `docs/apps_script_form_setup.md`）

## 2026-09-18 17:10 CST 第一批 commit 完成 + Maktar 上架（關閉中）

- **已 commit**（`40b724f`，未 push）：型錄架構重建全部異動一次性進版控，351 檔案，git status 已確認 config/ 與測試腳本內都只有佔位符沒有真實密鑰。
- **待決事項 2（Maktar）已拍板**：user 選「先做但關閉（推薦）」。已從 `P:\@三才WEB\2-廠商要先看三才網頁才決定是否能使用資料\同意-但要先看三才網站\Maktar--Qubii Duo手機自動備份\` 取素材，寫 `scripts/extract_maktar_catalog.py` 拆頁（企業產品型錄19頁、Sales Kit 6頁）輸出到 `assets/images/catalog/maktar/`，`index.html`+`temple-gifts.html` 同步加上 Maktar supplier-block（`data-vendor-toggle="maktar"`），`main.js` `VENDOR_ENABLED.maktar = false`（比照大嘉衣業模式，取得書面同意後改 true 即可上架）。Playwright 驗證跑在背景（驗證開關隱藏/顯示+多頁瀏覽器功能），結果待補。**這批異動尚未 commit**。
- **待決事項 4（光榮工藝社）已問過 user**：user 選「要上架的品牌型錄」，但實地查證 `P:\@三才WEB\@詢問廠商意見中\光榮工藝社\` 資料夾**完全是空的**（0 檔案），連一張圖片都沒有——沒辦法憑空生內容，**需 user 補素材**（型錄/照片/報價單等）才能繼續開發，本次先跳過不擋其他項目。
- Maktar 報價單 PDF（`Maktar 報價單 三才實業有限公司.pdf`）確認**未採用**，遵守「網站嚴禁公開物件價格」規則。

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
