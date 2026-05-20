import pygame
import math


def load_images(path, frame_count):
    sheet = pygame.image.load(path).convert_alpha()

    frames = []

    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()

    for i in range(frame_count):
        frame = sheet.subsurface(
            pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        )

        frame = pygame.transform.scale(frame, (110, 90))

        frames.append(frame)

    return frames


class Boss:
    def __init__(self, x, y):

        #animations
        self.idle = load_images("Bosses/Golem_1_idle.png", 8)
        self.walk = load_images("Bosses/Golem_1_walk.png", 10)
        self.attack = load_images("Bosses/Golem_1_attack.png", 11)
        self.hurt = load_images("Bosses/Golem_1_hurt.png", 4)
        self.die = load_images("Bosses/Golem_1_die.png", 13)

        #position
        self.x = x
        self.y = y

        #animation
        self.frame = 0
        self.animation_count = 0

        #state
        self.state = "idle"

        #hp
        self.hp = 20
        self.alive = True
        self.dead_done = False

        #movement
        self.speed = 1
        self.charge_speed = 5

        #attack
        self.attack_cooldown = 0
        self.attack_delay = 0
        self.charge_time = 0

        self.charge_x = 0
        self.charge_y = 0

        #hurt
        self.hurt_time = 0

    def get_rect(self):
        return pygame.Rect(self.x + 30, self.y + 30, 50, 45)

    def update_animation(self, speed):

        self.animation_count += 1

        if self.animation_count >= speed:

            self.animation_count = 0
            self.frame += 1

            if self.state == "idle":
                images = self.idle

            elif self.state == "walk":
                images = self.walk

            elif self.state == "attack":
                images = self.attack

            elif self.state == "hurt":
                images = self.hurt

            else:
                images = self.die

            if self.frame >= len(images):

                if self.state == "die":
                    self.frame = len(images) - 1
                    self.dead_done = True

                else:
                    self.frame = 0

    def move(self, player, walls):

        if not self.alive:
            self.state = "die"
            self.update_animation(6)
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #hurt animation
        if self.state == "hurt":

            self.hurt_time -= 1

            if self.hurt_time <= 0:
                self.state = "idle"

            self.update_animation(6)
            return

        player_rect = player.get_rect()
        boss_rect = self.get_rect()

        dx = player_rect.centerx - boss_rect.centerx
        dy = player_rect.centery - boss_rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        #attack
        if self.state == "attack":

            self.update_animation(4)

            if self.attack_delay > 0:
                self.attack_delay -= 1
                return

            if self.charge_time > 0:

                move_x = self.charge_x * self.charge_speed
                move_y = self.charge_y * self.charge_speed

                test_rect = self.get_rect().move(move_x, 0)

                blocked = False

                for wall in walls:
                    if test_rect.colliderect(wall):
                        blocked = True

                if not blocked:
                    self.x += move_x

                test_rect = self.get_rect().move(0, move_y)

                blocked = False

                for wall in walls:
                    if test_rect.colliderect(wall):
                        blocked = True

                if not blocked:
                    self.y += move_y

                self.charge_time -= 1
                return

            self.state = "idle"
            self.frame = 0
            return

        #start attack
        if distance < 220 and self.attack_cooldown <= 0:

            self.state = "attack"

            self.frame = 0
            self.animation_count = 0

            self.attack_delay = 40
            self.charge_time = 25
            self.attack_cooldown = 120

            if distance == 0:
                distance = 1

            self.charge_x = dx / distance
            self.charge_y = dy / distance

            return

        #follow player
        if distance < 500:

            self.state = "walk"

            if distance == 0:
                distance = 1

            move_x = dx / distance * self.speed
            move_y = dy / distance * self.speed

            test_rect = self.get_rect().move(move_x, 0)

            blocked = False

            for wall in walls:
                if test_rect.colliderect(wall):
                    blocked = True

            if not blocked:
                self.x += move_x

            test_rect = self.get_rect().move(0, move_y)

            blocked = False

            for wall in walls:
                if test_rect.colliderect(wall):
                    blocked = True

            if not blocked:
                self.y += move_y

            self.update_animation(6)

        else:
            self.state = "idle"
            self.update_animation(8)

    def hit(self):

        if not self.alive:
            return

        self.hp -= 1

        self.state = "hurt"

        self.frame = 0
        self.animation_count = 0

        self.hurt_time = 20

        if self.hp <= 0:

            self.hp = 0

            self.alive = False

            self.state = "die"

            self.frame = 0
            self.animation_count = 0

    def draw_health_bar(self, screen):

        if not self.alive:
            return

        bar_x = self.x
        bar_y = self.y - 15

        width = 100
        height = 10

        current_width = width * (self.hp / 20)

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (bar_x, bar_y, width, height)
        )

        pygame.draw.rect(
            screen,
            (180, 30, 30),
            (bar_x, bar_y, current_width, height)
        )

    def draw(self, screen):

        if self.state == "idle":
            images = self.idle

        elif self.state == "walk":
            images = self.walk

        elif self.state == "attack":
            images = self.attack

        elif self.state == "hurt":
            images = self.hurt

        else:
            images = self.die

        image = images[self.frame]

        screen.blit(image, (self.x, self.y))

        self.draw_health_bar(screen)

