# 詢價表單新架構 — Google Apps Script 部署步驟

> 建立日期：2026-09-18
> 取代對象：原本自架在 GCP VM 上的 n8n webhook（`docs/gcp_debug_refused.md` 記錄過連線不穩事故），
> 改用 Google 代管、免維運的 Apps Script + Google Sheet + LINE Messaging API。
> Apps Script 程式碼放在 `config/google-apps-script/Code.gs`，前端已改指向 `FORM_WEBHOOK`
> （見 `assets/js/main.js`），部署完成後把實際網址回填即可。

## 這一步需要 Alex 親自操作的原因

Apps Script 專案綁定在您自己的 Google 帳號底下，且 LINE Channel Access Token 屬於機密憑證，
不能透過對話明文傳遞或寫進 repo，所以這幾步需要您本人在瀏覽器完成。其餘（改網站程式碼）已經做完。

## 步驟

### 1. 建立 Google Sheet 並掛上 Apps Script
1. 開一份新的 Google 試算表（sheets.new）。
2. 選單「擴充功能 Extensions」→「Apps Script」，會開一個新分頁的編輯器。
3. 把 `config/google-apps-script/Code.gs` 的內容整段貼進去，取代編輯器裡預設的內容，儲存。

### 2. 取得 LINE Channel Access Token 與 User ID
若尚未建立過 LINE Messaging API channel，照 `docs/line_messaging_api_plan.md` 第一階段的步驟：
1. 前往 [LINE Developers Console](https://developers.line.biz/) 登入。
2. 建立 Provider（如「三才實業」）+ 新增一個 Messaging API Channel。
3. Basic settings 頁面最下方可以拿到：
   - **Channel Access Token (long-lived)**：需自行「Issue」產生。
   - **Your user ID**：頁面本身會顯示您（開發者本人）的 LINE User ID，用來當推播對象。
4. 用自己的 LINE 掃這個 Channel 的 QR Code，加它為好友（沒加好友收不到推播）。
5. 建議關閉「自動回應訊息」與「歡迎訊息」，避免機器人亂回。

### 3. 把 Token 填進 Apps Script（不要貼在對話或程式碼裡）
回到 Apps Script 編輯器：
1. 左側齒輪圖示「專案設定 Project Settings」。
2. 捲到「Script Properties」→「Add script property」，新增兩筆：
   - `LINE_CHANNEL_ACCESS_TOKEN` = 剛剛拿到的 Token
   - `LINE_USER_ID` = 剛剛拿到的 User ID

### 4. 部署成 Web App
1. 編輯器右上角「Deploy」→「New deployment」。
2. 類型選「Web app」。
3. Execute as：**Me**；Who has access：**Anyone**。
4. 按「Deploy」，會跳出授權畫面，允許存取（這是您自己的 Google 帳號授權自己的腳本，安全）。
5. 複製產生的網址（結尾是 `/exec`）。

### 5. 回填網址
把第 4 步拿到的 `/exec` 網址貼回給 Claude，會自動更新 `assets/js/main.js` 裡的
`FORM_WEBHOOK` 常數，並在瀏覽器實測一次表單送出流程（含 Google Sheet 有沒有寫入新的一列、
LINE 有沒有收到推播）確認整條路徑通了才算完成。

## 之後可選：淘汰舊的 n8n VM
新架構穩定運作幾天沒問題後，可以考慮把 GCP 上那台 n8n VM 關掉省成本；
這次先不動它，降低一次改動的風險範圍。
