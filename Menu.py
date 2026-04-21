import pygame
from Character import Player

pygame.init()


class Button(pygame.sprite.Sprite):
    def __init__(self, image_path, Hover_path, pos):
        super().__init__()

        self.Regular_image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(),(266,119))
        self.Hover_path = pygame.transform.scale(pygame.image.load(Hover_path).convert_alpha(),(266,119))

        self.Image_list = [self.Regular_image, self.Hover_path]

        self.image = self.Image_list[0]

        self.rect = self.image.get_rect(topleft=pos)

        self.hovered = False

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def menu():
    Screen1 = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Major 2")

    pygame.mixer.music.load("Musics/Menu.mp3")
    pygame.mixer.music.play(loops=-1)
    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    sound = pygame.mixer.Sound("Musics/Hover.mp3")

    start_button = Button("Graphics/image.png", "Graphics/Hovered_Start.png", (263, 400))
    quit_button = Button("Graphics/image2.png", "Graphics/Hovered_Quit.png", (260, 550))

    regular_buttons = pygame.sprite.Group()
    regular_buttons.add(start_button)
    regular_buttons.add(quit_button)

    Background = pygame.image.load("Graphics/Menu.jpeg").convert()
    Background = pygame.transform.scale(Background, (1280, 720))

    clock = pygame.time.Clock()
    Game_active = True

    while Game_active:
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(mouse_pos):
                    print("Start Game")
                    click.play()
                    character()

                if quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEMOTION:
                for x in regular_buttons.sprites():
                    if x.rect.collidepoint(mouse_pos):
                        x.image = x.Image_list[1]

                        if not x.hovered:
                            sound.play()
                            x.hovered = True
                    else:
                        x.image = x.Image_list[0]
                        x.hovered = False


        Screen1.blit(Background, (0, 0))

        # draw all sprites
        regular_buttons.draw(Screen1)

        pygame.display.update()
        clock.tick(60)

def first_scene():
    Screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Major 2")

    Game_active = True
    clock = pygame.time.Clock()

    while Game_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    Screen.blit(0, 0, 255)
    pygame.display.update()
    clock.tick(60)

def character():
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    player = Player()

    walls = [
        pygame.Rect(200, 150, 120, 180)
    ]

    game_active = True
    while game_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        player.move(keys, walls)

        screen.fill((30, 30, 30))

        for wall in walls:
            pygame.draw.rect(screen, (200, 50, 50), wall)

        player.draw(screen)

        pygame.draw.rect(screen, (0, 255, 0), player.get_rect(), 1)

        pygame.display.flip()
        clock.tick(60)
menu()
