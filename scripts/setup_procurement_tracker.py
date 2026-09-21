"""
三才實業採購追蹤器 — Google Apps Script 一鍵部署精靈

跑法：py -3 scripts\\setup_procurement_tracker.py
（必須在 repo 根目錄執行，跟 index.html 同一層）

流程：自動開瀏覽器到 sheets.new + 自動把 ProcurementTracker.gs 貼進剪貼簿 +
逐步引導建 quotes/Import 分頁 + 貼上 LINE Token（複用現有詢價表單那組）+
引導跑 runSelfTest 確認邏輯正確 + 引導設定每日排程 + 自動把資料匯出 CSV
複製到剪貼簿方便貼進 Import 分頁。

跟 gift-suppliers/ 的關係：本腳本不讀取、不寫入 gift-suppliers/ 底下任何
機密內容，只負責把「已經在 gift-suppliers/output/tracker_seed.csv 產生好的
非金額參照資料」複製到剪貼簿，實際產生那份 CSV 要先在 gift-suppliers/ 目錄
下跑 scripts/export_tracker_seed.py（那支腳本才會碰機密目錄，本腳本不會）。
"""
import subprocess
import sys
import tempfile
import webbrowser
from getpass import getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER_GS = ROOT / "config" / "google-apps-script" / "ProcurementTracker.gs"
SEED_CSV = ROOT / "gift-suppliers" / "output" / "tracker_seed.csv"


def copy_to_clipboard(text: str) -> bool:
    """用 PowerShell Set-Clipboard 讀 UTF-8 檔案寫剪貼簿，不用 clip.exe。

    clip.exe 會依系統目前 codepage（繁體中文 Windows 預設是 Big5 950，不是
    UTF-8）解讀 stdin 位元組再轉成 Unicode 剪貼簿格式；當 codepage 不是 65001
    時，中文字元的 UTF-8 多位元組序列會被誤判成 Big5 解碼，不但整段中文變
    亂碼，還可能巧合產生跳脫字元讓多行註解/字串語法被意外截斷（2026-09-21
    實測重現：在 950 codepage 下貼進 Apps Script 編輯器出現
    `Unexpected identifier` 語法錯誤）。PowerShell 字串一律用 Unicode 處理，
    不受 console codepage 影響，故改走這條路徑。
    """
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write(text)
            tmp_path = tmp.name
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Set-Clipboard -Value (Get-Content -Raw -Encoding UTF8 -LiteralPath '{tmp_path}')"],
            check=True,
        )
        Path(tmp_path).unlink(missing_ok=True)
        return True
    except Exception:
        return False


def pause(msg="完成後按 Enter 繼續..."):
    input(f"\n>>> {msg}")


def step(n, title):
    print(f"\n{'='*60}\n步驟 {n}：{title}\n{'='*60}")


def main():
    if not TRACKER_GS.exists():
        sys.exit(f"找不到 {TRACKER_GS}，請確認在 repo 根目錄執行本腳本。")

    print("三才實業採購追蹤器部署精靈開始。全程約需 5-10 分鐘。")
    print("這套系統只追蹤「談到哪一步了」，不存任何金額/MOQ 等商務資料，")
    print("正式報價內容永遠留在 gift-suppliers/ 的 Excel 主檔，不會進這份 Sheet。")

    # --- 步驟 1：建立獨立的新 Sheet + 貼 Apps Script ---
    step(1, "建立獨立的新 Google Sheet 並掛上 Apps Script")
    print("這份 Sheet 跟現有詢價表單那份是分開的兩個獨立專案（詢價表單那份是")
    print("Anyone 可存取的公開 doPost 端點，機密相關的追蹤資料不該跟公開入口同住）。")
    code_content = TRACKER_GS.read_text(encoding="utf-8")
    if copy_to_clipboard(code_content):
        print("ProcurementTracker.gs 的內容已複製到剪貼簿，等一下編輯器打開直接 Ctrl+V 貼上。")
    else:
        print(f"（自動複製到剪貼簿失敗，請自行開啟 {TRACKER_GS} 手動複製）")
    print("即將開啟瀏覽器到 sheets.new（新試算表）。")
    print("請依序：① 開啟後選單「擴充功能 Extensions」→「Apps Script」")
    print("        ② 全選編輯器裡預設的內容刪除，貼上剪貼簿內容（Ctrl+V）")
    print("        ③ 上方專案命名（例如「三才採購追蹤器」）並存檔（Ctrl+S）")
    webbrowser.open("https://sheets.new")
    pause()

    # --- 步驟 2：Script Properties（複用現有詢價表單那組 LINE Channel） ---
    step(2, "填入 LINE Channel（複用現有詢價表單那組，不用重新申請）")
    print("回到剛剛的 Apps Script 編輯器：左側齒輪圖示「專案設定 Project Settings」")
    print("→ 捲到「Script Properties」→「Add script property」，新增兩筆：")
    print("   LINE_CHANNEL_ACCESS_TOKEN 跟 LINE_USER_ID（跟詢價表單那組完全一樣的值）")
    print("如果手邊沒有現成的值，可以到 LINE Developers Console 的 Channel 頁面重新複製。")
    pause("拿到 Token/User ID 後按 Enter 繼續（接下來會請你貼上）")

    token = getpass("貼上 Channel Access Token（輸入時不會顯示，貼完按 Enter）：").strip()
    if token:
        copy_to_clipboard(token)
        print("已複製到剪貼簿，去貼上 LINE_CHANNEL_ACCESS_TOKEN 的值。")
        pause("貼完後按 Enter，準備複製 User ID")

    user_id = input("貼上 LINE User ID（U 開頭那串）：").strip()
    if user_id:
        copy_to_clipboard(user_id)
        print("已複製到剪貼簿，去新增 LINE_USER_ID 並貼上。")
    pause("兩筆都存好後按 Enter 繼續")

    # --- 步驟 3：自我測試 ---
    step(3, "跑一次自我測試，確認狀態機邏輯正確")
    print("編輯器工具列的函式下拉選單選「runSelfTest」，按執行（▶）。")
    print("第一次執行會跳授權畫面，允許存取（這是你自己的帳號授權自己的腳本）。")
    print("執行完成後，選單「檢視 View」→「記錄 Logs」，應該全部顯示 PASS。")
    print("⚠️ 若有任何一項顯示 FAIL，先不要繼續下一步，回報給 Claude 檢查。")
    pause("確認 Log 全部 PASS 後按 Enter 繼續")

    # --- 步驟 4：建立每日排程 ---
    step(4, "建立每個工作日早上 9 點自動檢查逾期的排程")
    print("函式下拉選單改選「setupDailyTrigger」，按執行（▶）。")
    print("執行完成、Log 顯示「已建立每日 09:00 執行 checkOverdue 的排程」即完成，")
    print("之後不需要再手動做任何事，逾期提醒會自動用 LINE 推播。")
    pause("執行完成後按 Enter 繼續")

    # --- 步驟 5：匯入參照資料 ---
    step(5, "匯入第一梯隊廠商參照資料")
    if SEED_CSV.exists():
        csv_content = SEED_CSV.read_text(encoding="utf-8-sig")
        if copy_to_clipboard(csv_content):
            print(f"已把 {SEED_CSV.name} 的內容複製到剪貼簿。")
        else:
            print(f"自動複製失敗，請自行開啟 {SEED_CSV} 複製內容。")
    else:
        print(f"找不到 {SEED_CSV}。")
        print("請先在 gift-suppliers/ 目錄下跑：py -3 scripts\\export_tracker_seed.py")
        print("跑完會產生這份 CSV，再重新執行本腳本，或手動開啟那份 CSV 自行複製貼上。")

    print("\n回到 Sheet 分頁（不是編輯器），重新整理頁面（F5），選單列應該會多一個「採購追蹤」。")
    print("新增一個分頁命名為「Import」，A1 儲存格貼上剛複製的內容（Ctrl+V，含標題列）。")
    print("貼完後選單「採購追蹤」→「匯入參照資料」，會跳出視窗顯示新增/更新筆數。")
    pause("完成後按 Enter 結束")

    print("\n全部步驟跑完。之後每天早上 9 點會自動檢查逾期並用 LINE 通知，不需要再手動操作。")
    print("這份新 Sheet 的網址記得存起來（供之後查看用），不需要回報給 Claude，")
    print("因為裡面不含金額資料，此腳本本身跟 ProcurementTracker.gs 可以直接 commit。")


if __name__ == "__main__":
    main()
