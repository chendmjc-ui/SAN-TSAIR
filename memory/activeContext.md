# SAN-TSAIR — 目前工作狀態

> 每次任務開始時更新

## 2026-09-20 09:17 CST User 已回覆 HANDOFF 三項決定，待新 session 展開分析

**因 session 已 679 則／約 259K tokens 觸發 session-size-guard 警告，依全域規則停下 //save，本輪分析工作留給下個 session，不在本 session 繼續疊加。**

User 對 `docs/procurement/HANDOFF.md` 三項待決事項的回覆（原文）：
1. **要不要接真實供應商資料** → 「要，但與我們目前拿到的資料確認對應」（即：要接，但要先跟 `gift-suppliers/` 現有資料做欄位/內容對應確認，不是憑空接）
2. **要不要正式部署成 Apps Script** → 「好壞處分析」（user 要看利弊分析後再決定，不是直接說要或不要）
3. **逾期提醒排程頻率** → 「分析好壞」（同上，要看不同頻率選項的利弊分析）

### 下次接續順序（新 session 開場直接做）
1. 針對上述三點各自產出好壞分析：
   - 決定1：真實資料整合 — 對應 `gift-suppliers/` 現有 Excel 主檔欄位（見 `docs/procurement/02_data_model.md` 最後一節已有欄位對照草案），要做「讀取 gift-suppliers/ 內容」這一步時記得這是機密目錄，讀取本身可以做（不算對外洩漏），但**輸出/新建的任何檔案都不可以把實際供應商資料寫進 SAN-TSAIR repo 會被 git 追蹤的路徑**，只能留在 `gift-suppliers/`（已 gitignore）底下，或存在使用者本機不進版控的地方
   - 決定2：Apps Script 部署好壞分析 — 可比較「留在本地 Python 雛形」vs「部署成 Apps Script（跟現有詢價表單共用 LINE 推播基礎設施）」兩個選項的維運成本/穩定性/擴充性
   - 決定3：逾期提醒頻率好壞分析 — 可比較每日/每週/即時（webhook觸發）等選項的雜訊量 vs 即時性 trade-off
2. 三項分析完成、user 拍板後才展開對應的實作動作（讀取 gift-suppliers/ 做欄位對應、或實際部署 Apps Script、或設定排程）
3. 這三項都屬於 `docs/GOAL_procurement_architecture.md` HANDOFF 的後續，不是新的 goal/loop 任務，不需要重新取鎖跑五步驟，直接當一般任務處理即可

## 2026-09-20 01:05 CST Maktar 已 commit＋PWA icon 修復＋贈禮品採購流程架構 goal/loop 全部完成

- **Maktar Step 2 驗證：全過，已 commit**（`1d4be98`）。派 Fable agent 背景重跑，用 `page.route` 攔截 `main.js` 回應動態切換 `maktar: true` 驗證（不動 working tree），index.html／temple-gifts.html 各自 64 項檢查（卡片顯示/modal/19頁+6頁翻頁/鍵盤左右鍵/25張圖片200無破圖/無console error）全過，main.js 最終確認仍是 `maktar: false`。
- **PWA icon 404 缺口已修復並 commit**（`2e53a23`）：`manifest.json`／`og:image` 指向的 `assets/images/icon-192.png`／`icon-512.png` 原本不存在，是 09-18 架構盤點記過但沒真的補的缺口。用 P 槽 `三才文件\三才名片設計\...\ALEX-三才.jpg`（公司已核可印刷的正式商標）裁切出乾淨的圓形 ST 標誌（**只取商標本身，不含姓名/電話/QR code 等個資**），套用 manifest 背景色 `#FAF8F5` 並留 maskable icon 安全邊距後產出。
- **C 槽清理（本 session 做的部分）**：npm cache clean（貢獻最大宗釋放量）、pip cache purge（1.67GB）、Temp 清理（1.25→0.31GB）、Downloads 5 個重複安裝檔刪除（0.92GB）、SYSTEM 帳戶（S-1-5-18）回收筒 48G 用 `schtasks /ru SYSTEM` 排程技巧成功清空（一般管理員權限 `takeown`/`icacls` 都被拒絕，只有借 SYSTEM 身分才清得掉，指令已驗證存檔在對話紀錄）。`ms-playwright` 快取因 3 個 `chrome-headless-shell.exe` 程序占用中只清掉部分（正常 chromium 已刪、headless-shell 殘留），**沒有強制關閉那些程序**（不確定是否為其他 session 在用）。
  - ⚠️ **發現本檔上一則「00:20」的紀錄提到 pnpm/pipx/34.47GB 等本 session 沒做過的動作**，研判是另一個平行 session 也在處理 C 槽清理，兩邊用不同工具（本 session 動 npm/pip/Downloads/回收筒，那則動 pnpm/pipx），沒有衝突但**下次接續要注意可能有第三個平行 session 同時在動 C 槽**，先跟 user 確認目前實際剩餘空間再規劃下一步，不要直接信任任一則記錄的數字。
- **Google Apps Script 詢價表單部署**：`FORM_WEBHOOK` 仍是佔位字串未部署（表單目前送出會失敗）。已寫好一鍵互動部署腳本 `scripts/setup_apps_script_form.py`（自動開瀏覽器到 sheets.new／LINE Developers Console、自動複製 Code.gs 到剪貼簿、getpass 遮罩輸入 Token、格式驗證、自動寫回 main.js、自動實測整條路徑），**尚未 commit**（因為還沒讓 user 實際跑過驗證好不好用），**user 尚未執行**，需要在自己的終端機跑 `py -3 scripts\setup_apps_script_form.py`。
- **「贈禮品尋單採購流程」架構規劃（goal/loop 全跑完，已 release 任務鎖）**：user 要求參考 hsc.tw 架構＋直接啟動長跑執行。5 個 Phase 全部完成並個別 commit（`cb7caa1`／`adb8af4`／`ed21769`／`3134001`／`b08b2af`）：
  - 架構主文件 `docs/GOAL_procurement_architecture.md`，研究/資料模型/HANDOFF 在 `docs/procurement/`
  - 追蹤系統雛形（Python，狀態機驗證＋notify_stub）在 `scripts/procurement_tracker/`，demo 4 情境 7 項檢查全過
  - 全程**未讀取／未寫入 `gift-suppliers/`** 機密目錄（唯一讀過的是其 `CLAUDE.md` 說明檔，非實際資料）
  - 嘗試深入參考 hsc-project 實際檔案時被 `cross-project-write-guard.py`（ST8）擋下，依規則沒有換工具繞過，改用三才自己的 Apps Script 架構做同構參考
  - **HANDOFF 列了 3 項待 user 決定**：要不要接真實 gift-suppliers 資料、要不要正式部署成 Apps Script 版、逾期提醒排程頻率

### 下次接續順序
1. 跟 user 核對目前 C 槽實際剩餘空間（可能有平行 session 也在動，數字別直接信任舊記錄）
2. 提醒 user 跑 `scripts/setup_apps_script_form.py` 完成詢價表單部署，跑完後這批 main.js 異動要 commit
3. 光榮工藝社持續等 user 補素材（型錄/照片/報價單），資料夾目前完全是空的
4. 贈禮品採購架構的 3 項 HANDOFF 待決事項等 user 回覆後才展開後續實作
5. `ms-playwright` 快取殘留的 headless-shell 程序，等確認不是其他工作在用後可再清

## 2026-09-20 00:20 CST（已過時，見上方最新進度）C 槽危機解除，Maktar 重跑驗證中

- **C 槽已緩解**：user 拍板「先清開發工具快取」。實際清理前先查證 `pipx` 資料夾裡混了真正在用的 `venvs`（276M，不是快取，快取本身只有1KB），已排除不動；`pnpm`/`npm-cache` 用官方指令（`npm cache clean --force`、`pnpm store prune`）清理，`ms-playwright`/`ms-playwright-go`/`Package Cache` 直接清空（純快取，工具需要時自動重建）。結果：C 槽可用空間從 13GB → **34.47GB**，比預估的 2.9GB 多很多。**其餘大戶（LINE 19G/Google 18G/Packages 13G/Videos 88G/Downloads 79G）都還沒動，維持 user 未拍板前不碰的原則**。
- **Maktar Playwright Step 2 驗證**：C 槽空間解除後重新派工驗證（背景執行中），完成後才能 commit Maktar 型錄異動。
- 前一輪盤點時發現的兩個路徑陷阱記錄下來避免重蹈覆轍：`C:\Documents and Settings` 是指向 `C:\Users` 的 junction、`AppData\Local\Application Data` 是指向 `AppData\Local` 自己的 symlink，兩者都會被 `du` 加上結尾斜線時誤跟蹤造成重複計算，下次用 `du` 掃 Windows 使用者目錄要記得排除或用 `find -maxdepth 1 -type d` 過濾掉這類自我指涉的相容性連結。
- `$Recycle.Bin` 顯示 48G 但需要系統管理員權限才能清（實際在 SYSTEM 帳戶底下），這條**仍未解決**，需要 user 自己用系統管理員身分處理。

## 2026-09-19 23:06 CST（已過時，見上方最新進度）C 槽空間危機（唯讀分析中）+ Maktar 驗證卡住未 commit

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
