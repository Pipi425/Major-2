import pygame

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

        for i in self.SoundEffects:
            i.set_volume(0.5)

        self.x = x
        self.y = y
        self.frame = 0
        self.count = 0
        self.speed = 1
        self.hp = 5
        self.alive = True
        self.stop = 0

        self.is_hit = False
        self.hit_timer = 0
        self.hit_flash_counter = 0

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

    def move(self, player, walls):
        if not self.alive:
            return

        if self.stop > 0:
            self.stop -= 1
            return

        moving = False

        player_x, player_y = player.get_center()
        enemy_x, enemy_y = self.get_center()

        dx = 0
        dy = 0

        if player_x > enemy_x:
            dx = self.speed
        elif player_x < enemy_x:
            dx = -self.speed

        if player_y > enemy_y:
            dy = self.speed
        elif player_y < enemy_y:
            dy = -self.speed

        if self.check_move(dx, 0, walls):
            self.x += dx
            moving = True

        if self.check_move(0, dy, walls):
            self.y += dy
            moving = True

        if moving:
            self.count += 1
            if self.count >= 8:
                self.count = 0
                self.frame += 1
                if self.frame >= 6:
                    self.frame = 0

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
        self.stop = 5

        self.is_hit = True
        self.hit_timer = 20

        if self.hp <= 0:
            self.alive = False
            self.SoundEffects[0].play()

    def draw(self, screen):
        if self.alive:
            screen.blit(self.get_image(), (self.x, self.y))