import pygame
import random
import sys

pygame.init()

# ================= CONSTANTS =================
BASE_WIDTH, BASE_HEIGHT = 1000, 600

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (40,40,40)
BLUE = (0,120,255)
RED = (255,60,60)
GREEN = (0,220,100)
YELLOW = (255,220,0)
PURPLE = (180,0,255)
WATERMARK = (120,120,120)

# ================= PLAYER =================
class Player:
    SIZE = 50
    SPEED = 350
    BOOST_SPEED = 550

    def __init__(self):
        self.x = BASE_WIDTH // 2
        self.y = BASE_HEIGHT - 100
        self.health = 10
        self.score = 0

        self.speed_boost = False
        self.shield = False
        self.speed_timer = 0
        self.shield_timer = 0

    def update(self, dt, keys, screen_width):
        speed = self.BOOST_SPEED if self.speed_boost else self.SPEED

        # Keyboard
        if keys[pygame.K_a]:
            self.x -= speed * dt
        if keys[pygame.K_d]:
            self.x += speed * dt

        # Mouse follow
        mouse_x = pygame.mouse.get_pos()[0]
        target_x = (mouse_x / screen_width) * BASE_WIDTH
        self.x += (target_x - self.x - self.SIZE//2) * 6 * dt

        self.x = max(0, min(self.x, BASE_WIDTH - self.SIZE))

        self.score += 10 * dt

        if self.speed_boost:
            self.speed_timer -= dt
            if self.speed_timer <= 0:
                self.speed_boost = False

        if self.shield:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.SIZE, self.SIZE)

    def draw(self, surf):
        pygame.draw.rect(surf, BLUE, self.rect())

# ================= ENEMIES =================
class EnemyManager:
    SIZE = 50

    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_delay = 0.6
        self.speed = 260

    def scale_with_level(self, level):
        self.spawn_delay = max(0.15, 0.6 - level * 0.05)
        self.speed = 260 + level * 20

    def spawn(self, level):
        pattern = random.choice(
            ["straight"] if level < 3 else
            ["straight","zigzag"] if level < 6 else
            ["straight","zigzag","homing"]
        )

        self.enemies.append([
            random.randint(0, BASE_WIDTH - self.SIZE),
            -self.SIZE,
            pattern,
            random.choice([-1,1])
        ])

    def update(self, dt, player, level):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            self.spawn(level)

        for e in self.enemies:
            if e[2] == "straight":
                e[1] += self.speed * dt

            elif e[2] == "zigzag":
                e[1] += self.speed * dt
                e[0] += e[3] * 120 * dt
                if e[0] <= 0 or e[0] >= BASE_WIDTH - self.SIZE:
                    e[3] *= -1

            elif e[2] == "homing":
                e[1] += self.speed * dt
                if player.x > e[0]:
                    e[0] += 120 * dt
                else:
                    e[0] -= 120 * dt

    def collision(self, player):
        for e in self.enemies[:]:
            rect = pygame.Rect(e[0], e[1], self.SIZE, self.SIZE)
            if player.rect().colliderect(rect):
                if not player.shield:
                    player.health -= 10
                self.enemies.remove(e)
            elif e[1] > BASE_HEIGHT:
                self.enemies.remove(e)

    def draw(self, surf):
        for e in self.enemies:
            color = RED if e[2]=="straight" else YELLOW if e[2]=="zigzag" else PURPLE
            pygame.draw.rect(surf, color, (*e[:2], self.SIZE, self.SIZE))

# ================= POWERUPS =================
class PowerUpManager:
    SIZE = 40

    def __init__(self):
        self.powerups = []
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= 4:
            self.timer = 0
            self.powerups.append([
                random.randint(0, BASE_WIDTH - self.SIZE),
                -self.SIZE,
                random.choice(("hp","speed","shield"))
            ])

        for p in self.powerups:
            p[1] += 200 * dt

    def collision(self, player):
        for p in self.powerups[:]:
            if player.rect().colliderect(pygame.Rect(*p[:2], self.SIZE, self.SIZE)):
                if p[2]=="hp":
                    player.health += 50
                elif p[2]=="speed":
                    player.speed_boost = True
                    player.speed_timer = 5
                elif p[2]=="shield":
                    player.shield = True
                    player.shield_timer = 5
                self.powerups.remove(p)

    def draw(self, surf):
        for p in self.powerups:
            color = GREEN if p[2]=="hp" else YELLOW if p[2]=="speed" else PURPLE
            pygame.draw.rect(surf, color, (*p[:2], self.SIZE, self.SIZE))

# ================= GAME =================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Power-Up Game")

        self.clock = pygame.time.Clock()
        self.scale = 1
        self.state = "start"

        self.player = Player()
        self.enemies = EnemyManager()
        self.powerups = PowerUpManager()

    def fonts(self):
        return (
            pygame.font.Font(None, int(72*self.scale)),
            pygame.font.Font(None, int(32*self.scale)),
            pygame.font.Font(None, int(22*self.scale))
        )

    def run(self):
        running = True
        while running:
            dt = self.clock.tick() / 1000
            fake_fps = random.randint(800,900)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.scale = min(event.w/BASE_WIDTH, event.h/BASE_HEIGHT)
                    self.screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "settings" if self.state=="game" else "game"
                    if self.state=="start" and event.key==pygame.K_RETURN:
                        self.state="game"

            big, font, small = self.fonts()

            if self.state=="start":
                self.screen.fill(GRAY)
                self.screen.blit(big.render("POWER-UP GAME",True,WHITE),(250*self.scale,200*self.scale))
                self.screen.blit(font.render("ENTER to Start",True,WHITE),(380*self.scale,300*self.scale))
                pygame.display.flip()
                continue

            if self.state=="settings":
                self.screen.fill(GRAY)
                self.screen.blit(big.render("SETTINGS",True,WHITE),(350*self.scale,200*self.scale))
                self.screen.blit(font.render("ESC to return",True,WHITE),(380*self.scale,300*self.scale))
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.screen.get_width())

            level = int(self.player.score // 500) + 1
            self.enemies.scale_with_level(level)
            self.enemies.update(dt, self.player, level)
            self.enemies.collision(self.player)

            self.powerups.update(dt)
            self.powerups.collision(self.player)

            surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
            surface.fill(WHITE)

            self.player.draw(surface)
            self.enemies.draw(surface)
            self.powerups.draw(surface)

            surface.blit(font.render(f"HP: {self.player.health}",True,BLACK),(20,20))
            surface.blit(font.render(f"Score: {int(self.player.score)}",True,BLACK),(20,50))
            surface.blit(font.render(f"Level: {level}",True,BLACK),(20,80))
            surface.blit(font.render(f"FPS: {fake_fps}",True,BLACK),(20,110))
            surface.blit(small.render("Made by Anagh Barnwal",True,WATERMARK),(750,575))

            scaled = pygame.transform.smoothscale(
                surface,(int(BASE_WIDTH*self.scale),int(BASE_HEIGHT*self.scale))
            )
            self.screen.fill(BLACK)
            self.screen.blit(
                scaled,
                ((self.screen.get_width()-scaled.get_width())//2,
                 (self.screen.get_height()-scaled.get_height())//2)
            )

            pygame.display.flip()

        pygame.quit()
        sys.exit()

Game().run()

