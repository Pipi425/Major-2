import pygame
import math

from Inventory import Inventory


class StorageChest:

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            x,
            y,
            64,
            64
        )

        self.inventory = Inventory(
            cols=8,
            rows=6
        )

        self.ui_open = False

        self.f_image = pygame.image.load(
            "Graphics/F.png"
        ).convert_alpha()

        self.f_image = pygame.transform.scale(self.f_image, (32, 32))

    def can_interact(self, player):

        area = self.rect.inflate(
            120,
            120
        )

        return area.colliderect(
            player.get_rect()
        )

    def draw_prompt(self, screen, player):

        if not self.can_interact(player):
            return

        offset = math.sin(
            pygame.time.get_ticks() * 0.01
        ) * 5

        screen.blit(
            self.f_image,
            (
                self.rect.centerx - 45,
                self.rect.top - 45 + offset
            )
        )

    def draw_collision(self, screen):

        pygame.draw.rect(
            screen,
            (255, 0, 255),
            self.rect,
            2
        )