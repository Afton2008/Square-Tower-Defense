import pygame
import sys
import math
import random
import json
import os

SAVE_FILE = "save_data.json"

# ---------------- SAVE SYSTEM ----------------
def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"shape": 0, "new_year_2026_claimed": False}
    return {"shape": 0, "new_year_2026_claimed": False}

def save_data(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

save = load_save()

towers_data = {
    "Pistol (400)":  {"price": 0,    "owned": True},
    "Shotgun (550)": {"price": 250,  "owned": True},
    "AR (480)":      {"price": 300,  "owned": True},
    "AK (650)":      {"price": 450,  "owned": True},

    # Tower belum owned
    "SMG (580)":     {"price": 600,  "owned": False},
    "Mafia (700)":   {"price": 800,  "owned": False},
    "Sniper (950)":  {"price": 900,  "owned": False},
    "Laser (1200)":  {"price": 1500, "owned": False},
    "Frost Blaster (1800)":  {"price": 0, "owned": False},
}

def save_inventory():
    inv = {name: data["owned"] for name, data in towers_data.items()}
    save["inventory"] = inv
    save_data(save)

def load_inventory():
    inv = save.get("inventory", {})
    for name, status in inv.items():
        if name in towers_data:
            towers_data[name]["owned"] = status

load_inventory()
pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1400, 680
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 40, 40)
GREEN_BG = (20, 120, 20)
CREAM = (240, 220, 170)
CREAM2 = (180, 160, 120)
LIGHT_GRAY = (240, 240, 240)
MID_GRAY = (200, 200, 200)
DARK_GRAY_TEXT = (70, 70, 70)
BLUE_BUTTON = (50, 120, 200)
RED_BUTTON = (200, 60, 60)
BLUE_COST = (0, 0, 150)

font_big = pygame.font.Font(None, 90)
font_mid = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 36)

current_lose_message = None
current_win_message = None
FONT_TOWER = pygame.font.SysFont("Arial", 18, bold=True)
FONT_UI_SMALL = pygame.font.SysFont("Arial", 16)
FONT_UI_MED = pygame.font.SysFont("Arial", 20)

# ------------------------------------------------
# GAME DATA (3 GAME)
# ------------------------------------------------
game_data = {
    1: {"name": "Circle Forest", "money": 1000, "base_hp": 10_000,
        "game_type": "td", "enemy": "circle" },

    2: {"name": "Coming Soon", "money": 1000, "base_hp": 5_000,
        "game_type": "td", "enemy": "triangle" },

    3: {"name": "????", "game_type": "story",
        "dialog_speed": 2, "chapters": 5 }
}

current_game = None
game_state = "intro"
inventory_state = "closed"
home_state = "home"
chapter1_state = "start"
td_state = "menu"
event_state = "start_screen"

# ------------------------------------------------
# ANIMASI INTRO — SQUARE BERGERAK
# ------------------------------------------------
square_x = 200
square_y = 340
square_speed = 4
square_dir = 1
info_page = 0
MAX_INFO_PAGE = 1

def draw_wrapped_text_center(surface, text, font, color, y, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, color)

        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "

    lines.append(current_line)

    for line in lines:
        rendered = font.render(line, True, color)
        surface.blit(
            rendered,
            (surface.get_width()//2 - rendered.get_width()//2, y)
        )
        y += rendered.get_height() + 5

def draw_text_center(text, font_obj, color, surf, y):
    rendered = font_obj.render(text, True, color)
    surf.blit(rendered, (surf.get_width()//2 - rendered.get_width()//2, y))

try:
    snow_particles
except NameError:
    snow_particles = []

def update_snow(screen, WIDTH, HEIGHT, spawn_rate=1):
    for _ in range(spawn_rate):
        snow_particles.append([random.randint(0, WIDTH), 0, random.randint(1,3)])

    for p in snow_particles[:]:
        p[1] += p[2]
        if p[1] > HEIGHT:
            snow_particles.remove(p)
            continue
        pygame.draw.circle(screen, (230, 240, 255), (p[0], p[1]), 3)

def fade_in(duration=900):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0,0,0))
    start = pygame.time.get_ticks()
    while True:
        now = pygame.time.get_ticks()
        t = now - start
        if t >= duration:
            break
        alpha = 255 - int((t / duration) * 255)
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0,0))
        pygame.display.update()
        clock.tick(FPS)

def winter_event_cutscene():
    texts = [
        "Setelah para Square mengalahkan Cyclo Lead...",
        "Mereka membawa para Circle ke markas untuk diberi kehidupan baru.",
        "Namun salju turun begitu lebat hingga menutup jalan pulang...",
        "Di tengah kekacauan itu, Pi Master dan pengikutnya kabur ke hutan salju!",
        "Square dan Circle mengejarnya jauh ke dalam hutan...",
        "Tetapi semakin dalam mereka masuk, semakin banyak mata mengintai...",
        "Sosok tinggi, kurus, dingin... simbol biru menyala...",
        "Suku kuno muncul dari balik kabut: ACOLYTE Of WENDIGO!",
        "Bertahanlah. Perburuan dimulai..."
    ]

    index = 0
    fade_in(700)

    while True:
        screen.fill((8, 14, 25))
        update_snow(screen, WIDTH, HEIGHT, spawn_rate=1)

        shake_x = random.randint(-1,1)
        shake_y = random.randint(-1,1)

        draw_wrapped_text_center(
            screen,
            texts[index],
            font_mid,
            (230,230,255),
            HEIGHT//2 - 80 + shake_y,
            1100
        )
        tip = font_small.render("Klik/tekan untuk lanjut...", True, (190,190,200))
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT - 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                index += 1
                fade_in(350)
                if index >= len(texts):
                    global event_state
                    event_state = "start_screen"
                    return

        pygame.display.update()
        clock.tick(FPS)

def start_winter_game():
    global event_state, game_state
    game_state = "event"
    event_state = "playing"

def draw_intro_animation():
    global square_x, square_dir
    square_x += square_speed * square_dir

    if square_x > WIDTH - 200:
        square_dir = -1
    if square_x < 200:
        square_dir = 1

    pygame.draw.rect(screen, BLUE, (square_x, square_y, 80, 80), border_radius=5)

# ------------------------------------------------
# ANIMASI CHAPTER 1 — CIRCLE MERAH MUTER
# ------------------------------------------------
circle_angle = 0
def draw_circle_animation():
    global circle_angle
    circle_angle += 0.04
    cx = WIDTH - 250 + math.cos(circle_angle) * 120
    cy = 200 + math.sin(circle_angle) * 120
    pygame.draw.circle(screen, RED, (int(cx), int(cy)), 40)

# ------------------------------------------------
# DRAW BUTTON
# ------------------------------------------------
def draw_button(text, x, y, w, h, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    color = BLUE if rect.collidepoint(mouse_pos) else GRAY

    pygame.draw.rect(screen, color, rect, border_radius=25)

    label = font_mid.render(text, True, WHITE)
    screen.blit(label, (x + w//2 - label.get_width()//2,
                        y + h//2 - label.get_height()//2))
    return rect

# ------------------------------------------------
# INTRO SCREEN – LAYAR SENTUH
# ------------------------------------------------
def intro_screen():
    global game_state
    mouse_pos = pygame.mouse.get_pos()

    screen.fill(BLACK)

    draw_intro_animation()

    title = font_big.render("SQUARE TOWER DEFENSE", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    subtitle = font_mid.render("Version 1.1.1", True, GRAY)  
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 250))
    
    developer_text = font_small.render("Developed by Afton", True, LIGHT_GRAY)
    x_pos = WIDTH - developer_text.get_width() - 20
    y_pos = HEIGHT - developer_text.get_height() - 20
    screen.blit(developer_text, (x_pos, y_pos))

    start_btn = draw_button("Mulai", WIDTH//2 - 330, 370, 660, 120, mouse_pos)
    info_btn = draw_button("Info", WIDTH//2 - 330, 510, 660, 100, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(mouse_pos):
                game_state = "home"
            if info_btn.collidepoint(mouse_pos):
                game_state = "info"

    pygame.display.update()

def info_screen():
    global game_state, info_page
    mouse_pos = pygame.mouse.get_pos()

    screen.fill((20, 20, 30))

    title = font_big.render("UPDATE INFO", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    y_offset = 140
    line_spacing = 35

    # ======================
    # PAGE 0 (LAMA)
    # ======================
    if info_page == 0:
        v1_title = font_mid.render("Version 1.0.0 - 6 Desember 2025", True, (100, 200, 255))
        screen.blit(v1_title, (WIDTH//2 - v1_title.get_width()//2, y_offset))
        y_offset += 50
        
        v1_desc = font_small.render("Pertama dibuat Square TD", True, LIGHT_GRAY)
        screen.blit(v1_desc, (WIDTH//2 - v1_desc.get_width()//2, y_offset))
        y_offset += 80

        v2_title = font_mid.render("Version 1.0.1 - 19 Desember 2025", True, (100, 200, 255))
        screen.blit(v2_title, (WIDTH//2 - v2_title.get_width()//2, y_offset))
        y_offset += 50
        
        v2_desc = font_small.render("Penambahan mekanisme Reward Lose", True, LIGHT_GRAY)
        screen.blit(v2_desc, (WIDTH//2 - v2_desc.get_width()//2, y_offset))
        y_offset += 80

        v3_title = font_mid.render("Version 1.1.0 - 25 Desember 2025", True, (100, 200, 255))
        screen.blit(v3_title, (WIDTH//2 - v3_title.get_width()//2, y_offset))
        y_offset += 50
        
        v3_lines = [
            "Penambahan Winter Event 2025",
            "+10 Musuh dan Boss baru",
            "+1 Tower Eksklusif",
            "Penambahan Update Info"
        ]
        
        for line in v3_lines:
            line_text = font_small.render(line, True, LIGHT_GRAY)
            screen.blit(line_text, (WIDTH//2 - line_text.get_width()//2, y_offset))
            y_offset += line_spacing

    elif info_page == 1:
        v4_title = font_mid.render("Version 1.1.1 - 1 Januari 2026", True, (100, 200, 255))
        screen.blit(v4_title, (WIDTH//2 - v4_title.get_width()//2, y_offset))
        y_offset += 50

        v4_lines = [
            "Penambahan History",
            "Perbaikan musuh dan tower",
            "Penambahan Hadiah tahun baru 2026"
        ]

        for line in v4_lines:
            text = font_small.render(line, True, LIGHT_GRAY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += line_spacing

    back_btn = draw_button("Kembali", WIDTH//2 - 200, 580, 400, 80, mouse_pos)

    prev_btn = None
    next_btn = None

    if info_page > 0:
        prev_btn = draw_button("Prev", 60, 580, 200, 60, mouse_pos)

    if info_page < MAX_INFO_PAGE:
        next_btn = draw_button("Next", WIDTH - 260, 580, 200, 60, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_btn.collidepoint(mouse_pos):
                game_state = "intro"

            if prev_btn and prev_btn.collidepoint(mouse_pos):
                info_page -= 1

            if next_btn and next_btn.collidepoint(mouse_pos):
                info_page += 1

    pygame.display.update()

def home_screen():
    global game_state
    mouse_pos = pygame.mouse.get_pos()
    screen.fill((20, 20, 40))

    title = font_big.render("HOME", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

    # New Year 2026 Bonus Check
    if not save.get("new_year_2026_claimed", False):
        bonus_rect = pygame.Rect(WIDTH//2 - 250, 150, 800, 70)
        pygame.draw.rect(screen, (255, 215, 0), bonus_rect, border_radius=15)
        bonus_text = font_mid.render("BONUS TAHUN BARU 2026!", True, (0, 0, 0))
        screen.blit(bonus_text, (bonus_rect.centerx - bonus_text.get_width()//2, bonus_rect.centery - bonus_text.get_height()//2))

    btn_inventory = draw_button("Inventory", WIDTH//2 - 250, 240, 500, 90, mouse_pos)
    btn_story     = draw_button("Story",     WIDTH//2 - 250, 350, 500, 90, mouse_pos)
    btn_event     = draw_button("Event",     WIDTH//2 - 250, 460, 500, 90, mouse_pos)
    btn_history   = draw_button("History",   WIDTH//2 - 250, 570, 500, 90, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check New Year bonus claim
            if not save.get("new_year_2026_claimed", False):
                bonus_rect = pygame.Rect(WIDTH//2 - 250, 150, 800, 70)
                if bonus_rect.collidepoint(event.pos):
                    save["shape"] = save.get("shape", 0) + 2026
                    save["new_year_2026_claimed"] = True
                    save_data(save)
                    return

            if btn_inventory.collidepoint(mouse_pos):
                game_state = "inventory"

            if btn_story.collidepoint(mouse_pos):
                game_state = "menu"

            if btn_event.collidepoint(mouse_pos):
                event_menu()
                return

            if btn_history.collidepoint(mouse_pos):
                game_state = "history"

    pygame.display.update()

ITEMS_PER_PAGE = 6
inventory_page = 0
history_index = 0

def event_menu():
    global game_state, event_state
    clock_local = pygame.time.Clock()
    chapter1_completed = save.get("chapter1_completed", False)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        screen.fill((20, 30, 45))
        title = font_big.render("EVENT MENU", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        if not chapter1_completed:
            locked_rect = pygame.Rect(WIDTH//2 - 250, 220, 500, 110)
            pygame.draw.rect(screen, (80, 80, 80), locked_rect, border_radius=25)

            lock_size = 40
            lock_x = WIDTH//2 - lock_size//2
            lock_y = 240
            pygame.draw.rect(screen, (200, 200, 200), (lock_x, lock_y + 15, lock_size, 25), border_radius=5)
            pygame.draw.circle(screen, (200, 200, 200), (lock_x + lock_size//2, lock_y + 10), 12, 3)

            locked_text = font_mid.render("Winter Event 2025", True, (150, 150, 150))
            screen.blit(locked_text, (WIDTH//2 - locked_text.get_width()//2, 285))

            info_text = font_small.render("Selesaikan Chapter 1 untuk membuka", True, (200, 150, 100))
            screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 500))
            
        else:
            btn_we = draw_button("Winter Event 2025", WIDTH//2 - 250, 220, 500, 110, mouse_pos)
        
        btn_back = draw_button("Kembali", WIDTH//2 - 150, 360, 300, 90, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if chapter1_completed and btn_we.collidepoint(mouse_pos):
                    game_state = "event"
                    event_state = "cutscene"
                    winter_event_cutscene()
                    return

                if btn_back.collidepoint(mouse_pos):
                    return

        pygame.display.update()
        clock_local.tick(FPS)

ITEMS_PER_PAGE = 6
inventory_page = 0
history_index = 0

def inventory_screen():
    global game_state, inventory_page

    mouse_pos = pygame.mouse.get_pos()
    screen.fill((30, 30, 50))

    title = font_big.render("INVENTORY", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    shape_text = font_small.render(f"Shape: {save.get('shape', 0)}", True, WHITE)
    screen.blit(shape_text, (WIDTH - shape_text.get_width() - 40, 20))

    tower_list = list(towers_data.items())
    total = len(tower_list)
    max_page = (total - 1) // ITEMS_PER_PAGE

    start = inventory_page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = tower_list[start:end]

    buttons = []

    LEFT_X = 100
    RIGHT_X = 750
    ROW_START_Y = 140
    ROW_GAP = 150

    for i, (name, data) in enumerate(page_items):
        col = i % 2
        row = i // 2
        x = LEFT_X if col == 0 else RIGHT_X
        y = ROW_START_Y + row * ROW_GAP
        owned = data["owned"]
        price = data["price"]
        txt = font_mid.render(name, True, WHITE)
        screen.blit(txt, (x, y))

        is_frost_blaster = (name == "Frost Blaster (1800)")
        
        if owned:
            buy_btn = draw_button("Owned", x, y + 50, 250, 80, mouse_pos)
            buttons.append((name, buy_btn, owned, price, is_frost_blaster))
        elif is_frost_blaster:
            buy_btn = draw_button("Event Reward", x, y + 50, 250, 80, mouse_pos)
            buttons.append((name, buy_btn, owned, price, is_frost_blaster))
        else:
            buy_btn = draw_button(f"Buy ({price})", x, y + 50, 250, 80, mouse_pos)
            buttons.append((name, buy_btn, owned, price, is_frost_blaster))

    btn_back = draw_button("Kembali", WIDTH//2 - 200, 600, 400, 100, mouse_pos)

    btn_next = None
    if inventory_page < max_page:
        btn_next = draw_button("Next >", 1100, 580, 200, 80, mouse_pos)

    btn_prev = None
    if inventory_page > 0:
        btn_prev = draw_button("< Prev", 100, 580, 200, 80, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            for name, rect, owned, price, is_frost_blaster in buttons:
                if rect.collidepoint(mouse_pos):
                    if is_frost_blaster and not owned: show_frost_blaster_info_popup()
                    elif not owned and not is_frost_blaster:
                        if save["shape"] >= price:
                            save["shape"] -= price
                            towers_data[name]["owned"] = True
                            save_inventory()
                            save_data(save)
                        else:
                            print("Shape tidak cukup!")
                    break

            if btn_next and btn_next.collidepoint(mouse_pos):
                inventory_page += 1

            if btn_prev and btn_prev.collidepoint(mouse_pos):
                inventory_page -= 1

            if btn_back.collidepoint(mouse_pos):
                inventory_page = 0
                game_state = "home"

    pygame.display.update()

def show_frost_blaster_info_popup():
    popup_running = True
    
    while popup_running:
        mouse_pos = pygame.mouse.get_pos()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        box_w, box_h = 600, 400
        box_x = WIDTH//2 - box_w//2
        box_y = HEIGHT//2 - box_h//2
        
        pygame.draw.rect(screen, (160, 220, 255), (box_x, box_y, box_w, box_h), 10)
        pygame.draw.rect(screen, (20, 40, 80), (box_x+10, box_y+10, box_w-20, box_h-20))

        icon_size = 80
        icon_x = WIDTH//2 - icon_size//2
        icon_y = box_y + 40
        pygame.draw.rect(
            screen, (160, 220, 255),
            (icon_x, icon_y, icon_size, icon_size),
            border_radius=8
        )

        title = font_big.render("Frost Blaster", True, (160, 220, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, icon_y + 100))

        lock_text = font_mid.render("LOCKED", True, (255, 200, 100))
        screen.blit(lock_text, (WIDTH//2 - lock_text.get_width()//2, icon_y + 160))

        info_y = icon_y + 210
        info_texts = [
            "Tower eksklusif yang tidak bisa dibeli!",
            "",
            "Cara mendapatkan:",
            "Selesaikan Winter Event 2025",
            "dan kalahkan semua wave musuh",
        ]
        
        for i, text in enumerate(info_texts):
            if text == "Cara mendapatkan:":
                color = (255, 255, 100)
            else:
                color = (200, 220, 255)
            
            info = font_small.render(text, True, color)
            screen.blit(info, (WIDTH//2 - info.get_width()//2, info_y + i*30))

        ok_btn = pygame.Rect(WIDTH//2 - 100, box_y + box_h + 20, 200, 60)
        pygame.draw.rect(screen, (100, 180, 255), ok_btn, border_radius=10)
        ok_text = font_mid.render("OK", True, WHITE)
        screen.blit(
            ok_text,
            (ok_btn.x + ok_btn.w//2 - ok_text.get_width()//2,
             ok_btn.y + ok_btn.h//2 - ok_text.get_height()//2)
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_btn.collidepoint(mouse_pos):
                    popup_running = False
        
        pygame.display.update()
        clock.tick(FPS)

# ------------------------------------------------
# HISTORY SCREEN
# ------------------------------------------------
def history_screen():
    global game_state, history_index
    mouse_pos = pygame.mouse.get_pos()
    screen.fill((10, 15, 25))
    title = font_big.render("HISTORY: SQUARE TD", True, (255, 255, 100))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

    content_area = pygame.Rect(WIDTH//2 - 700, 120, 1400, HEIGHT - 220)
    story_sections = [
        {
            "title": "AWAL MULA DUNIA",
            "locked": False,
            "content": [
                "Pada awal mula keberadaan dunia, tidak pernah ada satu ras pun yang menguasai segalanya.",
                "Dunia terbentuk dari banyak ras sudut, masing-masing lahir dengan bentuk, filosofi, dan wilayah yang berbeda.",
                "",
                "Ras-ras tersebut dikenal sebagai:",
                "• Circle",
                "• Triangle", 
                "• Square",
                "• Pentagon",
                "• serta berbagai ras sudut lain yang tersebar di seluruh penjuru dunia.",
                "",
                "Setiap ras hidup terpisah, membangun peradaban mereka sendiri, dan dipimpin oleh seorang pemimpin tertinggi.",
                "Para pemimpin ini menjaga sebuah artefak inti yang disebut Core.",
            ]
        },
        {
            "title": "CORE",
            "locked": False,
            "content": [
                "Core bukan sekadar benda. Core adalah:",
                "• sumber kekuatan ras",
                "• penopang kehidupan wilayah",
                "• simbol eksistensi dan kedaulatan",
                "",
                "Selama sebuah Core tetap ada, ras tersebut akan terus bertahan, meskipun pemimpinnya berganti.",
                "Namun jika Core hancur atau direbut, maka ras tersebut akan kehilangan masa depannya.",
                "",
                "Perbedaan bentuk, kepentingan, dan wilayah membuat dunia tidak pernah benar-benar bersatu.",
                "Perang kecil, konflik wilayah, dan perselisihan ideologi terus terjadi tanpa akhir.",
            ]
        },
        {
            "title": "ORGANISASI SQUARE TD",
            "locked": False,
            "content": [
                "Di tengah dunia yang terpecah belah tersebut, muncullah sebuah organisasi dengan ambisi besar.",
                "Sebuah organisasi yang percaya bahwa perdamaian hanya dapat tercapai melalui persatuan mutlak.",
                "",
                "Organisasi itu dikenal sebagai: ORGANISASI SQUARE TD",
                "Pemimpin mereka adalah sosok visioner bernama Commander Square.",
                "",
                "Commander Square percaya bahwa:",
                "\"Selama Core-Core tetap terpisah, dunia akan terus berada dalam siklus kehancuran.\"",
                "",
                "Ia meyakini sebuah ramalan kuno yang dikenal sebagai Legenda Core.",
                "Legenda tersebut menyatakan bahwa jika seluruh Core disatukan, maka:",
                "• perang akan berakhir",
                "• dunia akan berada di bawah satu sistem",
                "• dan keseimbangan abadi akan tercipta",
                "",
                "Sebagai langkah pertama menuju visi tersebut,",
                "Organisasi Square TD menetapkan target awal mereka: Wilayah Circle",
            ]
        },
        {
            "title": "CHAPTER I: CIRCLE INVASION",
            "locked": not save.get("chapter1_completed", False),
            "unlock_text": "Menangkan Chapter I untuk membuka",
            "content": [
                "Wilayah Circle dikenal sebagai daerah dengan keseimbangan sempurna dan pertahanan alami yang kuat.",
                "Wilayah ini dipimpin oleh seorang pemimpin legendaris bernama: Cyclo Lead",
                "",
                "Berbeda dengan pemimpin ras lainnya, Core Circle tidak disimpan terpisah.",
                "Core tersebut menyatu langsung di dalam tubuh Cyclo Lead.",
                "",
                "Selama Cyclo Lead hidup:",
                "• Core Circle tidak bisa dipisahkan",
                "• Wilayah Circle tetap stabil",
                "• Ras Circle berada di puncak kekuatannya",
                "",
                "Cyclo Lead tidak memimpin sendirian.",
                "Ia didampingi oleh dua asisten setia yang menjadi pilar kekuatan Circle:",
                "• Pi Master – ahli strategi dan manipulasi energi",
                "• Mafia Cent – komandan pasukan garis depan",
                "",
                "Ketiganya membentuk trinitas kekuasaan Circle.",
            ]
        },
        {
            "title": "PERANG CIRCLE",
            "locked": not save.get("chapter1_completed", False),
            "content": [
                "Organisasi Square TD melancarkan invasi besar-besaran ke wilayah Circle.",
                "Tujuan mereka jelas dan tanpa kompromi: Merebut Core Circle.",
                "",
                "Pertempuran dahsyat pun terjadi.",
                "Benturan bentuk dan energi memenuhi medan perang.",
                "Wilayah Circle yang damai berubah menjadi zona kehancuran.",
                "",
                "Pada puncak pertempuran, Cyclo Lead akhirnya gugur.",
                "Bersamaan dengan kematiannya:",
                "• Core Circle terlepas",
                "• keseimbangan wilayah runtuh",
                "• dan kekuasaan ras Circle jatuh",
                "",
                "Organisasi Square TD berhasil menguasai Core Circle.",
            ]
        },
        {
            "title": "CORE CIRCLE",
            "locked": not save.get("chapter1_completed", False),
            "content": [
                "Setelah perang berakhir,",
                "Organisasi Square TD tidak memusnahkan ras Circle yang tersisa.",
                "",
                "Sebaliknya, mereka:",
                "• mengamankan para Circle",
                "• membawa Core Circle",
                "• dan memulai perjalanan menuju markas utama",
                "",
                "Tujuan mereka adalah:",
                "memberi kehidupan baru bagi ras Circle di bawah satu dunia yang bersatu.",
                "",
                "Namun perjalanan tersebut tidak berjalan sesuai rencana.",
            ]
        },
        {
            "title": "WINTER EVENT 2025: ACOLYTE OF WENDIGO",
            "locked": not save.get("winter_event_completed", False),
            "unlock_text": "Menangkan Winter Event 2025 untuk membuka",
            "content": [
                "Di tengah perjalanan menuju markas, cuaca berubah secara tiba-tiba.",
                "Salju turun perlahan… lalu semakin lebat… semakin dingin…",
                "hingga berubah menjadi badai yang membekukan.",
                "",
                "• Jalur perjalanan tertutup",
                "• Pandangan terbatas",
                "• Waktu seolah melambat",
                "",
                "Dalam kekacauan tersebut, pengkhianatan terjadi.",
            ]
        },
        {
            "title": "PENGKHIANATAN DI TENGAH SALJU",
            "locked": not save.get("winter_event_completed", False),
            "content": [
                "Memanfaatkan kondisi yang kacau, Pi Master mengambil kesempatan.",
                "Bersama pasukan setianya, ia melarikan diri ke dalam hutan bersalju,",
                "tanpa sepengetahuan Organisasi Square TD.",
                "",
                "Mengetahui hal tersebut, Organisasi Square TD dan para Circle yang tersisa",
                "membuat keputusan berbahaya: Mereka bersatu untuk mengejar Pi Master.",
            ]
        },
        {
            "title": "HUTAN BERSALJU",
            "locked": not save.get("winter_event_completed", False),
            "content": [
                "Pengejaran membawa mereka semakin dalam ke hutan.",
                "",
                "Semakin jauh mereka melangkah:",
                "• udara terasa lebih berat",
                "• bayangan bergerak di antara pepohonan",
                "• tatapan terasa dari segala arah",
                "",
                "Hingga akhirnya mereka menyadari satu hal mengerikan:",
                "Mereka telah memasuki wilayah terlarang.",
            ]
        },
        {
            "title": "SUKU ACOLYTE OF WENDIGO",
            "locked": not save.get("winter_event_completed", False),
            "content": [
                "Wilayah tersebut adalah milik: Suku Acolyte of Wendigo",
                "Sebuah suku misterius dari ras Circle yang telah lama terisolasi.",
                "",
                "Suku ini dipimpin oleh seorang pemimpin fanatik bernama: Grand Shaman",
                "",
                "Grand Shaman memimpin pasukan mengerikan:",
                "• Haunting Wendigo",
                "• Crying Wendigo",
                "• Corrupted Pi Master",
                "",
                "Ia memegang sebuah artefak gelap: Tongkat Corrupt",
                "",
                "Pi Master adalah salah satu korban Corrupt tersebut,",
                "kehilangan kendali atas pikirannya.",
            ]
        },
        {
            "title": "PERTEMPURAN DI WILAYAH ACOLYTE",
            "locked": not save.get("winter_event_completed", False),
            "content": [
                "Tidak ada jalan mundur.",
                "Organisasi Square TD dan para Circle terpaksa berperang",
                "melawan Suku Acolyte of Wendigo.",
                "",
                "Pertempuran berlangsung di tengah hutan bersalju.",
                "Pasukan Wendigo menyerang tanpa henti,",
                "sementara kekuatan Corrupt membuat pertempuran semakin berat.",
                "",
                "Namun perlahan, pertahanan Grand Shaman mulai runtuh.",
                "Pada akhirnya, Grand Shaman dikalahkan.",
                "",
                "Tubuhnya membatu, dan Tongkat Corrupt berhasil direbut.",
            ]
        },
        {
            "title": "AKHIR KEKACAUAN",
            "locked": not save.get("winter_event_completed", False),
            "content": [
                "Dengan jatuhnya Grand Shaman:",
                "• pengaruh Corrupt menghilang",
                "• para korban dibebaskan",
                "• Pi Master kembali sadar",
                "",
                "Pi Master kembali ditangkap oleh Organisasi Square TD.",
                "Salju pun mereda. Kutukan hutan menghilang.",
                "",
                "Perjalanan menuju markas akhirnya dapat dilanjutkan.",
                "",
                "Di markas, Organisasi Square TD memberi para Circle tempat tinggal aman, hidup, makmur, dan hidup berdampingan",
                "Dengan perdamaian tercipta, Organisasi Square juga berhasil merekrut Circle sebagai pasukan.",
                "",
                "dan kini mereka siap melanjutkan pencarian target Core berikutnya.",
            ]
        }
    ]
      
    section = story_sections[history_index]
    title_color = (255, 200, 100) if not section["locked"] else (120, 120, 140)
    section_title = font_mid.render(section["title"], True, title_color)
    screen.blit(section_title, (content_area.left + 20, content_area.top))

    y = content_area.top + 60
    line_height = 28
    if section["locked"]:
        lock_text = font_small.render("? " + section.get("unlock_text", "Locked"), True, (150, 150, 170))
        screen.blit(lock_text, (content_area.left + 40, y))
    else:
        for line in section["content"]:
            color = (180, 200, 255) if line.startswith("•") else (200, 220, 240)
            line_surf = font_small.render(line, True, color)
            screen.blit(line_surf, (content_area.left + 40, y))
            y += line_height

    prev_btn = draw_button("Prev", content_area.left, HEIGHT - 650, 180, 50, mouse_pos)
    next_btn = draw_button("Next", content_area.right - 180, HEIGHT - 650, 180, 50, mouse_pos)
    back_btn = draw_button("Kembali", content_area.right - 270, HEIGHT - 80, 300, 55, mouse_pos)

    page_text = font_small.render(f"{history_index + 1} / {len(story_sections)}", True, (150, 150, 170))
    screen.blit(page_text, (WIDTH//2 - page_text.get_width()//2, HEIGHT - 140))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_btn.collidepoint(mouse_pos):
                game_state = "home"
            if prev_btn.collidepoint(mouse_pos):
                history_index = max(0, history_index - 1)
            if next_btn.collidepoint(mouse_pos):
                if history_index < len(story_sections) - 1:
                    history_index += 1
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                history_index = max(0, history_index - 1)
            elif event.key == pygame.K_RIGHT:
                if history_index < len(story_sections) - 1:
                    history_index += 1
            elif event.key == pygame.K_ESCAPE:
                game_state = "home"
    
    pygame.display.update()

# ------------------------------------------------
# MENU CHAPTER – LAYAR SENTUH
# ------------------------------------------------
def chapter_menu():
    global current_game, game_state
    mouse_pos = pygame.mouse.get_pos()

    screen.fill((10, 20, 10))

    title = font_big.render("Pilih Game", True, YELLOW)
    screen.blit(title, (100, 50))

    btn1 = draw_button("Chapter I – Circle Invasion", 100, 160, 650, 120, mouse_pos)
    btn2 = draw_button("Chapter II – Triangle War",   100, 300, 650, 120, mouse_pos)
    btn3 = draw_button("Chapter III – Slavery Square",100, 440, 650, 120, mouse_pos)

    btn_back = draw_button("Kembali", 100, 580, 300, 100, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn1.collidepoint(mouse_pos): 
                current_game = 1; game_state = "game"
            if btn2.collidepoint(mouse_pos): 
                current_game = 2; game_state = "game"
            if btn3.collidepoint(mouse_pos): 
                current_game = 3; game_state = "game"

            if btn_back.collidepoint(mouse_pos):
                game_state = "home"

    pygame.display.update()

# ------------------------------------------------
# PATH / WAYPOINTS for Chapter I
# ------------------------------------------------
path_waypoints = [
    (300, -40),
    (300, 150),
    (550, 150),
    (550, 350),
    (250, 350),
    (250, 550),
    (900, 550),
    (900, 250),
    (1200, 250),
    (1200, 450),
    (WIDTH + 40, 450)
]

def draw_path(surf, waypoints, width=80):
    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i+1]

        pygame.draw.line(surf, CREAM, (x1, y1), (x2, y2), width)

waves = [
    [   # Wave 1
        {"type": "basic", "count": 12, "interval": 600},
        {"type": "basic", "count": 4, "interval": 0}
    ],
    [   # Wave 2
        {"type": "basic", "count": 18, "interval": 400},
        {"type": "basic", "count": 3, "interval": 0}
    ],
    [   # Wave 3
        {"type": "basic", "count": 14, "interval": 450},
        {"type": "fast", "count": 16, "interval": 350}
    ],
    [   # Wave 4
        {"type": "tiny", "count": 22, "interval": 280},
        {"type": "basic", "count": 15, "interval": 400}
    ],
    [   # Wave 5
        {"type": "fast", "count": 14, "interval": 320},
        {"type": "basic", "count": 16, "interval": 380},
        {"type": "fast", "count": 10, "interval": 0}
    ],
    [   # Wave 6
        {"type": "fast", "count": 20, "interval": 300},
        {"type": "basic", "count": 17, "interval": 380},
        {"type": "armored", "count": 12, "interval": 900}
    ],
    [   # Wave 7
        {"type": "tiny", "count": 28, "interval": 250},
        {"type": "fast", "count": 18, "interval": 300},
        {"type": "armored", "count": 11, "interval": 800},
        {"type": "mafia", "count": 1, "interval": 8000},
        {"type": "basic", "count": 15, "interval": 0}
    ],
    [   # Wave 8
        {"type": "fast", "count": 15, "interval": 320},
        {"type": "splitter", "count": 8, "interval": 700},
        {"type": "splitter", "count": 4, "interval": 0}
    ],
    [   # Wave 9
        {"type": "tiny", "count": 30, "interval": 230},
        {"type": "splitter", "count": 10, "interval": 650},
        {"type": "fast", "count": 18, "interval": 300}
    ],
    [   # Wave 10
        {"type": "tiny", "count": 25, "interval": 240},
        {"type": "shield", "count": 6, "interval": 1000},
        {"type": "splitter", "count": 7, "interval": 680}
    ],
    [   # Wave 11
        {"type": "shield", "count": 8, "interval": 950},
        {"type": "splitter", "count": 9, "interval": 600},
        {"type": "fast", "count": 20, "interval": 290}
    ],
    [   # Wave 12
        {"type": "armored", "count": 12, "interval": 400},
        {"type": "phase", "count": 14, "interval": 420},
        {"type": "fast", "count": 16, "interval": 310}
    ],
    [   # Wave 13
        {"type": "phase", "count": 16, "interval": 390},
        {"type": "shield", "count": 7, "interval": 900},
        {"type": "splitter", "count": 8, "interval": 630}
    ],
    [   # Wave 14
        {"type": "shield", "count": 10, "interval": 420},
        {"type": "pi_jumper", "count": 11, "interval": 500},
        {"type": "pi_jumper", "count": 6, "interval": 0}
    ],
    [   # Wave 15
        {"type": "pi_jumper", "count": 15, "interval": 450},
        {"type": "phase", "count": 17, "interval": 370},
        {"type": "tiny", "count": 35, "interval": 210}
    ],
    [   # Wave 16
        {"type": "pi_jumper", "count": 18, "interval": 300},
        {"type": "rogue", "count": 10, "interval": 550},
        {"type": "shield", "count": 7, "interval": 920}
    ],
    [   # Wave 17
        {"type": "rogue", "count": 14, "interval": 480},
        {"type": "pi_jumper", "count": 13, "interval": 460},
        {"type": "phase", "count": 15, "interval": 380}
    ],
    [   # Wave 18
        {"type": "shield", "count": 9, "interval": 850},
        {"type": "giant", "count": 3, "interval": 11000},
        {"type": "phase", "count": 16, "interval": 360}
    ],
    [   # Wave 19
        {"type": "giant", "count": 6, "interval": 10000},
        {"type": "splitter", "count": 11, "interval": 580},
        {"type": "shield", "count": 8, "interval": 880}
    ],
    [   # Wave 20
        {"type": "rogue", "count": 15, "interval": 470},
        {"type": "pulse", "count": 8, "interval": 1050},
        {"type": "pi_jumper", "count": 14, "interval": 440}
    ],
    [   # Wave 21
        {"type": "giant", "count": 8, "interval": 1050},
        {"type": "pulse", "count": 9, "interval": 1000},
        {"type": "shield", "count": 10, "interval": 850},
        {"type": "phase", "count": 18, "interval": 350},
        {"type": "splitter", "count": 12, "interval": 550}
    ],
    [   # Wave 22
        {"type": "rogue", "count": 17, "interval": 430},
        {"type": "pi_jumper", "count": 16, "interval": 410},
        {"type": "pi_master", "count": 1, "interval": 330},
        {"type": "giant", "count": 5, "interval": 950},
        {"type": "pulse", "count": 10, "interval": 950},
        {"type": "shield", "count": 11, "interval": 800},
        {"type": "splitter", "count": 13, "interval": 500},
        {"type": "phase", "count": 20, "interval": 330}
    ],
    [   # Wave 23
        {"type": "rogue", "count": 20, "interval": 400},
        {"type": "chrono", "count": 7, "interval": 1100},
        {"type": "pulse", "count": 12, "interval": 900},
        {"type": "pi_jumper", "count": 18, "interval": 380},
        {"type": "chrono", "count": 3, "interval": 0}
    ],
    [   # Wave 24
        {"type": "chrono", "count": 10, "interval": 1000},
        {"type": "giant", "count": 8, "interval": 900},
        {"type": "phase", "count": 22, "interval": 310},
        {"type": "splitter", "count": 15, "interval": 480},
        {"type": "tiny", "count": 40, "interval": 190}
    ],
    [   # Wave 25
        {"type": "shield", "count": 14, "interval": 750},
        {"type": "fast_giant", "count": 4, "interval": 8000},
        {"type": "chrono", "count": 8, "interval": 1050},
        {"type": "rogue", "count": 22, "interval": 380},
        {"type": "fast_giant", "count": 2, "interval": 0}
    ],
    [   # Wave 26
        {"type": "fast_giant", "count": 6, "interval": 750},
        {"type": "chrono", "count": 12, "interval": 950},
        {"type": "pulse", "count": 14, "interval": 850},
        {"type": "pi_jumper", "count": 20, "interval": 350},
        {"type": "phase", "count": 25, "interval": 290}
    ],
    [   # Wave 27
        {"type": "fast_giant", "count": 5, "interval": 700},
        {"type": "orbital", "count": 5, "interval": 1200},
        {"type": "chrono", "count": 10, "interval": 1000},
        {"type": "splitter", "count": 18, "interval": 450},
        {"type": "orbital", "count": 3, "interval": 0}
    ],
    [   # Wave 28
        {"type": "orbital", "count": 8, "interval": 1100},
        {"type": "fast_giant", "count": 7, "interval": 650},
        {"type": "pulse", "count": 16, "interval": 800},
        {"type": "rogue", "count": 25, "interval": 350},
        {"type": "phase", "count": 28, "interval": 270}
    ],
    [   # Wave 29
        {"type": "orbital", "count": 10, "interval": 1050},
        {"type": "fast_giant", "count": 9, "interval": 600},
        {"type": "chrono", "count": 14, "interval": 900},
        {"type": "giant", "count": 8, "interval": 850},
        {"type": "pulse", "count": 18, "interval": 750},
        {"type": "splitter", "count": 20, "interval": 420},
        {"type": "pi_jumper", "count": 25, "interval": 320}
    ],
    [   # Wave 30
        {"type": "orbital", "count": 12, "interval": 1000},
        {"type": "fast_giant", "count": 10, "interval": 550},
        {"type": "chrono", "count": 16, "interval": 850},
        {"type": "pulse", "count": 20, "interval": 700},
        {"type": "titan", "count": 1, "interval": 15000},
        {"type": "rogue", "count": 30, "interval": 300}
    ],
    [   # Wave 31
        {"type": "titan", "count": 2, "interval": 12000},
        {"type": "mafia", "count": 1, "interval": 14000},
        {"type": "orbital", "count": 15, "interval": 950},
        {"type": "fast_giant", "count": 6, "interval": 6000},
        {"type": "fast_giant", "count": 6, "interval": 600},
        {"type": "chrono", "count": 18, "interval": 850},
        {"type": "pulse", "count": 22, "interval": 750},
        {"type": "giant", "count": 3, "interval": 900},
        {"type": "splitter", "count": 25, "interval": 420},
        {"type": "pi_jumper", "count": 30, "interval": 310},
        {"type": "pi_master", "count": 1, "interval": 16000},
        {"type": "phase", "count": 30, "interval": 300},
        {"type": "shield", "count": 20, "interval": 800},
        {"type": "boss", "count": 1, "interval": 24000},
        {"type": "titan", "count": 1, "interval": 251200}
    ]
]

# ------------------------------------------------
# ENEMY CLASS
# ------------------------------------------------
class Circle:
    def __init__(self):
        self.radius = 15
        self.color = RED
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = 1.0 + random.uniform(-0.2, 0.2)
        self.waypoint_index = 0
        self.path = path_waypoints
        self.x, self.y = self.path[0]
        self.reward = 50
        self.slow_modifier = 1.0
        self.slow_timer = 0
        self.frozen_timer = 0
        self.is_boss = False

    def take_damage(self, amount, damage_type="normal"):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def apply_slow(self, amount, duration):
        new_modifier = max(0.1, 1.0 - amount)

        if new_modifier < self.slow_modifier:
            self.slow_modifier = new_modifier
            self.slow_timer = int(duration * 60)

    def freeze(self, duration):
        if self.is_boss:
            return

        self.frozen_timer = int(duration * 60)

    def update(self):
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            return

        if self.slow_timer > 0:
            self.slow_timer -= 1
        else:
            self.slow_modifier = 1.0

        if self.waypoint_index >= len(self.path):
            return

        tx, ty = self.path[self.waypoint_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 2:
            self.waypoint_index += 1
        else:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * self.speed * (clock.get_time() / (1000/60))
            self.y += ny * self.speed * (clock.get_time() / (1000/60))

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class FastCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 15
        self.color = (255, 165, 0)
        self.max_hp = 80
        self.hp = self.max_hp
        self.speed = 2.0 + random.uniform(-0.2, 0.2)
        self.reward = 70

    def update(self):
        super().update()

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class TinyCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 10
        self.color = (255, 200, 0)
        self.max_hp = 40
        self.hp = self.max_hp
        self.speed = 1.5 + random.uniform(-0.2, 0.2)
        self.reward = 30

    def update(self):
        super().update()

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 8, self.radius*2, 5))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 8, hp_w, 5))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class ArmoredCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 20
        self.color = (139, 0, 0)
        self.max_hp = 300
        self.hp = self.max_hp
        self.speed = 0.7
        self.damage_reduction = 0.5
        self.reward = 150

    def update(self):
        super().update()

    def take_damage(self, amount):
        reduced = amount * (1 - self.damage_reduction)
        self.hp -= reduced

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class MafiaCent(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 40
        self.color = (0, 0, 0)
        self.max_hp = 15000
        self.hp = self.max_hp
        self.speed = 0.5
        self.reward = 1500
        self.gacha_cooldown = 7777
        self.last_gacha = pygame.time.get_ticks()
        self.lasers = []
        self.laser_duration = 6
        self.spawn_queue = []
        self.is_boss = True
    
    def update(self, enemies, towers):
        super().update()
        now = pygame.time.get_ticks()

        for laser in list(self.lasers):
            lx, ly, timer = laser
            timer -= 1
            if timer <= 0:
                self.lasers.remove(laser)
            else:
                idx = self.lasers.index(laser)
                self.lasers[idx] = (lx, ly, timer)

        for item in list(self.spawn_queue):
            cls, count, interval, last_time = item
            if count > 0 and now - last_time >= interval:
                e = cls()
                e.x, e.y = path_waypoints[0]
                e.waypoint_index = 0
                enemies.append(e)

                item[1] -= 1
                item[3] = now

            if item[1] <= 0:
                self.spawn_queue.remove(item)

        if now - self.last_gacha >= self.gacha_cooldown:
            self.perform_gacha(towers)
            self.last_gacha = now

    def perform_gacha(self, towers):
        roll = random.randint(1, 100)
        now = pygame.time.get_ticks()
        if roll <= 40:
            self.spawn_queue.append([ArmoredCircle, 7, 500, now])
            print("Mafia Cent: queued 7 ArmoredCircle!")
        elif roll <= 70:
            def goon_777_class():
                g = Circle()
                g.max_hp = 1500
                g.hp = 1500
                g.radius = 20
                g.color = (128, 0, 128)
                g.reward = 100
                return g
            self.spawn_queue.append([goon_777_class, 3, 500, now])
            print("Mafia Cent: queued 3 Goon 777 HP!")
        elif roll <= 90:
            for _ in range(7):
                self.shoot_random_tower(towers)
            print("Mafia Cent: 7 tembakan ke tower random!")
        else:
            def goon_777_class():
                g = Circle()
                g.max_hp = 777
                g.hp = 777
                g.radius = 20
                g.color = (128, 0, 128)
                return g
            self.spawn_queue.append([goon_777_class, 21, 200, now])
            print("Mafia Cent: queued 21 Goon 777 HP!")

    def shoot_random_tower(self, towers):
        if towers:
            target = random.choice(towers)
            damage = 50
            target.hp -= damage
            self.lasers.append((target.x, target.y, self.laser_duration))
            print(f"Mafia Cent shot tower at ({target.x}, {target.y}) for {damage} damage!")

    def apply_slow(self, amount, duration):
        capped_amount = min(amount, 0.2)
        super().apply_slow(capped_amount, duration)

    def draw(self, surf):
        bar_width = 600
        bar_height = 40
        x = WIDTH // 2 - bar_width // 2
        y = 50
        hp_ratio = self.hp / self.max_hp
        hp_width = int(bar_width * hp_ratio)

        if hp_ratio > 0.6:
            bar_color = (0, 255, 0)
        elif hp_ratio > 0.3:
            bar_color = (255, 255, 0)
        else:
            bar_color = (255, 0, 0)

        pygame.draw.rect(surf, (50, 50, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(surf, bar_color, (x, y, hp_width, bar_height))
        pygame.draw.rect(surf, (255, 0, 0), (x, y, bar_width, bar_height), 3)

        font = pygame.font.SysFont(None, 32)
        text = f"Mafia Cent: {self.hp} / {self.max_hp}"
        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y + bar_height // 2))

        outline_offsets = [(-1,0), (1,0), (0,-1), (0,1)]
        for ox, oy in outline_offsets:
            outline_surf = font.render(text, True, (255,0,0))
            surf.blit(outline_surf, (text_rect.x + ox, text_rect.y + oy))

        surf.blit(text_surf, text_rect)

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        for lx, ly, timer in self.lasers:
            pygame.draw.line(surf, YELLOW, (int(self.x), int(self.y)), (int(lx), int(ly)), 4)

class SplitterCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 18
        self.color = (255, 105, 180)
        self.max_hp = 720
        self.hp = self.max_hp
        self.speed = 1.0
        self.split_count = 6
        self.reward = 120

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            return self.split()
        return []

    def split(self):
        children = []
        for _ in range(self.split_count):
            tiny = TinyCircle()
            tiny.x = self.x + random.randint(-5, 5)
            tiny.y = self.y + random.randint(-5, 5)
            tiny.waypoint_index = self.waypoint_index
            children.append(tiny)
        return children

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 12, self.radius*2, 8))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 12, hp_w, 8))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class ShieldCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 20
        self.color = (0, 191, 255)
        self.max_hp = 1500
        self.hp = self.max_hp
        self.speed = 0.9
        self.shield_hp_max = 1800
        self.shield_hp = self.shield_hp_max
        self.reward = 180

    def update(self):
        super().update()

    def take_damage(self, amount):
        if self.shield_hp > 0:
            self.shield_hp -= amount
            if self.shield_hp < 0:
                self.hp += self.shield_hp
                self.shield_hp = 0
        else:
            self.hp -= amount

    def draw(self, surf):
        total_w = self.radius * 2
        x = int(self.x - self.radius)
        y = int(self.y - self.radius - 14)

        pygame.draw.rect(surf, (60, 60, 60), (x, y, total_w, 8))

        if self.shield_hp > 0:
            shield_ratio = max(self.shield_hp, 0) / self.shield_hp_max
            shield_w = int(total_w * shield_ratio)
            green_w = total_w - shield_w
            pygame.draw.rect(surf, (0, 200, 0), (x, y, green_w, 8))
            pygame.draw.rect(surf, (0, 150, 255), (x + green_w, y, shield_w, 8))
        else:
            hp_ratio = max(self.hp, 0) / self.max_hp
            hp_w = int(total_w * hp_ratio)
            pygame.draw.rect(surf, (0, 200, 0), (x, y, hp_w, 8))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class PhaseCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 16
        self.color = (0, 255, 255)
        self.max_hp = 800
        self.hp = self.max_hp
        self.speed = 1.2
        self.phase_duration = 0
        self.phase_max_duration = 360
        self.phase_cooldown = 180
        self.phase_cooldown_max = 180
        self.is_phase = False
        self.reward = 100

    def update(self):
        super().update()

        if self.phase_duration > 0:
            self.is_phase = True
            self.phase_duration -= 1
            return 

        self.is_phase = False

        if self.phase_cooldown > 0:
            self.phase_cooldown -= 1
        else:

            self.phase_duration = self.phase_max_duration
            self.phase_cooldown = self.phase_cooldown_max

    def take_damage(self, amount):
        if self.is_phase:
            return
        self.hp -= amount

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80),
                         (self.x - self.radius, self.y - self.radius - 10,
                          self.radius * 2, 6))
        pygame.draw.rect(surf, (0, 200, 0),
                         (self.x - self.radius, self.y - self.radius - 10,
                          hp_w, 6))

        if self.is_phase:
            color = (200, 255, 255)
        else:
            color = self.color

        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

class PiJumper(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 16
        self.color = (138, 43, 226)
        self.max_hp = 1256
        self.hp = self.max_hp
        self.speed = 1.0
        self.jump_cooldown = 180
        self.jump_distance_min = 140
        self.jump_distance_max = 200
        self.reward = 80
        self.font_pi = pygame.font.Font(None, self.radius * 2)

    def update(self):
        super().update()

        if self.jump_cooldown <= 0:
            self.jump()
            self.jump_cooldown = 180
        else:
            self.jump_cooldown -= 1

    def jump(self):
        if self.waypoint_index < len(path_waypoints):
            tx, ty = path_waypoints[self.waypoint_index]

            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                nx = dx / dist
                ny = dy / dist

                jump_dist = random.randint(self.jump_distance_min, self.jump_distance_max)

                self.x += nx * jump_dist
                self.y += ny * jump_dist

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80),
                         (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0),
                         (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        text_surface = self.font_pi.render("π", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(text_surface, text_rect)

class RogueCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 17
        self.color = (255, 20, 147)
        self.max_hp = 3960
        self.hp = self.max_hp
        self.speed = 1.0
        self.dash_cooldown = 90
        self.dash_distance = 25
        self.reward = 250

    def update(self):
        super().update()

        if self.dash_cooldown <= 0:
            self.dash()
            self.dash_cooldown = 90
        else:
            self.dash_cooldown -= 1

    def dash(self):
        angle = random.uniform(-math.pi/4, math.pi/4)
        if self.waypoint_index < len(path_waypoints):
            tx, ty = path_waypoints[self.waypoint_index]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                nx = dx / dist
                ny = dy / dist

                dash_x = nx * math.cos(angle) - ny * math.sin(angle)
                dash_y = nx * math.sin(angle) + ny * math.cos(angle)
                self.x += dash_x * self.dash_distance
                self.y += dash_y * self.dash_distance

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class GiantCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 40
        self.color = (90, 0, 0)
        self.max_hp = 20000
        self.hp = self.max_hp
        self.speed = 0.4
        self.damage_reduction = 0.45
        self.reward = 800

    def update(self):
        super().update()

    def take_damage(self, amount):
        reduced = amount * (1 - self.damage_reduction)
        self.hp -= reduced

    def draw(self, surf):
        bar_w = self.radius * 2
        hp_ratio = max(self.hp, 0) / self.max_hp
        hp_w = int(bar_w * hp_ratio)

        pygame.draw.rect(surf, (80, 80, 80), 
                         (self.x - self.radius, self.y - self.radius - 14, bar_w, 10))

        pygame.draw.rect(surf, (0, 200, 0), 
                         (self.x - self.radius, self.y - self.radius - 14, hp_w, 10))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class PulseWalker(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 18
        self.color = (0, 255, 127)
        self.max_hp = 7200
        self.hp = self.max_hp
        self.speed = 1.0
        self.pulse_radius = 120
        self.pulse_cooldown = 120
        self.reward = 300

    def update(self, towers=None):
        super().update()

        if self.pulse_cooldown <= 0:
            self.pulse(towers)
            self.pulse_cooldown = 120
        else:
            self.pulse_cooldown -= 1

    def pulse(self, towers):
        if not towers:
            return
        for t in towers:
            dx = self.x - t.x
            dy = self.y - t.y
            dist = math.hypot(dx, dy)
            if dist < self.pulse_radius:
                t.accuracy_penalty = 0.5
                t.accuracy_penalty_timer = 60

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        pygame.draw.circle(surf, (0, 255, 127, 50), (int(self.x), int(self.y)), self.pulse_radius, 1)

class PiMaster(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 60
        self.color = (0, 0, 0)
        self.font_pi = pygame.font.Font(None, self.radius * 4)
        self.shield_hp_max = 78500
        self.shield_hp = self.shield_hp_max
        self.hp_max = 157000
        self.hp = self.hp_max
        self.reward = 5000
        self.speed = 0.3
        self.speed_stage2 = 3.14
        self.damage_reduction = 0.22
        self.shield_active = True
        self.stage2 = False
        self.is_boss = True
        self.waypoint_index = 0
        self.reverse_path = False
        self.bolak_balik_count = 0
        self.max_bolak_balik = 22
        self.finished_bolak_balik = False
        self.spawn_queue_cooldown = 44500
        self.last_spawn_queue_time = 0
        self.initial_spawn_queue = []

    def take_damage(self, amount):
        reduced = amount * (1 - self.damage_reduction)

        if self.shield_active:
            self.shield_hp -= reduced
            if self.shield_hp <= 0:
                self.shield_active = False
                self.stage2 = True
                self.color = (255, 255, 0)
                self.waypoint_index = self.find_closest_waypoint()
        else:
            self.hp -= reduced

    def apply_slow(self, amount, duration):
        capped = min(amount, 0.2)
        super().apply_slow(capped, duration)

    def find_closest_waypoint(self):
        closest = 0
        min_dist = float("inf")
        for i, (wx, wy) in enumerate(path_waypoints):
            d = math.hypot(wx - self.x, wy - self.y)
            if d < min_dist:
                min_dist = d
                closest = i
        return closest

    def update(self, enemies=None, towers=None):
        if enemies is None:
            enemies = []

        if not self.stage2:
            super().update()
            return

        if not self.finished_bolak_balik:
            if not self.reverse_path and self.waypoint_index >= 8:
                self.reverse_path = True
            elif self.reverse_path and self.waypoint_index <= 1:
                self.reverse_path = False
                self.bolak_balik_count += 1

                if self.bolak_balik_count >= self.max_bolak_balik:
                    self.finished_bolak_balik = True
                    self.waypoint_index = 8
                    self.reverse_path = False

        self.waypoint_index = max(
            0, min(self.waypoint_index, len(path_waypoints) - 1)
        )

        tx, ty = path_waypoints[self.waypoint_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * self.speed_stage2
            self.y += ny * self.speed_stage2

        if dist <= self.speed_stage2 + 1:
            if self.reverse_path:
                self.waypoint_index -= 1
            else:
                self.waypoint_index += 1

        now = pygame.time.get_ticks()

        if not self.initial_spawn_queue and now - self.last_spawn_queue_time >= self.spawn_queue_cooldown:
            self.initial_spawn_queue = [
                [ShieldCircle, 22, 200, now],
                [PulseWalker, 7, 500, now],
                [GiantCircle, 3, 1000, now]
            ]
            self.last_spawn_queue_time = now

        for item in list(self.initial_spawn_queue):
            cls, count, interval, last_time = item
            if count > 0 and now - last_time >= interval:
                e = cls()
                e.x, e.y = path_waypoints[0]
                e.waypoint_index = 0
                enemies.append(e)
                item[1] -= 1
                item[3] = now

            if item[1] <= 0:
                self.initial_spawn_queue.remove(item)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)

        pygame.draw.circle(surf, self.color, (x, y), self.radius)

        if self.shield_active:
            pygame.draw.circle(surf, (255, 255, 0), (x, y), self.radius // 2)

        bar_width = 600
        bar_height = 40
        bx = WIDTH // 2 - bar_width // 2
        by = 50

        shield = max(self.shield_hp if self.shield_active else 0, 0)
        hp = max(self.hp, 0)

        pygame.draw.rect(surf, (50, 50, 50), (bx, by, bar_width, bar_height))

        hp_ratio = hp / self.hp_max
        pygame.draw.rect(
            surf, (0, 255, 0),
            (bx, by, int(bar_width * hp_ratio), bar_height)
        )

        if shield > 0:
            shield_ratio = shield / self.shield_hp_max
            pygame.draw.rect(
                surf, (0, 150, 255),
                (bx, by, int(bar_width * shield_ratio), bar_height)
            )

        pygame.draw.rect(surf, (255, 0, 0), (bx, by, bar_width, bar_height), 3)

        font = pygame.font.SysFont(None, 32)
        total = hp + shield
        text = f"Pi Master: {int(total)} / {int(self.hp_max)}"
        text_surf = font.render(text, True, (0, 0, 0))
        rect = text_surf.get_rect(center=(WIDTH // 2, by + bar_height // 2))

        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            surf.blit(
                font.render(text, True, (255, 0, 0)),
                (rect.x + ox, rect.y + oy)
            )

        surf.blit(text_surf, rect)

        if not self.shield_active:
            pi = self.font_pi.render("π", True, (255, 0, 0))
            surf.blit(pi, pi.get_rect(center=(x, y)))

class ChronoCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 20
        self.color = (0, 0, 255)
        self.max_hp = 9000
        self.hp = self.max_hp
        self.speed = 0.9
        self.slow_radius = 120
        self.slow_factor = 0.5
        self.reward = 350

    def update(self, towers=None):
        super().update()

        if towers:
            for t in towers:
                dx = self.x - t.x
                dy = self.y - t.y
                dist = math.hypot(dx, dy)
                if dist < self.slow_radius:
                    t.fire_rate_modifier = self.slow_factor
                    t.slow_timer = 60

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80), (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (0, 200, 0), (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        pygame.draw.circle(surf, (0, 0, 255, 50), (int(self.x), int(self.y)), self.slow_radius, 1)

class FastGiantCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 36
        self.color = (255, 165, 0)
        self.max_hp = 12000
        self.hp = self.max_hp
        self.speed = 1.1 + random.uniform(-0.1, 0.1)
        self.damage_reduction = 0.25
        self.reward = 600

    def update(self):
        super().update()

    def take_damage(self, amount):
        reduced = amount * (1 - self.damage_reduction)
        self.hp -= reduced

    def draw(self, surf):
        bar_w = self.radius * 2
        hp_ratio = max(self.hp, 0) / self.max_hp
        hp_w = int(bar_w * hp_ratio)

        pygame.draw.rect(surf, (80, 80, 80),
                         (self.x - self.radius, self.y - self.radius - 14, bar_w, 10))

        pygame.draw.rect(surf, (0, 200, 0),
                         (self.x - self.radius, self.y - self.radius - 14, hp_w, 10))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class OrbEnemy:
    def __init__(self, parent, angle_offset):
        self.parent = parent
        self.angle_offset = angle_offset
        self.radius = parent.orb_radius
        self.color = (200, 0, 0)
        self.max_hp = parent.orb_hp
        self.hp = self.max_hp
        self.orbit_distance = parent.orbit_distance
        self.x = parent.x
        self.y = parent.y
        self.dead = False
        self.reward = 40
        self.waypoint_index = -9999
        self.reached_goal = False

    def update(self):
        if self.dead:
            return

        angle = self.parent.orbit_angle + self.angle_offset
        self.x = self.parent.x + math.cos(angle) * self.orbit_distance
        self.y = self.parent.y + math.sin(angle) * self.orbit_distance

        if self.hp <= 0:
            self.dead = True

    def take_damage(self, Damage):
        if not self.dead:
            self.hp -= Damage

    def draw(self, surf):
        if self.dead:
            return
        
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        hp_percent = self.hp / self.max_hp
        bar_w = self.radius * 2
        filled = bar_w * hp_percent

        pygame.draw.rect(surf, (80, 0, 0),
                         (self.x - self.radius, self.y - self.radius - 6, bar_w, 4))
        pygame.draw.rect(surf, (255, 0, 0),
                         (self.x - self.radius, self.y - self.radius - 6, filled, 4))

class OrbitalCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 22
        self.color = (0, 150, 255)
        self.max_hp = 9500
        self.hp = self.max_hp
        self.speed = 0.85
        self.reward = 1000
        self.num_orbs = 3
        self.orbit_distance = 32
        self.orbit_speed = 0.07
        self.orbit_angle = 0
        self.orb_radius = 10
        self.orb_hp = 2400
        self.orbs = []

    def spawn_orbs(self, enemy_group):
        for i in range(self.num_orbs):
            angle = i * (2 * math.pi / self.num_orbs)
            orb = OrbEnemy(self, angle)
            self.orbs.append(orb)
            enemy_group.append(orb)

    def update(self):
        super().update()
        self.orbit_angle += self.orbit_speed

class TitanCircle(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 65
        self.color = (0, 0, 0)
        self.max_hp = 100000
        self.hp = self.max_hp
        self.shield_max = 25000
        self.shield = self.shield_max
        self.speed_normal = 0.3
        self.speed_enraged = 0.6
        self.speed = self.speed_normal
        self.reward = 7500
        self.defense = 0.5
        self.laser_cooldown = 6000
        self.last_laser = pygame.time.get_ticks()
        self.laser_target_pos = None
        self.laser_display_time = 250
        self.laser_display_end = 0
        self.is_firing = False
        self.stop_duration = 400
        self.stop_until = 0
        self.laser_width = 125

    def take_damage(self, Damage):
        Damage *= (1 - self.defense)

        if self.shield > 0:
            self.shield -= Damage
            if self.shield <= 0:
                self.shield = 0
                self.color = (200, 0, 0)
                self.speed = self.speed_enraged
        else:
            self.hp -= Damage

    def get_farthest_tower(self, towers):
        target = None
        max_dist = -1

        for t in towers:
            d = math.hypot(t.x - self.x, t.y - self.y)
            if d > max_dist:
                max_dist = d
                target = t

        return target

    def fire_laser(self, towers):
        if not towers:
            return

        target = self.get_farthest_tower(towers)
        if target is None:
            return

        tx, ty = target.x, target.y
        self.laser_target_pos = (tx, ty)

        now = pygame.time.get_ticks()
        self.laser_display_end = now + self.laser_display_time

        for t in towers:
            if t.hp > 0:
                if self.point_to_laser_distance(t.x, t.y, tx, ty) <= self.laser_width / 2:
                    t.hp -= 25
                    if t.hp < 0:
                        t.hp = 0

        self.is_firing = True
        self.stop_until = now + self.stop_duration

    def point_to_laser_distance(self, px, py, tx, ty):
        x1, y1 = self.x, self.y
        x2, y2 = tx, ty

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)

        t = ((px - x1)*dx + (py - y1)*dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))

        cx = x1 + t * dx
        cy = y1 + t * dy

        return math.hypot(px - cx, py - cy)

    def update(self, enemies, towers):
        now = pygame.time.get_ticks()

        if self.is_firing:
            if now >= self.stop_until:
                self.is_firing = False
            else:
                return

        super().update()

        if now - self.last_laser >= self.laser_cooldown:
            self.last_laser = now
            self.fire_laser(towers)

        if self.laser_target_pos and now >= self.laser_display_end:
            self.laser_target_pos = None

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        if self.shield > 0:
            pygame.draw.circle(
                surf, (255, 255, 255),
                (int(self.x), int(self.y)),
                self.radius - 10, 4
            )

        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 0, 0),
                         (self.x - self.radius, self.y - self.radius - 12, self.radius*2, 10))
        pygame.draw.rect(surf, (255, 0, 0),
                         (self.x - self.radius, self.y - self.radius - 12, hp_w, 10))

        if self.shield > 0:
            sw = int(self.radius * 2 * (self.shield / self.shield_max))
            pygame.draw.rect(surf, (50, 50, 50),
                             (self.x - self.radius, self.y - self.radius - 22, self.radius*2, 8))
            pygame.draw.rect(surf, (200, 200, 200),
                             (self.x - self.radius, self.y - self.radius - 22, sw, 8))

        if self.laser_target_pos:
            tx, ty = self.laser_target_pos

            pygame.draw.line(
                surf,
                (255, 0, 0),
                (int(self.x), int(self.y)),
                (int(tx), int(ty)),
                self.laser_width
            )

class CycleLead(Circle):
    def __init__(self):
        super().__init__()
        self.path = path_waypoints
        self.waypoint_index = 0
        self.radius = 70
        self.color = (0, 0, 0)
        self.max_hp = 314000
        self.hp = self.max_hp
        self.shield_max = 157000
        self.shield = self.shield_max
        self.defense = 0.314
        self.speed_normal = 0.55
        self.speed = self.speed_normal
        self.laser_cooldown = 5500
        self.last_laser = pygame.time.get_ticks()
        self.laser_target_pos = None
        self.laser_display_time = 260
        self.laser_display_end = 0
        self.is_firing = False
        self.stop_duration = 420
        self.stop_until = 0
        self.laser_width = 125
        self.spin_cooldown = 9000
        self.last_spin = pygame.time.get_ticks()
        self.spin_active = False
        self.spin_time = 1000
        self.spin_end = 0
        self.spin_angle = 0
        self.spin_speed = 6
        self.rage_spin_used = False
        self.rage_spin_active = False
        self.rage_spin_angle = 0
        self.rage_spin_count = 0
        self.rage_spin_rotations = 7
        self.rage_spin_speed = 12
        self.rage_spin_damage = 25
        self.rage_spin_tolerance = 8
        self.spin_disabled = False
        self.dead_core = None
        self.is_dead = False
        self.death_anim_active = False
        self.core_x = 0
        self.core_y = 0
        self.core_vx = 0
        self.core_vy = 0
        self.core_timer = 0
        self.to_delete = False
        self.is_boss = True

    def move(self):
        if self.waypoint_index < len(self.path):
            tx, ty = self.path[self.waypoint_index]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist < 3:
                self.waypoint_index = (self.waypoint_index + 1) % len(self.path)
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def take_damage(self, dmg):
        if self.shield > 0:
            self.shield -= dmg
            if self.shield <= 0:
                self.shield = 0
                self.color = (200, 0, 0)
            return

        dmg *= (1 - self.defense)
        self.hp -= dmg

        if self.hp <= 0 and not self.is_dead:
            self.hp = 0
            self.is_dead = True

            self.dead_core = (self.x, self.y)

            self.death_anim_active = True
            self.core_x, self.core_y = self.x, self.y

            ang = random.uniform(0, math.pi * 2)
            self.core_vx = math.cos(ang) * 6
            self.core_vy = math.sin(ang) * 6
            self.core_timer = 480

    def apply_slow(self, amount, duration):
        capped_amount = min(amount, 0.2)
        super().apply_slow(capped_amount, duration)

    def get_farthest_tower(self, towers):
        target = None
        max_dist = -1

        for t in towers:
            d = math.hypot(t.x - self.x, t.y - self.y)
            if d > max_dist:
                max_dist = d
                target = t

        return target

    def fire_main_laser(self, towers):
        if not towers:
            return

        target = self.get_farthest_tower(towers)
        if target is None:
            return

        tx, ty = target.x, target.y
        self.laser_target_pos = (tx, ty)

        now = pygame.time.get_ticks()
        self.laser_display_end = now + self.laser_display_time

        for t in towers:
            if t.hp > 0:
                if self.point_to_laser_distance(t.x, t.y, tx, ty) <= self.laser_width / 2:
                    t.hp -= 25
                    if t.hp < 0:
                        t.hp = 0

        self.is_firing = True
        self.stop_until = now + self.stop_duration

    def point_to_laser_distance(self, px, py, tx, ty):
        x1, y1 = self.x, self.y
        x2, y2 = tx, ty

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)

        t = ((px - x1)*dx + (py - y1)*dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))

        cx = x1 + t * dx
        cy = y1 + t * dy

        return math.hypot(px - cx, py - cy)

    def start_spin_laser(self):
        if self.spin_disabled:
            return
        self.spin_active = True
        self.spin_angle = 0
        self.spin_end = pygame.time.get_ticks() + self.spin_time

    def start_rage_spin(self):
        self.spin_disabled = True
        self.rage_spin_used = True
        self.rage_spin_active = True
        self.rage_spin_count = 0
        self.rage_spin_angle = 0
        self.is_firing = False
        self.stop_until = 0
        self.speed = 0

    def apply_rage_spin_damage_once(self, towers):
        if not towers:
            return

        for t in towers:
            dx = t.x - self.x
            dy = t.y - self.y
            angle_to_t = math.degrees(math.atan2(dy, dx))
            diff = abs((angle_to_t - self.rage_spin_angle + 180) % 360 - 180)
            dist = math.hypot(dx, dy)
            if diff <= self.rage_spin_tolerance and dist <= 500:
                t.hp -= self.rage_spin_damage
                if t.hp < 0:
                    t.hp = 0

    def handle_death(self):
        self.core_x += self.core_vx
        self.core_y += self.core_vy

        self.core_vx *= 0.95
        self.core_vy *= 0.95

        self.core_timer -= 1
        if self.core_timer <= 0:
            self.death_anim_active = False
            self.to_delete = True

    def update(self, enemies, towers):
        if self.death_anim_active:
            self.handle_death()
            return

        self.move()

        now = pygame.time.get_ticks()

        if (not self.rage_spin_used) and (self.hp <= self.max_hp * 0.3):
            self.start_rage_spin()

        if self.is_firing:
            if now >= self.stop_until:
                self.is_firing = False
            else:
                return

        if self.rage_spin_active:
            self.rage_spin_angle += self.rage_spin_speed

            if self.rage_spin_angle >= 360:
                self.rage_spin_angle -= 360
                self.rage_spin_count += 1

                self.apply_rage_spin_damage_once(towers)

                if self.rage_spin_count >= self.rage_spin_rotations:
                    self.rage_spin_active = False
                    self.speed = self.speed_normal
            return

        super().update()

        if now - self.last_laser >= self.laser_cooldown:
            self.last_laser = now
            self.fire_main_laser(towers)

        if (not self.spin_disabled) and (now - self.last_spin >= self.spin_cooldown):
            self.last_spin = now
            self.start_spin_laser()

        if self.spin_active:
            self.spin_angle += self.spin_speed
            if now >= self.spin_end:
                self.spin_active = False

        if self.laser_target_pos and now >= self.laser_display_end:
            self.laser_target_pos = None

    def draw(self, surf):
        if self.death_anim_active:
            pygame.draw.circle(surf, (50, 0, 0), (int(self.x), int(self.y)), self.radius)

            core_radius = 32
            pygame.draw.circle(surf, (255, 0, 0), (int(self.core_x), int(self.core_y)), core_radius)

            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x_end = self.core_x + math.cos(rad) * core_radius
                y_end = self.core_y + math.sin(rad) * core_radius
                pygame.draw.line(surf, (255, 100, 100), (int(self.core_x), int(self.core_y)), (int(x_end), int(y_end)), 2)

            for glow in range(1, 4):
                pygame.draw.circle(
                    surf,
                    (255, 50, 50),
                    (int(self.core_x), int(self.core_y)),
                    core_radius + glow * 4,
                    1
                )
            return

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        if self.shield > 0:
            pygame.draw.circle(
                surf, (255, 255, 255),
                (int(self.x), int(self.y)),
                self.radius - 10,
                4
            )

        core_radius = 32
        pygame.draw.circle(surf, (255, 0, 0), (int(self.x), int(self.y)), core_radius)

        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x_end = self.x + math.cos(rad) * core_radius
            y_end = self.y + math.sin(rad) * core_radius
            pygame.draw.line(surf, (255, 100, 100), (self.x, self.y), (x_end, y_end), 2)

        for glow in range(1, 4):
            pygame.draw.circle(
                surf,
                (255, 50, 50, 30),
                (int(self.x), int(self.y)),
                core_radius + glow * 4,
                1
            )

        bar_width = 600
        bar_height = 40
        bx = WIDTH // 2 - bar_width // 2
        by = 40

        shield = max(self.shield, 0)
        hp = max(self.hp, 0)

        pygame.draw.rect(surf, (50, 50, 50), (bx, by, bar_width, bar_height))

        hp_ratio = hp / self.max_hp
        hp_w = int(bar_width * hp_ratio)
        pygame.draw.rect(surf, (0, 255, 0), (bx, by, hp_w, bar_height))

        if shield > 0:
            shield_ratio = shield / self.shield_max
            shield_w = int(bar_width * shield_ratio)
            pygame.draw.rect(surf, (0, 150, 255), (bx, by, shield_w, bar_height))

        pygame.draw.rect(surf, (255, 0, 0), (bx, by, bar_width, bar_height), 3)

        font = pygame.font.SysFont(None, 32)
        total_value = hp + shield
        text = f"Cyclo Lead: {int(total_value)} / {int(self.max_hp)}"
        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(WIDTH // 2, by + bar_height // 2))

        outline_offsets = [(-1,0), (1,0), (0,-1), (0,1)]
        for ox, oy in outline_offsets:
            outline_surf = font.render(text, True, (255,0,0))
            surf.blit(outline_surf, (text_rect.x + ox, text_rect.y + oy))

        surf.blit(text_surf, text_rect)

        if self.laser_target_pos:
            tx, ty = self.laser_target_pos
            pygame.draw.line(
                surf,
                (255, 0, 0),
                (int(self.x), int(self.y)),
                (int(tx), int(ty)),
                self.laser_width
            )

        if self.spin_active:
            ang = math.radians(self.spin_angle)
            tx = self.x + math.cos(ang) * 500
            ty = self.y + math.sin(ang) * 500

            pygame.draw.line(
                surf,
                (255, 60, 60),
                (int(self.x), int(self.y)),
                (int(tx), int(ty)),
                self.laser_width
            )

        if self.rage_spin_active:
            ang = math.radians(self.rage_spin_angle)
            tx = self.x + math.cos(ang) * 500
            ty = self.y + math.sin(ang) * 500

            pygame.draw.line(
                surf,
                (255, 80, 80),
                (int(self.x), int(self.y)),
                (int(tx), int(ty)),
                self.laser_width
            )

class WendigoScout(Circle):
    def __init__(self):
        super().__init__()
        self.color = (180, 180, 255)
        self.radius = 12
        self.max_hp = 300
        self.hp = self.max_hp
        self.speed = 2.2 + random.uniform(-0.15, 0.15)
        self.reward = 60

    def update(self):
        super().update()

    def draw_small_logo(self, surf, x, y, scale=0.8):
        color = (120, 190, 255)
        thickness = max(1, int(2 * scale))
        temp = pygame.Surface((40, 40), pygame.SRCALPHA)
        cx, cy = 20, 20
        left_horn = [
            (cx - 10*scale, cy + 6*scale),
            (cx - 18*scale, cy + 2*scale),
            (cx - 20*scale, cy - 2*scale),
            (cx - 17*scale, cy - 8*scale),
            (cx - 13*scale, cy - 12*scale),
        ]
        pygame.draw.lines(temp, color, False, left_horn, thickness)

        right_horn = [
            (cx + 10*scale, cy + 6*scale),
            (cx + 18*scale, cy + 2*scale),
            (cx + 20*scale, cy - 2*scale),
            (cx + 17*scale, cy - 8*scale),
            (cx + 13*scale, cy - 12*scale),
        ]
        pygame.draw.lines(temp, color, False, right_horn, thickness)

        pygame.draw.ellipse(
            temp,
            color,
            (cx - 6*scale, cy - 4*scale, 12*scale, 10*scale),
            thickness
        )

        surf.blit(temp, (x - 20, y - 20))

    def draw(self, surf):
        if self.hp < self.max_hp:
            hp_ratio = max(0, self.hp / self.max_hp)
            hp_w = int(self.radius * 2 * hp_ratio)

            pygame.draw.rect(
                surf,
                (80, 80, 80),
                (self.x - self.radius, self.y - self.radius - 10, self.radius * 2, 6)
            )
            pygame.draw.rect(
                surf,
                (0, 200, 0),
                (self.x - self.radius, self.y - self.radius - 10, hp_w, 6)
            )

        pygame.draw.circle(
            surf,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        self.draw_small_logo(surf, self.x, self.y, scale=0.8)

class SnowMinion(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 13
        self.color = (220, 240, 255)
        self.max_hp = 220
        self.hp = self.max_hp
        self.speed = 1.1 + random.uniform(-0.1, 0.1)
        self.reward = 20

    def update(self):
        super().update()

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80),
                         (self.x - self.radius, self.y - self.radius - 8, self.radius*2, 5))
        pygame.draw.rect(surf, (0, 200, 0),
                         (self.x - self.radius, self.y - self.radius - 8, hp_w, 5))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class FrostGoblin(Circle):
    def __init__(self):
        super().__init__()
        self.color = (100, 150, 255)
        self.radius = 14
        self.max_hp = 360
        self.hp = self.max_hp
        self.speed = 1.7 + random.uniform(-0.1, 0.15)
        self.reward = 50
        self.slow_amount = 0.2
        self.slow_duration = 2.0
        self.touch_radius = self.radius + 18
        self.touch_cooldown = 0
        self.touch_cooldown_max = 60

    def update(self):
        super().update()

        if self.touch_cooldown > 0:
            self.touch_cooldown -= 1
            return

        for tower in state_data.get("towers", []):
            dist = math.hypot(tower.x - self.x, tower.y - self.y)

            if dist < self.touch_radius:
                if hasattr(tower, "apply_slow"):
                    tower.apply_slow(self.slow_amount, self.slow_duration)
                self.touch_cooldown = self.touch_cooldown_max
                break

class IceWolf(Circle):
    def __init__(self):
        super().__init__()
        self.color = (160, 220, 255)
        self.radius = 14
        self.max_hp = 380
        self.hp = self.max_hp
        self.speed = 2.6 + random.uniform(-0.1, 0.15)
        self.reward = 65

    def update(self):
        super().update()

class Permafrost(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 20
        self.color = (190, 240, 255)
        self.max_hp = 3000
        self.hp = self.max_hp
        self.speed = 0.55 + random.uniform(-0.05, 0.05)
        self.reward = 150
        self.split_count = 6
        self.ice_resistance = 0.4

    def take_damage(self, amount, damage_type="normal"):
        if damage_type == "ice":
            self.hp -= amount * self.ice_resistance
        else:
            self.hp -= amount

    def split(self):
        children = []
        for _ in range(self.split_count):
            sm = SnowMinion()
            sm.x = self.x + random.randint(-5, 5)
            sm.y = self.y + random.randint(-5, 5)
            sm.waypoint_index = self.waypoint_index
            sm.path = path_waypoints_winter
            children.append(sm)
        return children

    def update(self):
        super().update()

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80),
                         (self.x - self.radius, self.y - self.radius - 12, self.radius*2, 8))
        pygame.draw.rect(surf, (0, 200, 0),
                         (self.x - self.radius, self.y - self.radius - 12, hp_w, 8))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class HauntingWendigo(Circle):
    def __init__(self):
        super().__init__()
        self.color = (180, 180, 255)
        self.radius = 30
        self.max_hp = 90000  
        self.hp = self.max_hp  
        self.speed = 1.2  
        self.base_speed = self.speed  
        self.reward = 1200
        self.horn_color = (120, 190, 255)  
        self.horn_scale = 1.0
        self.screech_radius = 180  
        self.screech_dps = 40
        self.screech_tick = 0  
        self.screech_tick_rate = 60
        self.is_screeching = False
        self.is_boss = True

    def update(self, enemies, towers):  
        tower_in_range = False  
        for t in towers:  
            if not hasattr(t, "hp"):  
                continue  
            if math.hypot(t.x - self.x, t.y - self.y) <= self.screech_radius:  
                tower_in_range = True  
                break  

        if tower_in_range:  
            self.is_screeching = True  
            self.speed = 0  

            self.screech_tick += 1  
            if self.screech_tick >= self.screech_tick_rate:  
                self.screech_tick = 0  
                for t in towers:  
                    if not hasattr(t, "hp"):  
                        continue  
                    if math.hypot(t.x - self.x, t.y - self.y) <= self.screech_radius:  
                        t.hp = max(0, t.hp - self.screech_dps)  

        else:  
            self.is_screeching = False  
            self.speed = self.base_speed  
            self.screech_tick = 0  
            super().update()

    def apply_slow(self, amount, duration):
        capped_amount = min(amount, 0.2)
        super().apply_slow(capped_amount, duration)

    def draw(self, surf):
        bar_width = 600  
        bar_height = 40  
        x = WIDTH // 2 - bar_width // 2  
        y = 50  

        hp_ratio = self.hp / self.max_hp  
        hp_width = int(bar_width * hp_ratio)  

        if hp_ratio > 0.6:  
            bar_color = (0, 255, 0)  
        elif hp_ratio > 0.3:  
            bar_color = (255, 255, 0)  
        else:  
            bar_color = (255, 0, 0)  

        pygame.draw.rect(surf, (50, 50, 50), (x, y, bar_width, bar_height))  
        pygame.draw.rect(surf, bar_color, (x, y, hp_width, bar_height))  
        pygame.draw.rect(surf, (255, 0, 0), (x, y, bar_width, bar_height), 3)  

        font = pygame.font.SysFont(None, 32)  
        text = f"Haunting Wendigo: {self.hp} / {self.max_hp}"  
        text_surf = font.render(text, True, (0, 0, 0))  
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y + bar_height // 2))  

        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:  
            surf.blit(font.render(text, True, (255,0,0)),  
                      (text_rect.x + ox, text_rect.y + oy))  
        surf.blit(text_surf, text_rect)  

        if self.is_screeching:  
            pygame.draw.circle(  
                surf, (255, 0, 0),  
                (int(self.x), int(self.y)),  
                self.screech_radius,  
                1
            )  

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)  

        cx, cy = self.x, self.y  
        left_horn = [  
            (cx - self.radius*0.6, cy - self.radius),  
            (cx - self.radius*1.2, cy - self.radius*1.5),  
            (cx - self.radius*1.0, cy - self.radius*2.0)  
        ]  
        right_horn = [  
            (cx + self.radius*0.6, cy - self.radius),  
            (cx + self.radius*1.2, cy - self.radius*1.5),  
            (cx + self.radius*1.0, cy - self.radius*2.0)  
        ]  
        pygame.draw.lines(surf, self.horn_color, False, left_horn, 3)  
        pygame.draw.lines(surf, self.horn_color, False, right_horn, 3)

class FrozenTotemBearer(Circle):
    def __init__(self):
        super().__init__()
        self.color = (120, 200, 255)
        self.radius = 22
        self.max_hp = 7200
        self.hp = self.max_hp
        self.speed = 0.6 + random.uniform(-0.05, 0.05)
        self.reward = 220
        self.heal_percent_per_second = 0.02
        self.heal_radius = 80
        self.frozen_radius = 50

    def update(self):
        super().update()
        self.lasers = []
        for enemy in state_data.get("enemies", []):
            if enemy is self:
                continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.heal_radius:
                heal = enemy.max_hp * self.heal_percent_per_second * (clock.get_time() / 1000)
                enemy.hp = min(enemy.max_hp, enemy.hp + heal)
                self.lasers.append((self.x, self.y, enemy.x, enemy.y))

    def draw(self, surf):
        super().draw(surf)

        for lx1, ly1, lx2, ly2 in getattr(self, "lasers", []):
            pygame.draw.line(surf, (0, 255, 255), (lx1, ly1), (lx2, ly2), 2)

class Wendigo(Circle):
    def __init__(self):
        super().__init__()
        self.color = (150, 150, 200)
        self.radius = 32 
        self.max_hp = 24000  
        self.hp = self.max_hp  
        self.speed = 1.2
        self.base_speed = self.speed  
        self.reward = 450
        self.horn_color = (100, 150, 200)  

    def update(self):
        super().update()

    def draw(self, surf):
        super().draw(surf)
        pygame.draw.circle(
            surf,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        cx, cy = self.x, self.y
        left_horn = [
            (cx - self.radius * 0.5, cy - self.radius),
            (cx - self.radius * 0.9, cy - self.radius * 1.4),
            (cx - self.radius * 0.7, cy - self.radius * 1.8)
        ]
        right_horn = [
            (cx + self.radius * 0.5, cy - self.radius),
            (cx + self.radius * 0.9, cy - self.radius * 1.4),
            (cx + self.radius * 0.7, cy - self.radius * 1.8)
        ]

        pygame.draw.lines(surf, self.horn_color, False, left_horn, 3)
        pygame.draw.lines(surf, self.horn_color, False, right_horn, 3)

class SpiritChanneler(Circle):
    def __init__(self):
        super().__init__()
        self.color = (200, 180, 255)
        self.radius = 18
        self.max_hp = 3600
        self.hp = self.max_hp
        self.speed = 0.8 + random.uniform(-0.05, 0.05)
        self.reward = 180
        self.respawn_interval = 10.0
        self.time_since_last_respawn = 0.0
        self.respawn_count = 6
        self.respawn_types = [WendigoScout, FrostGoblin, IceWolf]
        self.is_paused = False
        self.paused_timer = 0.0

    def update(self, enemies_list):
        dt = clock.get_time() / 1000.0

        if self.is_paused:
            self.paused_timer -= dt
            if self.paused_timer <= 0:
                self.is_paused = False
            return

        super().update()

        self.time_since_last_respawn += dt
        if self.time_since_last_respawn >= self.respawn_interval:
            self.spawn_children(enemies_list)
            self.time_since_last_respawn = 0.0

    def spawn_children(self, enemies_list):
        for _ in range(self.respawn_count):
            enemy_type = random.choice(self.respawn_types)
            new_enemy = enemy_type()
            new_enemy.x, new_enemy.y = self.x, self.y
            new_enemy.waypoint_index = self.waypoint_index
            new_enemy.path = self.path

            enemies_list.append(new_enemy)

        self.is_paused = True
        self.paused_timer = 6.0

    def draw(self, surf):
        super().draw(surf)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        if self.is_paused:
            pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), self.radius+4, 2)

class IceShardLobber(Circle):
    def __init__(self):
        super().__init__()
        self.color = (120, 180, 255)
        self.radius = 18
        self.max_hp = 2200
        self.hp = self.max_hp
        self.speed = 0.9
        self.reward = 80
        self.attack_range = 260
        self.attack_cooldown = 3.75
        self.last_attack_time = 0
        self.aoe_radius = 60
        self.damage = 6
        self.waypoint_index = 0
        self.path = []

    def update(self, towers, event_data):
        self.move()
        self.try_attack(towers, event_data)

    def move(self):
        if self.waypoint_index >= len(self.path):
            return

        target_x, target_y = self.path[self.waypoint_index]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.waypoint_index += 1
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def try_attack(self, towers, event_data):
        now = pygame.time.get_ticks() / 1000.0
        if now - self.last_attack_time < self.attack_cooldown:
            return

        target = None
        min_dist = self.attack_range

        for t in towers:
            d = math.hypot(t.x - self.x, t.y - self.y)
            if d <= min_dist:
                min_dist = d
                target = t

        if not target:
            return

        self.last_attack_time = now

        for t in towers:
            d = math.hypot(t.x - target.x, t.y - target.y)
            if d <= self.aoe_radius:
                t.hp -= self.damage

        event_data.setdefault("effects", []).append({
            "type": "ice_aoe",
            "x": target.x,
            "y": target.y,
            "radius": self.aoe_radius,
            "timer": 0.35
        })

class CryingWendigo(Circle):
    def __init__(self):
        super().__init__()
        self.color = (160, 170, 255)
        self.radius = 40
        self.horn_color = (120, 190, 255)
        self.max_hp = 270000
        self.hp = self.max_hp
        self.speed = 1.2
        self.base_speed = self.speed
        self.reward = 3000
        self.base_resonance_radius = 200
        self.resonance_radius = self.base_resonance_radius
        self.base_resonance_damage = 55
        self.resonance_damage = self.base_resonance_damage
        self.base_resonance_rate = 45
        self.resonance_rate = self.base_resonance_rate
        self.resonance_tick = 0
        self.resonance_phase = 0
        self.is_resonating = False
        self.is_boss = True

    def update(self, enemies, towers):
        hp_ratio = self.hp / self.max_hp

        if hp_ratio < 0.3:
            self.resonance_damage = int(self.base_resonance_damage * 1.6)
            self.resonance_rate = int(self.base_resonance_rate * 0.65)
            self.resonance_radius = int(self.base_resonance_radius * 1.15)
        else:
            self.resonance_damage = self.base_resonance_damage
            self.resonance_rate = self.base_resonance_rate
            self.resonance_radius = self.base_resonance_radius

        tower_in_range = False
        for t in towers:
            if not hasattr(t, "hp"):
                continue
            if math.hypot(t.x - self.x, t.y - self.y) <= self.resonance_radius:
                tower_in_range = True
                break

        if tower_in_range:
            self.is_resonating = True
            self.speed = 0
            self.resonance_tick += 1

            if self.resonance_tick >= self.resonance_rate:
                self.resonance_tick = 0
                self.resonance_phase = 1 - self.resonance_phase

                for t in towers:
                    if not hasattr(t, "hp"):
                        continue

                    dist = math.hypot(t.x - self.x, t.y - self.y)

                    if self.resonance_phase == 0:
                        if dist <= self.resonance_radius:
                            t.hp = max(0, t.hp - self.resonance_damage)

                    else:
                        if dist <= self.resonance_radius * 0.6:
                            t.hp = max(0, t.hp - self.resonance_damage)
        else:
            self.is_resonating = False
            self.speed = self.base_speed
            self.resonance_tick = 0
            self.resonance_phase = 0
            super().update()

    def apply_slow(self, amount, duration):
        capped_amount = min(amount, 0.2)
        super().apply_slow(capped_amount, duration)

    def draw(self, surf):
        bar_width = 600
        bar_height = 40
        x = WIDTH // 2 - bar_width // 2
        y = 50

        hp_ratio = self.hp / self.max_hp
        hp_width = int(bar_width * hp_ratio)

        if hp_ratio > 0.6:
            bar_color = (0, 220, 0)
        elif hp_ratio > 0.3:
            bar_color = (230, 220, 0)
        else:
            bar_color = (220, 0, 0)

        pygame.draw.rect(surf, (40, 40, 40), (x, y, bar_width, bar_height))
        pygame.draw.rect(surf, bar_color, (x, y, hp_width, bar_height))
        pygame.draw.rect(surf, (255, 0, 0), (x, y, bar_width, bar_height), 3)

        font = pygame.font.SysFont(None, 32)
        text = f"Crying Wendigo: {self.hp} / {self.max_hp}"
        surf.blit(
            font.render(text, True, (0, 0, 0)),
            font.render(text, True, (0, 0, 0)).get_rect(center=(WIDTH // 2, y + bar_height // 2))
        )
        cx, cy = int(self.x), int(self.y)

        if self.is_resonating:
            r = self.resonance_radius if self.resonance_phase == 0 else int(self.resonance_radius * 0.6)
            pygame.draw.circle(
                surf,
                (180, 40, 60),
                (cx, cy),
                r,
                2
            )

        pygame.draw.circle(surf, self.color, (cx, cy), self.radius)

        eye_y = cy - self.radius * 0.2
        eye_dx = self.radius * 0.35

        pygame.draw.circle(surf, (25, 25, 50), (int(cx - eye_dx), int(eye_y)), 5)
        pygame.draw.circle(surf, (25, 25, 50), (int(cx + eye_dx), int(eye_y)), 5)

        pygame.draw.line(
            surf, (60, 60, 110),
            (cx - eye_dx - 6, eye_y - 2),
            (cx - eye_dx + 6, eye_y - 2), 2
        )
        pygame.draw.line(
            surf, (60, 60, 110),
            (cx + eye_dx - 6, eye_y - 2),
            (cx + eye_dx + 6, eye_y - 2), 2
        )

        tear_offset = (pygame.time.get_ticks() // 120) % 14
        for side in (-1, 1):
            pygame.draw.line(
                surf,
                (120, 200, 255),
                (int(cx + eye_dx * side), int(eye_y + 6)),
                (int(cx + eye_dx * side), int(eye_y + 22 + tear_offset)),
                2
            )

        left_horn = [
            (cx - self.radius * 0.4, cy - self.radius),
            (cx - self.radius * 1.0, cy - self.radius * 0.7),
            (cx - self.radius * 0.9, cy - self.radius * 0.1),
        ]
        right_horn = [
            (cx + self.radius * 0.4, cy - self.radius),
            (cx + self.radius * 1.0, cy - self.radius * 0.7),
            (cx + self.radius * 0.9, cy - self.radius * 0.1),
        ]

        pygame.draw.lines(surf, self.horn_color, False, left_horn, 3)
        pygame.draw.lines(surf, self.horn_color, False, right_horn, 3)

class UnstableSnowGolem(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 26
        self.color = (210, 230, 255)
        self.max_hp = 10800
        self.hp = self.max_hp
        self.speed = 0.5 + random.uniform(-0.05, 0.05)
        self.reward = 350
        self.split_count = 6
        self.ice_resistance = 0.6

    def take_damage(self, amount, damage_type="normal"):
        if damage_type == "ice":
            self.hp -= amount * self.ice_resistance
        else:
            self.hp -= amount

    def split(self):
        children = []
        for _ in range(self.split_count):
            pf = Permafrost()
            pf.x = self.x + random.randint(-8, 8)
            pf.y = self.y + random.randint(-8, 8)
            pf.waypoint_index = self.waypoint_index
            pf.path = path_waypoints_winter
            children.append(pf)
        return children

    def update(self):
        super().update()

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(
            surf, (80, 80, 80),
            (self.x - self.radius, self.y - self.radius - 14, self.radius * 2, 8)
        )
        pygame.draw.rect(
            surf, (0, 200, 0),
            (self.x - self.radius, self.y - self.radius - 14, hp_w, 8)
        )
        pygame.draw.circle(
            surf, self.color,
            (int(self.x), int(self.y)), self.radius
        )

class CorruptedPiJumper(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 18
        self.color = (90, 20, 120)
        self.max_hp = 5500
        self.hp = self.max_hp
        self.speed = 1.1
        self.reward = 250
        self.jump_cooldown = 150
        self.jump_distance_min = 160
        self.jump_distance_max = 220
        self.font_pi = pygame.font.Font(None, self.radius * 2)

    def update(self):
        super().update()

        if self.jump_cooldown <= 0:
            self.jump()
            self.jump_cooldown = 150
        else:
            self.jump_cooldown -= 1

    def jump(self):
        if self.waypoint_index < len(path_waypoints):
            tx, ty = path_waypoints[self.waypoint_index]

            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                nx = dx / dist
                ny = dy / dist

                jump_dist = random.randint(self.jump_distance_min, self.jump_distance_max)

                self.x += nx * jump_dist
                self.y += ny * jump_dist

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (50, 50, 50),
                         (self.x - self.radius, self.y - self.radius - 10, self.radius*2, 6))
        pygame.draw.rect(surf, (200, 50, 50),
                         (self.x - self.radius, self.y - self.radius - 10, hp_w, 6))

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        text_surface = self.font_pi.render("Ψ", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(text_surface, text_rect)

class CorruptedPiMaster(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 60
        self.color = (80, 0, 80)
        self.shield_color = (180, 0, 180)
        self.font_pi = pygame.font.Font(None, self.radius * 4)
        self.max_hp = 200000
        self.hp = self.max_hp
        self.shield_hp_max = 90000
        self.shield_hp = self.shield_hp_max
        self.reward = 8500
        self.speed = 0.3
        self.speed_stage2 = 4.0
        self.damage_reduction = 0.3
        self.shield_active = True
        self.stage2 = False
        self.is_boss = True
        self.waypoint_index = 0
        self.reverse_path = False
        self.bolak_balik_count = 0
        self.max_bolak_balik = 22
        self.finished_bolak_balik = False
        self.spawn_queue_cooldown = 44500
        self.last_spawn_queue_time = 0
        self.initial_spawn_queue = []

    def take_damage(self, amount):
        reduced = amount * (1 - self.damage_reduction)

        if self.shield_active:
            self.shield_hp -= reduced
            if self.shield_hp <= 0:
                self.shield_active = False
                self.stage2 = True
                self.color = (255, 0, 255)

                self.waypoint_index = self.find_closest_waypoint()
        else:
            self.hp -= reduced

    def apply_slow(self, amount, duration):
        capped = min(amount, 0.2)
        super().apply_slow(capped, duration)

    def find_closest_waypoint(self):
        closest = 0
        min_dist = float("inf")
        for i, (wx, wy) in enumerate(path_waypoints_winter):
            d = math.hypot(wx - self.x, wy - self.y)
            if d < min_dist:
                min_dist = d
                closest = i
        return closest

    def update(self, enemies=None, towers=None):
        if enemies is None:
            enemies = []

        if not self.stage2:
            super().update()
            return

        if not self.finished_bolak_balik:
            if not self.reverse_path and self.waypoint_index >= 8:
                self.reverse_path = True
            elif self.reverse_path and self.waypoint_index <= 1:
                self.reverse_path = False
                self.bolak_balik_count += 1

                if self.bolak_balik_count >= self.max_bolak_balik:
                    self.finished_bolak_balik = True
                    self.waypoint_index = 8
                    self.reverse_path = False

        self.waypoint_index = max(
            0, min(self.waypoint_index, len(path_waypoints_winter) - 1)
        )

        tx, ty = path_waypoints_winter[self.waypoint_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * self.speed_stage2
            self.y += ny * self.speed_stage2

        if dist <= self.speed_stage2 + 1:
            if self.reverse_path:
                self.waypoint_index -= 1
            else:
                self.waypoint_index += 1

        now = pygame.time.get_ticks()

        if not self.initial_spawn_queue and now - self.last_spawn_queue_time >= self.spawn_queue_cooldown:
            self.initial_spawn_queue = [
                [ShieldCircle, 20, 200, now],
                [PulseWalker, 9, 500, now],
                [GiantCircle, 6, 1000, now]
            ]
            self.last_spawn_queue_time = now

        for item in list(self.initial_spawn_queue):
            cls, count, interval, last_time = item
            if count > 0 and now - last_time >= interval:
                e = cls()
                e.x, e.y = path_waypoints_winter[0]
                e.waypoint_index = 0
                enemies.append(e)
                item[1] -= 1
                item[3] = now

            if item[1] <= 0:
                self.initial_spawn_queue.remove(item)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)

        pygame.draw.circle(surf, self.color, (x, y), self.radius)

        if self.shield_active:
            pygame.draw.circle(surf, self.shield_color, (x, y), self.radius // 2)

        bar_width = 600
        bar_height = 40
        bx = WIDTH // 2 - bar_width // 2
        by = 50

        shield = max(self.shield_hp if self.shield_active else 0, 0)
        hp = max(self.hp, 0)

        pygame.draw.rect(surf, (50, 50, 50), (bx, by, bar_width, bar_height))

        pygame.draw.rect(
            surf, (0, 255, 0),
            (bx, by, int(bar_width * (hp / self.max_hp)), bar_height)
        )

        if shield > 0:
            pygame.draw.rect(
                surf, (180, 0, 180),
                (bx, by, int(bar_width * (shield / self.shield_hp_max)), bar_height)
            )

        pygame.draw.rect(surf, (255, 0, 0), (bx, by, bar_width, bar_height), 3)

        font = pygame.font.SysFont(None, 32)
        total = hp + shield
        text = f"Corrupted Pi Master: {int(total)} / {int(self.max_hp)}"
        text_surf = font.render(text, True, (0, 0, 0))
        rect = text_surf.get_rect(center=(WIDTH // 2, by + bar_height // 2))

        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            surf.blit(
                font.render(text, True, (255, 0, 0)),
                (rect.x + ox, rect.y + oy)
            )

        surf.blit(text_surf, rect)

        if not self.shield_active:
            psi = self.font_pi.render("Ψ", True, (255, 0, 0))
            surf.blit(psi, psi.get_rect(center=(x, y)))

class Wendralith(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 40
        self.color = (150, 200, 255)
        self.max_hp = 80000
        self.hp = self.max_hp
        self.speed = 0.4
        self.damage_reduction = 0.45
        self.reward = 800

    def update(self):
        super().update()

    def take_damage(self, amount):
        reduced = amount * (1 - self.damage_reduction)
        self.hp -= reduced

    def draw_logo(self, surf, x, y, scale=1.4):
        color = (120, 190, 255)
        thickness = max(2, int(2 * scale))

        temp = pygame.Surface((80, 80), pygame.SRCALPHA)
        cx, cy = 40, 40
        left_horn = [
            (cx - 16*scale, cy + 10*scale),
            (cx - 26*scale, cy + 4*scale),
            (cx - 30*scale, cy - 2*scale),
            (cx - 24*scale, cy - 14*scale),
            (cx - 18*scale, cy - 20*scale),
        ]
        pygame.draw.lines(temp, color, False, left_horn, thickness)

        right_horn = [
            (cx + 16*scale, cy + 10*scale),
            (cx + 26*scale, cy + 4*scale),
            (cx + 30*scale, cy - 2*scale),
            (cx + 24*scale, cy - 14*scale),
            (cx + 18*scale, cy - 20*scale),
        ]
        pygame.draw.lines(temp, color, False, right_horn, thickness)

        pygame.draw.ellipse(
            temp,
            color,
            (cx - 10*scale, cy - 6*scale, 20*scale, 16*scale),
            thickness
        )

        surf.blit(temp, (x - 40, y - 40))

    def draw(self, surf):
        bar_w = self.radius * 2
        hp_ratio = max(self.hp, 0) / self.max_hp
        hp_w = int(bar_w * hp_ratio)

        pygame.draw.rect(
            surf,
            (80, 80, 80),
            (self.x - self.radius, self.y - self.radius - 14, bar_w, 10)
        )
        pygame.draw.rect(
            surf,
            (0, 180, 255),
            (self.x - self.radius, self.y - self.radius - 14, hp_w, 10)
        )

        pygame.draw.circle(
            surf,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        self.draw_logo(surf, self.x, self.y, scale=1.4)

class CorruptedIntruder(Circle):
    def __init__(self):
        super().__init__()
        self.radius = 18
        self.color = (120, 0, 120)
        self.max_hp = 14000
        self.hp = self.max_hp
        self.speed = 1.8 + random.uniform(-0.2, 0.2)
        self.reward = 200
        self.stealth = True
        self.waypoint_index = 0

    def update(self):
        super().update()

    def take_damage(self, amount, damage_type="normal"):
        self.hp -= amount

    def draw(self, surf):
        hp_w = int(self.radius * 2 * (self.hp / self.max_hp))
        pygame.draw.rect(surf, (80, 80, 80),
                         (self.x - self.radius, self.y - self.radius - 8, self.radius*2, 5))
        pygame.draw.rect(surf, (150, 0, 150),
                         (self.x - self.radius, self.y - self.radius - 8, hp_w, 5))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

class GrandShaman(Circle):
    def __init__(self):
        super().__init__()
        self.name = "Grand Shaman"
        self.is_boss = True
        self.radius = 55
        self.color = (120, 190, 255)
        self.hand_color = (160, 210, 255)
        self.staff_color = (120, 90, 60)
        self.staff_orb_idle = (170, 0, 200)
        self.staff_orb_channel = (255, 80, 80)
        self.staff_orb_laser = (255, 0, 255)
        self.staff_orb_heal = (0, 255, 180)
        self.staff_orb_color = self.staff_orb_idle
        self.font_name = pygame.font.SysFont(None, 26)
        self.max_hp = 200000
        self.hp = self.max_hp
        self.speed = 0.35
        self.reward = 12000
        self.summon_interval = 30.0
        self.summon_timer = 0.0
        self.channel_duration = 4.0
        self.channel_timer = 0.0
        self.is_channeling = False
        self.summon_pool = [
            Wendigo,
            HauntingWendigo,
            CryingWendigo
        ]
        self.laser_interval = 6.0
        self.laser_timer = 0.0
        self.laser_damage = 180
        self.laser_duration = 6
        self.lasers = []
        self.heal_threshold = 0.25
        self.heal_amount = 75000
        self.max_desperate_heals = 3
        self.desperate_heals_used = 0
        self.was_below_threshold = False
        self.is_dead = False
        self.death_anim_active = False
        self.to_delete = False
        self.stone_color = (150, 150, 150)
        self.staff_flying = False
        self.staff_x = 0
        self.staff_y = 0
        self.staff_vx = 0
        self.staff_vy = 0
        self.death_timer = 0
        self.DEATH_DURATION = 480

    def update(self, enemies, towers):
        dt = clock.get_time() / 1000.0

        if self.death_anim_active:
            if self.staff_flying:
                self.staff_x += self.staff_vx
                self.staff_y += self.staff_vy
                self.staff_vx *= 0.97
                self.staff_vy *= 0.97

            self.death_timer -= 1
            if self.death_timer <= 0:
                self.to_delete = True
            return

        hp_ratio = self.hp / self.max_hp
        if hp_ratio <= self.heal_threshold:
            if not self.was_below_threshold and self.desperate_heals_used < self.max_desperate_heals:
                self.hp = min(self.hp + self.heal_amount, self.max_hp)
                self.desperate_heals_used += 1
                self.staff_orb_color = self.staff_orb_heal
            self.was_below_threshold = True
        else:
            self.was_below_threshold = False

        for laser in list(self.lasers):
            lx, ly, timer = laser
            timer -= 1
            if timer <= 0:
                self.lasers.remove(laser)
            else:
                idx = self.lasers.index(laser)
                self.lasers[idx] = (lx, ly, timer)

        if self.is_channeling:
            self.channel_timer -= dt
            self.staff_orb_color = self.staff_orb_channel

            if self.channel_timer <= 0:
                self.perform_summon(enemies)
                self.is_channeling = False
                self.staff_orb_color = self.staff_orb_idle
            return

        super().update()

        self.summon_timer += dt
        if self.summon_timer >= self.summon_interval:
            self.start_channel()

        self.laser_timer += dt
        if self.laser_timer >= self.laser_interval:
            self.fire_laser(towers)
            self.laser_timer = 0.0

        if self.hp <= 0 and not self.is_dead:
            self.start_death_animation()

    def apply_slow(self, amount, duration):
        capped_amount = min(amount, 0.2)
        super().apply_slow(capped_amount, duration)

    def start_channel(self):
        self.is_channeling = True
        self.channel_timer = self.channel_duration
        self.summon_timer = 0.0

    def perform_summon(self, enemies):
        enemy_cls = random.choice(self.summon_pool)
        e = enemy_cls()
        e.x, e.y = self.x, self.y
        e.waypoint_index = self.waypoint_index
        e.path = self.path
        enemies.append(e)

    def fire_laser(self, towers):
        if not towers:
            return
        target = random.choice(towers)
        if hasattr(target, "hp"):
            target.hp -= self.laser_damage

        self.lasers.append((target.x, target.y, self.laser_duration))
        self.staff_orb_color = self.staff_orb_laser

    def start_death_animation(self):
        self.is_dead = True
        self.death_anim_active = True
        self.death_timer = self.DEATH_DURATION

        self.color = self.stone_color
        self.hand_color = self.stone_color
        self.staff_orb_color = (0, 0, 0)

        self.staff_flying = True
        self.staff_x = self.x + 80
        self.staff_y = self.y + 40

        ang = random.uniform(0, math.pi * 2)
        self.staff_vx = math.cos(ang) * 14
        self.staff_vy = math.sin(ang) * 14

    def draw_black_logo(self, surf, x, y, scale=1.8):
        color = (0, 0, 0)
        thickness = max(2, int(2 * scale))
        temp = pygame.Surface((110, 110), pygame.SRCALPHA)
        cx, cy = 55, 55

        left_horn = [
            (cx - 18*scale, cy + 12*scale),
            (cx - 32*scale, cy + 6*scale),
            (cx - 36*scale, cy - 2*scale),
            (cx - 28*scale, cy - 20*scale),
            (cx - 20*scale, cy - 30*scale),
        ]
        pygame.draw.lines(temp, color, False, left_horn, thickness)

        right_horn = [
            (cx + 18*scale, cy + 12*scale),
            (cx + 32*scale, cy + 6*scale),
            (cx + 36*scale, cy - 2*scale),
            (cx + 28*scale, cy - 20*scale),
            (cx + 20*scale, cy - 30*scale),
        ]
        pygame.draw.lines(temp, color, False, right_horn, thickness)

        pygame.draw.ellipse(
            temp, color,
            (cx - 14*scale, cy - 10*scale, 28*scale, 20*scale),
            thickness
        )

        surf.blit(temp, (x - 55, y - 55))

    def draw(self, surf):
        x, y = int(self.x), int(self.y)

        if self.death_anim_active:
            pygame.draw.circle(surf, self.stone_color, (x, y), self.radius)
            self.draw_black_logo(surf, x, y)

            if self.staff_flying:
                staff_end = (int(self.staff_x), int(self.staff_y))
                staff_start = (staff_end[0] - 40, staff_end[1] - 20)
                pygame.draw.line(surf, self.staff_color, staff_start, staff_end, 4)
                pygame.draw.circle(surf, (60, 0, 60), staff_end, 8)
            return

        hand_radius = 14
        hand_offset_x = 45
        hand_offset_y = 10

        left_hand = (x - hand_offset_x, y + hand_offset_y)
        right_hand = (x + hand_offset_x, y + hand_offset_y)

        pygame.draw.circle(surf, self.hand_color, left_hand, hand_radius)
        pygame.draw.circle(surf, self.hand_color, right_hand, hand_radius)

        staff_start = right_hand
        staff_end = (x + 80, y + 40)
        pygame.draw.line(surf, self.staff_color, staff_start, staff_end, 4)

        for lx, ly, timer in self.lasers:
            pygame.draw.line(surf, (255, 0, 255), staff_end, (int(lx), int(ly)), 4)

        pygame.draw.circle(surf, self.staff_orb_color, staff_end, 10)
        pygame.draw.circle(surf, self.color, (x, y), self.radius)
        self.draw_black_logo(surf, x, y)

        bar_w = 600
        bar_h = 40
        bx = WIDTH // 2 - bar_w // 2
        by = 100

        ratio = max(self.hp, 0) / self.max_hp
        hp_w = int(bar_w * ratio)

        pygame.draw.rect(surf, (50, 50, 50), (bx, by, bar_w, bar_h))
        pygame.draw.rect(surf, (0, 180, 255), (bx, by, hp_w, bar_h))
        pygame.draw.rect(surf, (255, 255, 255), (bx, by, bar_w, bar_h), 2)

        text = f"{self.name}: {int(self.hp)} / {self.max_hp}"
        text_surf = self.font_name.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(WIDTH // 2, by + bar_h // 2))

        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            outline = self.font_name.render(text, True, (0, 120, 255))
            surf.blit(outline, (text_rect.x + ox, text_rect.y + oy))

        surf.blit(text_surf, text_rect)

# ------------------------------------------------
# TOWER CLASS (Basic)
# ------------------------------------------------
class Tower:
    def __init__(self, x, y):
        self.name = "Square"
        self.cost = 400
        self.total_invest = self.cost
        self.x = x
        self.y = y
        self.size = 30
        self.color = BLUE
        self.range = 100
        self.damage = 30
        self.fire_rate = 0.7
        self.cooldown = 0.0
        self.last_shot_t = 0.0
        self.show_laser_timer = 0
        self.max_hp = 350
        self.hp = self.max_hp
        self.type_name = "Recruit"
        self.bullet_count = 1
        self.accuracy_penalty = 0.0    
        self.accuracy_penalty_timer = 0
        self.fire_rate_modifier = 1.0
        self.slow_timer = 0
        self.level = 1
        self.max_level = 4
        self.upgrade_info = {
            2: ["+12 Damage", "+30 Range", "Fire Rate +6%", "+130 HP"],
            3: ["+16 Damage", "+40 Range", "Fire Rate +12%", "+160 HP"],
            4: ["+30 Damage", "+60 Range", "Fire Rate +25%", "+250 HP"],
        }
        self.upgrade_cost = {
            1: 500,
            2: 800,
            3: 1300
        }

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt

        if self.accuracy_penalty_timer > 0:
            self.accuracy_penalty_timer -= 1
        else:
            self.accuracy_penalty = 0.0

        if self.slow_timer > 0:
            self.slow_timer -= 1
        else:
            self.fire_rate_modifier = 1.0

        target = self.get_first_enemy(enemies)

        if target and self.cooldown <= 0:
            if random.random() < self.accuracy_penalty:
                self.cooldown = self.fire_rate / self.fire_rate_modifier
                self.show_laser_timer = 6
                self.last_shot_pos = (target.x, target.y)
                return

            target.take_damage(self.damage)

            self.cooldown = self.fire_rate / self.fire_rate_modifier

            self.show_laser_timer = 6
            self.last_shot_pos = (target.x, target.y)

    def apply_slow(self, amount, duration):
        new_modifier = max(0.1, 1.0 - amount)

        if new_modifier < self.fire_rate_modifier:
            self.fire_rate_modifier = new_modifier

        self.slow_timer = int(duration * 60)

    def get_first_enemy(self, enemies):
        target = None
        best_progress = -999999

        for e in enemies:
            dx = e.x - self.x
            dy = e.y - self.y
            dist = math.hypot(dx, dy)

            if dist <= self.range:
                if e.waypoint_index > best_progress:
                    best_progress = e.waypoint_index
                    target = e

        return target

    def draw(self, surf, selected=False):
        if selected:
            pygame.draw.circle(surf, (0,0,0), (int(self.x), int(self.y)), self.range, 3)

        pygame.draw.rect(
            surf, self.color,
            (self.x - self.size//2, self.y - self.size//2, self.size, self.size),
            border_radius=6
        )

        level_text = FONT_TOWER.render(str(self.level), True, (0,0,0))
        surf.blit(level_text, (self.x - 6, self.y - 9))

        if getattr(self, "show_laser_timer", 0) > 0:
            try:
                lx, ly = self.last_shot_pos
                pygame.draw.line(
                    surf, YELLOW,
                    (int(self.x), int(self.y)),
                    (int(lx), int(ly)),
                    4
                )
            except Exception:
                pass

            self.show_laser_timer -= 1

        if self.hp < self.max_hp:
            hp_w = int(self.size * (self.hp / self.max_hp))
            pygame.draw.rect(
                surf, (80, 80, 80),
                (self.x - self.size//2, self.y - self.size//2 - 12, self.size, 8)
            )
            pygame.draw.rect(
                surf, (0, 255, 0),
                (self.x - self.size//2, self.y - self.size//2 - 12, hp_w, 8)
            )

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.level += 1

        self.total_invest += self.upgrade_cost[self.level - 1]

        if self.level == 2:
            self.damage += 12
            self.range += 30
            self.fire_rate *= 0.94
            self.max_hp += 130

        elif self.level == 3:
            self.damage += 16
            self.range += 40
            self.fire_rate *= 0.88
            self.max_hp += 160

        elif self.level == 4:
             self.damage += 30
             self.range += 60
             self.fire_rate *= 0.75
             self.max_hp += 250

        self.hp = self.max_hp

    def get_dps(self):
        total_damage = self.damage * self.bullet_count
        return total_damage / self.fire_rate

        self.level_text = FONT_TOWER.render(str(self.level), True, (0,0,0))
        return True

class Shotgunner(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Shotgun Square"
        self.cost = 550
        self.total_invest = self.cost
        self.size = 32
        self.color = (200, 180, 40)
        self.range = 80
        self.damage = 30
        self.pellets = 5
        self.fire_rate = 1.1
        self.max_hp = 300
        self.hp = self.max_hp
        self.type_name = "Breacher"
        self.bullet_count = self.pellets
        self.level = 1
        self.max_level = 4
        self.upgrade_info = {
            2: ["+6 Damage", "+1 Pellet", "+25 Range", "Fire Rate +7%", "+100 HP"],
            3: ["+9 Damage", "+1 Pellet", "+35 Range", "Fire Rate +14%", "+150 HP"],
            4: ["+14 Damage", "+2 Pellets", "+50 Range", "Fire Rate +22%", "+200 HP"],
        }
        self.upgrade_cost = {
            1: 800,
            2: 1200,
            3: 1800
        }
        self.cooldown = 0
        self.last_shots = []
        self.show_laser_timer = 0

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt

        target = self.get_first_enemy(enemies)
        if not target or self.cooldown > 0:
            return

        angle = math.atan2(target.y - self.y, target.x - self.x)
        pellet_spacing = 8
        aoe_radius = 15
        self.last_shots = []
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)
        perp_x = -dir_y
        perp_y = dir_x

        for i in range(self.pellets):
            offset = (i - (self.pellets - 1) / 2) * pellet_spacing

            hit_x = self.x + dir_x * self.range + perp_x * offset
            hit_y = self.y + dir_y * self.range + perp_y * offset

            self.last_shots.append((hit_x, hit_y))

            for e in enemies:
                dist = self.dist_point_to_segment(
                    e.x, e.y,
                    self.x, self.y,
                    hit_x, hit_y
                )
                if dist <= aoe_radius:
                    e.take_damage(self.damage)

        self.show_laser_timer = 3
        self.cooldown = self.fire_rate

    def draw(self, surf, selected=False):
        if selected:
            pygame.draw.circle(
                surf, (0, 0, 0),
                (int(self.x), int(self.y)),
                self.range, 2
            )

        pygame.draw.rect(
            surf, self.color,
            (self.x - self.size//2, self.y - self.size//2,
             self.size, self.size),
            border_radius=6
        )

        level_text = FONT_TOWER.render(str(self.level), True, (0, 0, 0))
        surf.blit(level_text, (self.x - 6, self.y - 9))

        if self.show_laser_timer > 0:
            for hit_x, hit_y in self.last_shots:
                pygame.draw.line(
                    surf, (255, 230, 100),
                    (int(self.x), int(self.y)),
                    (int(hit_x), int(hit_y)),
                    3
                )
            self.show_laser_timer -= 1

        if self.hp < self.max_hp:
            hp_w = int(self.size * (self.hp / self.max_hp))
            pygame.draw.rect(
                surf, (80, 80, 80),
                (self.x - self.size//2,
                 self.y - self.size//2 - 10,
                 self.size, 6)
            )
            pygame.draw.rect(
                surf, (0, 255, 0),
                (self.x - self.size//2,
                 self.y - self.size//2 - 10,
                 hp_w, 6)
            )

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.level += 1
        self.total_invest += self.upgrade_cost[self.level - 1]

        if self.level == 2:
            self.damage += 6
            self.pellets = 6
            self.range += 25
            self.max_hp += 100
            self.fire_rate *= 0.93

        elif self.level == 3:
            self.damage += 9
            self.pellets = 7
            self.range += 35
            self.max_hp += 150
            self.fire_rate *= 0.86

        elif self.level == 4:
            self.damage += 14
            self.pellets = 9
            self.range += 50
            self.max_hp += 200
            self.fire_rate *= 0.78

        self.hp = self.max_hp
        return True

    @staticmethod
    def dist_point_to_segment(px, py, x1, y1, x2, y2):
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D

        param = dot / len_sq if len_sq != 0 else -1

        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D

        dx = px - xx
        dy = py - yy
        return math.hypot(dx, dy)

class ARTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "AR Square"
        self.cost = 480
        self.total_invest = self.cost
        self.size = 28
        self.color = (90, 140, 255)
        self.range = 125
        self.damage = 12
        self.fire_rate = 0.16
        self.max_hp = 320
        self.hp = self.max_hp
        self.type_name = "Ranger"
        self.bullet_count = 1
        self.level = 1
        self.max_level = 4
        self.upgrade_info = {
            2: ["+7 Damage", "+35 Range", "Fire Rate +8%", "+90 HP"],
            3: ["+9 Damage", "+45 Range", "Fire Rate +13%", "+110 HP"],
            4: ["+14 Damage", "+60 Range", "Fire Rate +18%", "+140 HP"],
        }
        self.upgrade_cost = {
            1: 700,
            2: 1000,
            3: 1300
        }

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt

        target = self.get_first_enemy(enemies)

        if not target:
            return

        if self.cooldown <= 0:
            target.take_damage(self.damage)
            self.last_shot_pos = (target.x, target.y)
            self.show_laser_timer = 3
            self.cooldown = self.fire_rate

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.total_invest += self.upgrade_cost[self.level]
        self.level += 1

        if self.level == 2:
            self.damage += 7
            self.range += 35
            self.fire_rate *= 0.92
            self.max_hp += 90
        elif self.level == 3:
            self.damage += 9
            self.range += 45
            self.fire_rate *= 0.87
            self.max_hp += 110
        elif self.level == 4:
            self.damage += 14
            self.range += 60
            self.fire_rate *= 0.82
            self.max_hp += 140

        self.hp = self.max_hp
        return True

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Sniper Square"
        self.cost = 950
        self.total_invest = self.cost
        self.size = 32
        self.color = (200, 200, 255)
        self.range = 300
        self.damage = 150
        self.fire_rate = 2.0
        self.max_hp = 120
        self.hp = self.max_hp
        self.type_name = "Marksman"
        self.bullet_count = 1
        self.level = 1
        self.max_level = 4
        self.upgrade_info = {
            2: ["+50 Damage", "+50 Range", "Fire Rate +10%", "+40 HP"],
            3: ["+70 Damage", "+60 Range", "Fire Rate +15%", "+50 HP"],
            4: ["+100 Damage", "+70 Range", "Fire Rate +20%", "+60 HP"],
        }
        self.upgrade_cost = {
            1: 1000,
            2: 1300,
            3: 1600
        }

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt

        target = self.get_first_enemy(enemies)

        if target and self.cooldown <= 0:
            target.take_damage(self.damage)
            self.last_shot_pos = (target.x, target.y)
            self.show_laser_timer = 8
            self.cooldown = self.fire_rate

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.total_invest += self.upgrade_cost[self.level]
        self.level += 1

        if self.level == 2:
            self.damage += 50
            self.range += 50
            self.fire_rate *= 0.90
            self.max_hp += 40
        elif self.level == 3:
            self.damage += 70
            self.range += 60
            self.fire_rate *= 0.85
            self.max_hp += 50
        elif self.level == 4:
            self.damage += 100
            self.range += 70
            self.fire_rate *= 0.80
            self.max_hp += 60

        self.hp = self.max_hp
        return True

class AKTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "AK Square"
        self.cost = 650
        self.total_invest = self.cost
        self.size = 30
        self.color = (255, 200, 80)
        self.range = 175
        self.damage = 20
        self.fire_rate = 0.20
        self.max_hp = 180
        self.hp = self.max_hp
        self.type_name = "Gunner"
        self.bullet_count = 1
        self.level = 1
        self.max_level = 4
        self.upgrade_info = {
            2: ["+8 Damage", "+30 Range", "Fire Rate +10%", "+50 HP"],
            3: ["+10 Damage", "+40 Range", "Fire Rate +15%", "+60 HP"],
            4: ["+15 Damage", "+50 Range", "Fire Rate +20%", "+70 HP"],
        }
        self.upgrade_cost = {
            1: 800,
            2: 1100,
            3: 1400
        }

    def update(self, dt, enemies):
        super().update(dt, enemies)

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.total_invest += self.upgrade_cost[self.level]
        self.level += 1

        if self.level == 2:
            self.damage += 8
            self.range += 30
            self.fire_rate *= 0.90
            self.max_hp += 50
        elif self.level == 3:
            self.damage += 10
            self.range += 40
            self.fire_rate *= 0.85
            self.max_hp += 60
        elif self.level == 4:
            self.damage += 15
            self.range += 50
            self.fire_rate *= 0.80
            self.max_hp += 70

        self.hp = self.max_hp
        return True

class SMGTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "SMG Square"
        self.cost = 580 
        self.total_invest = self.cost
        self.size = 28
        self.color = (120, 120, 120)
        self.range = 110
        self.damage = 8
        self.fire_rate = 0.08
        self.max_hp = 250
        self.hp = self.max_hp
        self.type_name = "Gunner"
        self.bullet_count = 1
        self.level = 1
        self.max_level = 4
        self.upgrade_info = {
            2: ["+4 Damage", "+15 Range", "Fire Rate +12%", "+40 HP"],
            3: ["+5 Damage", "+20 Range", "Fire Rate +18%", "+50 HP"],
            4: ["+7 Damage", "+25 Range", "Fire Rate +25%", "+60 HP"],
        }
        self.upgrade_cost = {
            1: 750,
            2: 1000,
            3: 1200
        }

    def update(self, dt, enemies):
        super().update(dt, enemies)

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.total_invest += self.upgrade_cost[self.level]
        self.level += 1

        if self.level == 2:
            self.damage += 4
            self.range += 15
            self.fire_rate *= 0.88
            self.max_hp += 40
        elif self.level == 3:
            self.damage += 5
            self.range += 20
            self.fire_rate *= 0.82
            self.max_hp += 50
        elif self.level == 4:
            self.damage += 7
            self.range += 25
            self.fire_rate *= 0.75
            self.max_hp += 60

        self.hp = self.max_hp
        return True

class LaserTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Laser Circle"
        self.cost = 1200
        self.total_invest = self.cost
        self.size = 35
        self.color = (150, 0, 255)
        self.range = 200
        self.damage = 15
        self.fire_rate = 0.1
        self.max_hp = 200
        self.hp = self.max_hp
        self.type_name = "Marksman"
        self.bullet_count = 1
        self.level = 1
        self.max_level = 4
        self.firing_beam = False
        self.target_enemy = None
        self.beam_timer = 0
        self.beam_duration = 0.08
        self.upgrade_info = {
            2: ["+5 Damage", "+30 Range", "Fire Rate +5%", "+40 HP"],
            3: ["+8 Damage", "+40 Range", "Fire Rate +10%", "+50 HP"],
            4: ["+12 Damage", "+50 Range", "Fire Rate +15%", "+60 HP"],
        }
        self.upgrade_cost = {
            1: 1500,
            2: 2000,
            3: 2800
        }

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt

        if self.beam_timer > 0:
            self.beam_timer -= dt
        else:
            self.firing_beam = False

        target = self.get_first_enemy(enemies)

        if not target:
            self.firing_beam = False
            self.target_enemy = None
            return

        if self.cooldown <= 0:
            self.target_enemy = target
            target.take_damage(self.damage)

            self.cooldown = self.fire_rate
            self.firing_beam = True
            self.beam_timer = self.beam_duration

    def draw(self, surf, selected=False):

        if selected:
            pygame.draw.circle(surf, (0, 0, 0), (int(self.x), int(self.y)), self.range, 3)

        pygame.draw.circle(
            surf,
            self.color,
            (int(self.x), int(self.y)),
            self.size // 2
        )

        level_text = FONT_TOWER.render(str(self.level), True, (0, 0, 0))
        surf.blit(level_text, (self.x - 6, self.y - 9))

        if self.firing_beam and self.target_enemy:
            lx, ly = self.target_enemy.x, self.target_enemy.y
            pygame.draw.line(
                surf, (255, 0, 255),
                (int(self.x), int(self.y)),
                (int(lx), int(ly)),
                6
            )

        if self.hp < self.max_hp:
            hp_w = int(self.size * (self.hp / self.max_hp))

            pygame.draw.rect(
                surf, (80, 80, 80),
                (self.x - self.size//2, self.y - self.size//2 - 14, self.size, 8)
            )
            pygame.draw.rect(
                surf, (0, 255, 0),
                (self.x - self.size//2, self.y - self.size//2 - 14, hp_w, 8)
            )

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.total_invest += self.upgrade_cost[self.level]
        self.level += 1

        if self.level == 2:
            self.damage += 5
            self.range += 30
            self.fire_rate *= 0.95
            self.max_hp += 40

        elif self.level == 3:
            self.damage += 8
            self.range += 40
            self.fire_rate *= 0.90
            self.max_hp += 50

        elif self.level == 4:
            self.damage += 12
            self.range += 50
            self.fire_rate *= 0.85
            self.max_hp += 60

        self.hp = self.max_hp
        return True

class MafiaTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Mafia Circle"
        self.cost = 700
        self.total_invest = self.cost
        self.size = 34
        self.color = (139, 69, 19)
        self.range = 110
        self.damage = 28
        self.fire_rate = 1.0
        self.cooldown = 0.0
        self.max_hp = 420
        self.hp = self.max_hp
        self.type_name = "Ranger"
        self.bullet_count = 1
        self.level = 1
        self.max_level = 4
        self.cash_per_interval = 50
        self.cash_interval = 3.5
        self.cash_timer = 0.0
        self.show_laser_timer = 0
        self.last_shot_pos = (self.x, self.y)
        self.upgrade_info = {
            2: ["+10 Damage", "+25 Income", "-0.4s Interval", "+80 HP", "+15 Range", "Fire Rate +12%"],
            3: ["+15 Damage", "+35 Income", "-0.4s Interval", "+100 HP", "+20 Range", "Fire Rate +18%"],
            4: ["+22 Damage", "+45 Income", "-0.4s Interval", "+130 HP", "+30 Range", "Fire Rate +25%"],
        }
        self.upgrade_cost = {
            1: 1000,
            2: 1500,
            3: 2200
        }

    def update(self, dt, enemies, state_data=None):
        self.cash_timer += dt
        if self.cash_timer >= self.cash_interval:
            self.cash_timer -= self.cash_interval
            if state_data is not None:
                state_data['money'] += self.cash_per_interval

        self.cooldown -= dt
        target = self.get_first_enemy(enemies)

        if target and self.cooldown <= 0:
            target.take_damage(self.damage)
            self.cooldown = self.fire_rate

            self.last_shot_pos = (target.x, target.y)
            self.show_laser_timer = 6

        super().update(dt, enemies)

    def draw(self, surf, selected=False):
        if selected:
            pygame.draw.circle(surf, (0,0,0), (int(self.x), int(self.y)), self.range, 3)

        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size // 2)

        level_text = FONT_TOWER.render(str(self.level), True, (0, 0, 0))
        surf.blit(level_text, (self.x - 6, self.y - 9))

        progress = self.cash_timer / self.cash_interval
        if progress > 0.3:
            money_text = FONT_TOWER.render(f"+{self.cash_per_interval}", True, (255, 215, 0))
            surf.blit(money_text, (self.x - 15, self.y - self.size//2 - 25))

        if self.show_laser_timer > 0:
            try:
                lx, ly = self.last_shot_pos
                pygame.draw.line(
                    surf, (255, 255, 0),
                    (int(self.x), int(self.y)),
                    (int(lx), int(ly)),
                    4
                )
            except:
                pass

            self.show_laser_timer -= 1

        if self.hp < self.max_hp:
            hp_w = int(self.size * (self.hp / self.max_hp))
            pygame.draw.rect(
                surf, (80, 80, 80),
                (self.x - self.size//2, self.y - self.size//2 - 14, self.size, 8)
            )
            pygame.draw.rect(
                surf, (0, 255, 0),
                (self.x - self.size//2, self.y - self.size//2 - 14, hp_w, 8)
            )

    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.total_invest += self.upgrade_cost[self.level]
        self.level += 1

        if self.level == 2:
            self.damage += 10
            self.cash_per_interval += 25
            self.cash_interval = max(0.3, self.cash_interval - 0.4)
            self.max_hp += 80
            self.range += 15
            self.fire_rate *= 0.88

        elif self.level == 3:
            self.damage += 15
            self.cash_per_interval += 35
            self.cash_interval = max(0.3, self.cash_interval - 0.4)
            self.max_hp += 100
            self.range += 20
            self.fire_rate *= 0.82

        elif self.level == 4:
            self.damage += 22
            self.cash_per_interval += 45
            self.cash_interval = max(0.3, self.cash_interval - 0.4)
            self.max_hp += 130
            self.range += 30
            self.fire_rate *= 0.75

        self.hp = self.max_hp
        return True

class FrostBlasterTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Frost Blaste Squarer"
        self.type_name = "Ranger"
        self.cost = 1800
        self.total_invest = self.cost
        self.color = (160, 220, 255)
        self.laser_color = (190, 240, 255)
        self.laser_glow_color = (220, 250, 255)
        self.size = 32
        self.range = 160
        self.damage = 9
        self.fire_rate = 0.25
        self.max_hp = 380
        self.hp = self.max_hp
        self.chill_stacks = {}
        self.freeze_threshold = 18
        self.freeze_duration = 0.6
        self.slow_per_hit = 0.04
        self.max_slow = 0.3
        self.max_level = 4
        self.upgrade_cost = {
            1: 1000,
            2: 1600,
            3: 2500
        }
        self.upgrade_info = {
            2: ["+3 Damage", "+15 Range", "Freeze lebih cepat"],
            3: ["+4 Damage", "+20 Range", "+Slow stack"],
            4: ["+7 Damage", "Freeze +0.2s", "Overfreeze chance"],
        }

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt

        target = self.get_first_enemy(enemies)
        if not target or self.cooldown > 0:
            return

        target.take_damage(self.damage, damage_type="ice")

        stacks = self.chill_stacks.get(id(target), 0)
        if hasattr(target, "apply_slow"):
            slow_value = min(stacks * self.slow_per_hit, self.max_slow)
            target.apply_slow(slow_value, 0.2)

        stacks += 1
        self.chill_stacks[id(target)] = stacks

        if stacks >= self.freeze_threshold:
            if not getattr(target, "is_boss", False):
                if hasattr(target, "freeze"):
                    target.freeze(self.freeze_duration)
            self.chill_stacks[id(target)] = 0

        self.show_laser_timer = 3
        self.last_shot_pos = (target.x, target.y)
        self.cooldown = self.fire_rate

    def draw(self, surf, selected=False):
        if selected:
            pygame.draw.circle(
                surf,
                (0, 0, 0),
                (int(self.x), int(self.y)),
                self.range,
                3
            )

        pygame.draw.rect(
            surf,
            self.color,
            (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size),
            border_radius=6
        )

        level_text = FONT_TOWER.render(str(self.level), True, (0, 0, 0))
        surf.blit(level_text, (self.x - 6, self.y - 9))

        if getattr(self, "show_laser_timer", 0) > 0:
            try:
                lx, ly = self.last_shot_pos
                pygame.draw.line(
                    surf,
                    self.laser_glow_color,
                    (int(self.x), int(self.y)),
                    (int(lx), int(ly)),
                    6
                )
                pygame.draw.line(
                    surf,
                    self.laser_color,
                    (int(self.x), int(self.y)),
                    (int(lx), int(ly)),
                    3
                )
            except Exception:
                pass

            self.show_laser_timer -= 1

        if self.hp < self.max_hp:
            hp_w = int(self.size * (self.hp / self.max_hp))
            pygame.draw.rect(
                surf,
                (80, 80, 80),
                (self.x - self.size // 2, self.y - self.size // 2 - 12, self.size, 8)
            )
            pygame.draw.rect(
                surf,
                (0, 255, 0),
                (self.x - self.size // 2, self.y - self.size // 2 - 12, hp_w, 8)
            )

# ------------------------------------------------
# UI UPGRADE (FUNGSI DI LUAR CLASS)
# ------------------------------------------------
def draw_upgrade_ui(screen, tower):
    if tower is None:
        return None, None

    PANEL_X, PANEL_Y = 20, 20
    PANEL_W, PANEL_H = 320, 620
    PADDING_X = 25
    
    panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)

    pygame.draw.rect(screen, LIGHT_GRAY, panel_rect, border_radius=12)
    pygame.draw.rect(screen, MID_GRAY, (PANEL_X, PANEL_Y, PANEL_W, 60), border_radius=12)

    title_surface = font_mid.render(f"{tower.name}", True, BLACK)
    screen.blit(title_surface, (PANEL_X + PADDING_X - 5, PANEL_Y + 15))

    current_y = PANEL_Y + 80
    LINE_HEIGHT_STATS = 24
    
    stats_text = [
        f"Level    : {tower.level}",
        f"Type     : {tower.type_name}",
        f"DPS      : {tower.get_dps():.1f}",
        f"Damage    : {tower.damage}",
        f"Fire Rate   : {tower.fire_rate:.2f}s",
        f"Cooldown : {max(0, tower.cooldown):.2f}s",
        f"Range    : {tower.range}",
        f"HP          : {tower.hp}/{tower.max_hp}",
    ]

    for s in stats_text:
        stat_surface = font_small.render(s, True, BLACK)
        screen.blit(stat_surface, (PANEL_X + PADDING_X, current_y))
        current_y += LINE_HEIGHT_STATS

    current_y = PANEL_Y + 280 
    LINE_HEIGHT_EFFECTS = 20
    
    effects_title_surface = font_mid.render("Effects:", True, BLACK)
    screen.blit(effects_title_surface, (PANEL_X + PADDING_X, current_y))
    current_y += effects_title_surface.get_height() + 5

    effects = []
    if tower.fire_rate_modifier < 1.0:
        effects.append(f"Slowed ({int(tower.slow_timer/60)}s left)") 
    if tower.accuracy_penalty > 0:
        effects.append(f"Miss Chance: {int(tower.accuracy_penalty*100)}%")

    if not effects:
        effects.append("No Active Effects")

    for ef in effects:
        effect_surface = font_small.render(ef, True, DARK_GRAY_TEXT)
        screen.blit(effect_surface, (PANEL_X + PADDING_X + 10, current_y))
        current_y += LINE_HEIGHT_EFFECTS

    PREVIEW_Y = PANEL_Y + PANEL_H - 120
    
    if tower.level < tower.max_level:
        upgrade_title_surface = font_mid.render("Next Upgrade:", True, BLACK)
        screen.blit(upgrade_title_surface, (PANEL_X + PADDING_X, PREVIEW_Y - 35))
        current_y = PREVIEW_Y + upgrade_title_surface.get_height() - 195

        next_lv = tower.level + 1

        preview = tower.upgrade_info.get(next_lv, [])
        upgrade_price = tower.upgrade_cost.get(tower.level, 0)

        for p in preview:
            preview_surface = font_small.render(p, True, BLACK)
            screen.blit(preview_surface, (PANEL_X + PADDING_X + 10, current_y))
            current_y += preview_surface.get_height() + 3

        cost_surface = font_small.render(f"Cost: {upgrade_price}", True, BLUE_COST)
        screen.blit(cost_surface, (PANEL_X + PADDING_X, PANEL_Y + PANEL_H - 95))

    else:
        max_level_surface = font_small.render("Max Level Reached", True, DARK_GRAY_TEXT)
        screen.blit(max_level_surface, (PANEL_X + PADDING_X, PANEL_Y + PANEL_H - 95))
        upgrade_price = None

    BUTTON_Y = PANEL_Y + PANEL_H - 60 
    BUTTON_W, BUTTON_H = 130, 45
    BUTTON_GAP = 10

    upgrade_rect = pygame.Rect(PANEL_X + PADDING_X, BUTTON_Y, BUTTON_W, BUTTON_H)

    if tower.level < tower.max_level:
        pygame.draw.rect(screen, BLUE_BUTTON, upgrade_rect, border_radius=10)
        upgrade_text = font_small.render("Upgrade", True, WHITE)
    else:
        pygame.draw.rect(screen, MID_GRAY, upgrade_rect, border_radius=10)
        upgrade_text = font_small.render("Max", True, WHITE)

    screen.blit(
        upgrade_text,
        (
            upgrade_rect.x + (BUTTON_W - upgrade_text.get_width()) // 2,
            upgrade_rect.y + (BUTTON_H - upgrade_text.get_height()) // 2
        )
    )

    sell_price = int(tower.total_invest * 0.65)
    sell_rect = pygame.Rect(PANEL_X + PADDING_X + BUTTON_W + BUTTON_GAP, BUTTON_Y, BUTTON_W, BUTTON_H)
    pygame.draw.rect(screen, RED_BUTTON, sell_rect, border_radius=10)
    sell_text = font_small.render(f"Sell ({sell_price})", True, WHITE)
    screen.blit(sell_text, (sell_rect.x + (BUTTON_W - sell_text.get_width()) // 2, sell_rect.y + (BUTTON_H - sell_text.get_height()) // 2))

    return upgrade_rect, sell_rect

TOWER_TYPES = {
    "Pistol (400)": Tower,
    "Shotgun (550)": Shotgunner,
    "AR (480)": ARTower,
    "AK (650)": AKTower,

    "SMG (580)": SMGTower,
    "Mafia (700)": MafiaTower,
    "Sniper (950)": SniperTower,
    "Laser (1200)": LaserTower,
    "Frost Blaster (1800)": FrostBlasterTower,
}

# ------------------------------------------------
# CHAPTER 1 START SCREEN – sebelum gameplay
# ------------------------------------------------
def chapter1_start_screen():
    global chapter1_state
    global wave

    mouse_pos = pygame.mouse.get_pos()
    screen.fill(GREEN_BG)

    draw_circle_animation()

    title = font_big.render("CHAPTER I", True, WHITE)
    subtitle = font_mid.render("CIRCLE INVASION", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 130))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 230))

    desc = font_small.render("‎Circle Merah menentang Square dan harus menghentikannya sebelum semuanya hancur.", True, WHITE)
    screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 330))

    start_btn = draw_button("MULAI", WIDTH//2 - 200, 450, 400, 110, mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(mouse_pos):
                chapter1_state = "tower_select"

    pygame.display.update()

def tower_selection_screen(state_data):
    global chapter1_state
    screen.fill(DARK_GRAY_TEXT)

    # ===========================
    # Judul
    # ===========================
    title = font_big.render("Pilih 4 Tower", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

    # ===========================
    # Dapatkan tower yang dimiliki
    # ===========================
    owned_towers = [name for name, data in towers_data.items() if data["owned"]]

    # ===========================
    # Paging
    # ===========================
    towers_per_page = 8
    current_page = state_data.get('tower_page', 0)
    total_pages = (len(owned_towers) + towers_per_page - 1) // towers_per_page
    start_idx = current_page * towers_per_page
    end_idx = start_idx + towers_per_page
    displayed_towers = owned_towers[start_idx:end_idx]

    # ===========================
    # Grid posisi
    # ===========================
    positions = [
        (100, 200), (400, 200), (700, 200), (1000, 200),
        (100, 350), (400, 350), (700, 350), (1000, 350)
    ]
    w, h = 250, 120
    buttons = {}

    for idx, name in enumerate(displayed_towers):
        x, y = positions[idx]
        rect = pygame.Rect(x, y, w, h)

        if name in state_data['selected_towers']:
            pygame.draw.rect(screen, (100, 100, 255), rect)
            pygame.draw.rect(screen, (255, 255, 0), rect, 5)
        else:
            pygame.draw.rect(screen, (50, 50, 50), rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

        tower_text = font_small.render(name, True, WHITE)
        screen.blit(tower_text, (x + w//2 - tower_text.get_width()//2,
                                 y + h//2 - tower_text.get_height()//2))

        buttons[name] = rect

    # ===========================
    # Tombol MULAI
    # ===========================
    start_btn_color = GREEN_BG if len(state_data['selected_towers']) == 4 else GRAY
    start_btn_rect = pygame.Rect(WIDTH//2 - 200, 500, 400, 110)
    pygame.draw.rect(screen, start_btn_color, start_btn_rect)
    start_text = font_big.render("MULAI", True, WHITE)
    screen.blit(start_text, (start_btn_rect.x + start_btn_rect.w//2 - start_text.get_width()//2,
                             start_btn_rect.y + start_btn_rect.h//2 - start_text.get_height()//2))

    # ===========================
    # Tombol Next / Previous
    # ===========================
    prev_rect = pygame.Rect(50, 500, 150, 50)
    next_rect = pygame.Rect(WIDTH - 200, 500, 150, 50)
    pygame.draw.rect(screen, WHITE if current_page > 0 else GRAY, prev_rect)
    pygame.draw.rect(screen, WHITE if current_page < total_pages-1 else GRAY, next_rect)

    prev_text = font_small.render("Previous", True, DARK_GRAY_TEXT)
    next_text = font_small.render("Next", True, DARK_GRAY_TEXT)
    screen.blit(prev_text, (prev_rect.x + prev_rect.w//2 - prev_text.get_width()//2,
                            prev_rect.y + prev_rect.h//2 - prev_text.get_height()//2))
    screen.blit(next_text, (next_rect.x + next_rect.w//2 - next_text.get_width()//2,
                            next_rect.y + next_rect.h//2 - next_text.get_height()//2))

    # ===========================
    # Daftar tower yang dipilih
    # ===========================
    for i, t in enumerate(state_data['selected_towers']):
        text = font_small.render(t, True, WHITE)
        screen.blit(text, (50, 550 + i*30))

    # ===========================
    # Event Handling
    # ===========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            for name, rect in buttons.items():
                if rect.collidepoint(pos):
                    if name in state_data['selected_towers']:
                        state_data['selected_towers'].remove(name)
                    elif len(state_data['selected_towers']) < 4:
                        state_data['selected_towers'].append(name)
                    break

            if start_btn_rect.collidepoint(pos) and len(state_data['selected_towers']) == 4:
                chapter1_state = "playing"

            if prev_rect.collidepoint(pos) and current_page > 0:
                state_data['tower_page'] = current_page - 1
            if next_rect.collidepoint(pos) and current_page < total_pages - 1:
                state_data['tower_page'] = current_page + 1

    pygame.display.update()

def draw_lose_popup(screen, state_data):
    global current_lose_message

    if current_lose_message is None:
        pesan_list = [
            "Kalian tidak bisa merebut wilayah kami",
            "Kekuatan kalian tak berarti",
            "Kalian kembali saja ke kandang",
            "Ini adalah akhir perjuanganmu",
            "Kami selalu menang",
            "Kalian hanyalah gangguan"
        ]
        current_lose_message = random.choice(pesan_list)

    wave_reached = state_data['wave'] + 1
    base_reward = 40
    wave_bonus = wave_reached * 3
    total_reward = base_reward + wave_bonus

    if not state_data.get("lose_reward_given", False):
        save["shape"] = save.get("shape", 0) + total_reward
        save_data(save)
        state_data["lose_reward_given"] = True

    overlay_w, overlay_h = 1612, 720
    overlay_x = WIDTH//2 - overlay_w//2
    overlay_y = HEIGHT//2 - overlay_h//2

    overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (overlay_x, overlay_y))

    box_w, box_h = 550, 480
    box_x = WIDTH//2 - box_w//2
    box_y = HEIGHT//2 - box_h//2

    pygame.draw.rect(screen, (255, 0, 0), (box_x, box_y, box_w, box_h), 10)
    pygame.draw.rect(screen, (20, 0, 0), (box_x+10, box_y+10, box_w-20, box_h-20))

    cx, cy = box_x + box_w//2, box_y + 130
    r = 60
    pygame.draw.circle(screen, (255, 60, 60), (cx, cy), r)

    pygame.draw.circle(screen, (0, 0, 0), (cx - 20, cy - 15), 8)
    pygame.draw.circle(screen, (0, 0, 0), (cx + 20, cy - 15), 8)

    pygame.draw.arc(
        screen,
        (0, 0, 0),
        (cx - 30, cy - 10, 60, 50),
        0,
        3.14,
        4
    )

    lose_text = font_big.render("LOSE", True, (255, 80, 80))
    screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, box_y + 30))

    text_obj = font_small.render(current_lose_message, True, (255, 80, 80))
    screen.blit(text_obj, (WIDTH//2 - text_obj.get_width()//2, cy + 80))

    reward_title = font_mid.render("Reward:", True, (255, 200, 100))
    screen.blit(reward_title, (WIDTH//2 - reward_title.get_width()//2, cy + 130))

    wave_text = font_small.render(f"Wave Reached: {wave_reached}", True, (255, 180, 80))
    screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, cy + 175))

    shape_obj = font_small.render(f"+{total_reward} Shape", True, (100, 255, 255))
    screen.blit(shape_obj, (WIDTH//2 - shape_obj.get_width()//2, cy + 210))

    exit_w, exit_h = 240, 90
    exit_x = WIDTH//2 - exit_w//2
    exit_y = box_y + box_h - exit_h - 30

    pygame.draw.rect(screen, (255, 0, 0), (exit_x, exit_y, exit_w, exit_h), 8)
    exit_text = font_mid.render("EXIT", True, (255, 200, 200))
    screen.blit(
        exit_text,
        (
            exit_x + exit_w//2 - exit_text.get_width()//2,
            exit_y + exit_h//2 - exit_text.get_height()//2
        )
    )

    return pygame.Rect(exit_x, exit_y, exit_w, exit_h)

def draw_win_popup(screen):
    global current_win_message

    if current_win_message is None:
        pesan_list = [
            "Kemenangan mutlak!",
            "Wilayah berhasil dipertahankan!",
            "Tidak ada yang bisa menembus pertahanan kalian!",
            "Kekalahan bukan bagian dari rencana kami!",
            "Circle berhasil dipukul mundur!"
        ]
        current_win_message = random.choice(pesan_list)

    overlay_w, overlay_h = 1612, 720
    overlay_x = WIDTH//2 - overlay_w//2
    overlay_y = HEIGHT//2 - overlay_h//2

    overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (overlay_x, overlay_y))

    box_w, box_h = 550, 420
    box_x = WIDTH//2 - box_w//2
    box_y = HEIGHT//2 - box_h//2

    pygame.draw.rect(screen, (0, 0, 255), (box_x, box_y, box_w, box_h), 10)
    pygame.draw.rect(screen, (0, 50, 200), (box_x+10, box_y+10, box_w-20, box_h-20))

    win_text = font_big.render("WIN!", True, (80, 200, 255))
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, box_y + 30))

    cx, cy = box_x + box_w//2, box_y + 150
    size = 80
    rect = pygame.Rect(cx - size//2, cy - size//2, size, size)
    pygame.draw.rect(screen, (0, 0, 255), rect)

    pygame.draw.circle(screen, (0, 0, 0), (cx - 20, cy - 15), 8)
    pygame.draw.circle(screen, (0, 0, 0), (cx + 20, cy - 15), 8)

    pygame.draw.arc(
        screen,
        (0, 0, 0),
        (cx - 30, cy - 10, 60, 50),
        3.14, 0, 4
    )

    text_obj = font_small.render(current_win_message, True, (160, 220, 255))
    screen.blit(text_obj, (WIDTH//2 - text_obj.get_width()//2, cy + 80))

    shape_obj = font_small.render("+400 Shape diperoleh!", True, (100, 255, 255))
    screen.blit(shape_obj, (WIDTH//2 - shape_obj.get_width()//2, cy + 130))

    exit_w, exit_h = 240, 90
    exit_x = WIDTH//2 - exit_w//2
    exit_y = box_y + box_h - exit_h - 30

    pygame.draw.rect(screen, (0, 0, 255), (exit_x, exit_y, exit_w, exit_h), 8)
    exit_text = font_mid.render("EXIT", True, (180, 220, 255))
    screen.blit(
        exit_text,
        (
            exit_x + exit_w//2 - exit_text.get_width()//2,
            exit_y + exit_h//2 - exit_text.get_height()//2
        )
    )

    return pygame.Rect(exit_x, exit_y, exit_w, exit_h)

def spawn_enemy_by_type(t, state_data):
    if t == "basic": return Circle()
    elif t == "fast": return FastCircle()
    elif t == "tiny": return TinyCircle()
    elif t == "armored": return ArmoredCircle()
    elif t == "mafia": return MafiaCent()
    elif t == "splitter": return SplitterCircle()
    elif t == "shield": return ShieldCircle()
    elif t == "phase": return PhaseCircle()
    elif t == "pi_jumper": return PiJumper()
    elif t == "rogue": return RogueCircle()
    elif t == "giant": return GiantCircle()
    elif t == "pulse": return PulseWalker()
    elif t == "pi_master": return PiMaster()
    elif t == "chrono": return ChronoCircle()
    elif t == "fast_giant": return FastGiantCircle()
    elif t == "orbital": return OrbitalCircle()
    elif t == "titan": return TitanCircle()
    elif t == "boss": return CycleLead()
    return None

def start_wave(state_data, wave_index):
    spawner = {
        "wave_id": wave_index,
        "subwaves": [],
        "index": 0,
        "next_spawn": 0,
        "finished": False
    }

    for sw in waves[wave_index]:
        spawner["subwaves"].append({
            "type": sw["type"],
            "interval": sw["interval"],
            "remaining": sw["count"]
        })

    state_data["active_waves"].append(spawner)

def chapter1_screen(state_data):
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    screen.fill(GREEN_BG)

    if state_data["wave"] == 0 and len(state_data["active_waves"]) == 0:
        start_wave(state_data, 0)
    
    # ============================
    # PAUSE POPUP (SURRENDER)
    # ============================
    if state_data.get('paused') == "surrender":
        overlay = pygame.Surface((WIDTH + 220, HEIGHT + 40), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        popup = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 450, 300)
        pygame.draw.rect(screen, (50, 50, 50), popup)
        pygame.draw.rect(screen, (255, 255, 255), popup, 4)

        text = font_small.render("Apakah kamu yakin menyerah?", True, WHITE)
        screen.blit(text, (popup.x + 40, popup.y + 40))

        yes_btn = draw_button("Ya", popup.x + 60, popup.y + 150, 120, 60, mouse_pos)
        no_btn = draw_button("Tidak", popup.x + 220, popup.y + 150, 120, 60, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if yes_btn.collidepoint((mx, my)):
                    return "menu"
                if no_btn.collidepoint((mx, my)):
                    state_data['paused'] = False

        pygame.display.update()
        return "game"
 
    pygame.draw.rect(screen, CREAM2, (200, 0, 200, HEIGHT))
    pygame.draw.rect(screen, CREAM2, (200, 300, 800, 200))
    draw_path(screen, path_waypoints, width=25)

    title = font_mid.render(f"Wave: {state_data['wave']+1}", True, WHITE)
    screen.blit(title, (40, 20))

    skip_btn = draw_button("Lewati Wave", 40, 230, 250, 70, mouse_pos)

    data = game_data[1]
    money_text = font_small.render(f"Money: {state_data['money']}", True, YELLOW)
    hp_text = font_small.render(f"Base HP: {state_data['base_hp']}", True, (0, 255, 0))
    screen.blit(money_text, (40, 80))
    screen.blit(hp_text, (40, 120))

    total_tower = len(state_data["towers"])
    tower_color = (255, 0, 0) if total_tower >= 40 else WHITE
    tower_text = font_small.render(f"Total Square: {total_tower}/40", True, tower_color)
    screen.blit(tower_text, (40, 160))

    back_btn = draw_button("Menyerah", 50, 635, 250, 80, mouse_pos)

    tower_btns = []
    if 'selected_towers' in state_data:
        for i, t_name in enumerate(state_data['selected_towers']):
            btn = draw_button(t_name, WIDTH - 250, 50 + i*150, 250, 120, mouse_pos)
            tower_btns.append((t_name, btn))

    max_wp = len(path_waypoints)

    for e in list(state_data['enemies']):

        if isinstance(e, CycleLead) and e.death_anim_active:
            e.update(state_data['enemies'], state_data['towers'])
            e.draw(screen)
            continue

        if isinstance(e, CycleLead) and e.to_delete:
            try:
                state_data['enemies'].remove(e)
            except ValueError:
                pass
            continue

        if isinstance(e, (MafiaCent, PiMaster, TitanCircle, CycleLead)):
            e.update(state_data['enemies'], state_data['towers'])
        else:
            e.update()

        e.draw(screen)

        if e.waypoint_index >= max_wp:

            if isinstance(e, CycleLead):
                e.waypoint_index = 0
            else:
                state_data['base_hp'] -= int(e.hp)
                try:
                    state_data['enemies'].remove(e)
                except ValueError:
                    pass

            continue

        if e.hp <= 0:
            if isinstance(e, CycleLead):
                continue

            if isinstance(e, SplitterCircle):
                children = e.split()
                for c in children:
                    c.x, c.y = e.x, e.y
                    state_data['enemies'].append(c)

            state_data['money'] += e.reward

            try:
                state_data['enemies'].remove(e)
            except ValueError:
                pass

    dt = clock.get_time() / 1000.0

    for t in list(state_data['towers']):
        if isinstance(t, MafiaTower):
            t.update(dt, state_data['enemies'], state_data=state_data)
        else:
            t.update(dt, state_data['enemies'])

        t.draw(screen, selected=(state_data['selected_tower'] == t))

        if t.hp <= 0:
            state_data['towers'].remove(t)

    st = state_data['selected_tower']
    if st:
        upgrade_rect, sell_rect = draw_upgrade_ui(screen, st)
        st.upgrade_rect = upgrade_rect
        st.sell_rect = sell_rect

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            mouse_pos = (mx, my)
            ui_closed_this_frame = False

            for t_name, btn in tower_btns:
                if btn.collidepoint(mouse_pos):
                    state_data['selected_tower_type'] = t_name
                    state_data['selected_tower'] = None
                    state_data['place_mode'] = False
                    state_data['pending_pos'] = None
                    break

            if back_btn.collidepoint(mouse_pos):
                state_data['paused'] = "surrender"
                return "game"

            if skip_btn.collidepoint(mouse_pos):
                next_wave = state_data["wave"] + 1
                if next_wave < len(waves):
                    start_wave(state_data, next_wave)
                    state_data["wave"] = next_wave
                continue

            clicked_on_tower = False
            for t in state_data['towers']:
                if t.x - t.size//2 <= mx <= t.x + t.size//2 and \
                   t.y - t.size//2 <= my <= t.y + t.size//2:
                    state_data['selected_tower'] = t
                    clicked_on_tower = True
                    break
            if clicked_on_tower:
                continue

            st = state_data['selected_tower']
            if st:
                if hasattr(st, 'upgrade_rect') and st.upgrade_rect.collidepoint(mx, my):
                    lvl = st.level
                    cost = st.upgrade_cost.get(lvl)
                    if cost and state_data['money'] >= cost:
                        state_data['money'] -= cost
                        st.upgrade()
                    continue

                if hasattr(st, 'sell_rect') and st.sell_rect.collidepoint(mx, my):
                    refund = int(st.total_invest * 0.65)
                    state_data['money'] += refund
                    if st in state_data['towers']:
                        state_data['towers'].remove(st)
                    state_data['selected_tower'] = None
                    continue

            if state_data['selected_tower'] is not None:
                state_data['selected_tower'] = None
                ui_closed_this_frame = True

            if ui_closed_this_frame:
                continue

            valid_area = (mx > 180 and not (200 < mx < 400 and 0 < my < HEIGHT))
            tower_class = TOWER_TYPES.get(state_data.get('selected_tower_type', 'Square'))
            if not tower_class:
                continue
            new_tower = tower_class(mx, my)
            new_tower.state_data = state_data
            if valid_area and state_data['money'] >= new_tower.cost and len(state_data['towers']) < 40:
                if not state_data.get('place_mode', False):
                    state_data['place_mode'] = True
                    state_data['pending_pos'] = (mx, my)
                else:
                    state_data['towers'].append(new_tower)
                    state_data['money'] -= new_tower.cost
                    state_data['place_mode'] = False
                    state_data['pending_pos'] = None
                continue

            if state_data.get('place_mode', False) and not valid_area:
                state_data['place_mode'] = False
                state_data['pending_pos'] = None
                continue

# ======================================
# MULTI-WAVE SPAWNING SYSTEM
# ======================================
    now = pygame.time.get_ticks()

    for spawner in state_data["active_waves"]:
        current_wave_done = state_data["active_waves"][-1]["finished"]
        no_enemy = len(state_data["enemies"]) == 0
        not_last_wave = state_data["wave"] < (len(waves) - 1)

        if current_wave_done and no_enemy and not_last_wave:
            next_wave = state_data["wave"] + 1
            start_wave(state_data, next_wave)
            state_data["wave"] = next_wave
        
        if spawner["finished"]:
            continue

        subs = spawner["subwaves"]
        idx = spawner["index"]

        if idx >= len(subs):
            spawner["finished"] = True
            continue

        sw = subs[idx]

        if now >= spawner["next_spawn"] and sw["remaining"] > 0:
            enemy = spawn_enemy_by_type(sw["type"], state_data)
            if enemy:
                state_data["enemies"].append(enemy)

                if isinstance(enemy, OrbitalCircle):
                    enemy.spawn_orbs(state_data["enemies"])

            sw["remaining"] -= 1
            spawner["next_spawn"] = now + sw["interval"]

        if sw["remaining"] <= 0:
            spawner["index"] += 1

# ============================
    # WIN CHECK — wave final dan semua musuh sudah mati
# ============================
    final_wave = len(waves) - 1

    all_done = all(w["finished"] for w in state_data["active_waves"])
    no_enemy = len(state_data["enemies"]) == 0
    last_wave_reached = state_data["wave"] == (len(waves) - 1)

    if last_wave_reached and all_done and no_enemy:
        if not state_data.get("win_reward_given", False):
            save["shape"] = save.get("shape", 0) + 400
            save["chapter1_completed"] = True
            save_data(save)
            state_data["win_reward_given"] = True

        current_win_message = None
        exit_btn = draw_win_popup(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if exit_btn.collidepoint(mx, my):
                    return "menu"

        pygame.display.update()
        return "game"

    if state_data['base_hp'] <= 0:
        exit_btn = draw_lose_popup(screen, state_data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if exit_btn.collidepoint(mx, my):
                    return "menu"

        pygame.display.update()
        return "game"

    pygame.display.update()
    return "game"

# ------------------------------------------------
# Generic game_screen for other chapters (kept minimal)
# ------------------------------------------------
def game_screen():
    global current_game

    data = game_data[current_game]

    if current_game == 1:
        screen.fill(GREEN_BG)
        draw_circle_animation()
    else:
        screen.fill(BLACK)

    text1 = font_mid.render(f"Playing: {data['name']}", True, WHITE)
    screen.blit(text1, (50, 100))

    if data["game_type"] == "td":
        text2 = font_small.render(f"Money: {data['money']}", True, YELLOW)
        screen.blit(text2, (50, 180))

        text3 = font_small.render(f"Base HP: {data['base_hp']}", True, (0, 255, 0))
        screen.blit(text3, (50, 230))

    back_btn = draw_button("BACK", 50, 580, 250, 80, pygame.mouse.get_pos())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_btn.collidepoint(pygame.mouse.get_pos()):
                current_game = None
                return "menu"

    pygame.display.update()
    return "game"

def winter_event_start_screen():
    screen.fill((8, 14, 25))
    update_snow(screen, WIDTH, HEIGHT, 3)

    draw_text_center("WINTER EVENT", font_big, WHITE, screen, 120)
    draw_text_center("Chapter Event – Acolyte Of Wendigo", font_mid, (200,200,255), screen, 240)

    mouse = pygame.mouse.get_pos()
    btn = pygame.Rect(WIDTH//2 - 200, 380, 400, 120)
    pygame.draw.rect(screen, BLUE, btn)

    txt = font_mid.render("Mulai", True, WHITE)
    screen.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if btn.collidepoint(mouse):
                global event_state
                event_state = "tower_select"

    pygame.display.update()

def winter_event_tower_select(event_data):
    global event_state
    screen.fill(DARK_GRAY_TEXT)

    # ===========================
    # Judul
    # ===========================
    title = font_big.render("Pilih 4 Tower (Winter Event)", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

    # ===========================
    # Tower dimiliki
    # ===========================
    owned_towers = [name for name, data in towers_data.items() if data["owned"]]

    towers_per_page = 8
    current_page = event_data.get('tower_page', 0)
    total_pages = (len(owned_towers) + towers_per_page - 1) // towers_per_page
    start_idx = current_page * towers_per_page
    end_idx = start_idx + towers_per_page
    displayed_towers = owned_towers[start_idx:end_idx]

    # ===========================
    # Grid posisi
    # ===========================
    positions = [
        (100, 200), (400, 200), (700, 200), (1000, 200),
        (100, 350), (400, 350), (700, 350), (1000, 350)
    ]

    w, h = 250, 120
    buttons = {}

    for idx, name in enumerate(displayed_towers):
        x, y = positions[idx]
        rect = pygame.Rect(x, y, w, h)

        if name in event_data['selected_towers']:
            pygame.draw.rect(screen, (100, 100, 255), rect)
            pygame.draw.rect(screen, (255, 255, 0), rect, 5)
        else:
            pygame.draw.rect(screen, (50, 50, 50), rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

        tower_text = font_small.render(name, True, WHITE)
        screen.blit(
            tower_text,
            (x + w//2 - tower_text.get_width()//2,
             y + h//2 - tower_text.get_height()//2)
        )

        buttons[name] = rect

    # ===========================
    # Tombol MULAI
    # ===========================
    start_btn_color = GREEN_BG if len(event_data['selected_towers']) == 4 else GRAY
    start_btn_rect = pygame.Rect(WIDTH//2 - 200, 500, 400, 110)
    pygame.draw.rect(screen, start_btn_color, start_btn_rect)

    start_text = font_big.render("MULAI", True, WHITE)
    screen.blit(
        start_text,
        (start_btn_rect.x + start_btn_rect.w//2 - start_text.get_width()//2,
         start_btn_rect.y + start_btn_rect.h//2 - start_text.get_height()//2)
    )

    # ===========================
    # Tombol Next / Previous
    # ===========================
    prev_rect = pygame.Rect(50, 500, 150, 50)
    next_rect = pygame.Rect(WIDTH - 200, 500, 150, 50)

    pygame.draw.rect(screen, WHITE if current_page > 0 else GRAY, prev_rect)
    pygame.draw.rect(screen, WHITE if current_page < total_pages - 1 else GRAY, next_rect)

    prev_text = font_small.render("Previous", True, DARK_GRAY_TEXT)
    next_text = font_small.render("Next", True, DARK_GRAY_TEXT)

    screen.blit(
        prev_text,
        (prev_rect.x + prev_rect.w//2 - prev_text.get_width()//2,
         prev_rect.y + prev_rect.h//2 - prev_text.get_height()//2)
    )
    screen.blit(
        next_text,
        (next_rect.x + next_rect.w//2 - next_text.get_width()//2,
         next_rect.y + next_rect.h//2 - next_text.get_height()//2)
    )

    # ===========================
    # Daftar tower terpilih
    # ===========================
    for i, t in enumerate(event_data['selected_towers']):
        text = font_small.render(t, True, WHITE)
        screen.blit(text, (50, 550 + i * 30))

    # ===========================
    # Event Handling
    # ===========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            for name, rect in buttons.items():
                if rect.collidepoint(pos):
                    if name in event_data['selected_towers']:
                        event_data['selected_towers'].remove(name)
                    elif len(event_data['selected_towers']) < 4:
                        event_data['selected_towers'].append(name)
                    break

            if start_btn_rect.collidepoint(pos) and len(event_data['selected_towers']) == 4:
                event_state = "playing"
                start_winter_map()

            if prev_rect.collidepoint(pos) and current_page > 0:
                event_data['tower_page'] = current_page - 1
            if next_rect.collidepoint(pos) and current_page < total_pages - 1:
                event_data['tower_page'] = current_page + 1

    pygame.display.update()

def start_winter_map():
    global event_data, path_waypoints_winter, winter_waves

    event_data["money"] = 1500
    event_data["base_hp"] = 8000
    event_data["wave"] = 0
    event_data["enemies"] = []
    event_data["towers"] = []
    event_data["active_waves"] = []
    event_data["selected_tower"] = None
    event_data["place_mode"] = False
    event_data["pending_pos"] = None
    event_data["paused"] = False
    event_data["win_reward_given"] = False

    path_waypoints_winter = [
        (250, -40),
        (250, 120),
        (500, 120),
        (500, 220),
        (150, 220),
        (150, 320),
        (350, 320),
        (350, 450),
        (250, 450),
        (250, 370),
        (430, 370),
        (430, 520),
        (800, 520),
        (800, 300),
        (600, 300),
        (600, 600),
        (1000, 600),
        (1000, 250),
        (1300, 250),
        (WIDTH + 40, 250)
    ]

    winter_waves = [
         [ # Wave 1
             {"type": "wendigo_scout", "count": 10, "interval": 400},
             {"type": "wendigo_scout", "count": 5, "interval": 300}
         ],
         [ # Wave 2
             {"type": "wendigo_scout", "count": 15, "interval": 350},
             {"type": "wendigo_scout", "count": 8, "interval": 280}
         ],
         [ # Wave 3
             {"type": "wendigo_scout", "count": 12, "interval": 320},
             {"type": "snow_minion", "count": 21, "interval": 300}
         ],
         [ # Wave 4
             {"type": "wendigo_scout", "count": 18, "interval": 300},
             {"type": "snow_minion", "count": 30, "interval": 270}
         ],
         [ # Wave 5
             {"type": "snow_minion", "count": 36, "interval": 280},
             {"type": "frost_goblin", "count": 5, "interval": 350}
         ],
         [ # Wave 6
             {"type": "snow_minion", "count": 45, "interval": 250},
             {"type": "frost_goblin", "count": 7, "interval": 320}
         ],
         [ # Wave 7
             {"type": "frost_goblin", "count": 8, "interval": 300},
             {"type": "ice_wolf", "count": 4, "interval": 380}
         ],
         [ # Wave 8
             {"type": "frost_goblin", "count": 10, "interval": 280},
             {"type": "ice_wolf", "count": 6, "interval": 350}
         ],
         [ # Wave 9
             {"type": "snow_minion", "count": 54, "interval": 230},
             {"type": "frost_goblin", "count": 12, "interval": 270},
             {"type": "ice_wolf", "count": 7, "interval": 330}
         ],
         [ # Wave 10
             {"type": "permafrost", "count": 6, "interval": 500},
             {"type": "ice_wolf", "count": 24, "interval": 320}
         ],
         [ # Wave 11
             {"type": "permafrost", "count": 9, "interval": 480},
             {"type": "frost_goblin", "count": 15, "interval": 250},
             {"type": "ice_wolf", "count": 10, "interval": 300}
         ],
         [ # Wave 12
             {"type": "frost_goblin", "count": 18, "interval": 240},
             {"type": "ice_wolf", "count": 12, "interval": 280},
             {"type": "permafrost", "count": 12, "interval": 450},
             {"type": "snow_minion", "count": 60, "interval": 220},
             {"type": "haunting_wendigo", "count": 1, "interval": 440}
         ],
         [ # Wave 13
              {"type": "snow_minion", "count": 65, "interval": 210},
              {"type": "frost_goblin", "count": 20, "interval": 230},
              {"type": "ice_wolf", "count": 15, "interval": 270},
              {"type": "frozen_totem_bearer", "count": 3, "interval": 420}
          ],
          [ # Wave 14
              {"type": "frost_goblin", "count": 22, "interval": 220},
              {"type": "ice_wolf", "count": 18, "interval": 260},
              {"type": "permafrost", "count": 15, "interval": 430},
              {"type": "frozen_totem_bearer", "count": 4, "interval": 400}
          ],
          [ # Wave 15
              {"type": "snow_minion", "count": 70, "interval": 200},
              {"type": "ice_wolf", "count": 20, "interval": 250},
              {"type": "frozen_totem_bearer", "count": 5, "interval": 390},
              {"type": "wendigo", "count": 2, "interval": 430}
          ],
          [ # Wave 16
              {"type": "frost_goblin", "count": 25, "interval": 210},
              {"type": "permafrost", "count": 18, "interval": 410},
              {"type": "frozen_totem_bearer", "count": 6, "interval": 380},
              {"type": "spirit_channeler", "count": 2, "interval": 460}
          ],
          [ # Wave 17
              {"type": "snow_minion", "count": 75, "interval": 190},
              {"type": "ice_wolf", "count": 22, "interval": 240},
              {"type": "spirit_channeler", "count": 3, "interval": 440},
              {"type": "frozen_totem_bearer", "count": 7, "interval": 370},
              {"type": "wendigo", "count": 2, "interval": 420}
          ],
          [ # Wave 18
              {"type": "frost_goblin", "count": 28, "interval": 200},
              {"type": "permafrost", "count": 20, "interval": 400},
              {"type": "spirit_channeler", "count": 4, "interval": 430},
              {"type": "ice_shard_lobber", "count": 3, "interval": 470}
          ],
          [ # Wave 19
              {"type": "snow_minion", "count": 80, "interval": 180},
              {"type": "ice_wolf", "count": 25, "interval": 230},
              {"type": "frozen_totem_bearer", "count": 8, "interval": 360},
              {"type": "spirit_channeler", "count": 5, "interval": 420},
              {"type": "ice_shard_lobber", "count": 4, "interval": 450}
          ],
          [ # Wave 20
              {"type": "frost_goblin", "count": 30, "interval": 190},
              {"type": "permafrost", "count": 22, "interval": 390},
              {"type": "wendigo", "count": 3, "interval": 410},
              {"type": "frozen_totem_bearer", "count": 9, "interval": 350},
              {"type": "spirit_channeler", "count": 6, "interval": 410},
              {"type": "ice_shard_lobber", "count": 5, "interval": 440},
              {"type": "crying_wendigo", "count": 1, "interval": 440}
          ],
          [ # Wave 21
              {"type": "pi_jumper", "count": 12, "interval": 220},
              {"type": "shield", "count": 5, "interval": 400},
              {"type": "pulse_walker", "count": 8, "interval": 350},
              {"type": "giant", "count": 4, "interval": 480},
              {"type": "spirit_channeler", "count": 6, "interval": 400},
              {"type": "ice_shard_lobber", "count": 6, "interval": 430}
          ],
          [ # Wave 22
              {"type": "pi_jumper", "count": 18, "interval": 200},
              {"type": "corrupted_pi_jumper", "count": 6, "interval": 280},
              {"type": "shield", "count": 7, "interval": 380},
              {"type": "pulse_walker", "count": 10, "interval": 330},
              {"type": "giant", "count": 3, "interval": 460},
              {"type": "permafrost", "count": 25, "interval": 380},
              {"type": "frozen_totem_bearer", "count": 10, "interval": 340},
              {"type": "wendigo", "count": 4, "interval": 400},
               {"type": "corrupted_pi_master", "count": 1, "interval": 400},
               {"type": "wendigo", "count": 4, "interval": 400}
          ],
          [ # Wave 23
              {"type": "unstable_snow_golem", "count": 2, "interval": 550},
              {"type": "pi_jumper", "count": 22, "interval": 190},
              {"type": "corrupted_pi_jumper", "count": 8, "interval": 260},
              {"type": "shield", "count": 9, "interval": 360},
              {"type": "pulse_walker", "count": 12, "interval": 310},
              {"type": "giant", "count": 5, "interval": 440},
              {"type": "spirit_channeler", "count": 6, "interval": 390},
              {"type": "ice_shard_lobber", "count": 8, "interval": 420}
          ],
          [ # Wave 24
              {"type": "unstable_snow_golem", "count": 3, "interval": 530},
              {"type": "pi_jumper", "count": 25, "interval": 180},
              {"type": "corrupted_pi_jumper", "count": 10, "interval": 240},
              {"type": "shield", "count": 11, "interval": 340},
              {"type": "pulse_walker", "count": 15, "interval": 300},
              {"type": "giant", "count": 6, "interval": 420},
              {"type": "permafrost", "count": 30, "interval": 370},
              {"type": "wendigo", "count": 3, "interval": 430},
              {"type": "frozen_totem_bearer", "count": 12, "interval": 330},
              {"type": "haunting_wendigo", "count": 1, "interval": 660},
              {"type": "crying_wendigo", "count": 1, "interval": 1320}
          ],
          [ # Wave 25
              {"type": "wendralith", "count": 1, "interval": 600},
              {"type": "unstable_snow_golem", "count": 4, "interval": 500},
              {"type": "pi_jumper", "count": 30, "interval": 170},
              {"type": "corrupted_pi_jumper", "count": 12, "interval": 220},
              {"type": "shield", "count": 12, "interval": 320},
              {"type": "pulse_walker", "count": 18, "interval": 280},
              {"type": "giant", "count": 7, "interval": 400},
              {"type": "spirit_channeler", "count": 6, "interval": 380},
              {"type": "ice_shard_lobber", "count": 10, "interval": 410},
              {"type": "wendigo", "count": 2, "interval": 430}
          ],
          [ # Wave 26
             {"type": "corrupted_intruder", "count": 20, "interval": 550},
             {"type": "wendralith", "count": 1, "interval": 620},
             {"type": "unstable_snow_golem", "count": 5, "interval": 480},
             {"type": "corrupted_pi_jumper", "count": 15, "interval": 200},
             {"type": "shield", "count": 15, "interval": 300},
             {"type": "pulse_walker", "count": 22, "interval": 260},
             {"type": "giant", "count": 8, "interval": 380},
             {"type": "spirit_channeler", "count": 6, "interval": 360},
             {"type": "ice_shard_lobber", "count": 12, "interval": 400},
             {"type": "wendigo", "count": 6, "interval": 600}
         ],
         [ # Wave 27
             {"type": "corrupted_intruder", "count": 30, "interval": 520},
             {"type": "wendralith", "count": 2, "interval": 1200},
             {"type": "unstable_snow_golem", "count": 7, "interval": 900},
             {"type": "corrupted_pi_jumper", "count": 20, "interval": 180},
             {"type": "shield", "count": 18, "interval": 280},
             {"type": "pulse_walker", "count": 25, "interval": 240},
             {"type": "giant", "count": 10, "interval": 360},
             {"type": "spirit_channeler", "count": 6, "interval": 340},
             {"type": "ice_shard_lobber", "count": 12, "interval": 380},
             {"type": "wendigo", "count": 12, "interval": 2400},
             {"type": "grand_shaman", "count": 1, "interval": 700}
         ]
     ]

def create_event_enemy(t):
    if t == "wendigo_scout":
        enemy = WendigoScout()
    elif t == "snow_minion":
        enemy = SnowMinion()
    elif t == "frost_goblin":
        enemy = FrostGoblin()
    elif t == "ice_wolf":
        enemy = IceWolf()
    elif t == "permafrost":
        enemy = Permafrost()
    elif t == "haunting_wendigo":
        enemy = HauntingWendigo()
    elif t == "frozen_totem_bearer":
        enemy = FrozenTotemBearer()
    elif t == "wendigo":
        enemy = Wendigo()
    elif t == "spirit_channeler":
        enemy = SpiritChanneler()
    elif t == "ice_shard_lobber":
        enemy = IceShardLobber()
    elif t == "crying_wendigo":
        enemy = CryingWendigo()
    elif t == "pi_jumper":
        enemy = PiJumper()
    elif t == "shield":
        enemy = ShieldCircle()
    elif t == "pulse_walker":
        enemy = PulseWalker()
    elif t == "giant":
        enemy = GiantCircle()
    elif t == "corrupted_pi_jumper":
        enemy = CorruptedPiJumper()
    elif t == "corrupted_pi_master":
        enemy = CorruptedPiMaster()
    elif t == "unstable_snow_golem":
        enemy = UnstableSnowGolem()
    elif t == "wendralith":
        enemy = Wendralith()
    elif t == "corrupted_intruder":
        enemy = CorruptedIntruder()
    elif t == "grand_shaman":
        enemy = GrandShaman()
    else:
        return None
    return enemy

def start_winter_wave(event_data, wave_index):
    spawner = {
        "wave_id": wave_index,
        "subwaves": [],
        "index": 0,
        "next_spawn": 0,
        "finished": False
    }

    for sw in winter_waves[wave_index]:
        spawner["subwaves"].append({
            "type": sw["type"],
            "interval": sw["interval"],
            "remaining": sw["count"]
        })

    event_data["active_waves"].append(spawner)

def update_winter_spawn(event_data):
    global winter_waves

    if event_data["wave"] >= len(winter_waves):
        return

    wave = winter_waves[event_data["wave"]]

    if event_data["spawn_index"] < len(wave):
        group = wave[event_data["spawn_index"]]

        if pygame.time.get_ticks() - event_data["spawn_timer"] >= group["interval"]:
            enemy = create_event_enemy(group["type"])
            if enemy:
                event_data["enemies"].append(enemy)

            group["count"] -= 1
            event_data["spawn_timer"] = pygame.time.get_ticks()

            if group["count"] <= 0:
                event_data["spawn_index"] += 1

    if event_data["spawn_index"] >= len(wave) and len(event_data["enemies"]) == 0:
        event_data["wave"] += 1
        event_data["spawn_index"] = 0
        event_data["spawn_timer"] = pygame.time.get_ticks()

rocks = [
    (120, 200, 40, 28),
    (300, 450, 50, 30),
    (700, 300, 45, 25),
    (900, 550, 35, 20),
]
snow_patches = [
    (200, 150, 120),
    (600, 400, 180),
]

def draw_static_winter_background(screen, WIDTH, HEIGHT, rocks, snow_patches):
    screen.fill((25, 35, 60))
    for (x, y, r) in snow_patches:
        pygame.draw.circle(screen, (40, 55, 90), (x, y), r)

    for (x, y, w, h) in rocks:
        shadow = (40, 45, 60)
        main = (60, 70, 90)
        highlight = (110, 130, 170)

        pygame.draw.ellipse(screen, shadow, (x+3, y+3, w, h))
        pygame.draw.ellipse(screen, main, (x, y, w, h))
        pygame.draw.ellipse(screen, highlight, (x+4, y+4, w//3, h//3))

    grid_color = (35, 45, 70)
    grid_size = 80

    for gx in range(0, WIDTH, grid_size):
        pygame.draw.line(screen, grid_color, (gx, 0), (gx, HEIGHT), 1)

    for gy in range(0, HEIGHT, grid_size):
        pygame.draw.line(screen, grid_color, (0, gy), (WIDTH, gy), 1)

    horn_color = (110, 180, 255)

    center_x = WIDTH - 120
    base_y = 100

    pygame.draw.lines(
        screen, horn_color, False,
        [
            (center_x - 40, base_y + 30),
            (center_x - 60, base_y),
            (center_x - 55, base_y - 25),
            (center_x - 35, base_y - 45),
        ],
        4
    )

    pygame.draw.lines(
        screen, horn_color, False,
        [
            (center_x + 40, base_y + 30),
            (center_x + 60, base_y),
            (center_x + 55, base_y - 25),
            (center_x + 35, base_y - 45),
        ],
        4
    )

    pygame.draw.ellipse(
        screen, horn_color,
        (center_x - 18, base_y - 10, 36, 28), 2
    )

def draw_big_wendigo_logo(screen, WIDTH, HEIGHT):
    color = (120, 190, 255)
    thickness = 8
    cx = WIDTH // 2
    top_y = 320
    left_horn = [
        (cx - 220, top_y + 120),
        (cx - 320, top_y + 40),
        (cx - 360, top_y - 40),
        (cx - 330, top_y - 120),
        (cx - 260, top_y - 180),
    ]

    pygame.draw.lines(screen, color, False, left_horn, thickness)

    right_horn = [
        (cx + 220, top_y + 120),
        (cx + 320, top_y + 40),
        (cx + 360, top_y - 40),
        (cx + 330, top_y - 120),
        (cx + 260, top_y - 180),
    ]

    pygame.draw.lines(screen, color, False, right_horn, thickness)

    pygame.draw.ellipse(
        screen,
        color,
        (cx - 90, top_y - 40, 180, 140),
        thickness // 2
    )

def draw_lose_popup_winter(screen, state_data):
    global current_lose_message

    if current_lose_message is None:
        pesan_list = [
            "Acolyte of Wendigo menertawakanmu",
            "Kau tidak pantas mengganggu Wendralith",
            "Kekuatanmu terlalu lemah",
            "Hanya kegelapan yang menang",
            "Perjuanganmu berakhir di salju",
            "Wendigo selalu menang"
        ]
        current_lose_message = random.choice(pesan_list)

    wave_reached = state_data['wave'] + 1
    base_reward = 50
    wave_bonus = wave_reached * 5
    total_reward = base_reward + wave_bonus

    if not state_data.get("lose_reward_given", False):
        save["shape"] = save.get("shape", 0) + total_reward
        save_data(save)
        state_data["lose_reward_given"] = True

    overlay_w, overlay_h = 1612, 720
    overlay_x = WIDTH//2 - overlay_w//2
    overlay_y = HEIGHT//2 - overlay_h//2

    overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 40, 200))
    screen.blit(overlay, (overlay_x, overlay_y))

    box_w, box_h = 550, 480
    box_x = WIDTH//2 - box_w//2
    box_y = HEIGHT//2 - box_h//2

    pygame.draw.rect(screen, (180, 0, 255), (box_x, box_y, box_w, box_h), 10)
    pygame.draw.rect(screen, (10, 0, 30), (box_x+10, box_y+10, box_w-20, box_h-20))

    cx, cy = box_x + box_w//2, box_y + 130
    r = 60
    pygame.draw.circle(screen, (120, 0, 255), (cx, cy), r)

    pygame.draw.circle(screen, (0, 0, 0), (cx - 20, cy - 15), 8)
    pygame.draw.circle(screen, (0, 0, 0), (cx + 20, cy - 15), 8)

    pygame.draw.arc(
        screen,
        (0, 0, 0),
        (cx - 30, cy - 10, 60, 50),
        0,
        3.14,
        4
    )

    lose_text = font_big.render("LOSE", True, (255, 100, 255))
    screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, box_y + 30))

    text_obj = font_small.render(current_lose_message, True, (255, 150, 255))
    screen.blit(text_obj, (WIDTH//2 - text_obj.get_width()//2, cy + 80))

    reward_title = font_mid.render("Reward:", True, (180, 255, 255))
    screen.blit(reward_title, (WIDTH//2 - reward_title.get_width()//2, cy + 130))

    wave_text = font_small.render(f"Wave Reached: {wave_reached}", True, (200, 255, 255))
    screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, cy + 175))

    shape_obj = font_small.render(f"+{total_reward} Shape", True, (100, 255, 255))
    screen.blit(shape_obj, (WIDTH//2 - shape_obj.get_width()//2, cy + 210))

    exit_w, exit_h = 240, 90
    exit_x = WIDTH//2 - exit_w//2
    exit_y = box_y + box_h - exit_h - 30

    pygame.draw.rect(screen, (180, 0, 255), (exit_x, exit_y, exit_w, exit_h), 8)
    exit_text = font_mid.render("EXIT", True, (255, 200, 255))
    screen.blit(
        exit_text,
        (
            exit_x + exit_w//2 - exit_text.get_width()//2,
            exit_y + exit_h//2 - exit_text.get_height()//2
        )
    )

    return pygame.Rect(exit_x, exit_y, exit_w, exit_h)

def draw_win_popup_winter(screen, state_data):
    global current_win_message

    if current_win_message is None:
        pesan_list = [
            "Kalian berhasil mengusir Acolyte of Wendigo!",
            "Winter Realm aman kembali!",
            "Wendralith kalah di tangan kalian!",
            "Salju berhenti menjerat wilayahmu!",
            "Kemenangan abadi atas kegelapan!"
        ]
        current_win_message = random.choice(pesan_list)

    if not state_data.get("win_reward_given", False):
        save["shape"] = save.get("shape", 0) + 640
        save["winter_event_completed"] = True

        if not towers_data["Frost Blaster (1800)"]["owned"]:
            towers_data["Frost Blaster (1800)"]["owned"] = True
            save_inventory()

            state_data["got_frost_blaster"] = True

        save_data(save)
        state_data["win_reward_given"] = True

    overlay_w, overlay_h = 1612, 720
    overlay_x = WIDTH//2 - overlay_w//2
    overlay_y = HEIGHT//2 - overlay_h//2
    overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 60, 200))
    screen.blit(overlay, (overlay_x, overlay_y))

    box_w, box_h = 550, 420
    box_x = WIDTH//2 - box_w//2
    box_y = HEIGHT//2 - box_h//2
    pygame.draw.rect(screen, (0, 0, 255), (box_x, box_y, box_w, box_h), 10)
    pygame.draw.rect(screen, (20, 0, 50), (box_x+10, box_y+10, box_w-20, box_h-20))

    win_text = font_big.render("WIN!", True, (180, 150, 255))
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, box_y + 30))

    cx, cy = box_x + box_w//2, box_y + 150
    size = 120
    pygame.draw.rect(screen, (160, 220, 255), (cx - size//2, cy - size//2, size, size))

    pygame.draw.circle(screen, (0, 0, 0), (cx - 30, cy - 30), 8)
    pygame.draw.circle(screen, (0, 0, 0), (cx + 30, cy - 30), 8)

    pygame.draw.arc(
        screen,
        (0, 0, 0),
        (cx - 40, cy - 10, 80, 50),
        3.14, 0, 4
    )

    text_obj = font_small.render(current_win_message, True, (200, 200, 255))
    screen.blit(text_obj, (WIDTH//2 - text_obj.get_width()//2, cy + 80))

    shape_obj = font_small.render(
        f"+{shape_reward} Shape diperoleh!",
        True,
        (100, 255, 255)
    )
    screen.blit(shape_obj, (WIDTH//2 - shape_obj.get_width()//2, cy + 130))

    if state_data.get("got_frost_blaster", False):
        tower_text = font_small.render(
            "Tower Baru Dibuka: Frost Blaster!",
            True,
            (255, 200, 120)
        )
        screen.blit(
            tower_text,
            (WIDTH//2 - tower_text.get_width()//2, cy + 275)
        )

    exit_w, exit_h = 240, 90
    exit_x = WIDTH//2 - exit_w//2
    exit_y = box_y + box_h - exit_h - 30
    pygame.draw.rect(screen, (0, 0, 255), (exit_x, exit_y, exit_w, exit_h), 8)
    exit_text = font_mid.render("EXIT", True, (200, 200, 255))
    screen.blit(
        exit_text,
        (
            exit_x + exit_w//2 - exit_text.get_width()//2,
            exit_y + exit_h//2 - exit_text.get_height()//2
        )
    )

    return pygame.Rect(exit_x, exit_y, exit_w, exit_h)

def winter_event_gameplay(event_data):
    global event_state, path_waypoints_winter, winter_waves, current_win_message, current_lose_message
    
    mouse_pos = pygame.mouse.get_pos()

    if event_data["wave"] == 0 and len(event_data["active_waves"]) == 0:
        start_winter_wave(event_data, 0)
    
    # ============================
    # PAUSE POPUP (SURRENDER)
    # ============================
    if event_data.get('paused') == "surrender":
        overlay = pygame.Surface((WIDTH + 220, HEIGHT + 40), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        popup = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 450, 300)
        pygame.draw.rect(screen, (50, 50, 50), popup)
        pygame.draw.rect(screen, (255, 255, 255), popup, 4)

        text = font_small.render("Apakah kamu yakin menyerah?", True, WHITE)
        screen.blit(text, (popup.x + 40, popup.y + 40))

        yes_btn = draw_button("Ya", popup.x + 60, popup.y + 150, 120, 60, mouse_pos)
        no_btn = draw_button("Tidak", popup.x + 220, popup.y + 150, 120, 60, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if yes_btn.collidepoint((mx, my)):
                    return "menu"
                if no_btn.collidepoint((mx, my)):
                    event_data['paused'] = False

        pygame.display.update()
        return "game"
    
    # ------------------------------
    # BACKGROUND & LOGO
    # ------------------------------
    draw_static_winter_background(screen, WIDTH, HEIGHT, rocks, snow_patches)
    draw_big_wendigo_logo(screen, WIDTH, HEIGHT)

    # ------------------------------
    # PATH
    # ------------------------------
    for i in range(len(path_waypoints_winter) - 1):
        pygame.draw.line(screen, (200, 200, 240),
                         path_waypoints_winter[i],
                         path_waypoints_winter[i+1], 25)

    # ------------------------------
    # UI TEXT
    # ------------------------------
    title = font_mid.render(f"Wave: {event_data['wave']+1}", True, WHITE)
    screen.blit(title, (40, 20))

    money_text = font_small.render(f"Money: {event_data['money']}", True, YELLOW)
    hp_text = font_small.render(f"Base HP: {event_data['base_hp']}", True, (0, 255, 0))
    screen.blit(money_text, (40, 80))
    screen.blit(hp_text, (40, 120))
    
    total_tower = len(event_data["towers"])
    tower_color = (255, 0, 0) if total_tower >= 40 else WHITE
    tower_text = font_small.render(f"Total Square: {total_tower}/40", True, tower_color)
    screen.blit(tower_text, (40, 160))

    # ------------------------------
    # BUTTONS
    # ------------------------------
    skip_btn = draw_button("Lewati Wave", 40, 230, 250, 70, mouse_pos)
    back_btn = draw_button("Menyerah", 50, 635, 250, 80, mouse_pos)

    tower_btns = []
    for i, t_name in enumerate(event_data['selected_towers']):
        btn = draw_button(t_name, WIDTH - 250, 50 + i * 150, 250, 120, mouse_pos)
        tower_btns.append((t_name, btn))

    # ------------------------------
    # UPDATE & DRAW ENEMIES
    # ------------------------------
    max_wp = len(path_waypoints_winter)
    
    for e in list(event_data['enemies']):
        if isinstance(e, CorruptedPiMaster):
            e.update(event_data['enemies'], event_data['towers'])

        elif isinstance(e, HauntingWendigo):
            e.update(event_data['enemies'], event_data['towers'])

        elif isinstance(e, SpiritChanneler):
            e.update(event_data['enemies'])

        elif isinstance(e, IceShardLobber):
            e.update(event_data["towers"], event_data)

        elif isinstance(e, CryingWendigo):
            e.update(event_data['enemies'], event_data['towers'])
            
        elif isinstance(e, GrandShaman):
            e.update(event_data['enemies'], event_data['towers'])

        else:
            e.update()
    
        e.draw(screen)

        if e.waypoint_index >= max_wp:
            event_data["base_hp"] -= int(e.hp)
            try:
                event_data["enemies"].remove(e)
            except ValueError:    pass
            continue

        if e.hp <= 0:
    # ============================
    # BOSS / ENEMY WITH DEATH ANIM
    # ============================
            if hasattr(e, "death_anim_active"):
                if not getattr(e, "_reward_given", False):
                    event_data["money"] += e.reward
                    e._reward_given = True

                continue

    # ============================
    # FROZEN TOTEM DEATH EFFECT
    # ============================
            if isinstance(e, FrozenTotemBearer):
                event_data.setdefault("frozen_areas", []).append({
                    "x": e.x,
                    "y": e.y,
                    "radius": e.frozen_radius
                })

            if isinstance(e, Permafrost) or isinstance(e, UnstableSnowGolem):
                children = e.split()
                for c in children:
                    c.x, c.y = e.x, e.y
                    event_data['enemies'].append(c)

            event_data['money'] += e.reward

            try:
                event_data['enemies'].remove(e)
            except ValueError:
                pass

# ============================
# REMOVE ENEMY AFTER DEATH ANIM
# ============================
        for e in list(event_data["enemies"]):
            if getattr(e, "to_delete", False):
                try:
                    event_data["enemies"].remove(e)
                except ValueError:
                    pass

# ============================
# FROZEN GROUND REACTIVE
# ============================
        for area in list(event_data.get("frozen_areas", [])):
            pygame.draw.circle(
                screen,
                (150, 200, 255),
                (int(area["x"]), int(area["y"])),
                int(area["radius"]),
                2
            )

            for enemy in event_data["enemies"]:
                dist = math.hypot(enemy.x - area["x"], enemy.y - area["y"])
                if dist <= area["radius"]:
                    enemy.hp *= 2
                    enemy.radius *= 1.5

                    try:
                        event_data["frozen_areas"].remove(area)
                    except ValueError:
                        pass

                    break

# ============================
# DRAW & UPDATE EFFECTS
# ============================
    dt = clock.get_time() / 1000.0
    for ef in list(event_data.get("effects", [])):
        if ef["type"] == "ice_aoe":
            pygame.draw.circle(
                screen,
                (180, 220, 255),
                (int(ef["x"]), int(ef["y"])),
                int(ef["radius"]),
                2
            )

            ef["timer"] -= dt
            if ef["timer"] <= 0:
                event_data["effects"].remove(ef)

    # ------------------------------
    # UPDATE & DRAW TOWERS
    # ------------------------------
    dt = clock.get_time() / 1000.0
    
    for t in list(event_data['towers']):
        if isinstance(t, MafiaTower):
            t.update(dt, event_data['enemies'], state_data=event_data)
        else:
            t.update(dt, event_data['enemies'])
        
        t.draw(screen, selected=(event_data.get('selected_tower') == t))
        
        if t.hp <= 0:
            event_data['towers'].remove(t)

    # ------------------------------
    # PLACE MODE PREVIEW
    # ------------------------------
    if event_data.get("place_mode") and event_data.get("pending_pos"):
        px, py = event_data["pending_pos"]
        pygame.draw.circle(screen, (0, 255, 0), (px, py), 25, 2)

    # ------------------------------
    # UPGRADE / SELL UI
    # ------------------------------
    st = event_data.get('selected_tower')
    if st:
        upgrade_rect, sell_rect = draw_upgrade_ui(screen, st)
        st.upgrade_rect = upgrade_rect
        st.sell_rect = sell_rect

    # ------------------------------
    # MOUSE EVENTS
    # ------------------------------
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            mouse_pos = (mx, my)
            ui_closed_this_frame = False

            for t_name, btn in tower_btns:
                if btn.collidepoint(mouse_pos):
                    event_data['selected_tower_type'] = t_name
                    event_data['selected_tower'] = None
                    event_data['place_mode'] = False
                    event_data['pending_pos'] = None
                    break

            if back_btn.collidepoint(mouse_pos):
                event_data["paused"] = "surrender"
                return "game"

            if skip_btn.collidepoint(mouse_pos):
                next_wave = event_data["wave"] + 1
                if next_wave < len(winter_waves):
                    start_winter_wave(event_data, next_wave)
                    event_data["wave"] = next_wave
                continue

            clicked_on_tower = False
            for t in event_data['towers']:
                if t.x - t.size//2 <= mx <= t.x + t.size//2 and \
                   t.y - t.size//2 <= my <= t.y + t.size//2:
                    event_data['selected_tower'] = t
                    clicked_on_tower = True
                    break
            if clicked_on_tower:
                continue

            st = event_data.get('selected_tower')
            if st:
                if hasattr(st, 'upgrade_rect') and st.upgrade_rect.collidepoint(mx, my):
                    lvl = st.level
                    cost = st.upgrade_cost.get(lvl)
                    if cost and event_data['money'] >= cost:
                        event_data['money'] -= cost
                        st.upgrade()
                    continue

                if hasattr(st, 'sell_rect') and st.sell_rect.collidepoint(mx, my):
                    refund = int(st.total_invest * 0.65)
                    event_data['money'] += refund
                    if st in event_data['towers']:
                        event_data['towers'].remove(st)
                    event_data['selected_tower'] = None
                    continue

            if event_data.get('selected_tower') is not None:
                event_data['selected_tower'] = None
                ui_closed_this_frame = True

            if ui_closed_this_frame:
                continue

            valid_area = (mx > 180 and not (200 < mx < 400 and 0 < my < HEIGHT))
            tower_class = TOWER_TYPES.get(event_data.get('selected_tower_type'))
            
            if tower_class:
                new_tower = tower_class(mx, my)
                if valid_area and event_data['money'] >= new_tower.cost and len(event_data['towers']) < 40:
                    if not event_data.get('place_mode', False):
                        event_data['place_mode'] = True
                        event_data['pending_pos'] = (mx, my)
                    else:
                        event_data['towers'].append(new_tower)
                        event_data['money'] -= new_tower.cost
                        event_data['place_mode'] = False
                        event_data['pending_pos'] = None
                    continue

            if event_data.get('place_mode', False) and not valid_area:
                event_data['place_mode'] = False
                event_data['pending_pos'] = None
                continue

    # ======================================
    # MULTI-WAVE SPAWNING SYSTEM
    # ======================================
    now = pygame.time.get_ticks()

    for spawner in event_data["active_waves"]:
        current_wave_done = event_data["active_waves"][-1]["finished"]
        no_enemy = len(event_data["enemies"]) == 0
        not_last_wave = event_data["wave"] < (len(winter_waves) - 1)

        if current_wave_done and no_enemy and not_last_wave:
            next_wave = event_data["wave"] + 1
            start_winter_wave(event_data, next_wave)
            event_data["wave"] = next_wave
        
        if spawner["finished"]:
            continue

        subs = spawner["subwaves"]
        idx = spawner["index"]

        if idx >= len(subs):
            spawner["finished"] = True
            continue

        sw = subs[idx]

        if now >= spawner["next_spawn"] and sw["remaining"] > 0:
            enemy = create_event_enemy(sw["type"])

            if enemy:
                enemy.x, enemy.y = path_waypoints_winter[0]
                enemy.waypoint_index = 0
                enemy.path = path_waypoints_winter
                event_data["enemies"].append(enemy)

            sw["remaining"] -= 1
            spawner["next_spawn"] = now + sw["interval"]

        if sw["remaining"] <= 0:
            spawner["index"] += 1

    # ============================
    # WIN/LOSE LOOP WINTER EVENT
    # ============================
    all_done = all(w["finished"] for w in event_data["active_waves"])
    no_enemy = len(event_data["enemies"]) == 0
    last_wave_reached = event_data["wave"] == (len(winter_waves) - 1)

    if last_wave_reached and all_done and no_enemy:
        exit_btn = draw_win_popup_winter(screen, event_data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if exit_btn.collidepoint(mx, my):
                    current_win_message = None
                    return "menu"

        pygame.display.update()
        return "game"

    if event_data['base_hp'] <= 0:
        exit_btn = draw_lose_popup_winter(screen, event_data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if exit_btn.collidepoint(mx, my):
                    current_lose_message = None
                    return "menu"

        pygame.display.update()
        return "game"

    update_snow(screen, WIDTH, HEIGHT, 1)

    pygame.display.update()
    return "game"

def reset_event_data():
    return {
        'enemies': [],
        'towers': [],
        'selected_tower': None,
        'money': 1000,
        'base_hp': 8000,
        'wave': 0,
        'active_waves': [],
        'place_mode': False,
        'pending_pos': None,
        'selected_towers': [],
        'paused': False,
    }

# ------------------------------------------------
# MAIN LOOP - run
# ------------------------------------------------
state_data = {
    'enemies': [],
    'towers': [],
    'selected_tower': None,
    'last_spawn': 0,
    'spawn_interval': 1000,
    'money': game_data[1]['money'],
    'base_hp': game_data[1]['base_hp'],
    'wave': 0,
    'active_waves': [],
    'spawn_finished': False,
    'place_mode': False,
    'pending_pos': None,
    'selected_towers': [],
    'paused': False,
}

event_data = {
    'enemies': [],
    'towers': [],
    'selected_tower': None,
    'last_spawn': 0,
    'spawn_interval': 1000,
    'spawn_timer': 0,
    'spawn_index': 0,
    'money': 1000,
    'base_hp': 10000,
    'wave': 0,
    'active_waves': [],
    'spawn_finished': False,
    'place_mode': False,
    'pending_pos': None,
    'selected_towers': [],
    'paused': False,
}

while True:
    if game_state == "intro":
        intro_screen()

    elif game_state == "info":
        info_screen()

    elif game_state == "menu":
        chapter_menu()

    elif game_state == "home":
        home_screen()

    elif game_state == "inventory":
        inventory_screen()

    elif game_state == "history":
        history_screen()

    elif game_state == "game":
        if current_game == 1:
            if chapter1_state == "tower_select":
                tower_selection_screen(state_data)

            elif chapter1_state == "start":
                chapter1_start_screen()

            elif chapter1_state == "playing":
                res = chapter1_screen(state_data)
                if res == "menu":
                    chapter1_state = "tower_select"
                    current_game = None
                    game_state = "menu"
                    current_lose_message = None

                    state_data = {
                        'enemies': [],
                        'towers': [],
                        'selected_tower': None,
                        'last_spawn': 0,
                        'spawn_interval': 1000,
                        'money': game_data[1]['money'],
                        'base_hp': game_data[1]['base_hp'],
                        'wave': 0,
                        'active_waves': [],
                        'spawn_finished': False,
                        'place_mode': False,
                        'pending_pos': None,
                        'selected_towers': [],
                        'paused': False,
                    }

        else:
            game_state = game_screen()

    elif game_state == "event":
        if event_state == "cutscene":
            winter_event_cutscene()

        elif event_state == "start_screen":
            winter_event_start_screen()

        elif event_state == "tower_select":
            winter_event_tower_select(event_data)

        elif event_state == "playing":
            res = winter_event_gameplay(event_data)
            if res == "menu":
                event_state = "none"
                game_state = "home"
                event_data = reset_event_data()

    clock.tick(FPS)