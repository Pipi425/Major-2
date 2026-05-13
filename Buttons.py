import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self, image_path, Hover_path, pos, size = (266, 119)):
        super().__init__()

        self.Regular_image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(),size)
        self.Hover_path = pygame.transform.scale(pygame.image.load(Hover_path).convert_alpha(),size)

        self.Image_list = [self.Regular_image, self.Hover_path]

        self.image = self.Image_list[0]

        self.rect = self.image.get_rect(topleft=pos)

        self.hovered = False

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)