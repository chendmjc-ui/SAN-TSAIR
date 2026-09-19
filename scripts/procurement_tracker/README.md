# 贈禮品尋單採購流程 — 追蹤系統雛形

架構文件見 `docs/GOAL_procurement_architecture.md` 與 `docs/procurement/`。本資料夾是可運作
的雛形程式碼，用來驗證資料模型與狀態機設計（`docs/procurement/02_data_model.md`）是否可行。

## 檔案

| 檔案 | 用途 |
|---|---|
| `tracker.py` | 核心邏輯：`Store`（JSON 讀寫）、狀態機驗證、`notify_stub()` 通知函式 |
| `run_demo.py` | Phase 4 驗證腳本，用虛構資料跑過 4 個情境（正常流程/淘汰/非法轉換擋下/逾期偵測） |
| `demo_data.json` | 跑 `run_demo.py` 後產生，**全部是虛構資料**，可隨時刪除重跑 |

## 跑法

```
py -3 scripts\procurement_tracker\run_demo.py
```

## 目前是雛形，正式上線前要做的事（HANDOFF 待辦）

1. **`notify_stub()` 換成真的 LINE 推播**：比照 `config/google-apps-script/Code.gs` 的
   `notifyLine_()` 寫法，或是把整支 `tracker.py` 的邏輯搬到一支新的 Apps Script（例如
   `config/google-apps-script/ProcurementTracker.gs`），改用 Google Sheet 當資料庫，
   跟現有詢價表單共用同一個 LINE Channel Access Token。
2. **真實資料匯入**：`gift-suppliers/` 底下的 Excel 主檔要不要、以及怎麼匯入這套系統，
   欄位已經在 `docs/procurement/02_data_model.md` 對齊好了，但**這步涉及機密資料**，
   需要你本人決定整合方式（例如：是否要做一個需要登入的私有頁面、資料放哪裡），
   不是 Claude 可以自行決定的範圍。
3. **逾期偵測要排程觸發**：`check_overdue()` 目前要手動呼叫，正式上線需要一個排程
   （Apps Script 的 time-driven trigger，或 Windows Task Scheduler 跑 Python 版）
   每天自動跑一次。
