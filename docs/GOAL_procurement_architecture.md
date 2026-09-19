# /goal — 贈禮品尋單採購流程架構規劃（GOAL_procurement_architecture）

> 建立日期：2026-09-20
> 觸發：user 要求參考 hsc-project（hsc.tw）既有架構模式，規劃三才實業「贈禮品尋單採購流程」，直接啟動 goal/loop 長跑執行。
> 機密邊界：全程不讀取、不寫入 `gift-suppliers/` 目錄下任何實際供應商資料（報價/私人聯絡窗口），該目錄已 gitignore。需要範例資料時一律使用虛構/通用資料，不得引用真實廠商名稱與數字。

## 參考來源與範圍限制說明

原定參考 hsc-project 三個架構模式：
1. **goal-continuous-agent 多階段自跑 SOP** — 已直接沿用本 skill 本身（`C:\Users\pc\.claude\skills\goal-continuous-agent`），這就是 hsc 案例提煉出的架構，直接套用。
2. **LINE bot + 表單 + 後端通知架構** — 沒有深入讀取 hsc-project 內部程式碼（跨專案讀取在嘗試用 Bash 瀏覽 `hsc-project/reports/outreach_drafts_20260525/` 時被 `cross-project-write-guard.py` 擋下，訊息明確要求「不可換其他工具嘗試繞過」，故未再嘗試 Glob/Read 重取同一路徑）。改採本專案（SAN-TSAIR）剛完成的 Google Apps Script 詢價表單架構（`config/google-apps-script/Code.gs`：表單 → Google Sheet 留底 + LINE Messaging API 推播）作為同源參考——這套本身就是仿 hsc 系列 LINE 通知模式在三才落地的版本，結構對等。
3. **網站資訊架構/頁面組織方式** — hsc.tw 是 WordPress 站（見 hsc CLAUDE.md 對 `wp_postmeta`／mu-plugin／snippet 的描述），跟 SAN-TSAIR 純靜態 GitHub Pages 技術棧不同，直接套用程式碼結構意義不大；採用的是「分類驅動的資訊架構」這個抽象原則（依業務線分類、分廠商/分狀態管理），不搬技術細節。

**若之後需要更細緻地參考 hsc-project 實際檔案，需要 user 在該 session 或本 session 手動 `//jump hsc-project` 取得授權後才能讀取，本次先以上述替代方案繼續，不阻塞整個任務。**

---

## 0. Mission Statement

```
讓三才實業在本次 session 內，完成「贈禮品尋單採購流程」架構規劃與可運作雛形：
從純規劃概念 → 資料模型與狀態機設計 → 自動化追蹤/通知腳本雛形（虛構 demo 資料驗證）→ 文件化 HANDOFF。
所有本地規劃/設計/寫程式動作 agent 自動完成；
真實供應商資料整合、對外發信、任何 production 串接一律停下交 user。
```

## 1. Success Criteria

| # | 完成定義 | 量化驗證 |
|---|---|---|
| S1 | 架構研究文件完成，含三個參考模式的落地結論 | `docs/procurement/01_research.md` 存在且非空 |
| S2 | 資料模型 + 狀態機設計完成 | `docs/procurement/02_data_model.md` 存在，含欄位表與狀態圖 |
| S3 | 追蹤系統雛形程式碼完成 | `scripts/procurement_tracker/` 下有可執行腳本 |
| S4 | 用虛構 demo 資料完整跑過一次流程並驗證成功 | demo 執行輸出含成功訊息，且看得出資料寫入/狀態更新 |
| S5 | 全程未觸碰 `gift-suppliers/` 目錄 | `git status -- gift-suppliers/` 無變化 |
| S6 | HANDOFF 完成，列出待 user 決定的整合/部署事項 | `docs/procurement/HANDOFF.md` 存在 |
| S7 | user 確認 HANDOFF | 由 user 標 ✅ |

## 2. Phase 拆解

### Phase 1 — 架構研究與需求定義
- **核心動作**：整理三個參考模式的落地結論（已於本檔前言完成分析）；定義「尋單採購流程」的業務範圍（詢價 → 報價比較 → 樣品 → 決策 → 下單追蹤）
- **產出檔**：`docs/procurement/01_research.md`
- **Self-Eval**：文件涵蓋業務範圍定義 + 三模式結論 + 適用邊界 ✅
- **失敗回滾**：若範圍定義不清，先列 2-3 個候選範圍描述供下一 Phase 選用較窄者
- **預估時長**：10-15 min

### Phase 2 — 資料模型與狀態機設計
- **核心動作**：設計供應商/報價/採購單三個核心實體的欄位結構；設計狀態機（例如：待聯繫→已詢價→已報價→樣品中→決策中→已下單/已淘汰）
- **產出檔**：`docs/procurement/02_data_model.md`（含欄位表、狀態圖、與 `gift-suppliers/` 現有 Excel 欄位對照但不引用其實際內容）
- **Self-Eval**：欄位表完整、狀態機無死路（每個中間狀態都有後續路徑）✅
- **失敗回滾**：狀態機過於複雜時砍到最小可行（5 個狀態以內）
- **預估時長**：15-20 min

### Phase 3 — 追蹤系統雛形建置
- **核心動作**：比照 `config/google-apps-script/Code.gs` 的模式，寫一支獨立的採購追蹤雛形腳本（Google Apps Script 或本地 Python 皆可，擇一即可展示流程），含「新增/更新供應商狀態 → 寫入 Sheet/檔案 → 觸發提醒通知」三段
- **產出檔**：`scripts/procurement_tracker/` 下的程式碼 + README 說明如何接上真實資料
- **Self-Eval**：程式碼可執行（本地 dry-run 或 lint 通過）✅
- **失敗回滾**：若跨系統整合太複雜，先產出「單機版 CLI 工具」雛形，Web/Apps Script 化留給 HANDOFF 待辦
- **預估時長**：20-30 min

### Phase 4 — Demo 驗證
- **核心動作**：用完全虛構的供應商/報價資料（如「示範廠商A」）跑一次完整流程，驗證狀態轉換與通知邏輯正確
- **產出檔**：`scripts/procurement_tracker/demo_data.json`（或等效）+ 執行紀錄
- **Self-Eval**：Demo 執行無錯誤、狀態轉換符合 Phase 2 設計的狀態機 ✅
- **失敗回滾**：邏輯錯誤就地修正，重跑到通過為止（同檔修改不超過 ST5 門檻）
- **預估時長**：10-15 min

### Phase 5 — Final Review & HANDOFF
- **動作**：寫 `docs/procurement/HANDOFF.md`，列出：真實資料整合方式建議（如何在不外洩 `gift-suppliers/` 的前提下對接）、部署建議（若要正式化，需要哪些 user 親自操作的步驟，比照 Apps Script 部署模式）
- **結束標誌**：HANDOFF.md ready + 通知 user

## 3. Self-Loop Protocol

依 `checklists/per_phase_checklist.md` 七步跑，每 Phase 邊界印核彈評分。

## 4. Stop Criteria

沿用 `checklists/stop_criteria.md` 全部七條（ST1-ST7）+ ST8（跨專案防呆 deny）。本任務額外明確：
- **任何要讀取或寫入 `gift-suppliers/` 目錄內容的衝動 → 視同觸發 Stop，必須先問 user**（比對外發信同等級的機密邊界）
- 已於前言記錄一次 ST8 觸發（讀取 hsc-project 深入檔案），已改路徑處理，非阻斷性

## 5. 失敗模式回滾表

| 失敗模式 | 偵測 | 回滾 |
|---|---|---|
| hsc-project 參考資料讀不到（ST8） | cross-project-write-guard deny | 改用本專案既有 Apps Script 架構做同構參考，不強行繞過 |
| 狀態機設計過複雜 | Self-Eval 卡關 | 砍到最小可行版本（5 狀態內） |
| Demo 腳本執行失敗 | 執行報錯 | 就地除錯重跑，同檔修改不超過 2 次/24h（ST5） |

## 6. Cadence

| 時點 | Agent 動作 | User 動作 |
|---|---|---|
| 本次 session（一次性自跑）| Phase 1-5 全跑完 | 過程不介入；結尾審 HANDOFF |
| HANDOFF 之後 | 待命 | 決定是否要真的整合 `gift-suppliers/` 真實資料、是否要部署成正式工具 |

## 7. 一鍵啟動 Prompt（跨 session 接續用）

```
你是三才實業網站助理。讀完 c:\Users\pc\projects\SAN-TSAIR\docs\GOAL_procurement_architecture.md，依 Phase 1-5 順序執行。

規則：
1. 每 Phase 開始前印「核彈評分」+ 上一 Phase Self-Eval
2. 純本地動作（寫 .md / 寫程式 / git commit）= 自跑，不問
3. 絕對不讀取、不寫入 gift-suppliers/ 目錄任何內容
4. 觸發 ST1-ST8 任一立刻停下找 user
5. 全程核彈評分必印兩次（前/後）

當前 progress：見本檔 Phase 清單勾選狀態（於執行時更新）

完成所有 Phase 後印 HANDOFF.md，等 user。
```

## 8. 工程資產清單

| 資產 | 路徑 | 用途 |
|---|---|---|
| 本檔（Goal prompt） | `docs/GOAL_procurement_architecture.md` | 下個 agent 起點 |
| 研究文件 | `docs/procurement/01_research.md` | Phase 1 產出 |
| 資料模型 | `docs/procurement/02_data_model.md` | Phase 2 產出 |
| 追蹤系統雛形 | `scripts/procurement_tracker/` | Phase 3-4 產出 |
| HANDOFF | `docs/procurement/HANDOFF.md` | Phase 5 產出 |

## 10. 何時 //save

完成 Phase 5 HANDOFF 後執行 //save 更新 memory，git commit，停下等 user。

---

🕐 本檔建立：2026-09-20
**狀態**：架構 prompt v1.0，即將開跑
