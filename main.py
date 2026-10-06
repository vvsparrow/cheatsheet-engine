import os

from PIL import Image, ImageDraw, ImageFont

# --- ОБЩАЯ ЦВЕТОВАЯ ПАЛИТРА ---
BG_COLOR = (18, 20, 24)  # Темно-графитовый фон
HEADER_COLOR = (100, 200, 255)  # Голубой (шапка)
V1_COLOR = (240, 240, 240)  # Светло-серый (V1)
V2_COLOR = (255, 215, 0)  # Золотистый (V2)
V3_COLOR = (120, 255, 120)  # Ярко-зеленый (V3)
TRANS_COLOR = (160, 165, 175)  # Приглушенный серый (перевод)

# Шрифты
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# Ровно 120 глаголов (AmE, строгий алфавитный порядок)
VERBS = [
    ("arise", "arose", "arisen", "возникать"),
    ("awake", "awoke", "awoken", "будить/просыпаться"),
    ("be", "was/were", "been", "быть"),
    ("bear", "bore", "born", "рождать/носить"),
    ("beat", "beat", "beaten", "бить"),
    ("become", "became", "become", "становиться"),
    ("begin", "began", "begun", "начинать"),
    ("bend", "bent", "bent", "гнуть"),
    ("bet", "bet", "bet", "ставить ставку"),
    ("bind", "bound", "bound", "связывать"),
    ("bite", "bit", "bitten", "кусать"),
    ("bleed", "bled", "bled", "кровоточить"),
    ("blow", "blew", "blown", "дуть"),
    ("break", "broke", "broken", "ломать"),
    ("breed", "bred", "bred", "разводить"),
    ("bring", "brought", "brought", "приносить"),
    ("build", "built", "built", "строить"),
    ("burn", "burned", "burned", "жечь/гореть"),
    ("burst", "burst", "burst", "взрываться"),
    ("buy", "bought", "bought", "покупать"),
    ("catch", "caught", "caught", "ловить"),
    ("choose", "chose", "chosen", "выбирать"),
    ("come", "came", "come", "приходить"),
    ("cost", "cost", "cost", "стоить"),
    ("creep", "crept", "crept", "ползти"),
    ("cut", "cut", "cut", "резать"),
    ("deal", "dealt", "dealt", "иметь дело"),
    ("dig", "dug", "dug", "копать"),
    ("do", "did", "done", "делать"),
    ("draw", "drew", "drawn", "рисовать/тянуть"),
    ("dream", "dreamed", "dreamed", "мечтать"),
    ("drink", "drank", "drunk", "пить"),
    ("drive", "drove", "driven", "водить авто"),
    ("eat", "ate", "eaten", "есть/кушать"),
    ("fall", "fell", "fallen", "падать"),
    ("feed", "fed", "fed", "кормить"),
    ("feel", "felt", "felt", "чувствовать"),
    ("fight", "fought", "fought", "бороться"),
    ("find", "found", "found", "находить"),
    ("fit", "fit", "fit", "подходить по размеру"),
    ("fly", "flew", "flown", "летать"),
    ("forbid", "forbade", "forbidden", "запрещать"),
    ("forget", "forgot", "forgotten", "забывать"),
    ("forgive", "forgave", "forgiven", "прощать"),
    ("freeze", "froze", "frozen", "замерзать"),
    ("get", "got", "gotten", "получать"),
    ("give", "gave", "given", "давать"),
    ("go", "went", "gone", "идти/ехать"),
    ("grow", "grew", "grown", "расти"),
    ("hang", "hung", "hung", "висеть/вешать"),
    ("have", "had", "had", "иметь"),
    ("hear", "heard", "heard", "слышать"),
    ("hide", "hid", "hidden", "прятать"),
    ("hit", "hit", "hit", "ударять"),
    ("hold", "held", "held", "держать"),
    ("hurt", "hurt", "hurt", "ранить/болеть"),
    ("keep", "kept", "kept", "хранить"),
    ("know", "knew", "known", "знать"),
    ("lay", "laid", "laid", "класть"),
    ("lead", "led", "led", "вести"),
    ("leave", "left", "left", "покидать"),
    ("lend", "lent", "lent", "одалживать"),
    ("let", "let", "let", "позволять"),
    ("lie", "lay", "lain", "лежать"),
    ("light", "lit", "lit", "освещать/зажигать"),
    ("lose", "lost", "lost", "терять"),
    ("make", "made", "made", "делать/создавать"),
    ("mean", "meant", "meant", "значить"),
    ("meet", "met", "met", "встречать"),
    ("mistake", "mistook", "mistaken", "ошибаться"),
    ("pay", "paid", "paid", "платить"),
    ("put", "put", "put", "класть/ставить"),
    ("quit", "quit", "quit", "бросать/увольняться"),
    ("read", "read", "read", "читать"),
    ("ride", "rode", "ridden", "ехать верхом"),
    ("ring", "rang", "rung", "звонить"),
    ("rise", "rose", "risen", "подниматься"),
    ("run", "ran", "run", "бежать"),
    ("say", "said", "said", "сказать"),
    ("see", "saw", "seen", "видеть"),
    ("seek", "sought", "sought", "искать"),
    ("sell", "sold", "sold", "продавать"),
    ("send", "sent", "sent", "отправлять"),
    ("set", "set", "set", "устанавливать"),
    ("sew", "sewed", "sewn", "шить"),
    ("shake", "shook", "shaken", "трясти"),
    ("shine", "shone", "shone", "сиять"),
    ("shoot", "shot", "shot", "стрелять"),
    ("show", "showed", "shown", "показывать"),
    ("shut", "shut", "shut", "закрывать"),
    ("sing", "sang", "sung", "петь"),
    ("sink", "sank", "sunk", "тонуть"),
    ("sit", "sat", "sat", "сидеть"),
    ("sleep", "slept", "slept", "спать"),
    ("slide", "slid", "slid", "скользить"),
    ("speak", "spoke", "spoken", "говорить"),
    ("spend", "spent", "spent", "тратить"),
    ("spill", "spilled", "spilled", "разливать"),
    ("spin", "spun", "spun", "крутить/вращать"),
    ("split", "split", "split", "разделять/делить счёт"),
    ("spread", "spread", "spread", "распространять/мазать"),
    ("stand", "stood", "stood", "стоять"),
    ("steal", "stole", "stolen", "красть"),
    ("stick", "stuck", "stuck", "втыкать/липнуть"),
    ("strike", "struck", "struck", "бастовать/бить"),
    ("swear", "swore", "sworn", "клясться"),
    ("sweep", "swept", "swept", "мести"),
    ("swim", "swam", "swum", "плавать"),
    ("take", "took", "taken", "брать"),
    ("teach", "taught", "taught", "обучать"),
    ("tear", "tore", "torn", "рвать"),
    ("tell", "told", "told", "рассказывать"),
    ("think", "thought", "thought", "думать"),
    ("throw", "threw", "thrown", "бросать"),
    ("understand", "understood", "understood", "понимать"),
    ("upset", "upset", "upset", "расстраивать"),
    ("wake", "woke", "woken", "будить"),
    ("wear", "wore", "worn", "носить (одежду)"),
    ("win", "won", "won", "побеждать"),
    ("write", "wrote", "written", "писать"),
]


def get_fonts(size):
    font = ImageFont.truetype(FONT_PATH, size)
    bold_path = FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else FONT_PATH
    bold_font = ImageFont.truetype(bold_path, size)
    return font, bold_font


# 1. ГЕНЕРАТОР ДЛЯ МОНИТОРОВ И ПЛАНШЕТОВ (3 колонки по 40 глаголов)
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

        # Шапка
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


# 2. ГЕНЕРАТОР ПАНОРАМЫ ДЛЯ СМАРТФОНА (3 экрана со скроллом)
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


# 3. ГЕНЕРАТОР СЕРИИ КАРТОЧЕК ДЛЯ ЭКРАНА БЛОКИРОВКИ (Safe Zone под часы)
def render_lockscreen_cards(out_dir):
    cards_dir = os.path.join(out_dir, "mobile_lockscreen_cards")
    os.makedirs(cards_dir, exist_ok=True)

    # Универсальное разрешение 19.5:9
    W, H = 1290, 2796

    # Границы контента в процентах (38% сверху под часы, 15% снизу под свайп)
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

        # Шапка карточки
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

    # 1. ПК 2K (2560x1440) — с отступом слева под ярлыки
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

    # 2. Ноутбук Full HD (1920x1080)
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

    # 3. Планшет iPad Pro / Air / Android Tab (2048x2732, соотношение 4:3)
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

    # 4. Смартфон (Рабочий стол — Панорама на 3 экрана со скроллом)
    render_phone_scroll(os.path.join(out_dir, "verbs_phone_home_scroll_3240x2412.png"))

    # 5. Смартфон (Экран блокировки — 6 карточек с безопасной зоной под часы)
    render_lockscreen_cards(out_dir)

    print("--- Все устройства успешно сгенерированы! ---")


if __name__ == "__main__":
    generate_all()
