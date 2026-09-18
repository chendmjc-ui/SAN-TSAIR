# 三才實業專案 — n8n 登入安全 Cookie 問題排除
> 建立日期：2026-05-27 15:11

## 🔍 錯誤碼分析
`Your n8n server is configured to use a secure cookie...`
這是一個非常好的現象！代表**您已經成功連進 n8n 的網站了！**

這個錯誤是因為最新版的 n8n 系統預設開啟了最高等級的安全機制（要求必須有 HTTPS 安全鎖頭的網址才能登入）。但因為我們目前是用純 IP (`http://`) 連線，所以瀏覽器拒絕儲存登入憑證。

---

## 🚀 終極解法：關閉嚴格 Cookie 檢查
既然我們目前是測試階段並使用 IP 連線，我們只要在伺服器上加上 `N8N_SECURE_COOKIE=false` 這個環境變數，把這個嚴格檢查關掉即可。

請在 Cloud Shell 複製並貼上這行指令（這會自動幫您關掉舊的系統，套用新設定並重新啟動）：

```bash
gcloud compute ssh n8n-server --zone=us-west1-b --command="sudo docker stop n8n && sudo docker rm n8n && sudo docker run -d --restart always --name n8n -p 80:5678 -e N8N_SECURE_COOKIE=false -e WEBHOOK_URL=http://8.229.67.29/ -e EXECUTIONS_DATA_PRUNE=true -e EXECUTIONS_DATA_MAX_AGE=14 -e EXECUTIONS_PROCESS=main -e GENERIC_TIMEZONE=Asia/Taipei -e TZ=Asia/Taipei -v /home/n8n_data:/home/node/.n8n n8nio/n8n"
```

**執行後：**
只要終端機吐出新的一串英文代碼，請直接回到瀏覽器重新整理 **http://8.229.67.29** ，您就能順利填寫帳號密碼，進入 n8n 的後台了！
