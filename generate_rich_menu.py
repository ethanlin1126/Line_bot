"""
生成 Rich Menu 背景圖片（2500x843，2x2）
執行：python3 generate_rich_menu.py
輸出：rich_menu.png
"""
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

W, H = 2500, 843
COL, ROW = 2, 2
CW = W // COL
RH = H // ROW

BUTTONS = [
    {"label": "想跟我說什麼呢📝", "color": "#E8D5F5"},
    {"label": "累了嗎？休息一下🌳", "color": "#C6DCF7"},
    {"label": "想吃什麼呢😋",     "color": "#FADADD"},
    {"label": "想我了嗎🗓️",      "color": "#FAE3C6"},
]

DIVIDER = "#C8B8B8"
TEXT_COLOR = "#4A3A3A"
FONT_SIZE = 110


def get_font(size):
    candidates = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), "#FFF8F5")
draw = ImageDraw.Draw(img)
font_label = get_font(FONT_SIZE)

# 先畫背景和格線
for i, btn in enumerate(BUTTONS):
    col = i % COL
    row = i // COL
    x0, y0 = col * CW, row * RH
    x1, y1 = x0 + CW, y0 + RH
    draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=btn["color"])

draw.line([(CW, 0), (CW, H)], fill=DIVIDER, width=3)
draw.line([(0, RH), (W, RH)], fill=DIVIDER, width=3)

# 用 Pilmoji 畫文字（支援 emoji）
with Pilmoji(img) as pilmoji:
    for i, btn in enumerate(BUTTONS):
        col = i % COL
        row = i // COL
        x0, y0 = col * CW, row * RH

        # 計算文字寬高以置中
        w, h = pilmoji.getsize(btn["label"], font=font_label, emoji_scale_factor=1.15)
        lx = x0 + (CW - w) // 2
        ly = y0 + (RH - h) // 2
        pilmoji.text((lx, ly), btn["label"], fill=TEXT_COLOR, font=font_label, emoji_scale_factor=1.15)

img.save("rich_menu.png")
print("rich_menu.png 已生成！")
