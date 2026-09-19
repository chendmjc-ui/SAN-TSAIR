# HANDOFF — 贈禮品尋單採購流程架構

> 完成日期：2026-09-20
> 對應 `docs/GOAL_procurement_architecture.md` 全部 5 個 Phase

## 完成的 Phase

| Phase | 狀態 | 主要交付物 |
|---|---|---|
| 1. 架構研究與需求定義 | ✅ | `docs/procurement/01_research.md` |
| 2. 資料模型與狀態機設計 | ✅ | `docs/procurement/02_data_model.md` |
| 3. 追蹤系統雛形建置 | ✅ | `scripts/procurement_tracker/{tracker.py,README.md}` |
| 4. Demo 驗證 | ✅ | `scripts/procurement_tracker/run_demo.py` + `demo_data.json`（4 情境 7 項檢查全過）|
| 5. Final Review & HANDOFF | ✅ | 本檔 |

## 機密邊界確認

全程**未讀取、未寫入** `gift-suppliers/` 目錄。唯一「參考」是讀取其 `CLAUDE.md` 說明檔
（非機密內容本身，僅記載欄位名稱與流程說明），用來讓 Phase 2 的資料模型欄位命名可以
跟現有 Excel 主檔對齊，沒有引用任何實際供應商名稱、報價數字或聯絡窗口。

## 這次做了什麼（一句話）

參考 hsc-project 的多階段自跑架構 + 三才自己剛完成的 Apps Script 表單通知模式 +
型錄分類組織原則，設計出一套「供應商/報價/採購單」三實體 + 狀態機的架構，並用
虛構資料寫了一支可運作的 Python 雛形驗證整個設計可行。

## 待你決定的事項（這是本次 goal/loop 刻意停下、不自行決定的範圍）

1. **要不要真的把 `gift-suppliers/` 的真實資料接進來？**
   欄位已經對齊好了（見 `docs/procurement/02_data_model.md` 最後一節），但實際整合方式
   （做成需要登入的私有頁面？留在 Excel + 只是加自動提醒？）需要你決定，這涉及機密
   資料存放位置的判斷，不是 Claude 該自行拍板的範圍。
2. **要不要正式部署成 Apps Script 版本？**
   目前雛形是本地 Python，`README.md` 已經寫好怎麼比照 `config/google-apps-script/Code.gs`
   改寫成真正會推播 LINE 通知的版本，需要你本人操作部署（同一套帳號授權模式）。
3. **逾期提醒要多久跑一次？**
   雛形的 `check_overdue()` 要手動呼叫，正式上線需要排程（Apps Script time-driven
   trigger 或 Task Scheduler），頻率（每天一次？每小時？）由你決定。

## 參考限制說明

原計畫參考 hsc-project 網站程式碼的「LINE bot + 表單」細節，實際執行時嘗試用 Bash 瀏覽
`hsc-project/reports/outreach_drafts_20260525/` 被跨專案防呆機制擋下（ST8），依 Stop
Criteria 規則沒有嘗試換工具繞過，改用三才自己已完成的同構架構（Apps Script + Sheet +
LINE）作為參考基礎，效果等價。若之後想直接參考 hsc-project 實際檔案，需要在該視窗打
`//jump hsc-project` 取得跨專案讀取授權。

## 下個 session 接續 Prompt（若有需要）

```
讀完 c:\Users\pc\projects\SAN-TSAIR\docs\GOAL_procurement_architecture.md 與本 HANDOFF，
Phase 1-5 已全部完成。若 user 對上述 3 個待決事項有回覆，依回覆內容展開後續實作；
若沒有新指示，這個任務目前是完成狀態，等 user 主動提起。
```

## 資產清單

| 資產 | 路徑 |
|---|---|
| 架構主文件 | `docs/GOAL_procurement_architecture.md` |
| 研究文件 | `docs/procurement/01_research.md` |
| 資料模型 | `docs/procurement/02_data_model.md` |
| 追蹤系統雛形 | `scripts/procurement_tracker/` |
| 本檔 | `docs/procurement/HANDOFF.md` |
