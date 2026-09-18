# 三才實業專案 — LINE Messaging API (官方帳號) 整合計畫
> 建立日期：2026-05-27 11:15

## 🎯 升級動機與差異比較
目前網站詢價表單預設規劃使用的是 **LINE Notify**（單純的純文字推播）。若要升級至 **LINE Messaging API**（LINE 官方帳號 API），主要優勢如下：
1. **版面更專業**：支援 **Flex Message**，可排版出精美的卡片式訊息（如：粗體標題、雙欄位排版、自訂顏色），不再是生硬的純文字。
2. **雙向互動**：未來可加入快速回覆按鈕（如：「直接回電給客戶」、「回覆已收到」）。
3. **品牌形象**：通知來源會是「三才實業官方帳號」，而非預設的「LINE Notify」機器人。

---

## 🛠️ 第一階段：LINE Developer 後台設定
要啟用 Messaging API，您需要自行（或授權工程師）完成以下前置作業：
1. 前往 [LINE Developers Console](https://developers.line.biz/) 登入。
2. 建立 Provider（如：三才實業），並新增一個 **Messaging API Channel**。
3. 取得兩項關鍵金鑰：
   * **Channel Access Token (Long-lived)**：用於發送 API 請求的通行證。
   * **Your User ID**：位於 Channel 基本設定的最下方（以 `U` 開頭），用於指定「通知要發送給哪位管理員」。
4. 關閉「自動回覆訊息」設定，避免機器人隨機亂回話。

---

## 🚀 第二階段：n8n 邏輯升級與實作
我們已為您將原本的 LINE Notify 節點替換為 **LINE Messaging API (HTTP Request)**。

### ✅ 已建立的 n8n 工作流檔案：`n8n_line_messaging_api_workflow.json`
* **使用方式**：直接在您的 n8n 畫面中點選 `Import from File` 匯入該檔案。
* **底層邏輯檢測**：
  * **Webhook 節點**：接收來自 `index.html` 的 JSON Payload。
  * **HTTP Request 節點**：
    * Method：`POST`
    * URL：`https://api.line.me/v2/bot/message/push`
    * Headers：設定 `Authorization: Bearer YOUR_TOKEN`
    * Body：使用 JSON 格式編寫了精美的 Flex Message，自動將表單的 `{{$json.body.name}}`、`{{$json.body.phone}}` 嵌入卡片欄位中。

---

## 🧪 第三階段：自動化測試腳本
為了確認底層邏輯與金鑰無誤，已為您準備了專屬的 Python 測試環境腳本：`test_line_messaging_api.py`。

### 測試步驟：
1. 打開 `test_line_messaging_api.py`。
2. 將第 7 行的 `YOUR_CHANNEL_ACCESS_TOKEN` 替換為您的真實 Token。
3. 將第 8 行的 `YOUR_USER_ID` 替換為您的管理員 ID。
4. 在終端機執行：`py test_line_messaging_api.py`。
5. **成功結果**：您的手機 LINE 將會立即收到一張排版精美的「🏆 新詢價單通知」Flex Message 卡片。

---

## 📈 系統防呆與資安規範
* **反 AI 偵測與 SEO**：此計畫全數在後端 (n8n/Python) 與 Server-side 執行，前端原始碼依然保持輕量且不會洩漏任何 API Key，對 AEO/SEO 檢測沒有任何負面影響。
* **交接紀錄**：此計畫已被完整獨立記錄，後續只需將 Token 安全置入 n8n credentials 中即可正式上線。
