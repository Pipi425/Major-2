import pygame
import math


DIRECTIONS = ["down", "up", "left", "right"]


def load_skeleton_row(sheet, row, frame_count, size):
    images = []

    frame_width = sheet.get_width() // 6
    frame_height = sheet.get_height() // 8

    for i in range(frame_count):
        image = sheet.subsurface(
            pygame.Rect(
                i * frame_width,
                row * frame_height,
                frame_width,
                frame_height
            )
        ).copy()

        image = pygame.transform.scale(image, size)
        images.append(image)

    return images


def load_skeleton_images(path, size):
    sheet = pygame.image.load(path).convert_alpha()

    return {
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
                pygame.Rect(
                    (start + i) * frame_width,
                    0,
                    frame_width,
                    frame_height
                )
            ).copy()

            image = pygame.transform.scale(image, size)
            images[direction].append(image)

    return images


def load_projectile_images(folder, size):
    images = []

    for i in range(20):
        path = folder + "/1_" + str(i).zfill(3) + ".png"
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
        images.append(image)

    return images


def load_sheet_images(path, frame_count, size):
    sheet = pygame.image.load(path).convert_alpha()
    images = []

    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()

    for i in range(frame_count):
        start_x = round(
            i * sheet_width / frame_count
        )

        end_x = round(
            (i + 1) * sheet_width / frame_count
        )

        frame_width = end_x - start_x

        image = sheet.subsurface(
            pygame.Rect(
                start_x,
                0,
                frame_width,
                sheet_height
            )
        ).copy()

        image = pygame.transform.scale(
            image,
            size
        )

        images.append(image)

    return images


def damage_player(player, damage):
    if player.dead:
        return

    player.health -= damage
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


class WizardProjectile:
    def __init__(self, x, y, target_x, target_y, images):
        self.x = x
        self.y = y

        dx = target_x - x
        dy = target_y - y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            distance = 1

        self.move_x = dx / distance
        self.move_y = dy / distance

        angle = -math.degrees(
            math.atan2(
                self.move_y,
                self.move_x
            )
        )

        self.images = []

        for image in images:
            turned_image = pygame.transform.rotate(
                image,
                angle
            )

            self.images.append(turned_image)

        self.frame = 0
        self.frame_count = 0

        self.speed = 4
        self.damage = 2
        self.life = 220
        self.active = True

    def get_rect(self):
        return pygame.Rect(
            int(self.x) - 10,
            int(self.y) - 10,
            20,
            20
        )

    def move(self, player, walls):
        if not self.active:
            return

        self.x += self.move_x * self.speed
        self.y += self.move_y * self.speed

        self.life -= 1

        if self.life <= 0:
            self.active = False
            return

        projectile_rect = self.get_rect()

        for wall in walls:
            if projectile_rect.colliderect(wall):
                self.active = False
                return

        if projectile_rect.colliderect(
            player.get_hurt_rect()
        ):
            damage_player(
                player,
                self.damage
            )

            self.active = False
            return

        self.frame_count += 1

        if self.frame_count >= 5:
            self.frame_count = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.frame = 0

    def draw(self, screen):
        if not self.active:
            return

        image = self.images[self.frame]

        draw_x = int(self.x) - image.get_width() // 2
        draw_y = int(self.y) - image.get_height() // 2

        screen.blit(
            image,
            (draw_x, draw_y)
        )


class WizardMagicCircle:
    def __init__(self, x, y, start_images, idle_images):
        self.x = x
        self.y = y

        self.start_images = start_images
        self.idle_images = idle_images

        self.state = "start"

        self.frame = 0
        self.frame_count = 0

        self.radius = 72

        self.damage = 1
        self.damage_wait = 45
        self.damage_timer = 0

        self.life = 240
        self.active = True

    def get_images(self):
        if self.state == "start":
            return self.start_images

        return self.idle_images

    def player_inside(self, player):
        player_rect = player.get_hurt_rect()

        dx = player_rect.centerx - self.x
        dy = player_rect.centery - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        return distance <= self.radius

    def move(self, player):
        if not self.active:
            return

        self.frame_count += 1

        if self.frame_count >= 3:
            self.frame_count = 0
            self.frame += 1

            if self.state == "start":
                if self.frame >= len(self.start_images):
                    self.state = "idle"
                    self.frame = 0

            else:
                if self.frame >= len(self.idle_images):
                    self.frame = 0

        if self.state != "idle":
            return

        self.life -= 1

        if self.life <= 0:
            self.active = False
            return

        if self.damage_timer > 0:
            self.damage_timer -= 1

        if self.player_inside(player):
            if self.damage_timer <= 0:
                damage_player(
                    player,
                    self.damage
                )

                self.damage_timer = self.damage_wait

    def draw(self, screen):
        if not self.active:
            return

        images = self.get_images()
        image = images[self.frame]

        draw_x = int(self.x) - image.get_width() // 2
        draw_y = int(self.y) - image.get_height() // 2

        screen.blit(
            image,
            (draw_x, draw_y)
        )


class SkeletonWizard:
    def __init__(self, x, y):
        self.images = load_skeleton_images(
            "SkeletonWizard/Skeleton_8-Sheet-NoOutline.png",
            (70, 70)
        )

        self.book_images = load_book_images(
            "SkeletonWizard/Book-Sheet-NoOutline.png",
            (90, 90)
        )

        self.projectile_images = load_projectile_images(
            "SkeletonWizard",
            (48, 48)
        )

        self.magic_start_images = load_sheet_images(
            "SkeletonWizard/Tree_of_Glory-Sheet(1).png",
            31,
            (170, 170)
        )

        self.magic_idle_images = load_sheet_images(
            "SkeletonWizard/tree_of_glory_idle-Sheet(1).png",
            43,
            (170, 170)
        )

        self.x = x
        self.y = y

        self.state = "idle"
        self.direction = "down"

        self.frame = 0
        self.frame_count = 0

        self.book_frame = 0
        self.book_frame_count = 0

        self.hp = 8
        self.max_hp = 8

        self.alive = True
        self.dead_done = False

        self.speed = 1

        self.detect_range = 550
        self.shoot_range = 430
        self.magic_range = 145

        self.shoot_cooldown = 0
        self.magic_cooldown = 0

        self.attack_timer = 0
        self.cast_done = False

        self.target_x = 0
        self.target_y = 0

        self.hurt_time = 0

        self.projectiles = []
        self.magic_circles = []

    def set_state(self, state):
        if self.state == state:
            return

        self.state = state

        self.frame = 0
        self.frame_count = 0

        if state == "shoot_attack":
            self.book_frame = 0
            self.book_frame_count = 0
            self.cast_done = False

        if state == "magic_attack":
            self.book_frame = 0
            self.book_frame_count = 0
            self.cast_done = False

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
            return

        self.frame_count = 0
        self.frame += 1

        if self.frame >= len(images):
            self.frame = 0

    def play_book_animation(self, speed):
        images = self.book_images[self.direction]

        self.book_frame_count += 1

        if self.book_frame_count < speed:
            return

        self.book_frame_count = 0
        self.book_frame += 1

        if self.book_frame >= len(images):
            self.book_frame = len(images) - 1

    def get_player_distance(self, player):
        player_rect = player.get_rect()
        wizard_rect = self.get_rect()

        dx = player_rect.centerx - wizard_rect.centerx
        dy = player_rect.centery - wizard_rect.centery

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
        return pygame.Rect(
            int(self.x) + 24,
            int(self.y) + 40,
            22,
            22
        )

    def get_hurt_rect(self):
        return pygame.Rect(
            int(self.x) + 18,
            int(self.y) + 12,
            34,
            54
        )

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

        self.move_and_check_wall(
            move_x,
            move_y,
            walls
        )

        self.play_animation(8)

    def walk_away_from_player(self, dx, dy, distance, walls):
        self.set_state("walk")

        move_x = -dx / distance * self.speed
        move_y = -dy / distance * self.speed

        self.move_and_check_wall(
            move_x,
            move_y,
            walls
        )

        self.play_animation(8)

    def start_shoot_attack(self, player):
        self.set_state("shoot_attack")

        self.shoot_cooldown = 100
        self.attack_timer = 30

        player_rect = player.get_hurt_rect()

        self.target_x = player_rect.centerx
        self.target_y = player_rect.centery

    def shoot_projectile(self):
        if self.cast_done:
            return

        wizard_rect = self.get_rect()

        projectile = WizardProjectile(
            wizard_rect.centerx,
            wizard_rect.centery,
            self.target_x,
            self.target_y,
            self.projectile_images
        )

        self.projectiles.append(projectile)
        self.cast_done = True

    def start_magic_attack(self):
        self.set_state("magic_attack")

        self.magic_cooldown = 300
        self.attack_timer = 45

    def cast_magic_circle(self):
        if self.cast_done:
            return

        wizard_rect = self.get_rect()

        circle = WizardMagicCircle(
            wizard_rect.centerx,
            wizard_rect.bottom + 5,
            self.magic_start_images,
            self.magic_idle_images
        )

        self.magic_circles.append(circle)
        self.cast_done = True

    def active_magic_circle(self):
        for circle in self.magic_circles:
            if circle.active:
                return True

        return False

    def count_cooldowns(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.magic_cooldown > 0:
            self.magic_cooldown -= 1

    def update_attacks(self, player, walls):
        for projectile in self.projectiles[:]:
            projectile.move(
                player,
                walls
            )

            if not projectile.active:
                self.projectiles.remove(projectile)

        for circle in self.magic_circles[:]:
            circle.move(player)

            if not circle.active:
                self.magic_circles.remove(circle)

    def hit(self, damage):
        if not self.alive:
            return

        self.hp -= damage

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.dead_done = True
            return

        self.set_state("hurt")
        self.hurt_time = 18

    def move(self, player, walls):
        self.update_attacks(
            player,
            walls
        )

        if not self.alive:
            return

        self.count_cooldowns()

        if self.state == "hurt":
            self.hurt_time -= 1
            self.play_animation(6)

            if self.hurt_time <= 0:
                self.set_state("idle")

            return

        dx, dy, distance = self.get_player_distance(player)

        self.face_player(dx, dy)

        if self.state == "shoot_attack":
            self.play_animation(10)
            self.play_book_animation(4)

            self.attack_timer -= 1

            if self.attack_timer <= 15:
                self.shoot_projectile()

            if self.attack_timer <= 0:
                self.set_state("idle")

            return

        if self.state == "magic_attack":
            self.play_animation(10)
            self.play_book_animation(4)

            self.attack_timer -= 1

            if self.attack_timer <= 20:
                self.cast_magic_circle()

            if self.attack_timer <= 0:
                self.set_state("idle")

            return

        if distance <= self.magic_range:
            if self.magic_cooldown <= 0:
                if not self.active_magic_circle():
                    self.start_magic_attack()
                    return

            self.walk_away_from_player(
                dx,
                dy,
                distance,
                walls
            )

            return

        if distance <= self.shoot_range:
            if self.shoot_cooldown <= 0:
                self.start_shoot_attack(player)
                return

            self.set_state("idle")
            self.play_animation(10)
            return

        if distance <= self.detect_range:
            self.walk_to_player(
                dx,
                dy,
                distance,
                walls
            )

            return

        self.set_state("idle")
        self.play_animation(10)

    def draw_magic(self, screen):
        for circle in self.magic_circles:
            circle.draw(screen)

        for projectile in self.projectiles:
            projectile.draw(screen)

    def draw_health_bar(self, screen):
        if not self.alive:
            return

        bar_x = int(self.x) + 8
        bar_y = int(self.y) - 8

        width = 55
        height = 6

        current_width = int(
            width * self.hp / self.max_hp
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (
                bar_x,
                bar_y,
                width,
                height
            )
        )

        pygame.draw.rect(
            screen,
            (180, 30, 30),
            (
                bar_x,
                bar_y,
                current_width,
                height
            )
        )

    def draw(self, screen):
        self.draw_magic(screen)

        if not self.alive:
            return

        images = self.get_images()
        image = images[self.frame]

        screen.blit(
            image,
            (
                int(self.x),
                int(self.y)
            )
        )

        if self.state == "shoot_attack":
            book = self.book_images[
                self.direction
            ][self.book_frame]

            book_x = (
                self.get_rect().centerx
                - book.get_width() // 2
            )

            book_y = (
                self.get_rect().centery
                - book.get_height() // 2
            )

            screen.blit(
                book,
                (
                    book_x,
                    book_y
                )
            )

        if self.state == "magic_attack":
            book = self.book_images[
                self.direction
            ][self.book_frame]

            book_x = (
                self.get_rect().centerx
                - book.get_width() // 2
            )

            book_y = (
                self.get_rect().centery
                - book.get_height() // 2
            )

            screen.blit(
                book,
                (
                    book_x,
                    book_y
                )
            )

        self.draw_health_bar(screen)
