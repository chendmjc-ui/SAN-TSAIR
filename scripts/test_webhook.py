import urllib.request, json
url = "https://n8n.yourdomain.com/webhook/contact"
data = json.dumps({"name": "Test User", "phone": "0912345678", "service": "測試服務", "qty": "10", "msg": "這是一封測試訊息", "time": "2026-05-27T00:00:00Z"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    urllib.request.urlopen(req)
    print("Webhook test successful")
except Exception as e:
    print("Webhook test failed:", e)
