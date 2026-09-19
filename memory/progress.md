# SAN-TSAIR — 進度記錄

> 每次任務開始時更新

## 2026-09-20
- C 槽危機解除（SYSTEM 回收筒用 schtasks/SYSTEM 身分技巧清空、npm/pip 快取、Downloads 重複檔）
- Maktar Step 2 Playwright 驗證 64 項全過，已 commit（1d4be98）
- 補上 PWA icon 404 缺口（用公司正式商標裁切製作），已 commit（2e53a23）
- 寫好 Google Apps Script 一鍵部署互動腳本（scripts/setup_apps_script_form.py），等 user 執行
- 「贈禮品尋單採購流程」架構規劃 goal/loop 全 5 Phase 完成並個別 commit，全程未碰 gift-suppliers/ 機密資料，HANDOFF 列 3 項待 user 決定

## 2026-09-19
- 09-18 待辦 1-5 續辦：commit（40b724f）已完成、Maktar 已拍板「先做但關閉」並完成開發、光榮工藝社已問過 user 但資料夾確認全空需補素材
- Maktar Playwright 驗證中途撞到 C 槽磁碟寫入失敗（ENOSPC），查出 C 槽 918G/931G 已用僅剩 13GB，緊急插入唯讀磁碟盤點（未刪除任何檔案，詳見 activeContext.md）
- 查出 `$Recycle.Bin` 顯示的 48G 其實在 SYSTEM 帳戶底下需要系統管理員權限才能清，一般權限清不到
- Downloads/AppData 大宗佔用細部排行已掃一半（AppData 子項掃描被 //save 中斷），C 槽清理清單尚未收斂完成
- Maktar 型錄異動因 Playwright Step 2 未驗證完成，故意先不 commit

## 2026-09-18
- 完成現有網站架構全面盤點（詳見 activeContext.md）
- 詢價表單從 n8n webhook 改接 Google Apps Script（程式碼完成，部署待 user 操作）
- 品牌型錄從假資料全面換成 `P:\@三才WEB\@三才WEB.xlsx` 追蹤表裡真實已同意廠商資料
- 型錄改分兩類：服飾・制服系列（大嘉衣業[關]/富雷克/瑋瑋服飾/萬宇）、企業禮贈品系列（丹露實業/創冠UNAVI）
- 服飾類 7 支制服 PDF 型錄（原177MB）拆頁壓縮成 webp（19MB），modal 加多頁翻頁器，Playwright 實測通過
- 確立「網站嚴禁公開物件價格/批發報價」規則，存入 auto-memory
- 下一步：Apps Script 部署收尾 → Maktar/光榮工藝社狀態由 user 決定 → 全部 review 後一次 commit
