import pygame
import random
from button import Button
from Character import Character, Special_1, Special_2, Special_3, Special_4, Special_5, Special_6

# -------------------------------
# Initialize pygame
# -------------------------------
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

# Screen settings
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-Based Battle Game")
background = pygame.transform.scale(pygame.image.load("image/bg7.jpg").convert(), (WIDTH, HEIGHT))

clock = pygame.time.Clock()

# -------------------------------
# Colors
# -------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOODBLUE = (40, 100, 230)
RED = (200, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 200)
GRAY = (180, 180, 200)
DARK_GRAY = (180, 180, 200)
YELLOW = (220, 220, 50)
LIGHT_BLUE = (160, 210, 255)
PURPLE = (150, 80, 180)
ORANGE = (255, 180, 50)

# -------------------------------
# Fonts
# -------------------------------
title_font = pygame.font.SysFont(None, 52)
font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 24)
smaller_font = pygame.font.SysFont(None, 20)
# Battle positions — 2 characters per side
HERO_X = [90, 330]
GOBLIN_X = [700, 940]
CHAR_Y = 120

# Selection screen positions — 3 characters per side
HERO_SEL_X = [10, 200, 390]
GOBLIN_SEL_X = [620, 800, 990]
SEL_CHAR_Y = 250

TEAM_LABEL_Y = 85
DIVIDER_X = WIDTH // 2
DIVIDER_TOP = 95
DIVIDER_BOTTOM = 515
ACTION_PANEL_RECT = pygame.Rect(40, 560, 330, 190)
LOG_RECT = pygame.Rect(400, 560, 760, 190)
BUTTON_Y = 625
RESTART_RECT = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 25, 150, 50)

ENEMY_ACTION_DELAY = 1800  # ms between each goblin's action

def load_image(path, w, h):
    """Load an image scaled to (w, h), return None if file missing."""
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (w, h))
    except (pygame.error, FileNotFoundError):
        return None

def load_sound(path, volume=1.0):
    """Load a sound effect, return None if audio is unavailable."""
    if not pygame.mixer.get_init():
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except (pygame.error, FileNotFoundError):
        return None

def play_sound(sound):
    if sound is not None:
        sound.play()

def start_bgm():
    if not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.music.load("sound/bgm2.mp3")
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except (pygame.error, FileNotFoundError):
        pass

ACTION_SOUNDS = {
    "Orangecat": load_sound("sound/magic.mp3", 0.7),
    "Applecat": load_sound("sound/bow_shoot.mp3", 0.7),
    "Bananacat": load_sound("sound/sword.mp3", 0.7),
    "Drog": load_sound("sound/knife.mp3", 0.7),
    "Cheems": load_sound("sound/gunshot.mp3", 0.7),
    "Witchdog": load_sound("sound/lightning.mp3", 0.7),
}
WIN_SOUND = load_sound("sound/yay.mp3", 0.8)
LOSE_SOUND = load_sound("sound/bell.mp3", 0.8)
HEAL_SOUND = load_sound("sound/heal.mp3", 0.7)

def play_action_sound(character):
    play_sound(ACTION_SOUNDS.get(character.name))

def play_special_sound(character):
    if character.name in ("Orangecat", "Witchdog"):
        play_sound(HEAL_SOUND)
    else:
        play_action_sound(character)

# -------------------------------
# Draw a single character slot
# Dead characters are not drawn at all
# -------------------------------
def draw_character(surface, character, x, y, fallback_color,
                   is_active=False, is_target=False):
    if not character.is_alive():
        return

    ox = character.shake_offset()
    slot_w = max(character.sprite_w, 120)
    center_x = x + slot_w // 2

    # Highlight border
    if is_active:
        pygame.draw.rect(surface, YELLOW, (x + ox - 4, y - 4, slot_w + 8, character.sprite_h + 32), 3, border_radius=10)
    if is_target:
        pygame.draw.rect(surface, ORANGE, (x + ox - 4, y - 4, slot_w + 8, character.sprite_h + 32), 3, border_radius=10)

    # Name
    name_surf = small_font.render(character.name, True, WHITE)
    surface.blit(name_surf, (center_x + ox - name_surf.get_width() // 2, y))

    # Sprite — image if available, otherwise fallback colored rect
    img = character.images.get(character.current_action) or character.images.get("base")
    if img:
        surface.blit(img, (x + ox, y + 18))
    else:
        pygame.draw.rect(surface, fallback_color,
                         (x + ox, y + 18, character.sprite_w, character.sprite_h), border_radius=10)

    # HP bar (no shake offset — stays fixed)
    bar_w = 100
    bar_h = 12
    bar_y = y + 230
    bar_x = center_x - bar_w // 2
    pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_w, bar_h))
    hp_ratio = character.hp / character.max_hp
    pygame.draw.rect(surface, GREEN, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
    hp_text = small_font.render(f"{character.hp}/{character.max_hp}", True, WHITE)
    surface.blit(hp_text, (center_x - hp_text.get_width() // 2, bar_y + 14))

    # Level and EXP bar
    exp = getattr(character, "exp", 0)
    level = getattr(character, "level", 1)
    exp_y = bar_y + 60
    exp_ratio = min(1, exp / 100)
    level_text1 = small_font.render(f"Lv {level}", True, WHITE)
    surface.blit(level_text1, (bar_x, exp_y - 18))
    pygame.draw.rect(surface, GRAY, (bar_x, exp_y, bar_w, bar_h))
    pygame.draw.rect(surface, GOODBLUE, (bar_x, exp_y, int(bar_w * exp_ratio), bar_h))
    pygame.draw.rect(surface, WHITE, (bar_x, exp_y, bar_w, bar_h), 1)
    level_text2 = small_font.render(f"EXP {exp}/100", True, WHITE)
    surface.blit(level_text2, (bar_x, exp_y + bar_h + 4))


# -------------------------------
# Draw battle log
# -------------------------------
def draw_log(surface, log_messages):
    log_rect = LOG_RECT
    pygame.draw.rect(surface, LIGHT_BLUE, log_rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, log_rect, 2, border_radius=10)

    title = font.render("Battle Log", True, WHITE)
    surface.blit(title, (log_rect.x + 10, log_rect.y + 10))

    start_y = log_rect.y + 45
    for i, msg in enumerate(log_messages[-6:]):
        text_surface = small_font.render(msg, True, WHITE)
        surface.blit(text_surface, (log_rect.x + 10, start_y + i * 24))


def special_target_for(character, opponents):
    if getattr(character.skill, "target_self", False):
        return character

    alive_opponents = [opponent for opponent in opponents if opponent.is_alive()]
    if not alive_opponents:
        return None
    return random.choice(alive_opponents)


# -------------------------------
# Single goblin AI action
# -------------------------------
def goblin_act(goblin, heroes, battle_log):
    alive_heroes = [h for h in heroes if h.is_alive()]
    if not alive_heroes:
        return
    goblin.stop_defending()
    if goblin.hp < goblin.max_hp * 0.5:
        choices = ["defend", "attack", "special"]
        weights = [0.5, 0.3, 0.2]
    else:
        choices = ["attack", "defend", "special"]
        weights = [0.6, 0.2, 0.2]
    action = random.choices(choices, weights=weights, k=1)[0]
    if action == "special" and goblin.special_cooldown == 0:
        target = special_target_for(goblin, heroes)
        result = goblin.use_special(target)
        battle_log.append(result)
        play_special_sound(goblin)
        goblin.trigger_action("special")
    elif action == "defend":
        goblin.defend()
        battle_log.append(f"{goblin.name} used DEFEND.")
        goblin.trigger_action("defend")
    else:
        target = random.choice(alive_heroes)
        damage = goblin.attack_target(target)
        if target.last_defended:
            battle_log.append(f"{target.name} defended! {goblin.name} dealt only {damage} dmg.")
        else:
            battle_log.append(f"{goblin.name} dealt {damage} dmg to {target.name}.")
        play_action_sound(goblin)
        goblin.trigger_action("attack")
    goblin.reduce_cooldown()


# -------------------------------
# Create all characters with images
# -------------------------------
def create_all_characters():
    """Create all 3 heroes and 3 goblins with loaded images."""
    heroes = [
        Character("Orangecat", 100, 25,  8, Special_2()),
        Character("Applecat",  80, 20, 10, Special_3()),
        Character("Bananacat",  80, 30,  4, Special_1()),
    ]
    goblins = [
        Character("Drog",     80, 30,  6, Special_4()),
        Character("Cheems",  120, 20, 10, Special_5()),
        Character("Witchdog", 70, 25,  5, Special_6()),
    ]
    hero_sizes = {
        "Orangecat": (180, 180),
        "Applecat":  (180, 180),
        "Bananacat": (220, 180),
    }
    goblin_sizes = {
        "Drog":     (150, 150),
        "Cheems":   (160, 160),
        "Witchdog": (210, 160),
    }

    for hero in heroes:
        n = hero.name.lower()
        w, h = hero_sizes[hero.name]
        hero.sprite_w, hero.sprite_h = w, h
        hero.images["base"]    = load_image(f"image/{n}_base.png",    w, h)
        hero.images["attack"]  = load_image(f"image/{n}_attack.png",  w, h)
        hero.images["defend"]  = load_image(f"image/{n}_defend.png",  w, h)
        hero.images["special"] = load_image(f"image/{n}_special.png", w, h)

    for goblin in goblins:
        n = goblin.name.lower()
        w, h = goblin_sizes[goblin.name]
        goblin.sprite_w, goblin.sprite_h = w, h
        goblin.images["base"]    = load_image(f"image/{n}_base.png",    w, h)
        goblin.images["attack"]  = load_image(f"image/{n}_attack.png",  w, h)
        goblin.images["defend"]  = load_image(f"image/{n}_defend.png",  w, h)
        goblin.images["special"] = load_image(f"image/{n}_special.png", w, h)

    return heroes, goblins


# -------------------------------
# Character selection screen
# -------------------------------
def character_select_screen(all_heroes, all_goblins):
    """
    Player clicks to pick exactly 2 heroes.
    2 goblins are randomly selected after the player chooses heroes.
    Returns (selected_heroes, selected_goblins) — each a list of 2 Character objects.
    """
    hero_selected = []  # indices of chosen heroes

    start_button = Button(
        WIDTH // 2 - 80, HEIGHT - 85, 160, 50,
        text="Start Battle",
        bg_color=GREEN,
        text_color=WHITE,
        font=font,
    )

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Hero slot click detection
                for i, hero in enumerate(all_heroes):
                    slot_w = max(hero.sprite_w, 120)
                    hit = pygame.Rect(HERO_SEL_X[i], SEL_CHAR_Y, slot_w, hero.sprite_h + 20)
                    if hit.collidepoint(mx, my):
                        if i in hero_selected:
                            hero_selected.remove(i)
                        elif len(hero_selected) < 2:
                            hero_selected.append(i)

                # Start button
                if len(hero_selected) == 2 and start_button.is_clicked((mx, my)):
                    goblin_selected = sorted(random.sample(range(3), 2))
                    return (
                        [all_heroes[i] for i in sorted(hero_selected)],
                        [all_goblins[i] for i in goblin_selected],
                    )

        # --- Draw selection screen ---
        screen.blit(background, (0, 0))

        # Title
        title_surf = title_font.render("Select Your Team", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 20))

        # Instruction
        inst_surf = font.render("Click to choose 2 heroes  |  Enemy team is chosen at random", True, DARK_GRAY)
        screen.blit(inst_surf, (WIDTH // 2 - inst_surf.get_width() // 2, 78))

        # Centre divider
        pygame.draw.line(screen, WHITE, (DIVIDER_X, 110), (DIVIDER_X, 660), 2)

        # Team labels
        hl = font.render("Heroes", True, YELLOW)
        gl = font.render("Goblins", True, ORANGE)
        screen.blit(hl, (DIVIDER_X // 2 - hl.get_width() // 2, 115))
        screen.blit(gl, (DIVIDER_X + DIVIDER_X // 2 - gl.get_width() // 2, 115))

        # Draw heroes — YELLOW border when selected
        for i, hero in enumerate(all_heroes):
            draw_character(screen, hero, HERO_SEL_X[i], SEL_CHAR_Y, BLUE,
                           is_active=(i in hero_selected))

        # Draw goblins — enemy team is not chosen until the player starts
        for i, goblin in enumerate(all_goblins):
            draw_character(screen, goblin, GOBLIN_SEL_X[i], SEL_CHAR_Y, RED)

        # Selection counter
        count_surf = font.render(f"Heroes selected: {len(hero_selected)} / 2", True, WHITE)
        screen.blit(count_surf, (40, HEIGHT - 90))

        # Start button (enabled only when 2 heroes are chosen)
        start_button.draw(screen, len(hero_selected) == 2)

        pygame.display.flip()


# -------------------------------
# Initialise battle state
# -------------------------------
def create_new_game(heroes, goblins):
    battle_log = ["The battle begins!"]
    return heroes, goblins, battle_log


def next_alive(characters, start_idx):
    i = start_idx
    while i < len(characters) and not characters[i].is_alive():
        i += 1
    return i

def next_alive_goblin(characters, start_idx):
    i = start_idx
    while i < len(characters):
        if characters[i].is_alive():
            return i
        i += 1

    i = 0
    while i < start_idx:
        if characters[i].is_alive():
            return i
        i += 1

    return None

def random_alive_enemy(enemies):
    alive_enemies = [enemy for enemy in enemies if enemy.is_alive()]
    if not alive_enemies:
        return None
    return random.choice(alive_enemies)

# -------------------------------
# Main game function
# -------------------------------
def main():
    start_bgm()

    # Show selection screen before the first battle
    all_heroes, all_goblins = create_all_characters()
    selected_heroes, selected_goblins = character_select_screen(all_heroes, all_goblins)
    heroes, goblins, battle_log = create_new_game(selected_heroes, selected_goblins)

    player_turn = True
    current_hero_idx = next_alive(heroes, 0)
    turn_transition = False
    turn_transition_timer = 0
    TURN_TRANSITION_DELAY = 1000   # 1 second

    # Enemy phase state
    current_goblin_idx = 0
    enemy_action_timer = 0

    game_over = False
    winner_text = ""

    # Buttons
    attack_button = Button(
        ACTION_PANEL_RECT.x + 20, BUTTON_Y, 70, 90,
        text="Attack",
        text_color=(255, 255, 255),
        font=font,
        image_path="image/sword.png"
    )
    defend_button = Button(
        ACTION_PANEL_RECT.x + 115, BUTTON_Y, 95, 90,
        text="Defend",
        text_color=(255, 255, 255),
        font=font,
        image_path="image/shield.png"
    )
    special_button = Button(
        ACTION_PANEL_RECT.x + 240, BUTTON_Y, 60, 90,
        text="Special",
        text_color=(255, 255, 255),
        font=font,
        image_path="image/special.png"
    )
    restart_button = Button(RESTART_RECT.x, RESTART_RECT.y, RESTART_RECT.width, RESTART_RECT.height, "Restart", GREEN)

    def finish_hero_turn():
        nonlocal current_goblin_idx, current_hero_idx, turn_transition, turn_transition_timer
        current_goblin_idx = current_hero_idx  # paired goblin responds
        current_hero_idx = next_alive(heroes, current_hero_idx + 1)
        turn_transition = True
        turn_transition_timer = TURN_TRANSITION_DELAY

    def end_game(text, sound):
        nonlocal game_over, winner_text
        game_over = True
        winner_text = text
        play_sound(sound)

    running = True
    while running:
        dt = clock.tick(60)

        # Update shake animations for all characters
        for c in heroes + goblins:
            c.update(dt)

        # -------------------------------
        # Event handling
        # -------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if game_over and restart_button.is_clicked(mouse_pos):
                    # Return to selection screen for a fresh game
                    all_heroes, all_goblins = create_all_characters()
                    selected_heroes, selected_goblins = character_select_screen(all_heroes, all_goblins)
                    heroes, goblins, battle_log = create_new_game(selected_heroes, selected_goblins)
                    player_turn = True
                    current_hero_idx = next_alive(heroes, 0)
                    turn_transition = False
                    turn_transition_timer = 0
                    current_goblin_idx = 0
                    enemy_action_timer = 0
                    game_over = False
                    winner_text = ""
                    start_bgm()

                if player_turn and not turn_transition and not game_over and current_hero_idx < len(heroes):
                    hero = heroes[current_hero_idx]

                    if attack_button.is_clicked(mouse_pos):
                        goblin = random_alive_enemy(goblins)
                        if goblin is not None:
                            hero.stop_defending()
                            damage = hero.attack_target(goblin)
                            if goblin.last_defended:
                                battle_log.append(f"{goblin.name} defended! {hero.name} dealt only {damage} dmg.")
                            else:
                                battle_log.append(
                                    f"{hero.name} attacked {goblin.name} for {damage} dmg."
                                )
                            play_action_sound(hero)
                            hero.reduce_cooldown()
                            hero.trigger_action("attack")
                            finish_hero_turn()

                    elif defend_button.is_clicked(mouse_pos):
                        hero.stop_defending()
                        hero.defend()
                        battle_log.append(f"{hero.name} used DEFEND.")
                        hero.reduce_cooldown()
                        hero.trigger_action("defend")
                        finish_hero_turn()

                    elif special_button.is_clicked(mouse_pos):
                        if hero.special_cooldown > 0:
                            battle_log.append(
                                f"Special not ready. Cooldown: {hero.special_cooldown} turn(s)."
                            )
                        else:
                            target = special_target_for(hero, goblins)
                            if target is not None:
                                hero.stop_defending()
                                result = hero.use_special(target)
                                battle_log.append(result)
                                play_special_sound(hero)
                                hero.reduce_cooldown()
                                hero.trigger_action("special")
                                finish_hero_turn()

        # -------------------------------
        # Check win: all goblins dead
        # -------------------------------
        if all(not g.is_alive() for g in goblins) and not game_over:
            end_game("You Win!", WIN_SOUND)
        # -------------------------------
        # Turn transition: keep showing "Your Turn" briefly
        # -------------------------------
        if turn_transition and not game_over:
            turn_transition_timer -= dt
            if turn_transition_timer <= 0:
                turn_transition = False
                player_turn = False
                enemy_action_timer = ENEMY_ACTION_DELAY
        # -------------------------------
        # Enemy turn phase — one goblin per tick
        # -------------------------------
        if not player_turn and not game_over:
            enemy_action_timer -= dt
            if enemy_action_timer <= 0:
                alive_goblin_idx = next_alive_goblin(goblins, current_goblin_idx)

                if alive_goblin_idx is not None:
                    current_goblin_idx = alive_goblin_idx
                    goblin_act(goblins[current_goblin_idx], heroes, battle_log)

                # Wrap hero index if all heroes have gone this round
                if current_hero_idx >= len(heroes):
                    current_hero_idx = next_alive(heroes, 0)

                player_turn = True

        # -------------------------------
        # Check lose: all heroes dead
        # -------------------------------
        if all(not h.is_alive() for h in heroes) and not game_over:
            end_game("You Lose!", LOSE_SOUND)

        # -------------------------------
        # Drawing
        # -------------------------------
        screen.blit(background, (0, 0))

        # Title — shows turn phase
        if game_over:
            title_text = winner_text
            title_color = WHITE
        elif player_turn or turn_transition:
            title_text = "Your Turn"
            title_color = BLUE
        else:
            title_text = "Enemy Turn"
            title_color = RED
        title_surface = title_font.render(title_text, True, title_color)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 25))

        # Team labels
        heroes_label = font.render("Heroes", True, YELLOW)
        goblins_label = font.render("Goblins", True, ORANGE)
        screen.blit(heroes_label, (DIVIDER_X // 2 - heroes_label.get_width() // 2, TEAM_LABEL_Y))
        screen.blit(goblins_label, (DIVIDER_X + DIVIDER_X // 2 - goblins_label.get_width() // 2, TEAM_LABEL_Y))

        # Draw heroes
        for i, hero in enumerate(heroes):
            is_active = (
                player_turn and not game_over
                and not turn_transition
                and i == current_hero_idx
            )
            draw_character(screen, hero, HERO_X[i], CHAR_Y, BLUE, is_active=is_active)

        # Draw goblins
        for i, goblin in enumerate(goblins):
            is_active = (
                not player_turn and not game_over
                and i == current_goblin_idx
            )
            draw_character(screen, goblin, GOBLIN_X[i], CHAR_Y, RED,
                           is_active=is_active)

        # Button panel box
        panel_rect = ACTION_PANEL_RECT
        pygame.draw.rect(screen, LIGHT_BLUE, panel_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, panel_rect, 2, border_radius=10)
        screen.blit(small_font.render("Actions", True, WHITE), (panel_rect.x + 8, panel_rect.y + 5))

        # Action buttons
        buttons_enabled = player_turn and not game_over and not turn_transition
        attack_button.draw(screen, buttons_enabled)
        defend_button.draw(screen, buttons_enabled)
        special_button.draw(screen, buttons_enabled)

        # Current hero info
        if player_turn and not turn_transition and not game_over and current_hero_idx < len(heroes):
            hero = heroes[current_hero_idx]
            info = small_font.render(
                f"{hero.name}'s action  |  Lv: {hero.level}  EXP: {hero.exp}  Special CD: {hero.special_cooldown}", True, WHITE
            )
            screen.blit(info, (LOG_RECT.x + 10, LOG_RECT.y - 35))
        # Current goblin info
        elif not player_turn and not game_over:
            goblin_idx = next_alive_goblin(goblins, current_goblin_idx)
            if goblin_idx is not None:
                goblin = goblins[goblin_idx]
                info = small_font.render(
                    f"{goblin.name}'s action  |  Lv: {goblin.level}  EXP: {goblin.exp}  Special CD: {goblin.special_cooldown}", True, WHITE
                )
                screen.blit(info, (LOG_RECT.x + 10, LOG_RECT.y - 35))

        # Restart button — only after game over
        if game_over:
            restart_button.draw(screen, True)

        # Battle log
        draw_log(screen, battle_log)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
