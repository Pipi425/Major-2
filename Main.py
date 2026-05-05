from struct import iter_unpack
from turtle import Screen

import pygame
import random
from Character import Player
import pytmx
from Arrow import Arrow, load_arrow_images
from MeleeWeapon import MeleeWeapon, load_melee_images
from Enemy import Enemy

pygame.init()

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

def menu():
    pygame.mixer.music.stop()
    Screen1 = pygame.display.set_mode((1280, 768))
    pygame.display.set_caption("Major 2")

    pygame.mixer.music.load("Musics/Menu.mp3")
    pygame.mixer.music.play(loops=-1)
    Dragon = pygame.mixer.Sound("SoundEffects/DragonDeep.mp3")
    Dragon.set_volume(0.1)
    Dragon.play()
    ScaryCave = pygame.mixer.Sound("SoundEffects/ScaryCave.mp3")
    ScaryCave.set_volume(0.1)
    ScaryCave.play(loops=-1)
    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)
    sound = pygame.mixer.Sound("Musics/Hover.mp3")
    sound.set_volume(0.2)

    start_button = Button("Graphics/image.png", "Graphics/Hovered_Start.png", (253, 430))
    quit_button = Button("Graphics/image2.png", "Graphics/Hovered_Quit.png", (250, 580))

    regular_buttons = pygame.sprite.Group()
    regular_buttons.add(start_button)
    regular_buttons.add(quit_button)

    Background = pygame.image.load("Graphics/Menu.jpeg").convert()
    Background = pygame.transform.scale(Background, (1280, 768))

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
                    click.play()
                    first_scene()

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
    pygame.mixer.music.stop()

    arrow_cooldown = 1500
    melee_cooldown = 750

    last_arrow_time = 0
    last_melee_time = 0

    enemy = Enemy(1000, 200)
    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)
    sound = pygame.mixer.Sound("Musics/Hover.mp3")
    sound.set_volume(0.2)
    CaveWater = pygame.mixer.Sound("SoundEffects/CaveWater.mp3")
    CaveWater.set_volume(0.4)
    CaveWater.play()
    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)
    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)
    melee_hit = pygame.mixer.Sound("SoundEffects/Melee_slash.mp3")
    melee_hit.set_volume(0.1)
    melee_sounds = []

    for i in range(1, 4):
        sound = pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        sound.set_volume(0.1)
        melee_sounds.append(sound)


    pygame.mixer.music.load("Musics/Cave.mp3")
    pygame.mixer.music.play(loops=-1)

    pygame.display.set_caption("Major 2")
    Screen = pygame.display.set_mode((1280, 768))
    Screen1 = pygame.surface.Surface((1280, 768))
    Screen1.fill((255, 0, 0, 128))

    arrow_images = load_arrow_images()
    arrows = []

    melee_images = load_melee_images()
    melee_weapons = []

    tiled_map = pytmx.load_pygame("Maps/first scene.tmx", pixelalpha=True)
    b1 = pygame.Surface((1280, 768)).convert_alpha()

    MenuButton = Button("Graphics/MenuButton.png", "Graphics/Hovered_MenuButton.png", (20, 680), size = (164, 66))
    regular_buttons = pygame.sprite.Group()
    regular_buttons.add(MenuButton)

    def draw_image_layers(n):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = tiled_map.get_tile_image_by_gid(gid)
                    if tile_image:
                        pixel_x = x * tiled_map.tilewidth
                        pixel_y = y * tiled_map.tileheight
                        n.blit(tile_image, (pixel_x, pixel_y))
        return n

    SF = draw_image_layers(b1)

    player = Player()
    walls = []
    object_layer = tiled_map.get_layer_by_name("collision")

    for obj in object_layer:
        walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))


    Game_active = True
    clock = pygame.time.Clock()

    while Game_active:
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    menu()

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

            if event.type == pygame.KEYDOWN:
                current_time = pygame.time.get_ticks()

                if event.key == pygame.K_e:
                    if current_time - last_arrow_time >= arrow_cooldown:
                        arrow1.play()
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        last_arrow_time = current_time

                if event.key == pygame.K_q:
                    if current_time - last_melee_time >= melee_cooldown:
                        random.choice(melee_sounds).play()
                        x, y = player.get_center()
                        melee_weapons.append(MeleeWeapon(x, y, player.direction, melee_images))
                        last_melee_time = current_time

        keys = pygame.key.get_pressed()
        player.move(keys, walls)
        enemy.move(player, walls)

        for arrow in arrows[:]:
            alive = arrow.update()

            if not alive or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

            elif enemy.alive and arrow.hit_enemy(enemy.get_rect()):
                enemy.hit()
                arrows.remove(arrow)
                arrow_hit.play()

        for weapon in melee_weapons[:]:
            alive = weapon.update()

            if not alive:
                melee_weapons.remove(weapon)

            elif enemy.alive and weapon.hit_enemy(enemy.get_rect()) and not weapon.hit:
                melee_hit.play()
                enemy.hit()
                weapon.hit = True

        if enemy.alive and enemy.get_rect().colliderect(player.get_rect()):
            player.take_hit()

        Screen.blit(SF, (0, 0))

        player.draw(Screen)
        enemy.draw(Screen)

        regular_buttons.draw(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        pygame.display.update()
        clock.tick(60)
menu()