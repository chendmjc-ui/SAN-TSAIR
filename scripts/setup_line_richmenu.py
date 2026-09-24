# ============================================================
# 三才實業 - LINE Rich Menu 日/夜版本建立腳本
# ============================================================
# 只負責「建立」兩個 rich menu 物件(day/night)+上傳對應圖片，
# 不會呼叫 set-default，不影響任何現有客戶當下看到的選單。
# 要不要把哪一個設成預設、要不要接上 n8n 排程自動切換，是後續
# 另外確認的步驟，故意跟「建立」分開，避免一次執行就影響真實客戶。
#
# 執行前提：專案根目錄 .env 已有 LINE_CHANNEL_ACCESS_TOKEN（見
# scripts/test_line_messaging_api.py 的讀取方式，本檔沿用同一套）
import os
import json
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), '..')
WEBSITE_BASE = 'https://chendmjc-ui.github.io/SAN-TSAIR/'

DAY_IMAGE = os.path.join(ROOT, 'samples', 'line_richmenu_demo', 'layer1-a-cream-accent.png')
NIGHT_IMAGE = os.path.join(ROOT, 'samples', 'line_richmenu_demo', 'layer1-c-dark-gold.png')


def _load_env():
    env = {}
    env_path = os.path.join(ROOT, '.env')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                k, _, v = line.partition('=')
                env[k] = v
    return env


def _areas():
    # 2500x843，三等分欄位（834+833+833=2500），對應找禮品/找制服/找獎牌
    # 2026-09-24 改為 type=message：點下去等同客戶自己在LINE打了這句話，
    # 直接觸發 line-ai-webhook 的 AI 回覆邏輯，全程留在LINE對話框內，
    # 不再跳出瀏覽器（原本 type=uri 跳官網造成的摩擦力，見 activeContext.md）
    return [
        {
            'bounds': {'x': 0, 'y': 0, 'width': 834, 'height': 843},
            'action': {'type': 'message', 'label': '找禮品', 'text': '我想了解企業禮贈品有哪些選擇'}
        },
        {
            'bounds': {'x': 834, 'y': 0, 'width': 833, 'height': 843},
            'action': {'type': 'message', 'label': '找制服', 'text': '我想了解團體制服訂製'}
        },
        {
            'bounds': {'x': 1667, 'y': 0, 'width': 833, 'height': 843},
            'action': {'type': 'message', 'label': '找獎牌', 'text': '我想了解匾額獎牌製作'}
        },
    ]


def create_rich_menu(token, name, chat_bar_text):
    body = {
        'size': {'width': 2500, 'height': 843},
        'selected': False,
        'name': name,
        'chatBarText': chat_bar_text,
        'areas': _areas(),
    }
    req = urllib.request.Request(
        'https://api.line.me/v2/bot/richmenu',
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())['richMenuId']


def upload_image(token, rich_menu_id, image_path):
    with open(image_path, 'rb') as f:
        data = f.read()
    req = urllib.request.Request(
        f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content',
        data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'image/png',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def main():
    token = _load_env().get('LINE_CHANNEL_ACCESS_TOKEN', '')
    if not token:
        print('找不到 LINE_CHANNEL_ACCESS_TOKEN，先確認 .env 有設定')
        return

    for path in (DAY_IMAGE, NIGHT_IMAGE):
        if not os.path.exists(path):
            print(f'找不到圖片：{path}')
            return

    day_id = create_rich_menu(token, '三才實業-日版-Layer1', '服務選單')
    upload_image(token, day_id, DAY_IMAGE)
    print(f'日版 rich menu 建立完成，richMenuId = {day_id}')

    night_id = create_rich_menu(token, '三才實業-夜版-Layer1', '服務選單')
    upload_image(token, night_id, NIGHT_IMAGE)
    print(f'夜版 rich menu 建立完成，richMenuId = {night_id}')

    print()
    print('兩個 rich menu 都只是「建立」完成，目前尚未設成任何人看到的預設選單。')
    print('下一步：確認要不要現在設其中一個為預設、以及日夜自動切換的排程時間點。')


if __name__ == '__main__':
    main()
