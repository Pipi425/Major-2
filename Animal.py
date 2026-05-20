import pygame
import random

class Animal:

    def __init__(self, x, y, folder_type, animal_type, size=(48, 48), speed=1):

        self.type = animal_type

        self.animations = {

            "up": [
                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_u1.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_u2.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_u3.png").convert_alpha(),
                    size
                ),
            ],

            "down": [
                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_d1.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_d2.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_d3.png").convert_alpha(),
                    size
                ),
            ],

            "left": [
                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_l1.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_l2.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_l3.png").convert_alpha(),
                    size
                ),
            ],

            "right": [
                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_r1.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_r2.png").convert_alpha(),
                    size
                ),

                pygame.transform.scale(
                    pygame.image.load(f"Animals/{folder_type}/{animal_type}_r3.png").convert_alpha(),
                    size
                ),
            ]
        }

        self.direction = random.choice(["up", "down", "left", "right"])

        self.image_index = 0
        self.animation_timer = 0
        self.animation_speed = 150

        self.image = self.animations[self.direction][0]

        self.x = x
        self.y = y

        self.speed = speed

        self.moving = False

        self.move_timer = 0
        self.pause_timer = 0

        self.set_new_state()

    def set_new_state(self):

        self.moving = random.choice([True, False])

        if self.moving:

            self.direction = random.choice(
                ["up", "down", "left", "right"]
            )

            self.move_timer = pygame.time.get_ticks() + random.randint(1000, 3000)

        else:

            self.pause_timer = pygame.time.get_ticks() + random.randint(500, 2000)

    def update(self, walls):

        current_time = pygame.time.get_ticks()

        if self.moving:

            dx = 0
            dy = 0

            if self.direction == "up":
                dy = -self.speed

            elif self.direction == "down":
                dy = self.speed

            elif self.direction == "left":
                dx = -self.speed

            elif self.direction == "right":
                dx = self.speed

            future_rect = pygame.Rect(
                self.x + dx,
                self.y + dy,
                self.image.get_width(),
                self.image.get_height()
            )

            collided = False

            for wall in walls:

                if future_rect.colliderect(wall):
                    collided = True
                    break

            if collided:

                self.direction = random.choice(
                    ["up", "down", "left", "right"]
                )

            else:

                self.x += dx
                self.y += dy

            if current_time >= self.move_timer:
                self.set_new_state()

            if current_time - self.animation_timer >= self.animation_speed:

                self.animation_timer = current_time

                self.image_index += 1

                if self.image_index >= 3:
                    self.image_index = 0

        else:

            self.image_index = 1

            if current_time >= self.pause_timer:
                self.set_new_state()

        self.image = self.animations[self.direction][self.image_index]

    def draw(self, screen, walls):

        self.update(walls)

        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):

        return pygame.Rect(
            self.x,
            self.y,
            self.image.get_width(),
            self.image.get_height()
        )