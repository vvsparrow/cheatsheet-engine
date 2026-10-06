import os

from PIL import Image, ImageDraw, ImageFont

from data.irregular_verbs import VERBS

BG_COLOR = (18, 20, 24)  # Темно-графитовый фон
HEADER_COLOR = (100, 200, 255)  # Голубой (шапка)
V1_COLOR = (240, 240, 240)  # Светло-серый (V1)
V2_COLOR = (255, 215, 0)  # Золотистый (V2)
V3_COLOR = (120, 255, 120)  # Ярко-зеленый (V3)
TRANS_COLOR = (160, 165, 175)  # Приглушенный серый (перевод)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def get_fonts(size):
    font = ImageFont.truetype(FONT_PATH, size)
    bold_path = FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else FONT_PATH
    bold_font = ImageFont.truetype(bold_path, size)
    return font, bold_font


def render_grid_wallpaper(
    w, h, font_size, line_spacing, margin_x, margin_y, col_width, offsets, out_path
):
    img = Image.new("RGB", (w, h), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    font, bold_font = get_fonts(font_size)
    dx_v1, dx_v2, dx_v3, dx_tr = offsets

    verbs_per_col = 40
    for col in range(3):
        x = margin_x + col * col_width
        y = margin_y

        draw.text((x + dx_v1, y), "V1 (Infinitive)", fill=HEADER_COLOR, font=bold_font)
        draw.text((x + dx_v2, y), "V2 (Past)", fill=HEADER_COLOR, font=bold_font)
        draw.text((x + dx_v3, y), "V3 (Participle)", fill=HEADER_COLOR, font=bold_font)
        draw.text((x + dx_tr, y), "Translation", fill=HEADER_COLOR, font=bold_font)

        y += font_size + line_spacing + 6
        draw.line([(x, y - 3), (x + col_width - 25, y - 3)], fill=HEADER_COLOR, width=1)

        start_idx = col * verbs_per_col
        end_idx = start_idx + verbs_per_col
        for v1, v2, v3, trans in VERBS[start_idx:end_idx]:
            draw.text((x + dx_v1, y), v1, fill=V1_COLOR, font=font)
            draw.text((x + dx_v2, y), v2, fill=V2_COLOR, font=font)
            draw.text((x + dx_v3, y), v3, fill=V3_COLOR, font=bold_font)
            draw.text((x + dx_tr, y), trans, fill=TRANS_COLOR, font=font)
            y += font_size + line_spacing

    img.save(out_path)
    print(f"[OK] Создан: {out_path}")


def render_phone_scroll(out_path):
    screen_w, screen_h = 1080, 2412
    total_w = screen_w * 3
    img = Image.new("RGB", (total_w, screen_h), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_size, line_spacing = 26, 22
    font, bold_font = get_fonts(font_size)
    margin_x, margin_y = 50, 160
    offsets = (0, 230, 470, 710)

    for page in range(3):
        page_x = page * screen_w + margin_x
        y = margin_y

        draw.text((page_x + offsets[0], y), "V1", fill=HEADER_COLOR, font=bold_font)
        draw.text((page_x + offsets[1], y), "V2", fill=HEADER_COLOR, font=bold_font)
        draw.text((page_x + offsets[2], y), "V3", fill=HEADER_COLOR, font=bold_font)
        draw.text(
            (page_x + offsets[3], y), "Перевод", fill=HEADER_COLOR, font=bold_font
        )

        y += font_size + line_spacing + 10
        draw.line(
            [(page_x, y - 8), (page_x + screen_w - (margin_x * 2), y - 8)],
            fill=HEADER_COLOR,
            width=2,
        )

        start_idx = page * 40
        end_idx = start_idx + 40
        for v1, v2, v3, trans in VERBS[start_idx:end_idx]:
            draw.text((page_x + offsets[0], y), v1, fill=V1_COLOR, font=font)
            draw.text((page_x + offsets[1], y), v2, fill=V2_COLOR, font=font)
            draw.text((page_x + offsets[2], y), v3, fill=V3_COLOR, font=bold_font)
            draw.text((page_x + offsets[3], y), trans, fill=TRANS_COLOR, font=font)
            y += font_size + line_spacing

    img.save(out_path)
    print(f"[OK] Создан (Панорама): {out_path}")


def render_lockscreen_cards(out_dir):
    cards_dir = os.path.join(out_dir, "mobile_lockscreen_cards")
    os.makedirs(cards_dir, exist_ok=True)

    W, H = 1290, 2796

    top_y = int(H * 0.38)
    bottom_y = int(H * 0.85)
    margin_x = int(W * 0.07)

    available_width = W - (2 * margin_x)
    available_height = bottom_y - top_y

    verbs_per_card = 20
    total_cards = len(VERBS) // verbs_per_card
    total_rows = verbs_per_card + 1

    row_height = available_height // (total_rows + 1)
    font_size = int(row_height * 0.52)
    line_spacing = row_height - font_size

    font, bold_font = get_fonts(font_size)

    col_v1 = margin_x
    col_v2 = margin_x + int(available_width * 0.18)
    col_v3 = margin_x + int(available_width * 0.38)
    col_tr = margin_x + int(available_width * 0.60)

    for card_idx in range(total_cards):
        img = Image.new("RGB", (W, H), color=BG_COLOR)
        draw = ImageDraw.Draw(img)
        y = top_y

        draw.text((col_v1, y), "V1", fill=HEADER_COLOR, font=bold_font)
        draw.text((col_v2, y), "V2", fill=HEADER_COLOR, font=bold_font)
        draw.text((col_v3, y), "V3", fill=HEADER_COLOR, font=bold_font)
        draw.text((col_tr, y), "Перевод", fill=HEADER_COLOR, font=bold_font)

        y += font_size + line_spacing
        draw.line(
            [(margin_x, y - line_spacing // 2), (W - margin_x, y - line_spacing // 2)],
            fill=HEADER_COLOR,
            width=3,
        )

        start = card_idx * verbs_per_card
        end = start + verbs_per_card
        for v1, v2, v3, trans in VERBS[start:end]:
            draw.text((col_v1, y), v1, fill=V1_COLOR, font=font)
            draw.text((col_v2, y), v2, fill=V2_COLOR, font=font)
            draw.text((col_v3, y), v3, fill=V3_COLOR, font=bold_font)
            draw.text((col_tr, y), trans, fill=TRANS_COLOR, font=font)
            y += font_size + line_spacing

        card_path = os.path.join(
            cards_dir, f"lockscreen_part_{card_idx + 1}_of_{total_cards}.png"
        )
        img.save(card_path)

    print(
        f"[OK] Создан пак из {total_cards} карточек для экрана блокировки: {cards_dir}"
    )


def generate_all():
    out_dir = os.path.join(os.path.dirname(__file__), "screensavers")
    os.makedirs(out_dir, exist_ok=True)
    print("--- Запуск генерации полного пакета обоев ---")

    render_grid_wallpaper(
        w=2560,
        h=1440,
        font_size=19,
        line_spacing=9,
        margin_x=260,
        margin_y=115,
        col_width=740,
        offsets=(0, 155, 310, 485),
        out_path=os.path.join(out_dir, "verbs_desktop_2K_2560x1440.png"),
    )

    render_grid_wallpaper(
        w=1920,
        h=1080,
        font_size=14,
        line_spacing=7,
        margin_x=120,
        margin_y=80,
        col_width=570,
        offsets=(0, 120, 240, 375),
        out_path=os.path.join(out_dir, "verbs_laptop_1080p_1920x1080.png"),
    )

    render_grid_wallpaper(
        w=2048,
        h=2732,
        font_size=23,
        line_spacing=26,
        margin_x=80,
        margin_y=280,
        col_width=640,
        offsets=(0, 135, 270, 420),
        out_path=os.path.join(out_dir, "verbs_tablet_ipad_2048x2732.png"),
    )

    render_phone_scroll(os.path.join(out_dir, "verbs_phone_home_scroll_3240x2412.png"))

    render_lockscreen_cards(out_dir)

    print("--- Все устройства успешно сгенерированы! ---")


if __name__ == "__main__":
    generate_all()
