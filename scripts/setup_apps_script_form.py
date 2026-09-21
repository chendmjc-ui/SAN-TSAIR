"""
三才實業詢價表單 — Google Apps Script 一鍵部署精靈

跑法：py -3 scripts\\setup_apps_script_form.py
（必須在 repo 根目錄執行，跟 index.html 同一層）

流程：自動開瀏覽器到對的設定頁 + 自動把 Code.gs 貼進剪貼簿 +
逐步跟你要 Token/URL（格式自動驗證）+ 自動寫回 main.js +
自動實測整條路徑（Sheet 寫入 + LINE 推播）。

不會做的事：不會幫你在 Google/LINE 網頁上按按鈕（那些只能你自己
登入操作），Token 只會停留在這個腳本的記憶體跟本機檔案，不會被
印出完整內容、不會被送去任何地方，除非是你貼進 Apps Script 網頁。
"""
import json
import re
import subprocess
import sys
import tempfile
import time
import webbrowser
from getpass import getpass
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
MAIN_JS = ROOT / "assets" / "js" / "main.js"
CODE_GS = ROOT / "config" / "google-apps-script" / "Code.gs"


def copy_to_clipboard(text: str):
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
    if not MAIN_JS.exists() or not CODE_GS.exists():
        sys.exit(f"找不到必要檔案，請確認在 repo 根目錄執行本腳本（目前偵測根目錄：{ROOT}）")

    print("三才實業詢價表單部署精靈開始。全程約需 5 分鐘，你只需要登入 Google／LINE 操作幾個按鈕。")

    # --- 步驟 1：建立 Sheet + 貼 Apps Script ---
    step(1, "建立 Google 試算表並掛上 Apps Script")
    code_content = CODE_GS.read_text(encoding="utf-8")
    if copy_to_clipboard(code_content):
        print("Code.gs 的內容已經複製到剪貼簿了，等一下編輯器打開直接 Ctrl+V 貼上即可。")
    else:
        print(f"（自動複製到剪貼簿失敗，請自行開啟 {CODE_GS} 手動複製）")
    print("即將開啟瀏覽器到 sheets.new（新試算表）。")
    print("請依序：① 開啟後選單「擴充功能 Extensions」→「Apps Script」")
    print("        ② 全選編輯器裡預設的內容刪除，貼上剪貼簿內容（Ctrl+V）")
    print("        ③ 上方專案命名（例如「三才詢價表單」）並存檔（Ctrl+S）")
    webbrowser.open("https://sheets.new")
    pause()

    # --- 步驟 2：LINE Channel ---
    step(2, "取得 LINE Channel Access Token 與 User ID")
    print("即將開啟瀏覽器到 LINE Developers Console。")
    print("若還沒建立過 Messaging API Channel，先建立 Provider（如「三才實業」）+ 新增 Channel。")
    print("進入 Channel 的 Basic settings 頁面，最下方可以拿到 Channel Access Token 與你的 User ID。")
    print("記得用自己的 LINE 掃 QR Code 加這個 Channel 為好友（沒加好友收不到推播）。")
    webbrowser.open("https://developers.line.biz/console/")
    pause("拿到 Token 與 User ID 後按 Enter 繼續")

    token = getpass("貼上 Channel Access Token（輸入時不會顯示，貼完按 Enter）：").strip()
    while len(token) < 50:
        print(f"這個長度看起來不太像正常的 Channel Access Token（只有 {len(token)} 字元，正常應該很長一串）。")
        retry = input("要重新輸入嗎？(y/n，選 n 就照這個值繼續): ").strip().lower()
        if retry == "n":
            break
        token = getpass("重新貼上 Channel Access Token：").strip()

    user_id = input("貼上 LINE User ID（U 開頭那串）：").strip()
    while not re.match(r"^U[0-9a-f]{32}$", user_id):
        print(f"格式看起來不太對：LINE User ID 應該是 U 開頭 + 32 位英數字，總長 33。你貼的是「{user_id}」。")
        retry = input("要重新輸入嗎？(y/n，選 n 就照這個值繼續): ").strip().lower()
        if retry == "n":
            break
        user_id = input("重新貼上 LINE User ID：").strip()

    # --- 步驟 3：填進 Script Properties ---
    step(3, "把 Token 填進 Apps Script 的 Script Properties")
    print("回到剛剛的 Apps Script 編輯器分頁：左側齒輪圖示「專案設定 Project Settings」")
    print("→ 捲到「Script Properties」→「Add script property」，新增兩筆：")
    print("   LINE_CHANNEL_ACCESS_TOKEN = （接下來會幫你複製到剪貼簿，直接貼）")
    input("按 Enter，會把 Token 複製到剪貼簿...")
    copy_to_clipboard(token)
    print("已複製 Token 到剪貼簿，去貼上 LINE_CHANNEL_ACCESS_TOKEN 的值。")
    pause("貼完 Token 這筆後按 Enter，準備複製 User ID")
    copy_to_clipboard(user_id)
    print("已複製 User ID 到剪貼簿，去新增第二筆 LINE_USER_ID 並貼上。")
    pause("兩筆都存好後按 Enter 繼續")

    # --- 步驟 4：部署 ---
    step(4, "部署成 Web App")
    print("編輯器右上角「Deploy」→「New deployment」→ 類型選「Web app」")
    print("Execute as：Me　／　Who has access：Anyone")
    print("按 Deploy，會跳授權畫面，允許存取（這是你自己的帳號授權自己的腳本）。")
    pause("部署完成、拿到結尾是 /exec 的網址後按 Enter 繼續")

    exec_url = input("貼上部署產生的 /exec 網址：").strip()
    while not re.match(r"^https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec$", exec_url):
        print("格式看起來不太對，正常應該長這樣：https://script.google.com/macros/s/AKfycb.../exec")
        exec_url = input("重新貼上 /exec 網址：").strip()

    # --- 步驟 5：寫回 main.js ---
    step(5, "自動寫回 main.js")
    content = MAIN_JS.read_text(encoding="utf-8")
    if "PASTE_APPS_SCRIPT_EXEC_URL_HERE" not in content:
        print("main.js 裡找不到預期的佔位字串，可能已經被改過了，跳過自動寫入，請自行確認。")
    else:
        new_content = content.replace(
            "const FORM_WEBHOOK = 'PASTE_APPS_SCRIPT_EXEC_URL_HERE';",
            f"const FORM_WEBHOOK = '{exec_url}';",
        )
        MAIN_JS.write_text(new_content, encoding="utf-8")
        print(f"已寫入 {MAIN_JS}")

    # --- 步驟 6：實測整條路徑 ---
    step(6, "實測整條路徑（送一筆測試資料）")
    payload = json.dumps({
        "name": "[部署測試] 請忽略",
        "phone": "0000000000",
        "service": "部署測試",
        "qty": "0",
        "msg": "這是 setup_apps_script_form.py 自動送出的測試資料，確認整條路徑通了即可刪除這列",
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }).encode("utf-8")
    req = request.Request(exec_url, data=payload, headers={"Content-Type": "text/plain;charset=utf-8"}, method="POST")
    try:
        with request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        if body.get("ok"):
            print("測試成功！Google Sheet 應該多了一列測試資料，LINE 應該收到一則推播通知。")
            print("請實際去確認這兩件事，確認後可以把 Sheet 裡那列測試資料刪掉。")
        else:
            print(f"Apps Script 回應了但標記失敗：{body}")
            print("常見原因：Script Properties 兩筆沒存對、或還沒加 LINE Channel 為好友。")
    except error.HTTPError as e:
        print(f"HTTP 錯誤 {e.code}：{e.read().decode('utf-8', 'ignore')}")
        print("常見原因：Deploy 時 Who has access 沒選到 Anyone。")
    except Exception as e:
        print(f"測試呼叫失敗：{e}")
        print("main.js 已經寫入這個網址了，但你可能需要手動確認部署狀態或重新部署一次。")

    print("\n全部步驟跑完。若上面顯示測試成功，這批 main.js 的改動記得回報給 Claude 一次性 commit。")


if __name__ == "__main__":
    main()
