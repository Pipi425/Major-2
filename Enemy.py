import pygame
import math

class Enemy:
    def __init__(self, x, y):
        self.images = []
        self.images_hit = []
        self.SoundEffects = []

        for i in range(1, 7):
            img = pygame.image.load(f"Enemies/fly_{i}.png").convert_alpha()
            img_hit = pygame.image.load(f"Enemies/fly_{i}_hit.png").convert_alpha()
            img = pygame.transform.scale(img, (60, 60))
            img_hit = pygame.transform.scale(img_hit, (60, 60))
            self.images.append(img)
            self.images_hit.append(img_hit)

        self.SoundEffects.append(pygame.mixer.Sound("SoundEffects/Fly_death.mp3"))
        self.SoundEffects[0].set_volume(0.5)

        self.SoundEffects.append(pygame.mixer.Sound("SoundEffects/Fly_chase.mp3"))
        self.SoundEffects[1].set_volume(0.2)

        self.spawn_x = x
        self.spawn_y = y

        self.x = x
        self.y = y

        self.frame = 0
        self.count = 0
        self.speed = 1
        self.hp = 5
        self.max_hp = 5
        self.alive = True

        self.is_hit = False
        self.hit_timer = 0
        self.hit_flash_counter = 0

        self.aggro = False
        self.state = "idle"
        self.lose_timer = 0

        self.idle_count = 0
        self.hit_stun_timer = 0

        self.last_state = "idle"

    def get_image(self):
        normal = self.images[self.frame]

        if not self.is_hit:
            return normal

        if (self.hit_flash_counter // 5) % 2 == 0:
            return normal
        else:
            return self.images_hit[self.frame]

    def get_rect(self):
        if not self.alive:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x + 8, self.y + 10, 30, 30)

    def get_center(self):
        image = self.images[self.frame]
        rect = image.get_rect(topleft=(self.x, self.y))
        return rect.center

    def check_move(self, dx, dy, walls):
        test_rect = self.get_rect().move(dx, dy)
        for wall in walls:
            if test_rect.colliderect(wall):
                return False
        return True

    def animate(self, speed):
        self.count += 1
        if self.count >= speed:
            self.count = 0
            self.frame += 1
            if self.frame >= 6:
                self.frame = 0

    def move(self, player, walls):
        if not self.alive:
            return

        if pygame.time.get_ticks() < self.hit_stun_timer:
            self.animate(999)
            return

        player_x, player_y = player.get_center()
        enemy_x, enemy_y = self.get_center()

        dx = player_x - enemy_x
        dy = player_y - enemy_y
        dist_sq = dx * dx + dy * dy

        DETECTION_RANGE = 300
        LOSE_RANGE = 500

        if self.state == "chase":
            if dist_sq > LOSE_RANGE * LOSE_RANGE:
                self.lose_timer = 120
                self.state = "lost"

        if self.state == "idle":
            if dist_sq <= DETECTION_RANGE * DETECTION_RANGE:
                self.state = "chase"

        elif self.state == "lost":

            self.lose_timer -= 1

            self.animate(6)

            if self.lose_timer <= 0:
                self.state = "return"

        elif self.state == "return":
            dx = self.spawn_x - self.x
            dy = self.spawn_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 5:
                self.x = self.spawn_x
                self.y = self.spawn_y
                self.state = "idle"
                self.aggro = False
            else:
                if dx > 0:
                    self.x += self.speed
                elif dx < 0:
                    self.x -= self.speed

                if dy > 0:
                    self.y += self.speed
                elif dy < 0:
                    self.y -= self.speed

        if self.state != self.last_state:
            if self.state == "chase":
                self.SoundEffects[1].play()
            elif self.state == "lost":
                self.SoundEffects[1].play()

            self.last_state = self.state

        if self.state == "chase":
            self.aggro = True

            mx = self.speed if player_x > enemy_x else -self.speed
            my = self.speed if player_y > enemy_y else -self.speed

            if self.check_move(mx, 0, walls):
                self.x += mx

            if self.check_move(0, my, walls):
                self.y += my

            self.animate(6)

        elif self.state == "return":
            self.animate(8)

        elif self.state == "idle":
            self.animate(6)

        if self.is_hit:
            self.hit_timer -= 1
            self.hit_flash_counter += 1

            if self.hit_timer <= 0:
                self.is_hit = False
                self.hit_flash_counter = 0

    def hit(self):
        if not self.alive:
            return

        self.hp -= 1

        self.is_hit = True
        self.hit_timer = 20

        self.hit_stun_timer = pygame.time.get_ticks() + 100

        if self.hp <= 0:
            self.alive = False
            self.SoundEffects[0].play()

    def draw_health_bar(self, screen):
        if not self.alive:
            return

        bar_x = self.x + 8
        bar_y = self.y - 8

        width = 55
        height = 6

        current_width = int(width * self.hp / self.max_hp)

        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, width, height))
        pygame.draw.rect(screen, (180, 30, 30), (bar_x, bar_y, current_width, height))

    def draw(self, screen):
        if self.alive:
            screen.blit(self.get_image(), (self.x, self.y))

        self.draw_health_bar(screen)