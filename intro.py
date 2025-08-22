import pgzrun
from pgzero.actor import Actor
from pygame import Rect

WIDTH = 512
HEIGHT = 512
TITLE = "Platformer Kodland"

game_state = "menu"
sound_on = True
score = 0
lives = 3

difficulty_levels = ["Easy", "Normal", "Hard"]
difficulty_index = 1

menu_btn = {
    "start": Rect((WIDTH // 2 - 110, 260), (220, 48)),
    "sound": Rect((WIDTH // 2 - 110, 318), (220, 48)),
    "diff":  Rect((WIDTH // 2 - 110, 376), (220, 48)),
    "exit":  Rect((WIDTH // 2 - 110, 434), (220, 48)),
}

class Platform:
    def __init__(self, pos, image="platform"):
        self.actor = Actor(image, pos)
    def draw(self):
        self.actor.draw()

class Coin:
    def __init__(self, pos):
        self.actor = Actor("coin_gold", pos)
        self.collected = False
    def draw(self):
        if not self.collected:
            self.actor.draw()

class Hero:
    def __init__(self, pos):
        self.actor = Actor("character_purple_front", pos)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.invincible = 0
        self.respawn_pos = pos
        self.idle_sprites = ["character_purple_idle", "character_purple_jump"]
        self.walk_sprites = ["character_purple_walk_a", "character_purple_walk_b"]
        self.current_frame = 0
        self.anim_timer = 0
    def update(self):
        if self.invincible > 0:
            self.invincible -= 1
        self.vy += 0.5
        self.actor.y += self.vy
        if self.actor.y > HEIGHT - 50:
            self.actor.y = HEIGHT - 50
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        for p in platforms:
            if self.actor.colliderect(p.actor) and self.vy >= 0:
                self.actor.y = p.actor.top - self.actor.height / 2
                self.vy = 0
                self.on_ground = True
        self.actor.x += self.vx
        self.actor.x = max(20, min(WIDTH - 20, self.actor.x))
        self.anim_timer += 1
        if self.vx != 0:
            if self.anim_timer % 10 == 0:
                self.current_frame = (self.current_frame + 1) % len(self.walk_sprites)
                self.actor.image = self.walk_sprites[self.current_frame]
        else:
            if self.anim_timer % 30 == 0:
                self.current_frame = (self.current_frame + 1) % len(self.idle_sprites)
                self.actor.image = self.idle_sprites[self.current_frame]
    def jump(self):
        if self.on_ground:
            self.vy = -13
            if sound_on:
                sounds.jump.play()
    def hit(self):
        global lives
        if self.invincible == 0:
            lives = max(lives - 1, 0)
            self.actor.pos = self.respawn_pos
            self.vx = 0
            self.vy = 0
            self.invincible = 60
            if sound_on:
                sounds.resurge.play()
    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self, pos, patrol_min, patrol_max, speed=2):
        self.actor = Actor("ladybug_fly", pos)
        self.vx = speed
        self.patrol_min = patrol_min
        self.patrol_max = patrol_max
        self.sprites = ["ladybug_walk_a", "ladybug_walk_b"]
        self.current_frame = 0
        self.anim_timer = 0
    def update(self):
        self.actor.x += self.vx
        if self.actor.x < self.patrol_min or self.actor.x > self.patrol_max:
            self.vx *= -1
        self.anim_timer += 1
        if self.anim_timer % 15 == 0:
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.actor.image = self.sprites[self.current_frame]
    def draw(self):
        self.actor.draw()

def params_for_difficulty():
    level = difficulty_levels[difficulty_index]
    if level == "Easy":
        return {"lives": 4, "enemy_speed": 2, "extra_enemies": 0}
    if level == "Hard":
        return {"lives": 2, "enemy_speed": 3, "extra_enemies": 1}
    return {"lives": 3, "enemy_speed": 2, "extra_enemies": 0}

def create_level():
    global hero, enemies, coins, platforms, score, lives
    cfg = params_for_difficulty()
    hero = Hero((80, HEIGHT - 70))
    platforms = [
        Platform((120, 420)),
        Platform((300, 320)),
        Platform((450, 220))
    ]
    enemies = [
        Enemy((300, 300), 260, 340, cfg["enemy_speed"]),
        Enemy((450, 200), 420, 480, cfg["enemy_speed"])
    ]
    for i in range(cfg["extra_enemies"]):
        enemies.append(Enemy((210, 380), 180, 270, cfg["enemy_speed"]))
    coins = [
        Coin((180, 380)),
        Coin((300, 280)),
        Coin((450, 180))
    ]
    score = 0
    lives = cfg["lives"]

def update():
    global game_state, score, lives
    if game_state != "game":
        return
    hero.update()
    for e in enemies:
        e.update()
    defeated = []
    for e in enemies:
        if hero.actor.colliderect(e.actor):
            if hero.actor.bottom <= e.actor.top + 10 and hero.vy > 0:
                defeated.append(e)
                hero.vy = -8
                if sound_on:
                    sounds.hit.play()
            else:
                hero.hit()
                if lives <= 0:
                    game_over()
                    return
    for e in defeated:
        enemies.remove(e)
    if len(enemies) == 0:
        game_win()
        return
    for c in coins:
        if (not c.collected) and hero.actor.colliderect(c.actor):
            c.collected = True
            score += 10
            if sound_on:
                sounds.coin.play()

def draw():
    screen.clear()
    if game_state == "game":
        screen.blit("background_game", (0, 0))
        for p in platforms:
            p.draw()
        for c in coins:
            c.draw()
        for e in enemies:
            e.draw()
        hero.draw()
        screen.draw.text(f"Score: {score}", topleft=(10, 10), fontsize=32, color="black")
        screen.draw.text(f"Lives: {lives}", topleft=(10, 46), fontsize=28, color="black")
    elif game_state == "menu":
        screen.blit("background_start", (0, 0))
        screen.draw.text("Platformer Kodland", center=(WIDTH // 2, 170), fontsize=60, color="black")
        for key in ["start", "sound", "diff", "exit"]:
            screen.draw.filled_rect(menu_btn[key], (255, 255, 255))
        screen.draw.text("Start Game", center=menu_btn["start"].center, fontsize=36, color="black")
        screen.draw.text(f"Sound: {'ON' if sound_on else 'OFF'}", center=menu_btn["sound"].center, fontsize=36, color="black")
        screen.draw.text(f"Difficulty: {difficulty_levels[difficulty_index]}", center=menu_btn["diff"].center, fontsize=30, color="black")
        screen.draw.text("Exit", center=menu_btn["exit"].center, fontsize=36, color="black")
    elif game_state == "game_over":
        screen.blit("background_end", (0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=70, color="red")
        screen.draw.text("Click or ENTER to return to Menu", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=28, color="black")
    elif game_state == "win":
        screen.blit("background_end", (0, 0))
        screen.draw.text("YOU WIN!", center=(WIDTH // 2, HEIGHT // 2), fontsize=70, color="green")
        screen.draw.text("Click or ENTER to return to Menu", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=28, color="black")

def on_key_down(key):
    global game_state
    if game_state == "game":
        if key == keys.SPACE:
            hero.jump()
        if key == keys.LEFT:
            hero.vx = -5
        if key == keys.RIGHT:
            hero.vx = 5
    elif game_state in ("game_over", "win"):
        if key == keys.RETURN:
            music.stop()
            set_state("menu")

def on_key_up(key):
    if game_state == "game":
        if key in (keys.LEFT, keys.RIGHT):
            hero.vx = 0

def on_mouse_down(pos):
    global game_state, sound_on, difficulty_index
    if game_state == "menu":
        if menu_btn["start"].collidepoint(pos):
            sounds.click.play()
            start_game()
        elif menu_btn["sound"].collidepoint(pos):
            sounds.click.play()
            sound_toggle()
        elif menu_btn["diff"].collidepoint(pos):
            sounds.click.play()
            difficulty_index = (difficulty_index + 1) % len(difficulty_levels)
        elif menu_btn["exit"].collidepoint(pos):
            sounds.click.play()
            exit()
    elif game_state in ("game_over", "win"):
        sounds.click.play()
        set_state("menu")

def set_state(state):
    global game_state
    game_state = state

def start_game():
    create_level()
    set_state("game")
    if sound_on:
        music.play("background")
        music.set_volume(0.3)

def sound_toggle():
    global sound_on
    sound_on = not sound_on
    if not sound_on:
        music.stop()
    else:
        if game_state == "game":
            music.play("background")
            music.set_volume(0.3)

def game_win():
    set_state("win")
    music.stop()
    if sound_on:
        sounds.coin.play()

def game_over():
    set_state("game_over")
    music.stop()
    if sound_on:
        sounds.hit.play()

pgzrun.go()
