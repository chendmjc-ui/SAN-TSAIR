# 三才實業專案 — GCP 雲端全自動化接管 (Cloud Shell 一鍵部署)
> 建立日期：2026-05-27 11:40

收到！由於您的本機電腦（Windows）尚未安裝 `gcloud` 終端機工具，身為 AI 系統，我無法直接穿透到您的瀏覽器中幫您點擊按鈕。
**但是，為了貫徹「全自動化」的原則，我已為您準備了「Cloud Shell 一鍵自動創建指令」！**

您不需要在複雜的 GCP 介面中一個一個尋找按鈕，只需要透過 Google 內建的雲端終端機，貼上我為您寫好的這段程式碼，Google 就會在背景為您完成：
1. 自動選擇符合**終身免費額度**的美國奧勒岡州 (`us-west1-b`) 機房與 `e2-micro` 機型。
2. 自動開通 30GB 免費標準硬碟。
3. 自動開啟 80 (HTTP) 與 443 (HTTPS) 防火牆。
4. 自動注入我們稍早準備好的 `install_n8n_gcp.sh` (含 2GB Swap 防護與 Docker 安裝)。

---

## 🚀 最終交接：請執行以下三步

### 步驟 1：開啟 GCP Cloud Shell
1. 在瀏覽器中回到您的 [Google Cloud Console (控制台)](https://console.cloud.google.com/)。
2. 確認左上角的專案是您剛建立的 `San-Tsair-Automation`。
3. 點擊畫面右上角，有一個 **`>_` (啟用 Cloud Shell)** 的小圖示。
4. 畫面下方會彈出一個黑色的終端機視窗，等待它連線並顯示出 `~$` 提示字元。

### 步驟 2：貼上全自動化指令
請將以下整段指令（包含所有換行）**完全複製，然後在下方的黑色終端機中按右鍵貼上，最後按下 Enter 送出**。
*(如果系統跳出「授權 Cloud Shell 撥打 API」的提示，請點擊「授權」)*

```bash
gcloud compute instances create n8n-santsair-server \
    --zone=us-west1-b \
    --machine-type=e2-micro \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --tags=http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=n8n-santsair-server,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231213,mode=rw,size=30,type=pd-standard \
    --metadata=startup-script="#!/bin/bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo mkdir -p /home/n8n_data
sudo chown -R 1000:1000 /home/n8n_data
sudo docker run -d --restart always --name n8n -p 80:5678 -e EXECUTIONS_DATA_PRUNE=true -e EXECUTIONS_DATA_MAX_AGE=14 -e EXECUTIONS_PROCESS=main -e GENERIC_TIMEZONE=Asia/Taipei -e TZ=Asia/Taipei -v /home/n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n"
```

### 步驟 3：取得 n8n 網址並開始使用
指令送出後，大約等待 10~20 秒，畫面上會出現一個表格。
請查看表格中 `EXTERNAL_IP` 那一欄的數字。
接著，打開您的瀏覽器新分頁，輸入：
`http://該組外部IP`
*(例如 `http://34.125.xx.xx`)*

恭喜！您的 n8n 全自動化接單系統已經正式上線！首次進入會要求您設定一組管理員帳號密碼，設定完後即可匯入我們先前產出的 `n8n_line_messaging_api_workflow.json`。
