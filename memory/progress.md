# SAN-TSAIR — 進度記錄

> 每次任務開始時更新

## 2026-09-18
- 完成現有網站架構全面盤點（詳見 activeContext.md）
- 詢價表單從 n8n webhook 改接 Google Apps Script（程式碼完成，部署待 user 操作）
- 品牌型錄從假資料全面換成 `P:\@三才WEB\@三才WEB.xlsx` 追蹤表裡真實已同意廠商資料
- 型錄改分兩類：服飾・制服系列（大嘉衣業[關]/富雷克/瑋瑋服飾/萬宇）、企業禮贈品系列（丹露實業/創冠UNAVI）
- 服飾類 7 支制服 PDF 型錄（原177MB）拆頁壓縮成 webp（19MB），modal 加多頁翻頁器，Playwright 實測通過
- 確立「網站嚴禁公開物件價格/批發報價」規則，存入 auto-memory
- 下一步：Apps Script 部署收尾 → Maktar/光榮工藝社狀態由 user 決定 → 全部 review 後一次 commit
