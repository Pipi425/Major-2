import pygame
import random
from Character import Player
import pytmx
from Arrow import Arrow, load_arrow_images
from MeleeWeapon import MeleeWeapon, load_melee_images
from Enemy import Enemy
from Dialogue import DialogueSystem
from NPCs import NPC
from Buttons import Button
from Inventory import Inventory, InventoryUI, Item
from Animal import Animal
from Chest import Chest

pygame.init()

Screen1 = pygame.display.set_mode((1280, 768))
pygame.display.set_caption("Major 2")

icon = pygame.image.load("Graphics/icon.png")
pygame.display.set_icon(icon)

f_icon = pygame.image.load("Graphics/F.png").convert_alpha()
f_icon = pygame.transform.scale(f_icon, (30, 30))

def menu(player):
    pygame.mixer.music.stop()

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
                    player.set_position(297, 389)

                    click.play()

                    return "first_scene"

                if quit_button.is_clicked(mouse_pos):
                    return "quit"

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

        regular_buttons.draw(Screen1)

        pygame.display.update()
        clock.tick(60)

def first_scene(player):
    player.set_position(297, 389)

    pygame.mixer.music.stop()

    arrow_cooldown = 1500
    melee_cooldown = 750
    last_arrow_time = 0
    last_melee_time = 0

    enemies = [
        Enemy(1000, 200),
        Enemy(950, 300),
        Enemy(1100, 250)
    ]

    chest = Chest(800, 384)
    chest.set_loot(Item(
        "Sword",
        "Items/Item01.png",
        "A sharp blade that deal 1 damage per slash"
    ))

    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group()
    regular_buttons.add(MenuButton)

    inventory = Inventory(cols=6, rows=3)
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_hit = pygame.mixer.Sound("SoundEffects/Melee_slash.mp3")
    melee_hit.set_volume(0.1)

    melee_sounds = []
    for i in range(1, 4):
        s = pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        s.set_volume(0.1)
        melee_sounds.append(s)

    ChangeScene = pygame.mixer.Sound("SoundEffects/ChangeScene.mp3")

    CaveWater = pygame.mixer.Sound("SoundEffects/CaveWater.mp3")
    CaveWater.set_volume(0.4)
    CaveWater.play()

    pygame.mixer.music.load("Musics/Cave.mp3")
    pygame.mixer.music.play(-1)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()
    arrows = []
    melee_weapons = []

    tiled_map = pytmx.load_pygame("Maps/first scene.tmx", pixelalpha=True)
    b1 = pygame.Surface((1280, 768)).convert_alpha()

    def draw_map(surf):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    img = tiled_map.get_tile_image_by_gid(gid)
                    if img:
                        surf.blit(img, (x * tiled_map.tilewidth, y * tiled_map.tileheight))
        return surf

    SF = draw_map(b1)

    walls = []
    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    walls.append(chest.hitbox)

    scene_change_rect = pygame.Rect(1210, 40, 60, 60)

    player.weapon = None
    player.armor = None

    chest_looted = False

    fade_surface = pygame.Surface((1280, 768))
    fade_surface.fill((255, 255, 255))
    fade_alpha = 0
    fading = False
    fade_start = 0

    Game_active = True

    while Game_active:

        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        chest_open = chest.state == "opened"
        freeze_world = ui_open or chest_open or fading

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            if event.type == pygame.MOUSEMOTION:

                for x in regular_buttons.sprites():

                    if x.rect.collidepoint(mouse_pos):

                        x.image = x.Image_list[1]

                        if not x.hovered:
                            click.play()
                            x.hovered = True

                    else:
                        x.image = x.Image_list[0]
                        x.hovered = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if event.key == pygame.K_f:
                    if chest.state == "opened":
                        chest.close_ui()

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                if not freeze_world:
                    if event.key == pygame.K_e:
                        if now - last_arrow_time >= arrow_cooldown:
                            x, y = player.get_center()
                            arrows.append(Arrow(x, y, player.direction, arrow_images))
                            arrow1.play()
                            last_arrow_time = now

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= melee_cooldown:
                            x, y = player.get_center()
                            melee_weapons.append(MeleeWeapon(x, y, player.direction, melee_images))
                            random.choice(melee_sounds).play()
                            last_melee_time = now

        if not freeze_world:
            player.move(keys, walls)
            for enemy in enemies:
                enemy.move(player, walls)

        chest.update(player)

        if chest.state == "opened" and not chest_looted:
            if chest.loot_item:
                inventory.add_item(chest.loot_item)
                player.weapon = chest.loot_item
            chest_looted = True

        if not freeze_world:
            for arrow in arrows[:]:
                if not arrow.update() or arrow.off_screen(1280, 768):
                    arrows.remove(arrow)
                    continue

                for enemy in enemies:
                    if enemy.alive and arrow.hit_enemy(enemy.get_rect()):
                        enemy.hit()
                        arrows.remove(arrow)
                        arrow_hit.play()
                        break

            for weapon in melee_weapons[:]:
                if not weapon.update():
                    melee_weapons.remove(weapon)
                    continue

                for enemy in enemies:
                    if enemy.alive and weapon.hit_enemy(enemy):
                        enemy.hit()
                        melee_hit.play()

            for enemy in enemies:
                if enemy.alive and enemy.get_rect().colliderect(player.get_hurt_rect()):
                    player.take_hit()

            if player.health <= 0:
                player.dead = True

            if player.dead:

                white = pygame.Surface(Screen.get_size())
                white.fill((255, 255, 255))

                old_screen = Screen.copy()

                for alpha in range(0, 255, 8):
                    Screen.blit(old_screen, (0, 0))
                    white.set_alpha(alpha)
                    Screen.blit(white, (0, 0))

                    pygame.display.update()
                    clock.tick(60)

                pygame.mixer.music.stop()
                pygame.mixer.stop()

                player.dead = False
                player.health = player.max_health
                return "first_scene"

        Screen.blit(SF, (0, 0))

        chest.draw(Screen)
        player.draw(Screen)

        regular_buttons.draw(Screen)

        for enemy in enemies:
            enemy.draw(Screen)

        player.draw_health_bar(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        if chest.state == "opened":
            chest.draw_loot_ui(Screen)

        if player.get_rect().colliderect(scene_change_rect) and not fading:
            fading = True
            fade_start = now
            ChangeScene.play()
            pygame.mixer.music.fadeout(1000)

        if fading:
            elapsed = now - fade_start
            fade_alpha = min(255, int(elapsed / 2000 * 255))

            fade_surface.set_alpha(fade_alpha)
            Screen.blit(fade_surface, (0, 0))

            if elapsed >= 2000:
                CaveWater.stop()
                return "second_scene"

        pygame.display.update()
        clock.tick(60)

def second_scene(player):
    player.set_position(617, 720)

    pygame.mixer.music.stop()

    arrow_cooldown = 1500
    melee_cooldown = 750

    last_arrow_time = 0
    last_melee_time = 0

    enemies = []

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    sound = pygame.mixer.Sound("Musics/Hover.mp3")
    sound.set_volume(0.2)

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

    pygame.mixer.music.load("Musics/Main World.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)

    pygame.display.set_caption("Major 2")

    Screen = pygame.display.set_mode((1280, 768))

    Screen1 = pygame.surface.Surface((1280, 768))
    Screen1.fill((255, 0, 0, 128))

    arrow_images = load_arrow_images()
    arrows = []

    melee_images = load_melee_images()
    melee_weapons = []

    dialogue = DialogueSystem()

    animals = [
        Animal(100, 10, "Cow", "cow", size=(72,72)),
        Animal(900, 20, "Sheep", "sheep"),
        Animal(300, 30, "Cow", "cow", size=(72,72)),
        Animal(1100, 15, "Sheep", "sheep"),
        Animal(250, 5, "Cow", "cow", size=(72,72)),
        Animal(1000, 20, "Sheep", "sheep"),
        Animal(50, 10, "Cow", "cow", size=(72,72)),
        Animal(1150, 15, "Sheep", "sheep"),

    ]

    tiled_map = pytmx.load_pygame("Maps/untitled.tmx", pixelalpha=True)

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group()
    regular_buttons.add(MenuButton)

    def draw_image_layers(n):

        for layer in tiled_map.visible_layers:

            if isinstance(layer, pytmx.TiledTileLayer):

                for x, y, gid in layer:

                    tile_image = tiled_map.get_tile_image_by_gid(gid)

                    if tile_image:
                        tile_image = pygame.transform.scale(
                            tile_image,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )

                        pixel_x = x * tiled_map.tilewidth * SCALE
                        pixel_y = y * tiled_map.tileheight * SCALE

                        n.blit(tile_image, (pixel_x, pixel_y))

        return n

    SF = draw_image_layers(b1)

    npc = NPC(720, 450)

    walls = []

    walls.append(npc.get_rect())

    object_layer = tiled_map.get_layer_by_name("collision")

    for obj in object_layer:
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

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
                    return "menu"

            if event.type == pygame.MOUSEMOTION:

                for x in regular_buttons.sprites():

                    if x.rect.collidepoint(mouse_pos):

                        x.image = x.Image_list[1]

                        if not x.hovered:
                            click.play()
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

                        arrows.append(
                            Arrow(x, y, player.direction, arrow_images)
                        )

                        last_arrow_time = current_time

                if event.key == pygame.K_q:

                    if current_time - last_melee_time >= melee_cooldown:

                        random.choice(melee_sounds).play()

                        x, y = player.get_center()

                        melee_weapons.append(
                            MeleeWeapon(x, y, player.direction, melee_images)
                        )

                        last_melee_time = current_time

                if event.key == pygame.K_f:

                    if dialogue.active:
                        dialogue.next_line()

                    elif player.get_rect().inflate(40, 40).colliderect(npc.get_rect()):
                        npc.sound[0].play()
                        dialogue.start([
                            "You came out of that cave…?!",
                            "That place is extremely dangerous.",
                            "You shouldn’t go back there again.",
                            "You look exhausted…",
                            "Eldermoor City is just ahead.",
                            "You can rest there for a while."
                        ])

        keys = pygame.key.get_pressed()

        player.move(keys, walls)

        near_npc = player.get_rect().inflate(40, 40).colliderect(npc.get_rect())

        for enemy in enemies:
            enemy.move(player, walls)

        for arrow in arrows[:]:

            alive = arrow.update()

            if not alive or arrow.off_screen(1280, 768):
                arrows.remove(arrow)
                continue

            for enemy in enemies:

                if enemy.alive and arrow.hit_enemy(enemy.get_rect()):

                    enemy.hit()

                    arrows.remove(arrow)

                    arrow_hit.play()

                    break

        for weapon in melee_weapons[:]:

            alive = weapon.update()

            if not alive:
                melee_weapons.remove(weapon)
                continue

            for enemy in enemies:

                if enemy.alive and weapon.hit_enemy(enemy):

                    melee_hit.play()

                    enemy.hit()

        for enemy in enemies:

            if enemy.alive and enemy.get_rect().colliderect(player.get_hurt_rect()):

                player.take_hit()

        Screen.blit(SF, (0, 0))

        dialogue.update()

        npc.draw(Screen)

        for animal in animals:
            animal.draw(Screen, walls)

        if near_npc:
            offset_y = -30 + int(3 * pygame.time.get_ticks() / 300 % 2)
            Screen.blit(f_icon, (npc.x + 8, npc.y + offset_y))

        player.draw(Screen)

        player.draw_health_bar(Screen)

        regular_buttons.draw(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        dialogue.draw(Screen)

        pygame.display.update()

        clock.tick(60)

player = Player(spawn_x=297, spawn_y=389)

current_scene = "menu"

while True:

    if current_scene == "menu":
        current_scene = menu(player)

    elif current_scene == "first_scene":
        current_scene = first_scene(player)

    elif current_scene == "second_scene":
        current_scene = second_scene(player)

    elif current_scene == "quit":
        break

pygame.quit()

