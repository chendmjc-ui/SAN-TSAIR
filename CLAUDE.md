# SAN-TSAIR（三才實業）

## 專案性質

三才實業對外正式網站，GitHub Pages 部署：`https://chendmjc-ui.github.io/SAN-TSAIR/`
（remote: `github.com/chendmjc-ui/SAN-TSAIR`）。任何進版控並推送的檔案即為公開內容。

## 子專案

- `gift-suppliers/` — 禮贈品供應商開發（20家候選廠商盡調、第一梯隊8家話術、MVP測試規劃）。
  **已在 `.gitignore` 排除，禁止進版控**：內含供應商報價、私人聯絡窗口、內部盡調評估，一旦推送
  即公開洩漏。詳細規則見該目錄自己的 `CLAUDE.md`。

## 目錄結構

> 2026-08-10：原專案由 Google Antigravity 開發，檔案全平放在根目錄；現收斂到 Claude Code，
> 依 `c:\Users\pc\projects\CLAUDE.md` 的「產出規範」整理為子資料夾。網站實際服務的檔案維持在根目錄
> （GitHub Pages 直接從 repo 根目錄／指定分支服務靜態檔，路徑一動 URL 就變）。

| 路徑 | 內容 | 可否搬動 |
|---|---|---|
| `index.html`, `temple-gifts.html` | 網站頁面 | 否，URL 依賴根目錄路徑 |
| `assets/` | CSS／JS／圖片 | 否，`index.html` 直接引用 `assets/css/style.min.css` |
| `sw.js`, `manifest.json`, `robots.txt`, `sitemap.xml`, `llms.txt`, `.nojekyll` | PWA／SEO／爬蟲規範檔 | 否，慣例要求在網站根目錄 |
| `docs/` | 專案文件、GCP／n8n 部署筆記、事故紀錄 | 是（已完成） |
| `scripts/` | Python／Shell 維運腳本（AEO 掃描、歷史 patch 腳本、LINE 測試） | 是（已完成） |
| `config/n8n/` | n8n workflow JSON 匯出檔 | 是（已完成） |
| `output/aeoscan_reports/` | `scripts/aeoscan_system.py` 產出的時間戳報告 | 是（已完成） |
| `gift-suppliers/` | 禮贈品供應商子專案（gitignore） | 是（已完成，見上） |

`scripts/aeoscan_system.py` 已改用 `__file__` 推算根目錄（不再寫死 `c:\Users\pc\projects\SAN-TSAIR`），
報告輸出改寫到 `output/aeoscan_reports/`；`.github/workflows/aeoscan.yml` 對應改成
`python scripts/aeoscan_system.py`。搬移後已本機重跑一次，55/55 分（100%）確認無回歸。

`scripts/patch_all_2.py` / `patch_bulk.py` / `patch_line.py` / `patch_html.py` / `patch_head_aeo.py` /
`patch_neutral.py` 是歷史一次性修補腳本（已執行完畢的 commit 紀錄），內部多用相對路徑
（`'index.html'`、`'assets/css/style.css'`），**必須在 repo 根目錄下執行**
（例如 `python scripts/patch_bulk.py`），不能在 `scripts/` 目錄內直接跑。

## 上層規則

繼承 `c:\Users\pc\projects\CLAUDE.md` 全域準則。本檔僅補專屬內容，不重複貼全域規則。
