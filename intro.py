import pgzrun
from numpy.random import set_state
from pgzero.actor import Actor
from pygame import Rect

WIDTH = 512
HEIGHT = 512
TITLE = "Platformer Kodland"

game_state = "menu"
sound_on = True

score = 0
lives = 3

menu_btn = {
    "start": Rect((WIDTH/2 - 100, 280), (200, 50)),
    "sound": Rect((WIDTH/2 - 100, 340), (200, 50)),
    "exit": Rect((WIDTH/2 - 100, 400), (200, 50))
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
    def __init__(self,pos):
        self.actor = Actor("character_purple_front", pos)
        self.vx = 0
        self.vy = 0
        self.on_ground = False

        self.idle_sprites = ["character_purple_idle", "character_purple_jump"]
        self.walk_sprites = ["character_purple_walk_a", "character_purple_walk_b"]
        self.current_frame = 0
        self.anim_timer = 0

    def update(self):
        self.vy += 0.5 #gravity
        self.actor.y += self.vy

        if self.actor.y > HEIGHT - 50:
            self.actor.y = HEIGHT - 50
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        for p in platforms:
            if self.actor.colliderect(p.actor) and self.vy >= 0:
                self.actor.y = p.actor.top - self.actor.height/2
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
            self.vy = -10
            if sound_on:
                sounds.jump.play()

    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self, pos, patrol_min, patrol_max):
        self.actor = Actor("ladybug_fly", pos)
        self.vx = 2
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


def create_level():
    global hero, enemies, coins, platforms, score, lives

    hero = Hero((100, HEIGHT - 70))

    enemies = [Enemy((200, HEIGHT - 90), 150, 300),
               Enemy((350, 350), 300, 420),
               Enemy((440, 250), 300, 500)]

    coins = [Coin((150, 360)),
             Coin((350, 300)),
             Coin((250, 200))]

    platforms = [Platform((150, 400)),
                 Platform((350, 300)),
                 Platform((250, 200))]

    score = 0
    lives = 3


create_level()


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
            if hero.actor.bottom <= e.actor.top + 10 and hero.vy > 0 :
                defeated.append(e)
                hero.vy = -8
                if sound_on:
                    sounds.hit.play()

            else:
                lives -= 1
                if lives <= 0:
                    game_over()

    for e in defeated:
        enemies.remove(e)

    if len(enemies) == 0:
        game_win()

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
        screen.draw.text(f"lives:{lives}", topleft=(10, 46), fontsize=28, color="black")

    elif game_state == "menu":
        screen.blit("background_start", (0, 0))
        screen.draw.text("Platformer Kodland", center=(WIDTH / 2, 150), fontsize=70, color="black")

        screen.draw.filled_rect(menu_btn["start"], (255, 255, 255))
        screen.draw.text("Start Game", center=menu_btn["start"].center, fontsize=40, color="black")

        screen.draw.filled_rect(menu_btn["sound"], (255, 255, 255))
        screen.draw.text(f"Sound: {'ON' if sound_on else 'OFF'}", center=menu_btn["sound"].center, fontsize=40, color="black")

        screen.draw.filled_rect(menu_btn["exit"], (255, 255, 255))
        screen.draw.text("Exit", center=menu_btn["exit"].center, fontsize=40, color="black")


    elif game_state == "game_over":
        screen.blit("background_end", (0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=70, color="red")
        screen.draw.text("Click to return to Menu", center=(WIDTH/2, HEIGHT/2 + 60), fontsize=32, color="black")

    elif game_state == "win":
        screen.blit("background_end", (0, 0))
        screen.draw.text("YOU WIN!", center=(WIDTH/2, HEIGHT/2), fontsize=70, color="green")
        screen.draw.text("Click to return to Menu", center=(WIDTH/2, HEIGHT/2 + 60), fontsize=32, color="black")

def on_key_down(key):
    global game_state, sound_on

    if game_state == "game":
        if key == keys.SPACE:
            hero.jump()
        if key == keys.LEFT:
            hero.vx = -5
        if key == keys.RIGHT:
            hero.vx = 5

    elif game_state == "game_over":
        if key == keys.RETURN:
            music.stop()
            set_state("menu")

def on_key_up(key):
    if game_state == "game":
        if key in (keys.LEFT, keys.RIGHT):
            hero.vx = 0

def on_mouse_down(pos):
    global game_state

    if game_state == "menu":
        if menu_btn["start"].collidepoint(pos):
            start_game()
        elif menu_btn["sound"].collidepoint(pos):
            sound_toggle()
        elif menu_btn["exit"].collidepoint(pos):
            exit()

    elif game_state == "game_over":
        game_state = "menu"


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
    global game_state

    game_state = "win"
    music.stop()

    if sound_on:
        sounds.coin.play()

def game_over():
    set_state("game_over")
    music.stop()
    if sound_on:
        sounds.hit.play()

pgzrun.go()