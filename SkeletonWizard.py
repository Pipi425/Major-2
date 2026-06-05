import pygame
import math


DIRECTIONS = ["down", "up", "left", "right"]


def load_skeleton_row(sheet, row, frame_count, size):
    images = []

    frame_width = sheet.get_width() // 6
    frame_height = sheet.get_height() // 8

    for i in range(frame_count):
        image = sheet.subsurface(
            pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height)
        ).copy()

        image = pygame.transform.scale(image, size)
        images.append(image)

    return images


def load_skeleton_images(path, size):
    sheet = pygame.image.load(path).convert_alpha()

    images = {
        "idle": {
            "down": load_skeleton_row(sheet, 0, 4, size),
            "up": load_skeleton_row(sheet, 2, 4, size),
            "left": load_skeleton_row(sheet, 4, 4, size),
            "right": load_skeleton_row(sheet, 6, 4, size)
        },

        "walk": {
            "down": load_skeleton_row(sheet, 1, 6, size),
            "up": load_skeleton_row(sheet, 3, 6, size),
            "left": load_skeleton_row(sheet, 5, 6, size),
            "right": load_skeleton_row(sheet, 7, 6, size)
        }
    }

    return images


def load_book_images(path, size):
    sheet = pygame.image.load(path).convert_alpha()
    images = {}

    frame_width = sheet.get_width() // 32
    frame_height = sheet.get_height()

    starts = {
        "down": 0,
        "up": 8,
        "right": 16,
        "left": 24
    }

    for direction in DIRECTIONS:
        images[direction] = []
        start = starts[direction]

        for i in range(8):
            image = sheet.subsurface(
                pygame.Rect((start + i) * frame_width, 0, frame_width, frame_height)
            ).copy()

            image = pygame.transform.scale(image, size)
            images[direction].append(image)

    return images


def load_projectile_images(folder, size):
    images = []

    for i in range(20):
        file_name = "1_" + str(i).zfill(3) + ".png"
        image = pygame.image.load(folder + "/" + file_name).convert_alpha()
        image = pygame.transform.scale(image, size)
        images.append(image)

    return images


class WizardProjectile:
    def __init__(self, x, y, dx, dy, images):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = dy

        self.images = images

        self.frame = 0
        self.frame_count = 0

        self.speed = 5
        self.damage = 2
        self.life = 130
        self.active = True

    def get_rect(self):
        image = self.images[self.frame]

        return pygame.Rect(
            self.x + 10,
            self.y + 10,
            image.get_width() - 20,
            image.get_height() - 20
        )

    def play_animation(self):
        self.frame_count += 1

        if self.frame_count < 3:
            return

        self.frame_count = 0
        self.frame += 1

        if self.frame >= len(self.images):
            self.frame = 0

    def hit_player(self, player):
        if player.hit:
            return

        player.health -= self.damage
        player.hp = player.health

        player.hit = True
        player.hit_timer = 60
        player.hit_flash_counter = 0

        if player.health <= 0:
            player.health = 0
            player.hp = 0
            player.dead = True

        if len(player.hurt_sound) > 0:
            player.hurt_sound[0].play()

    def move(self, player, walls):
        if not self.active:
            return

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        self.life -= 1
        self.play_animation()

        for wall in walls:
            if self.get_rect().colliderect(wall):
                self.active = False
                return

        if self.get_rect().colliderect(player.get_hurt_rect()):
            self.hit_player(player)
            self.active = False
            return

        if self.life <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        image = self.images[self.frame]

        if self.dx < 0:
            image = pygame.transform.flip(image, True, False)

        screen.blit(image, (self.x, self.y))


class SkeletonWizard:
    def __init__(self, x, y):
        self.images = load_skeleton_images("SkeletonWizard/Skeleton_8-Sheet-NoOutline.png", (70, 70))
        self.book_images = load_book_images("SkeletonWizard/Book-Sheet-NoOutline.png", (90, 90))
        self.projectile_images = load_projectile_images("SkeletonWizard", (55, 55))

        self.x = x
        self.y = y

        self.state = "idle"
        self.direction = "down"

        self.frame = 0
        self.frame_count = 0

        self.book_frame = 0
        self.book_frame_count = 0

        self.hp = 9
        self.max_hp = 9

        self.alive = True
        self.dead_done = False

        self.speed = 1
        self.detect_range = 520
        self.attack_range = 360
        self.safe_range = 150

        self.attack_cooldown = 0
        self.shoot_done = False
        self.hurt_time = 0

        self.projectiles = []

    def set_state(self, state):
        if self.state == state:
            return

        self.state = state
        self.frame = 0
        self.frame_count = 0

        if state == "attack":
            self.book_frame = 0
            self.book_frame_count = 0
            self.shoot_done = False

    def get_images(self):
        if self.state == "walk":
            images = self.images["walk"][self.direction]
        else:
            images = self.images["idle"][self.direction]

        if self.frame >= len(images):
            self.frame = 0

        return images

    def play_animation(self, speed):
        images = self.get_images()

        self.frame_count += 1

        if self.frame_count < speed:
            return False

        self.frame_count = 0
        self.frame += 1

        if self.frame < len(images):
            return False

        self.frame = 0
        return True

    def play_book_animation(self, speed):
        images = self.book_images[self.direction]

        self.book_frame_count += 1

        if self.book_frame_count < speed:
            return False

        self.book_frame_count = 0
        self.book_frame += 1

        if self.book_frame < len(images):
            return False

        self.book_frame = len(images) - 1
        return True

    def get_player_distance(self, player):
        player_rect = player.get_rect()
        skeleton_rect = self.get_rect()

        dx = player_rect.centerx - skeleton_rect.centerx
        dy = player_rect.centery - skeleton_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            distance = 1

        return dx, dy, distance

    def face_player(self, dx, dy):
        if abs(dx) > abs(dy):
            if dx < 0:
                self.direction = "left"
            else:
                self.direction = "right"
        else:
            if dy < 0:
                self.direction = "up"
            else:
                self.direction = "down"

    def get_rect(self):
        return pygame.Rect(self.x + 24, self.y + 40, 22, 22)

    def get_hurt_rect(self):
        return pygame.Rect(self.x + 18, self.y + 12, 34, 54)

    def move_and_check_wall(self, move_x, move_y, walls):
        old_x = self.x
        old_y = self.y

        self.x += move_x

        for wall in walls:
            if self.get_rect().colliderect(wall):
                self.x = old_x
                break

        self.y += move_y

        for wall in walls:
            if self.get_rect().colliderect(wall):
                self.y = old_y
                break

    def walk_to_player(self, dx, dy, distance, walls):
        self.set_state("walk")

        move_x = dx / distance * self.speed
        move_y = dy / distance * self.speed

        self.move_and_check_wall(move_x, move_y, walls)
        self.play_animation(8)

    def walk_away_from_player(self, dx, dy, distance, walls):
        self.set_state("walk")

        move_x = -dx / distance * self.speed
        move_y = -dy / distance * self.speed

        self.move_and_check_wall(move_x, move_y, walls)
        self.play_animation(8)

    def start_attack(self):
        self.set_state("attack")
        self.attack_cooldown = 150

    def shoot_projectile(self, player):
        if self.shoot_done:
            return

        if self.book_frame < 4:
            return

        player_rect = player.get_rect()
        skeleton_rect = self.get_rect()

        dx = player_rect.centerx - skeleton_rect.centerx
        dy = player_rect.centery - skeleton_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            distance = 1

        dx = dx / distance
        dy = dy / distance

        sword_x = skeleton_rect.centerx - 25
        sword_y = skeleton_rect.centery - 25

        self.projectiles.append(
            WizardProjectile(sword_x, sword_y, dx, dy, self.projectile_images)
        )

        self.shoot_done = True

    def count_cooldown(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def update_projectiles(self, player, walls):
        for projectile in self.projectiles[:]:
            projectile.move(player, walls)

            if not projectile.active:
                self.projectiles.remove(projectile)

    def hit(self):
        if not self.alive:
            return

        self.hp -= 1

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.dead_done = True
            return

        self.set_state("hurt")
        self.hurt_time = 18

    def move(self, player, walls):
        self.update_projectiles(player, walls)

        if not self.alive:
            return

        self.count_cooldown()

        if self.state == "hurt":
            self.hurt_time -= 1
            self.play_animation(6)

            if self.hurt_time <= 0:
                self.set_state("idle")

            return

        dx, dy, distance = self.get_player_distance(player)
        self.face_player(dx, dy)

        if self.state == "attack":
            self.play_animation(10)
            self.shoot_projectile(player)

            if self.play_book_animation(4):
                self.set_state("idle")

            return

        if distance < self.safe_range:
            self.walk_away_from_player(dx, dy, distance, walls)
            return

        if distance < self.attack_range and self.attack_cooldown <= 0:
            self.start_attack()
            return

        if distance < self.detect_range and distance > self.attack_range - 70:
            self.walk_to_player(dx, dy, distance, walls)
            return

        self.set_state("idle")
        self.play_animation(10)

    def draw_magic(self, screen):
        pass

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
        for projectile in self.projectiles:
            projectile.draw(screen)

        if not self.alive:
            return

        images = self.get_images()
        image = images[self.frame]

        screen.blit(image, (self.x, self.y))

        if self.state == "attack":
            book = self.book_images[self.direction][self.book_frame]

            book_x = self.get_rect().centerx - book.get_width() // 2
            book_y = self.get_rect().centery - book.get_height() // 2

            screen.blit(book, (book_x, book_y))

        self.draw_health_bar(screen)