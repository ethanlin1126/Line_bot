"""
執行方式：python3 setup_rich_menu.py
會自動建立 Rich Menu 並綁定到機器人。
需要先準備一張 2500x843 的圖片，命名為 rich_menu.png 放在同目錄。
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {TOKEN}'}


def create_rich_menu():
    """建立 Rich Menu 結構（2列2欄，共4個按鈕）"""
    body = {
        "size": {"width": 2500, "height": 843},
        "selected": True,
        "name": "主選單",
        "chatBarText": "功能選單",
        "areas": [
            # 第一列
            {
                "bounds": {"x": 0, "y": 0, "width": 1250, "height": 421},
                "action": {"type": "message", "text": "我想跟你說..."}
            },
            {
                "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 421},
                "action": {"type": "message", "text": "我好累喔"}
            },
            # 第二列
            {
                "bounds": {"x": 0, "y": 421, "width": 1250, "height": 422},
                "action": {"type": "message", "text": "你覺得我要吃什麼"}
            },
            {
                "bounds": {"x": 1250, "y": 421, "width": 1250, "height": 422},
                "action": {"type": "message", "text": "你什麼時候回來"}
            },
        ]
    }
    resp = requests.post(
        'https://api.line.me/v2/bot/richmenu',
        headers={**HEADERS, 'Content-Type': 'application/json'},
        json=body
    )
    resp.raise_for_status()
    rich_menu_id = resp.json()['richMenuId']
    print(f'[1] Rich Menu 建立成功：{rich_menu_id}')
    return rich_menu_id


def upload_image(rich_menu_id: str, image_path: str):
    with open(image_path, 'rb') as f:
        resp = requests.post(
            f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content',
            headers={**HEADERS, 'Content-Type': 'image/png'},
            data=f
        )
    resp.raise_for_status()
    print(f'[2] 圖片上傳成功')


def set_default(rich_menu_id: str):
    resp = requests.post(
        f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}',
        headers=HEADERS
    )
    resp.raise_for_status()
    print(f'[3] 已設為預設選單')


def delete_all_rich_menus():
    resp = requests.get('https://api.line.me/v2/bot/richmenu/list', headers=HEADERS)
    for menu in resp.json().get('richmenus', []):
        mid = menu['richMenuId']
        requests.delete(f'https://api.line.me/v2/bot/richmenu/{mid}', headers=HEADERS)
        print(f'已刪除舊選單：{mid}')


if __name__ == '__main__':
    image_path = os.path.join(os.path.dirname(__file__), 'rich_menu.png')
    if not os.path.exists(image_path):
        print('請先執行 python3 generate_rich_menu.py 生成圖片')
        exit(1)

    delete_all_rich_menus()
    rid = create_rich_menu()
    upload_image(rid, image_path)
    set_default(rid)
    print('\n完成！重新開啟 LINE 聊天室即可看到選單。')
