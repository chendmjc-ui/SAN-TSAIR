# 補回 .github/workflows/aeoscan.yml
# 背景：chendmjc-ui（repo owner，有 push 權限）目前的 gh token 缺 workflow scope，
# 之前推送這個檔案被 GitHub 拒絕，所以先從 commit 移除讓其他內容上線（見 commit c638c22）。
# 這支腳本負責：確認登入帳號 -> 補 workflow scope -> 從 git 歷史還原檔案 -> commit -> push。
# 需要你手動操作的部分：瀏覽器裝置授權那步，腳本會印出網址跟代碼，用 chendmjc-ui 帳號登入完成即可。

$ErrorActionPreference = "Stop"

Write-Host "==> 目前 gh 登入帳號狀態" -ForegroundColor Cyan
gh auth status 2>&1 | Write-Host

$activeAccount = (gh api user --jq .login 2>$null)
Write-Host ""
Write-Host "==> 目前 active account: $activeAccount" -ForegroundColor Cyan

if ($activeAccount -ne "chendmjc-ui") {
    Write-Host "目前 active 帳號不是 chendmjc-ui，先切換..." -ForegroundColor Yellow
    gh auth switch -u chendmjc-ui
    if (-not $?) {
        Write-Host "切換失敗，可能這台機器的 gh 從未登入過 chendmjc-ui。" -ForegroundColor Red
        Write-Host "改用 gh auth login 走瀏覽器裝置授權（下一步會處理，請耐心跟著畫面走）。" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==> 補 workflow scope（會開啟瀏覽器裝置授權流程）" -ForegroundColor Cyan
Write-Host "⚠️ 重要：瀏覽器彈出登入頁時，務必用 chendmjc-ui 帳號登入，不是 alex1491tw-sketch" -ForegroundColor Yellow
Write-Host ""

gh auth refresh -h github.com -s workflow

Write-Host ""
Write-Host "==> 驗證 scope 是否補上" -ForegroundColor Cyan
$statusOutput = gh auth status 2>&1 | Out-String
Write-Host $statusOutput
if ($statusOutput -notmatch "workflow") {
    Write-Host "看起來 workflow scope 還沒補上，腳本停止，請重新執行一次確認瀏覽器有完成登入。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==> 從 git 歷史還原 aeoscan.yml（commit c638c22 之前的版本）" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ".github/workflows" | Out-Null
$ymlContent = git show c638c22~1:.github/workflows/aeoscan.yml
[System.IO.File]::WriteAllText("$pwd\.github\workflows\aeoscan.yml", ($ymlContent -join "`n") + "`n", [System.Text.UTF8Encoding]::new($false))

Write-Host "還原內容預覽："
Get-Content ".github/workflows/aeoscan.yml"

Write-Host ""
$confirm = Read-Host "確認內容正確，要 git add + commit + push 嗎？(y/n)"
if ($confirm -ne "y") {
    Write-Host "已中止，檔案已還原在本機但尚未 commit。" -ForegroundColor Yellow
    exit 0
}

git add .github/workflows/aeoscan.yml
git commit -m "chore: 補回 aeoscan workflow，chendmjc-ui token 已補 workflow scope"
git push

Write-Host ""
Write-Host "==> 完成，workflow 檔案已推送。" -ForegroundColor Green
