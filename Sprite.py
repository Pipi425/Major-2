import pygame


class SpriteObject:

    def __init__(self, x, y, image_path, size=None):

        self.image = pygame.image.load(image_path).convert_alpha()

        if size:
            self.image = pygame.transform.scale(self.image, size)

        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):

        screen.blit(self.image, self.rect)