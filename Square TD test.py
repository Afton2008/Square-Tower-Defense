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
    "Laser (1,2K)":  {"price": 1500, "owned": False},
    "Frost Blast (1,8K)":  {"price": 0, "owned": False},
    "Poison (650)":  {"price": 2400, "owned": False},
    "Flamethrower (800)":  {"price": 3200, "owned": False},
    "Medic (950)":  {"price": 3800, "owned": False},
    "Tesla (1,1K)":  {"price": 4400, "owned": False},
    "Railgun (1,5K)":  {"price": 6000, "owned": False},
    "Slingdrone (420)":  {"price": 0, "owned": False},  # Rare - dari spin
    "Void Pulse (3K)":  {"price": 0, "owned": False},  # Mythic Tower - hanya dari spin
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

# Rarity Colors untuk Spin System
RARITY_COMMON = (150, 150, 150)      # Abu-abu
RARITY_UNCOMMON = (50, 200, 50)      # Hijau
RARITY_RARE = (50, 120, 255)         # Biru
RARITY_LEGENDARY = (255, 165, 0)     # Orange
RARITY_MYTHIC = (200, 0, 255)        # Ungu

font_big = pygame.font.Font(None, 90)
font_mid = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 36)

# ================================================
# SPIN SYSTEM VARIABLES
# ================================================
SPIN_COST = 25
spin_state = "idle"
spin_animation_progress = 0
spin_result = None
spin_animation_start_time = 0
SPIN_DURATION = 3000
active_boosts = []
temp_money_boosts = []
SPIN_REWARDS = {
    "Common": {
        "weight": 50,  # 50%
        "color": RARITY_COMMON,
        "items": [
            {"name": "100 Money", "type": "money", "amount": 100},
            {"name": "250 Money", "type": "money", "amount": 250},
            {"name": "Nothing", "type": "nothing", "amount": 0},
        ]
    },
    "Uncommon": {
        "weight": 30,  # 30%
        "color": RARITY_UNCOMMON,
        "items": [
            {"name": "500 Money", "type": "money", "amount": 500},
            {"name": "Small Boost", "type": "boost", "amount": 1.5, "duration": 300000},  # 5 menit
            {"name": "Nothing", "type": "nothing", "amount": 0},
        ]
    },
    "Rare": {
        "weight": 14,  # 14%
        "color": RARITY_RARE,
        "items": [
            {"name": "Slingdrone Tower", "type": "tower", "tower_name": "Slingdrone (420)"},
            {"name": "2500 Money", "type": "money", "amount": 2500},
            {"name": "Nothing", "type": "nothing", "amount": 0},
        ]
    },
    "Legendary": {
        "weight": 5,  # 5%
        "color": RARITY_LEGENDARY,
        "items": [
            {"name": "7500 Money", "type": "money", "amount": 7500},
            {"name": "Big Boost", "type": "boost", "amount": 2.0, "duration": 600000},  # 10 menit
        ]
    },
    "Mythic": {
        "weight": 1,  # 1%
        "color": RARITY_MYTHIC,
        "items": [
            {"name": "Void Pulse", "type": "tower", "tower_name": "Void Pulse (3K)"},
        ]
    }
}

current_lose_message = None
current_win_message = None
FONT_TOWER = pygame.font.SysFont("Arial", 18, bold=True)
FONT_UI_SMALL = pygame.font.SysFont("Arial", 16)
FONT_UI_MED = pygame.font.SysFont("Arial", 20)

# ------------------------------------------------
# BOSS HP BAR SYSTEM
# ------------------------------------------------
class BossHPBar:
    def __init__(self):
        self.displayed_bosses = []
        self.MAX_DISPLAYED = 3
        self.bar_height = 40
        self.bar_spacing = 10
        self.start_y = 10
        
    def update(self, all_bosses):
        for boss in all_bosses:
            boss.display_hp_bar = False

        self.displayed_bosses = [boss for boss in self.displayed_bosses if boss.hp > 0]

        for boss in all_bosses:
            if boss.hp > 0 and boss not in self.displayed_bosses:
                self.displayed_bosses.append(boss)

        self.displayed_bosses.sort(key=lambda b: b.hp, reverse=True)

        self.displayed_bosses = self.displayed_bosses[:self.MAX_DISPLAYED]

        for i, boss in enumerate(self.displayed_bosses):
            boss.hp_bar_slot = i
            boss.hp_bar_y = self.start_y + i * (self.bar_height + self.bar_spacing)
            boss.display_hp_bar = True
    
    def reset(self):
        self.displayed_bosses = []

boss_hp_bar = BossHPBar()

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

# ------------------------------------------------
# ANIMASI INTRO — CIRCLE MERAH BERGERAK
# ------------------------------------------------
circle_x = WIDTH - 200
circle_y = 340
circle_speed = 3
circle_dir = -1

# ------------------------------------------------
# ANIMASI INTRO — CYCLO CORE (unlock setelah Chapter 1)
# ------------------------------------------------
core_angle = 0
core_radius = 30
core_orbit_radius = 100

# ------------------------------------------------
# ANIMASI INTRO — GRAND SHAMAN STAFF (unlock setelah Winter Event)
# ------------------------------------------------
staff_float_offset = 0
staff_rotation = 0

# ------------------------------------------------
# ANIMASI GARIS LUAR TOMBOL
# ------------------------------------------------
border_colors = [(255, 0, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255)]
border_color_index = 0
border_color_timer = 0
border_color_change_interval = 300

# ------------------------------------------------
# CLICK COOLDOWN
# ------------------------------------------------
last_click_time = 0
click_cooldown = 800

def can_click():
    global last_click_time
    current_time = pygame.time.get_ticks()
    if current_time - last_click_time >= click_cooldown:
        last_click_time = current_time
        return True
    return False

def format_number(num):
    return f"{int(num):,}".replace(",", ".")

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
# ANIMASI INTRO — CIRCLE MERAH BERGERAK
# ------------------------------------------------
def draw_circle_intro_animation():
    global circle_x, circle_dir
    circle_x += circle_speed * circle_dir
    
    if circle_x > WIDTH - 200:
        circle_dir = -1
    if circle_x < 200:
        circle_dir = 1
    
    pygame.draw.circle(screen, RED, (int(circle_x), int(circle_y)), 40)

# ------------------------------------------------
# ANIMASI INTRO — CYCLO CORE (unlock Chapter 1)
# ------------------------------------------------
def draw_core_animation():
    global core_angle
    core_angle += 0.05
    center_x = WIDTH // 2
    center_y = 200
    cx = center_x + math.cos(core_angle) * core_orbit_radius
    cy = center_y + math.sin(core_angle) * core_orbit_radius

    pygame.draw.circle(screen, (255, 0, 0), (int(cx), int(cy)), core_radius)

    for angle in range(0, 360, 45):
        rad = math.radians(angle + core_angle * 50)
        x_end = cx + math.cos(rad) * core_radius
        y_end = cy + math.sin(rad) * core_radius
        pygame.draw.line(screen, (255, 100, 100), (int(cx), int(cy)), (int(x_end), int(y_end)), 2)

    for glow in range(1, 4):
        pygame.draw.circle(screen, (255, 50, 50), (int(cx), int(cy)), core_radius + glow * 4, 1)

# ------------------------------------------------
# ANIMASI INTRO — GRAND SHAMAN STAFF (unlock Winter Event)
# ------------------------------------------------
def draw_staff_animation():
    global staff_float_offset, staff_rotation

    staff_float_offset += 0.05
    float_y = math.sin(staff_float_offset) * 15
    staff_rotation += 1
    staff_x = WIDTH - 150
    staff_y = HEIGHT - 150 + float_y
    staff_color = (120, 90, 60)
    staff_start = (staff_x, staff_y + 40)
    staff_end = (staff_x + 80, staff_y + 40)
    pygame.draw.line(screen, staff_color, staff_start, staff_end, 4)
    orb_color = (170, 0, 200)
    orb_pos = staff_end
    pulse = abs(math.sin(staff_float_offset * 2))
    orb_radius = int(10 + pulse * 3)
    
    pygame.draw.circle(screen, orb_color, orb_pos, orb_radius)
    pygame.draw.circle(screen, (255, 100, 255), orb_pos, orb_radius - 3)

    for i in range(4):
        angle = math.radians(staff_rotation + i * 90)
        px = orb_pos[0] + math.cos(angle) * 20
        py = orb_pos[1] + math.sin(angle) * 20
        pygame.draw.circle(screen, (200, 150, 255), (int(px), int(py)), 3)

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
    global border_color_index, border_color_timer
    
    rect = pygame.Rect(x, y, w, h)
    is_hovered = rect.collidepoint(mouse_pos)
    color = BLUE if is_hovered else GRAY

    if is_hovered:
        current_time = pygame.time.get_ticks()
        if current_time - border_color_timer > border_color_change_interval:
            border_color_index = (border_color_index + 1) % len(border_colors)
            border_color_timer = current_time

        pygame.draw.rect(screen, color, rect, border_radius=25)

        pygame.draw.rect(screen, border_colors[border_color_index], rect, width=5, border_radius=25)
    else:
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

    if save.get("chapter1_completed", False):
        draw_core_animation()
        draw_circle_intro_animation()

    if save.get("winter_event_completed", False):
        draw_staff_animation()

    title = font_big.render("SQUARE TOWER DEFENSE", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    subtitle = font_mid.render("Version 1.2.0", True, GRAY)  
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
            if not can_click():
                continue
                
            mx, my = event.pos
            if start_btn.collidepoint(mx, my):
                game_state = "home"
            elif info_btn.collidepoint(mx, my):
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
    # PAGE 0
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

    # ======================
    # PAGE 1
    # ======================
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

        y_offset += 40

        v5_title = font_mid.render("Version 1.2.0 - 14 F