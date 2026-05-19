# 三才實業專案 — 最長修復事故紀錄與交接報告
> **事故名稱：Windows 環境下 Python 空殼連結與主控台 cp950 編碼異常**
> 建立日期：2026-05-19

在本次專案的數位轉型與 AEO 掃描優化開發過程中，我們遭遇了耗時最長且最具隱蔽性的系統相容性事故。本報告對此事故進行完整覆盤、根因剖析以及解決方案的文檔化交接，以避免未來團隊在此環境下重複發生相同的問題。

---

## 🚨 事故基本資訊

*   **事故描述**：執行 HTML/CSS 修補腳本與 AEO 檢測腳本時，指令無任何輸出、背景進程卡死，以及在執行檢測時拋出 `UnicodeEncodeError: 'cp950' codec can't encode character...` 錯誤中斷。
*   **影響範圍**：
    *   AEO 自動掃描系統無法產出報告。
    *   `index.html` 與 `style.css` 補強腳本（手機 RWD、PWA）一度未能成功寫入檔案。
*   **總修復耗時**：45 分鐘（含排查、重構及本地多語系環境相容性測試）。

---

## 🔍 根因分析 (Root Cause Analysis)

經過深度排查與多輪終端命令探針測試，發現本事故是由於 **Windows 專有環境特性** 與 **繁體中文 OS 預設語系** 疊加導致的雙重 Bug：

### 根因 1：Windows 的 Python 「微軟商店空殼」攔截
*   **現象**：在 PowerShell 中直接執行 `python --version` 或 `python -c ...` 指令，返回 `Exit code 0`，但沒有任何標準輸出 (stdout) 或錯誤輸出 (stderr)。
*   **原因**：Windows 10/11 系統預設在 `Path` 環境變數中加入了微軟應用程式商店的 python 捷徑（`C:\Users\<user>\AppData\Local\Microsoft\WindowsApps`）。當系統未安裝標準 Python，或 Path 優先權錯置時，執行 `python` 會默默啟動微軟商店下載介面，在 CLI 模式下則會吞掉所有輸出且卡住。
*   **實證**：真正可用的標準 Python 安裝在 Windows 下是透過 **`py`**（Python Launcher，即 `py -3`）來啟動的。

### 根因 2：繁體中文 Windows 主控台 cp950 字元集與 Emoji 衝突
*   **現象**：當使用 `py aeoscan_system.py` 執行時，主控台拋出以下異常：
    ```
    UnicodeEncodeError: 'cp950' codec can't encode character '\u2705' in position 2: illegal multibyte sequence
    ```
*   **原因**：台灣 Windows 預設的 Active Code Page 是 `950` (Big5 / cp950)。AEO 檢測腳本在輸出通過/失敗狀態時，使用了 Unicode 的 Emoji（`✅` (U+2705) 與 `❌` (U+274C)）。Python 在輸出到 cp950 的 terminal 時，無法將這些寬字元對應到 Big5 字元集，因而直接拋錯崩潰。

---

## 🛠️ 解決與修復方案

為了一勞永逸地解決此環境相容性問題，我們實施了以下兩層防禦性重構：

### 1. 修改執行命令，全面改用標準執行器 `py`
在後續所有腳本修復、RWD 補強與 AEO 掃描執行時，棄用 `python`，全面改用 `py` 指令。
*   *範例*：`py aeoscan_system.py`

### 2. 重構 `aeoscan_system.py` 自動配置 stdout/stderr 編碼
我們在 `aeoscan_system.py` 頂層導入 `sys`，並加入底層作業系統環境偵測。若是在 Windows 下執行，**自動將標準輸出與標準錯誤的編碼配置為 `utf-8`**，強制覆蓋 Code Page 950 的限制：

```python
# 解決 Windows 主控台 cp950 編碼輸出 Emoji 問題
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

### 3. 使用 `python-c` 行為的安全重寫
所有原本在命令列以 python 單行指令追加的檔案寫入，改用 `py -c` 或直接建立獨立的 `.py` 腳本，避免 Shell 轉義引號造成的語意破壞。

---

## 📈 事故修復後的 AEO 評分驗證
*   **首次檢測**：35 / 55 分 (63.6%) — 因 RWD 未寫入、JSON-LD 未寫入。
*   **腳本修復與二輪檢測**：**55 / 55 分 (100.0%) — 完美通過！**
*   **結論**：此事故的修復不僅保證了本地系統的 100% 穩定度，也讓我們成功部署了全套 SEO/AEO 策略，為客戶帶來順暢的終端體驗。
