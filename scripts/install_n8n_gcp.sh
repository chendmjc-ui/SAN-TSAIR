#!/bin/bash
# ==========================================
# 三才實業 - GCP 免費機型 (e2-micro) n8n 一鍵安裝腳本
# 包含：Swap 虛擬記憶體防當機、Docker 自動安裝、n8n 最佳化參數
# ==========================================

echo "🚀 開始執行 n8n 全自動安裝腳本..."

# 1. 建立 2GB Swap 虛擬記憶體 (解決 1GB RAM 容易當機的問題)
echo "📦 正在建立 2GB Swap 空間..."
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# 寫入 fstab 確保重開機後依然生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 2. 更新系統並安裝 Docker 與 Docker Compose
echo "🐳 正在安裝 Docker..."
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose

# 3. 建立 n8n 資料夾與權限
echo "📁 建立 n8n 持久化資料夾..."
sudo mkdir -p /home/n8n_data
# n8n 容器內預設使用 node(1000) 用戶，需給予對應權限
sudo chown -R 1000:1000 /home/n8n_data

# 4. 啟動 n8n 容器 (帶入 e2-micro 最佳化環境變數)
echo "🤖 正在啟動 n8n 伺服器..."
sudo docker run -d \
  --restart always \
  --name n8n \
  -p 80:5678 \
  -e EXECUTIONS_DATA_PRUNE=true \
  -e EXECUTIONS_DATA_MAX_AGE=14 \
  -e EXECUTIONS_PROCESS=main \
  -e N8N_DIAGNOSTICS_ENABLED=false \
  -e GENERIC_TIMEZONE="Asia/Taipei" \
  -e TZ="Asia/Taipei" \
  -v /home/n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n

echo "✅ 安裝完成！"
echo "請在 GCP 設定防火牆開啟 80 Port (HTTP)，並在瀏覽器輸入您的虛擬機外部 IP 即可進入 n8n。"
