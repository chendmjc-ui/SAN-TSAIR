import urllib.request
import json

# ==========================================
# 三才實業 - LINE Messaging API 測試腳本
# ==========================================
# 請將下方的 TOKEN 與 USER_ID 替換為真實資料
LINE_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
USER_ID = 'YOUR_USER_ID'

url = 'https://api.line.me/v2/bot/message/push'

# Flex Message 格式 (與 n8n 工作流中的結構一致)
flex_message = {
    "to": USER_ID,
    "messages": [
        {
            "type": "flex",
            "altText": "三才實業 - 新詢價單通知",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🏆 新詢價單通知",
                            "weight": "bold",
                            "color": "#B45309",
                            "size": "xl"
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "姓名", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                {"type": "text", "text": "王大明 (測試)", "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "電話", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                {"type": "text", "text": "0912-345-678", "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
                            ]
                        }
                    ]
                }
            }
        }
    ]
}

data = json.dumps(flex_message).encode('utf-8')
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
}

req = urllib.request.Request(url, data=data, headers=headers)
try:
    if LINE_ACCESS_TOKEN != 'YOUR_CHANNEL_ACCESS_TOKEN':
        urllib.request.urlopen(req)
        print("✅ LINE Messaging API 測試成功！請檢查手機是否收到 Flex Message。")
    else:
        print("⚠️ 測試中斷：請先將程式碼中的 TOKEN 與 USER_ID 替換為真實資料。")
except Exception as e:
    print("❌ LINE Messaging API 測試失敗:", e)
