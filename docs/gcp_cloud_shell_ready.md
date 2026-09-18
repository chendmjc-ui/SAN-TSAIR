# 三才實業專案 — Cloud Shell 一鍵自動架設指令 (已針對您的畫面校正)
> 建立日期：2026-05-27 12:04

太棒了！我從您的畫面看到，您已經成功開啟了 Cloud Shell 終端機，目前的專案是 **`hsc-dashboard-syn`**。

您現在**只需要做一個動作**：
將下方這個灰框內的整段程式碼（包含所有換行）**完全複製，然後在您的黑色終端機畫面中點擊右鍵「貼上」，並按下 Enter 送出**。

*(如果系統跳出視窗詢問是否「授權 (Authorize)」，請點擊授權)*

```bash
gcloud compute instances create n8n-server \
    --project=hsc-dashboard-syn \
    --zone=us-west1-b \
    --machine-type=e2-micro \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --tags=http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=n8n-server,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231213,mode=rw,size=30,type=pd-standard \
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

---

## 🎯 執行後的下一步
送出指令後，大約等待 15 秒，畫面上會吐出一個表格。
請注意看表格中 **`EXTERNAL_IP`**（外部 IP）那一欄的數字。
接著，打開您瀏覽器的新分頁，輸入：
`http://該組數字`
*(例如 `http://34.125.12.34`)*

恭喜！您就會看到 n8n 的初始設定畫面了。設定好帳號密碼後，就能直接匯入我們之前產出的 `n8n_line_messaging_api_workflow.json` 檔案。
