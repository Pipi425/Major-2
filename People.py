import pygame
import random


class People:
    def __init__(self, x, y, skin_name="villager1", dialogue=None):

        # ================= POSITION =================
        self.x = x
        self.y = y
        self.rect_size = 45
        self.speed = 1

        # ================= LOAD SPRITES =================
        self.skin_name = skin_name
        self.load_animations()

        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = pygame.time.get_ticks()
        self.frame_delay = 180

        self.image = self.animations["down"][0]

        # ================= MOVEMENT =================
        self.move_dir = [0, 0]
        self.change_dir_time = pygame.time.get_ticks() + random.randint(1000, 3000)

        # ================= INTERACTION =================
        self.dialogue = dialogue or ["Hello."]
        self.show_f = False

    # =====================================================
    # LOAD ANIMATIONS
    # =====================================================
    def load_animations(self):

        base = f"NPCs/PeopleSet/{self.skin_name}/"

        self.animations = {
            "down": [
                pygame.transform.scale(pygame.image.load(base + "down_0.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "down_1.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "down_2.png").convert_alpha(), (45, 45)),
            ],
            "up": [
                pygame.transform.scale(pygame.image.load(base + "up_0.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "up_1.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "up_2.png").convert_alpha(), (45, 45)),
            ],
            "left": [
                pygame.transform.scale(pygame.image.load(base + "left_0.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "left_1.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "left_2.png").convert_alpha(), (45, 45)),
            ],
            "right": [
                pygame.transform.scale(pygame.image.load(base + "right_0.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "right_1.png").convert_alpha(), (45, 45)),
                pygame.transform.scale(pygame.image.load(base + "right_2.png").convert_alpha(), (45, 45)),
            ],
        }

    # =====================================================
    # RANDOM MOVE
    # =====================================================
    def random_move(self):

        current = pygame.time.get_ticks()

        if current >= self.change_dir_time:

            self.move_dir = random.choice([
                (0, -1),
                (0, 1),
                (-1, 0),
                (1, 0),
                (0, 0)
            ])

            self.change_dir_time = current + random.randint(1000, 2500)

    # =====================================================
    # COLLISION
    # =====================================================
    def check_collision(self, dx, dy, walls):

        rect = self.get_rect().move(dx, dy)

        for w in walls:
            if rect.colliderect(w):
                return True

        return False

    def check_people_collision(self, dx, dy, people_list):

        rect = self.get_rect().move(dx, dy)

        for p in people_list:
            if p is self:
                continue
            if rect.colliderect(p.get_rect()):
                return True

        return False

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, player, walls, people_list):

        self.random_move()

        dx = self.move_dir[0] * self.speed
        dy = self.move_dir[1] * self.speed

        # direction
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        # move
        if not self.check_collision(dx, 0, walls) and not self.check_people_collision(dx, 0, people_list):
            self.x += dx

        if not self.check_collision(0, dy, walls) and not self.check_people_collision(0, dy, people_list):
            self.y += dy

        self.animate()
        self.handle_interaction(player)

    # =====================================================
    # ANIMATION (正常走路)
    # =====================================================
    def animate(self):

        current = pygame.time.get_ticks()

        if current - self.frame_timer > self.frame_delay:
            self.frame_timer = current
            self.frame_index = (self.frame_index + 1) % 3

        self.image = self.animations[self.direction][self.frame_index]

    # =====================================================
    # INTERACTION
    # =====================================================
    def handle_interaction(self, player):

        dist = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        self.show_f = dist < 60

    def interact(self):
        return random.choice(self.dialogue)

    # =====================================================
    # DRAW (F在头顶)
    # =====================================================
    def draw(self, screen, font=None):

        screen.blit(self.image, (self.x, self.y))

        if self.show_f and font:
            text = font.render("F", True, (255, 255, 255))
            screen.blit(text, (self.x + 15, self.y - 20))

    # =====================================================
    # RECT
    # =====================================================
    def get_rect(self):
        return pygame.Rect(self.x, self.y, 45, 45)