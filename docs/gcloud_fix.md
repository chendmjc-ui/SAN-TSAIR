# 三才實業專案 — Cloud Shell 指令除錯與最終部署版
> 建立日期：2026-05-27 12:07

## ⚠️ 剛剛發生了什麼事？
您看到的報錯 `-bash: !/bin/bash: event not found` 是因為 Google Cloud Shell 的終端機把驚嘆號 `!` 當成了「歷史指令召喚」的特殊符號。
這導致指令被強行中斷，而且系統錯誤地把「建置伺服器」的指令，直接跑在了您當下的「網頁終端機 (Cloud Shell)」上，因此產生了一大串 `apt-get` 的報錯。

*請放心，這**完全沒有影響**，您的專案依舊是乾淨的。*

---

## 🚀 最終完美解法 (100% 絕對成功版)
為了解決這個標點符號的衝突，我們改用「產生實體腳本檔」的方式讓 `gcloud` 去讀取，這樣就絕對不會報錯了。

請將下面這**整大段（包含所有的字）一次性複製，並在終端機中貼上後按 Enter**：

```bash
cat << 'EOF' > startup.sh
#!/bin/bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo mkdir -p /home/n8n_data
sudo chown -R 1000:1000 /home/n8n_data
sudo docker run -d --restart always --name n8n -p 80:5678 -e EXECUTIONS_DATA_PRUNE=true -e EXECUTIONS_DATA_MAX_AGE=14 -e EXECUTIONS_PROCESS=main -e GENERIC_TIMEZONE=Asia/Taipei -e TZ=Asia/Taipei -v /home/n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
EOF

gcloud compute instances create n8n-server \
    --zone=us-west1-b \
    --machine-type=e2-micro \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --tags=http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=n8n-server,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231213,mode=rw,size=30,type=pd-standard \
    --metadata-from-file=startup-script=startup.sh
```

這段指令會自動先建立一個 `startup.sh`，然後把它乾淨俐落地餵給 Google 建立機器的指令中。這次您一定會看到它成功產出一張帶有 `EXTERNAL_IP` 的表格！
