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
from Inventory import Inventory, InventoryUI, Consumable
from Animal import Animal
from Chest import Chest
from Sprite import SpriteObject
from SavePoint import SavePoint
from Boss import Boss
from SkeletonSoldier import SkeletonSoldier
from SkeletonBoxer import SkeletonBoxer
from SkeletonWizard import SkeletonWizard
from SaveSystem import (
    save_game,
    load_game,
    apply_save_data,
    respawn_from_save,
    reset_save_data,
    make_sword,
    make_key,
    make_axe,
    make_bow,
    make_head_1,
    make_chest_1,
    make_legs_1,
    make_hands_1,
    make_head_2,
    make_chest_2,
    make_legs_2,
    make_hands_2,
    make_sword_1
)
from Hint import HintAnimation

pygame.init()

Screen1 = pygame.display.set_mode((1280, 768))
pygame.display.set_caption("Major 2")

icon = pygame.image.load("Graphics/icon.png")
pygame.display.set_icon(icon)

f_icon = pygame.image.load("Graphics/F.png").convert_alpha()
f_icon = pygame.transform.scale(f_icon, (30, 30))

def draw_save_message(screen, text):

    box = pygame.Rect(390, 560, 500, 100)

    pygame.draw.rect(screen, (25, 25, 25), box, border_radius=15)
    pygame.draw.rect(screen, (230, 220, 180), box, 3, border_radius=15)

    font = pygame.font.SysFont(None, 42)

    message = font.render(text, True, (240, 235, 210))

    screen.blit(
        message,
        (
            box.centerx - message.get_width() // 2,
            box.centery - message.get_height() // 2
        )
    )

def menu(player, game_data):
    pygame.mixer.music.stop()
    pygame.mixer.stop()

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

                    save_data = load_game()

                    if save_data is not None:
                        return apply_save_data(player, game_data, save_data)

                    player.set_position(250, 330)
                    player.health = player.max_health
                    player.hp = player.health
                    player.weapon = None

                    game_data["loaded_position"] = False
                    game_data["looted_chests"] = set()
                    game_data["first_boss_dead"] = False
                    game_data["second_boss_dead"] = False

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

def first_scene(player, game_data):
    player.can_attack = True

    if not game_data["loaded_position"]:
        player.set_position(250, 330)
    else:
        game_data["loaded_position"] = False

    pygame.mixer.music.stop()
    pygame.mixer.stop()

    arrow_cooldown = 1500
    last_arrow_time = 0
    last_melee_time = 0

    enemies = [
        Enemy(1000, 200),
        Enemy(950, 300),
        Enemy(1100, 250)
    ]

    chest = Chest(
        816,
        384,
        "cave_chest"
    )

    chest.set_loot(make_sword())

    chest.load_state(game_data)

    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group()
    regular_buttons.add(MenuButton)

    inventory = game_data["inventory"]
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
    pygame.mixer.music.play(-1, fade_ms=2000)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    tiled_map = pytmx.load_pygame(
        "Maps/first scene.tmx",
        pixelalpha=True
    )

    b1 = pygame.Surface((1280, 768)).convert_alpha()

    def draw_map(surf):

        for layer in tiled_map.visible_layers:

            if isinstance(layer, pytmx.TiledTileLayer):

                for x, y, gid in layer:

                    img = tiled_map.get_tile_image_by_gid(gid)

                    if img:
                        surf.blit(
                            img,
                            (
                                x * tiled_map.tilewidth,
                                y * tiled_map.tileheight
                            )
                        )

        return surf

    SF = draw_map(b1)

    walls = []

    ice_rects = []

    for obj in tiled_map.get_layer_by_name("collision"):

        walls.append(
            pygame.Rect(
                obj.x,
                obj.y,
                obj.width,
                obj.height
            )
        )

    walls.append(chest.hitbox)

    scene_change_rect = pygame.Rect(1210, 40, 60, 60)

    save_point = SavePoint("cave_save")

    walls.append(save_point.get_rect())

    save_message_timer = 0
    save_message_text = ""

    fade_surface = pygame.Surface((1280, 768))
    fade_surface.fill((255, 255, 255))

    fade_alpha = 0
    fading = False
    fade_start = 0

    Game_active = True

    while Game_active:

        near_save_point = save_point.is_near(player)

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

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                if event.key == pygame.K_p:

                    if near_save_point:

                        save_game(
                            player,
                            "first_scene",
                            game_data,
                            save_point.save_point_id
                        )

                        save_message_timer = 120
                        save_message_text = "Progress saved."

                if event.key == pygame.K_r:

                    if near_save_point:
                        return reset_save_data(player, game_data)

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

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):

                        if now - last_arrow_time >= arrow_cooldown:

                            x, y = player.get_center()

                            arrows.append(
                                Arrow(
                                    x,
                                    y,
                                    player.direction,
                                    arrow_images
                                )
                            )

                            arrow1.play()

                            last_arrow_time = now
                            player.bow_cooldown = player.bow.cooldown * 0.06
                            player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:

                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

        if not freeze_world:

            player.move(keys, walls, ice_rects)

            for enemy in enemies:
                enemy.move(player, walls)

        chest.update(player)

        if chest.give_loot:

            if chest.loot_item:
                inventory.add_item(chest.loot_item)

            game_data["looted_chests"].add(
                chest.chest_id
            )

            chest.give_loot = False

        if not freeze_world:

            for arrow in arrows[:]:

                if not arrow.update() or arrow.off_screen(1280, 768):

                    arrows.remove(arrow)

                    continue

                for enemy in enemies:

                    if enemy.alive and arrow.hit_enemy(enemy.get_rect()):

                        damage = 1
                        if player.bow:
                            damage = player.bow.damage

                        enemy.hit(damage)

                        arrows.remove(arrow)

                        arrow_hit.play()

                        break

            for weapon in melee_weapons[:]:

                if not weapon.update():

                    melee_weapons.remove(weapon)

                    continue

                for enemy in enemies:

                    if enemy.alive and weapon.hit_enemy(enemy):

                        damage = 1

                        if player.weapon:
                            damage = player.weapon.attack

                        enemy.hit(damage)

                        melee_hit.play()

            for enemy in enemies:

                if enemy.alive and enemy.get_rect().colliderect(
                    player.get_hurt_rect()
                ):
                    player.take_hit(1)

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

                return respawn_from_save(player, game_data)

        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        chest.draw(Screen)

        player.draw(Screen)

        regular_buttons.draw(Screen)

        for enemy in enemies:
            enemy.draw(Screen)

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

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        if fading:

            elapsed = now - fade_start

            fade_alpha = min(
                255,
                int(elapsed / 2000 * 255)
            )

            fade_surface.set_alpha(fade_alpha)

            Screen.blit(fade_surface, (0, 0))

            if elapsed >= 2000:

                CaveWater.stop()

                return "second_scene"

        if save_message_timer > 0:

            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        pygame.display.update()

        clock.tick(60)

def second_scene(player, game_data):
    player.can_attack = False

    if game_data.get("Scene_Back"):
        player.set_position(570, -80)
        game_data["Scene_Back"] = False
    else:
        player.set_position(570, 652)

    pygame.mixer.music.stop()
    pygame.mixer.stop()

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    pygame.mixer.music.load("Musics/Main World.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, fade_ms=2000)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
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

    def draw_image_layers(n):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        n.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return n

    SF = draw_image_layers(b1)

    npc = NPC(720, 450)

    npc_gift_given = game_data.get("npc_gift_given", False)
    npc_gift = game_data.get("npc_gift", False)

    save_point = SavePoint("village_save")

    walls = [
        npc.get_rect(),
        save_point.get_rect()
    ]

    ice_rects = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    fade_surface = pygame.Surface((1280, 768))
    fade_surface.fill((255, 255, 255))

    fading = False
    fade_start = 0

    scene_change_rect = pygame.Rect(0, -10, 1280, 10)

    Game_active = True

    while Game_active:

        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        dialogue_active = dialogue.active
        freeze_world = ui_open or fading or dialogue_active

        near_save_point = save_point.is_near(player)

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

                # ================= SAVE =================
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "second_scene",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ================= INVENTORY =================
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                # F = 使用物品（你新系统）
                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                # ================= COMBAT =================
                if not freeze_world:

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        arrow1.play()
                        last_arrow_time = now
                        player.bow_cooldown = player.bow.cooldown * 0.06
                        player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:
                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

                # ================= DIALOGUE =================
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
                        npc_gift = True

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

        near_npc = player.get_rect().inflate(40, 40).colliderect(npc.get_rect())

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        # ================= RENDER =================
        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        npc.draw(Screen)

        for animal in animals:
            animal.draw(Screen, walls)

        player.draw(Screen)


        regular_buttons.draw(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        dialogue.update()
        dialogue.draw(Screen)

        if near_npc:
            offset_y = -30 + int(3 * pygame.time.get_ticks() / 300 % 2)
            Screen.blit(f_icon, (npc.x + 8, npc.y + offset_y))

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        # ================= SCENE CHANGE =================
        if player.get_rect().colliderect(scene_change_rect):
            return "eldermoor_scene"

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)
            save_message_timer -= 1

        # ================= NPC GIFT =================
        if not dialogue.active and not npc_gift_given and npc_gift:
            apple = Consumable(
                "Apple",
                "Items/Apple.png",
                "An apple that restore 2 health.",
                heal=2
            )

            game_data["inventory"].add_item(apple)

            npc_gift_given = True
            game_data["npc_gift_given"] = True

            save_message_timer = 120
            save_message_text = "Received Apple!"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        pygame.display.update()
        clock.tick(60)

def eldermoor_scene(player, game_data):
    player.can_attack = False

    if game_data.get("Scene_Back"):
        player.set_position(570, 0)
        pygame.mixer.music.load("Musics/Main World.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1, fade_ms=2000)
        game_data["Scene_Back"] = False
    elif game_data["scene"] == "eldermoor_scene":
        pygame.mixer.music.load("Musics/Main World.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1, fade_ms=2000)
        player.set_position(570, 450)
    else:
        player.set_position(570, 650)

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    river = pygame.mixer.Sound("SoundEffects/River.mp3")
    river.set_volume(0.01)
    river.play(-1)

    bird = pygame.mixer.Sound("SoundEffects/Bird.mp3")
    bird.set_volume(0.1)
    bird.play(-1)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/Eldermoor/Eldermoor City.tmx",
        pixelalpha=True
    )

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("eldermoor_save")

    # ================= UI =================
    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    houses = [

        SpriteObject(
            352,
            416,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            736,
            416,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            -32,
            64,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            160,
            64,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            352,
            64,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            736,
            64,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            928,
            64,
            "Graphics/House.png",
            size=(192, 256)
        ),

        SpriteObject(
            1120,
            64,
            "Graphics/House.png",
            size=(192, 256)
        )

    ]

    # ================= COLLISION =================
    walls = [save_point.get_rect()]

    ice_rects = []

    Change_Scene = []

    Change_Scene_1 = []

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        freeze_world = ui_open

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= UI BUTTON =================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "eldermoor_scene",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                # ===== COMBAT =====
                if not freeze_world:

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        arrow1.play()
                        last_arrow_time = now
                        player.bow_cooldown = player.bow.cooldown * 0.06
                        player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:
                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        # ================= RENDER =================
        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        player.draw(Screen)


        for i in houses:
            i.draw(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        regular_buttons.draw(Screen)

        if save_message_timer > 0:

            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.stop()
                pygame.mixer.stop()
                return "IroHouse"

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout()
                game_data["Scene_Back"] = True
                pygame.mixer.stop()
                return "second_scene"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def IroHouse(player, game_data):
    player.can_attack = False

    if game_data.get("House_Out"):
        player.set_position(1046, 220)
        game_data["House_Out"] = False
    elif game_data.get("Scene_Back"):
        player.set_position(570, 0)
        game_data["Scene_Back"] = False
    else:
        player.set_position(570, 650)

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    pygame.mixer.music.load("Musics/Home.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, fade_ms=2000)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrows = []
    melee_weapons = []

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/Home/IroHouse.tmx",
        pixelalpha=True
    )

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("IroHouse_save")

    # ================= UI =================
    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    # ================= COLLISION =================
    walls = [save_point.get_rect()]

    ice_rects = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    Change_Scene = []

    Change_Scene_1 = []

    House = []

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("House"):
        House.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        freeze_world = ui_open

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= UI BUTTON =================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "IroHouse",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        # ================= RENDER =================
        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        player.draw(Screen)


        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        regular_buttons.draw(Screen)

        if save_message_timer > 0:

            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                print("Going to IroHome")
                return "IroHome"

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                game_data["Scene_Back"] = True
                return "eldermoor_scene"

        for rect in House:
            if player.get_rect().colliderect(rect):
                return "InHouse"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)


        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def InHouse(player, game_data):
    player.can_attack = False
    player.set_position(715, 420)

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/Home/InHouse.tmx",
        pixelalpha=True
    )

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= UI =================
    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    # ================= COLLISION =================
    walls = []

    ice_rects = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    Change_Scene = []

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )
    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        freeze_world = ui_open

        keys = pygame.key.get_pressed()

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= UI BUTTON =================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

        # ================= RENDER =================
        Screen.blit(SF, (0, 0))

        player.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        regular_buttons.draw(Screen)

        if save_message_timer > 0:

            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                game_data["House_Out"] = True
                return "IroHouse"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def IroHome(player, game_data):
    player.can_attack = False
    if game_data.get("Scene_Back"):
        player.set_position(570, 384)
        game_data["Scene_Back"] = False
    else:
        player.set_position(570, 653)

    pygame.mixer.music.stop()
    pygame.mixer.stop()

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    pygame.mixer.music.load("Musics/Main World.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, fade_ms=2000)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/Home/IroHome.tmx",
        pixelalpha=True
    )

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("IroHome_save")

    # ================= UI =================
    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    # ================= COLLISION =================
    walls = [save_point.get_rect()]

    ice_rects = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    Change_Scene = []

    Change_Scene_1 = []

    Change_Scene_2 = []

    Change_Scene_3 = []

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene_2"):
        Change_Scene_2.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene_3"):
        Change_Scene_3.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )
    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        freeze_world = ui_open

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= UI BUTTON =================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "IroHouse",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

        # ================= RENDER =================
        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        player.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        regular_buttons.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                game_data["Scene_Back"] = True
                return "IroHouse"

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                return "SnowVillage"

        for rect in Change_Scene_2:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                return "DesertVillage"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def SnowVillage(player, game_data):
    # ================= INIT =================
    player.can_attack = False
    if game_data.get("Scene_Back"):
        player.set_position(-50, 350)
        game_data["Scene_Back"] = False
    else:
        player.set_position(1200, 220)

    pygame.mixer.music.stop()

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    pygame.mixer.music.load("Musics/Snowy.mp3")
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1, fade_ms=2000)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/First Boss/SnowVillage.tmx",
        pixelalpha=True
    )

    SCALE = 1

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("SnowVillage_save")

    # ================= UI =================
    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    # ================= COLLISION =================
    walls = [save_point.get_rect()]

    ice_rects = []

    Change_Scene = []

    Change_Scene_1 = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Ice"):
        ice_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        freeze_world = ui_open

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= UI BUTTON =================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "SnowVillage",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        player.draw(Screen)


        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        regular_buttons.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                if game_data["MazeSolved"]:
                    return "Maze_Solved"
                else:
                    return "Maze"

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                game_data["Scene_Back"] = True
                return "IroHome"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        pygame.display.update()
        clock.tick(60)

    pygame.mixer.music.stop()
    pygame.mixer.stop()

def Maze(player, game_data):
    # ================= INIT =================
    player.can_attack = True

    if game_data["scene"] == "Maze":
        pygame.mixer.music.load("Musics/Snowy.mp3")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1, fade_ms=2000)
        player.set_position(90, 440)
    else:
        player.set_position(1200, 350)

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    skeletons = []

    skeletons.append(SkeletonSoldier(544, 192))
    skeletons.append(SkeletonSoldier(832, 192))
    skeletons.append(SkeletonSoldier(544, 416))
    skeletons.append(SkeletonSoldier(832, 416))
    skeletons.append(SkeletonSoldier(544, 640))
    skeletons.append(SkeletonSoldier(832, 640))

    chest = Chest(
        1008,
        176,
        "maze_chest"
    )

    chest.set_loot(make_key())

    chest.load_state(game_data)

    chest1 = Chest(
        1168,
        656,
        "maze_chest_1"
    )

    chest1.set_loot(make_axe())

    chest1.load_state(game_data)

    chest2 = Chest(
        400,
        656,
        "maze_chest_2"
    )

    chest2.set_loot(make_head_1())

    chest2.load_state(game_data)

    chest3 = Chest(
        144,
        96,
        "maze_chest_3"
    )

    chest3.set_loot(make_hands_1())

    chest3.load_state(game_data)

    chest4 = Chest(
        1232,
        16,
        "maze_chest_4"
    )

    chest4.set_loot(make_legs_1())

    chest4.load_state(game_data)

    hint = HintAnimation(
        x=1002,
        y=130
    )

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/First Boss/Maze.tmx",
        pixelalpha=True
    )

    SCALE = 1

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("Maze_save")

    # ================= COLLISION =================
    walls = [save_point.get_rect()]

    walls.append(chest.hitbox)
    walls.append(chest1.hitbox)
    walls.append(chest2.hitbox)
    walls.append(chest3.hitbox)
    walls.append(chest4.hitbox)

    ice_rects = []

    Change_Scene = []

    save_message_timer = 0
    save_message_text = ""

    fade_surface = pygame.Surface((1280, 768))
    fade_surface.fill((255, 255, 255))

    fade_alpha = 0
    fading = False
    fade_start = 0

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Ice"):
        ice_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        chest_open = (
                chest.state == "opened"
                or
                chest1.state == "opened"
                or
                chest2.state == "opened"
                or
                chest3.state == "opened"
                or
                chest4.state == "opened"
        )

        freeze_world = ui_open or chest_open or fading

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                if event.key == pygame.K_f:

                    if chest.state == "opened":
                        chest.close_ui()

                        fading = True
                        fade_start = now

                        game_data["MazeSolved"] = True

                        pygame.mixer.music.fadeout(2000)

                    if chest1.state == "opened":
                        chest1.close_ui()
                    if chest2.state == "opened":
                        chest2.close_ui()
                    if chest3.state == "opened":
                        chest3.close_ui()
                    if chest4.state == "opened":
                        chest4.close_ui()

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "Maze",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                # ===== COMBAT =====
                if not freeze_world:

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        arrow1.play()
                        last_arrow_time = now
                        player.bow_cooldown = player.bow.cooldown * 0.06
                        player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:
                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)
            chest.update(player)
            chest1.update(player)
            chest2.update(player)
            chest3.update(player)
            chest4.update(player)

            for sk in skeletons:
                sk.move(player, walls)

                for weapon in melee_weapons:

                    for skeleton in skeletons:
                        for arrow in skeleton.arrows[:]:

                            if weapon.attack_rect.colliderect(arrow.get_rect()):
                                arrow.active = False
                                skeleton.arrows.remove(arrow)

                    if weapon.hit_enemy(sk) and sk.alive:

                        damage = 0

                        if player.weapon:
                            damage = player.weapon.attack

                        sk.hit(damage)

                for arrow in arrows:

                    if sk.alive and arrow.hit_enemy(sk.get_rect()):

                        damage = 0

                        if player.bow:
                            damage = player.bow.damage

                        sk.hit(damage)

                        arrows.remove(arrow)

                        arrow_hit.play()

                        break

        if chest.give_loot:

            if chest.loot_item:
                inventory.add_item(chest.loot_item)

            game_data["looted_chests"].add(
                chest.chest_id
            )

            chest.give_loot = False

        if chest1.give_loot:

            if chest1.loot_item:
                inventory.add_item(chest1.loot_item)

            game_data["looted_chests"].add(
                chest1.chest_id
            )

            chest1.give_loot = False

        if chest2.give_loot:

            if chest2.loot_item:
                inventory.add_item(chest2.loot_item)

            game_data["looted_chests"].add(
                chest2.chest_id
            )

            chest2.give_loot = False

        if chest3.give_loot:

            if chest3.loot_item:
                inventory.add_item(chest3.loot_item)

            game_data["looted_chests"].add(
                chest3.chest_id
            )

            chest3.give_loot = False

        if chest4.give_loot:

            if chest4.loot_item:
                inventory.add_item(chest4.loot_item)

            game_data["looted_chests"].add(
                chest4.chest_id
            )

            chest4.give_loot = False

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        hint.update()
        hint.draw(Screen)

        chest.draw(Screen)
        chest1.draw(Screen)
        chest2.draw(Screen)
        chest3.draw(Screen)
        chest4.draw(Screen)

        for sk in skeletons:
            sk.draw(Screen)

        player.draw(Screen)

        if chest.state == "opened":
            chest.draw_loot_ui(Screen)

        if chest1.state == "opened":
            chest1.draw_loot_ui(Screen)

        if chest2.state == "opened":
            chest2.draw_loot_ui(Screen)

        if chest3.state == "opened":
            chest3.draw_loot_ui(Screen)

        if chest4.state == "opened":
            chest4.draw_loot_ui(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.stop()
                game_data["Scene_Back"] = True
                return "SnowVillage"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        if fading:

            elapsed = now - fade_start

            fade_alpha = min(
                255,
                int(elapsed / 2000 * 255)
            )

            fade_surface.set_alpha(fade_alpha)

            Screen.blit(fade_surface, (0, 0))

            if elapsed >= 2000:
                pygame.mixer.music.stop()
                game_data["Maze_Solved"] = True

                return "Maze_Solved"

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

            return respawn_from_save(player, game_data)

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def Maze_Solved(player, game_data):
    # ================= INIT =================
    player.can_attack = True

    if game_data["scene"] == "Maze_Solved":
        pygame.mixer.music.load("Musics/Snowy.mp3")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1, fade_ms=2000)
        player.set_position(90, 440)
    elif game_data["MazeSolved"]:
        pygame.mixer.music.load("Musics/Snowy.mp3")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1, fade_ms=2000)
        player.set_position(90, 440)
    elif game_data["Scene_Back"]:
        player.set_position(-50, 350)
        game_data["Scene_Back"] = False
    else:
        player.set_position(1200, 350)

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    skeletons = []

    skeletons.append(SkeletonSoldier(544, 192))
    skeletons.append(SkeletonSoldier(832, 192))
    skeletons.append(SkeletonSoldier(544, 416))
    skeletons.append(SkeletonSoldier(832, 416))
    skeletons.append(SkeletonSoldier(544, 640))
    skeletons.append(SkeletonSoldier(832, 640))

    chest = Chest(
        1008,
        176,
        "maze_chest"
    )

    chest.set_loot(make_key())

    chest.load_state(game_data)

    chest1 = Chest(
        1168,
        656,
        "maze_chest_1"
    )

    chest1.set_loot(make_axe())

    chest1.load_state(game_data)

    chest2 = Chest(
        400,
        656,
        "maze_chest_2"
    )

    chest2.set_loot(make_head_1())

    chest2.load_state(game_data)

    chest3 = Chest(
        144,
        96,
        "maze_chest_3"
    )

    chest3.set_loot(make_hands_1())

    chest3.load_state(game_data)

    chest4 = Chest(
        1232,
        16,
        "maze_chest_4"
    )

    chest4.set_loot(make_legs_1())

    chest4.load_state(game_data)

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/First Boss/Maze_Soved.tmx",
        pixelalpha=True
    )

    SCALE = 1

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("MazeSolved_save")

    # ================= COLLISION =================
    walls = [save_point.get_rect()]

    walls.append(chest.hitbox)
    walls.append(chest1.hitbox)
    walls.append(chest2.hitbox)
    walls.append(chest3.hitbox)
    walls.append(chest4.hitbox)


    ice_rects = []

    Change_Scene = []

    Change_Scene_1 = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Ice"):
        ice_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        chest_open = (
                chest.state == "opened"
                or
                chest1.state == "opened"
                or
                chest2.state == "opened"
                or
                chest3.state == "opened"
                or
                chest4.state == "opened"
        )

        freeze_world = ui_open or chest_open

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                if event.key == pygame.K_f:

                    if chest.state == "opened":
                        chest.close_ui()
                    if chest1.state == "opened":
                        chest1.close_ui()
                    if chest2.state == "opened":
                        chest2.close_ui()
                    if chest3.state == "opened":
                        chest3.close_ui()
                    if chest4.state == "opened":
                        chest4.close_ui()

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "Maze_Solved",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                # ===== COMBAT =====
                if not freeze_world:

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        arrow1.play()
                        last_arrow_time = now
                        player.bow_cooldown = player.bow.cooldown * 0.06
                        player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:
                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)
            chest.update(player)
            chest1.update(player)
            chest2.update(player)
            chest3.update(player)
            chest4.update(player)

            for sk in skeletons:
                sk.move(player, walls)

                for weapon in melee_weapons:

                    for skeleton in skeletons:
                        for arrow in skeleton.arrows[:]:

                            if weapon.attack_rect.colliderect(arrow.get_rect()):
                                arrow.active = False
                                skeleton.arrows.remove(arrow)

                    if weapon.hit_enemy(sk) and sk.alive:

                        damage = 0

                        if player.weapon:
                            damage = player.weapon.attack

                        sk.hit(damage)

                for arrow in arrows:

                    if sk.alive and arrow.hit_enemy(sk.get_rect()):

                        damage = 0

                        if player.bow:
                            damage = player.bow.damage

                        sk.hit(damage)

                        arrows.remove(arrow)

                        arrow_hit.play()

                        break



        if chest.give_loot:

            if chest.loot_item:
                inventory.add_item(chest.loot_item)

            game_data["looted_chests"].add(
                chest.chest_id
            )

            chest.give_loot = False

        if chest1.give_loot:

            if chest1.loot_item:
                inventory.add_item(chest1.loot_item)

            game_data["looted_chests"].add(
                chest1.chest_id
            )

            chest1.give_loot = False

        if chest2.give_loot:

            if chest2.loot_item:
                inventory.add_item(chest2.loot_item)

            game_data["looted_chests"].add(
                chest2.chest_id
            )

            chest2.give_loot = False

        if chest3.give_loot:

            if chest3.loot_item:
                inventory.add_item(chest3.loot_item)

            game_data["looted_chests"].add(
                chest3.chest_id
            )

            chest3.give_loot = False

        if chest4.give_loot:

            if chest4.loot_item:
                inventory.add_item(chest4.loot_item)

            game_data["looted_chests"].add(
                chest4.chest_id
            )

            chest4.give_loot = False


        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        Screen.blit(SF, (0, 0))

        save_point.draw(Screen, near_save_point)

        for sk in skeletons:
            sk.draw(Screen)

        player.draw(Screen)

        chest.draw(Screen)
        chest1.draw(Screen)
        chest2.draw(Screen)
        chest3.draw(Screen)
        chest4.draw(Screen)

        if chest.state == "opened":
            chest.draw_loot_ui(Screen)

        if chest1.state == "opened":
            chest1.draw_loot_ui(Screen)

        if chest2.state == "opened":
            chest2.draw_loot_ui(Screen)

        if chest3.state == "opened":
            chest3.draw_loot_ui(Screen)

        if chest4.state == "opened":
            chest4.draw_loot_ui(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.stop()
                game_data["Scene_Back"] = True
                return "SnowVillage"

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                if not game_data["Boss1"]:
                    pygame.mixer.music.stop()
                game_data["Scene_Back"] = True
                return "First_Boss"

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

            return respawn_from_save(player, game_data)

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def First_Boss(player, game_data):
    # ================= INIT =================
    player.can_attack = True
    player.set_position(1200, 350)

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    if not game_data["Boss1"]:
        pygame.mixer.music.load("Musics/FirstBoss.mp3")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)

    chest = None

    if game_data["Boss1"]:
        chest = Chest(
            304,
            368,
            "boss1_chest"
        )

        chest.set_loot(make_bow())
        chest.load_state(game_data)


    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    boss = Boss(400, 200)

    boss_leave_warning = False

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/First Boss/Boss.tmx",
        pixelalpha=True
    )

    SCALE = 1

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= COLLISION =================
    walls = []

    if chest:
        walls.append(chest.hitbox)

    ice_rects = []

    Change_Scene = []

    fading = False
    fade_start = 0

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Ice"):
        ice_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open

        if chest:
            chest_open = chest.state == "opened"
            freeze_world = ui_open or boss_leave_warning or chest_open
        else:
            freeze_world = ui_open or boss_leave_warning

        keys = pygame.key.get_pressed()

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if boss_leave_warning:

                    if event.key == pygame.K_y:
                        pygame.mixer.music.fadeout(1000)
                        return "Maze_Solved"

                    elif event.key == pygame.K_n:
                        boss_leave_warning = False
                        player.x -= 50

                    continue

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                if chest:
                    if event.key == pygame.K_f:
                        if chest.state == "opened":
                            chest.close_ui()

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                # ===== COMBAT =====
                if not freeze_world:

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        arrow1.play()
                        last_arrow_time = now
                        player.bow_cooldown = player.bow.cooldown * 0.06
                        player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:
                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

        # ================= UPDATE =================


        for weapon in melee_weapons:

            if weapon.hit_enemy(boss) and boss.alive and not game_data["Boss1"]:

                damage = 0

                if player.weapon:
                    damage = player.weapon.attack

                boss.hit(damage)

        for arrow in arrows:

            if boss.alive and arrow.hit_enemy(boss.get_rect()) and not game_data["Boss1"]:

                damage = 0

                if player.bow:
                    damage = player.bow.damage

                boss.hit(damage)

                arrows.remove(arrow)

                arrow_hit.play()

                break


        if not freeze_world:
            player.move(keys, walls, ice_rects)

            if chest:
                chest.update(player)

            if not game_data["Boss1"]:
                boss.move(player, walls)

            if boss.alive and not game_data["Boss1"]:
                if boss.get_rect().colliderect(player.get_hurt_rect()):
                    player.take_hit(boss.damage)

        if chest:
            if chest.give_loot:

                if chest.loot_item:
                    inventory.add_item(chest.loot_item)

                game_data["looted_chests"].add(
                    chest.chest_id
                )

                chest.give_loot = False

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        Screen.blit(SF, (0, 0))

        if chest:
            chest.draw(Screen)

        player.draw(Screen)

        if chest:
            if chest.state == "opened":
                chest.draw_loot_ui(Screen)

        if not game_data["Boss1"]:
            boss.draw(Screen)

        if boss.dead_done and not fading:
            fading = True
            fade_start = pygame.time.get_ticks()

            # 所有声音淡出
            pygame.mixer.music.fadeout(1500)

            game_data["Boss1"] = True

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:

            if player.get_rect().colliderect(rect):

                if not game_data["Boss1"]:

                    boss_leave_warning = True
                else:

                    pygame.mixer.music.fadeout(1000)
                    return "Maze_Solved"

        if boss_leave_warning:
            panel = pygame.Rect(240, 250, 800, 200)

            pygame.draw.rect(Screen, (20, 20, 20), panel, border_radius=12)
            pygame.draw.rect(Screen, (255, 255, 255), panel, 2, border_radius=12)

            font = pygame.font.SysFont(None, 42)

            text1 = font.render(
                "You have not defeated the boss.",
                True,
                (255, 255, 255)
            )

            text2 = font.render(
                "Are you sure you want to leave?",
                True,
                (255, 255, 255)
            )

            text3 = font.render(
                "[Y] Yes    [N] No",
                True,
                (255, 255, 0)
            )

            Screen.blit(
                text1,
                (panel.centerx - text1.get_width() // 2, panel.y + 40)
            )

            Screen.blit(
                text2,
                (panel.centerx - text2.get_width() // 2, panel.y + 90)
            )

            Screen.blit(
                text3,
                (panel.centerx - text3.get_width() // 2, panel.y + 145)
            )

        if player.health <= 0:
            player.dead = True

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

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

            return respawn_from_save(player, game_data)

        if fading:
            elapsed = pygame.time.get_ticks() - fade_start

            if elapsed >= 3000:
                return "First_Boss"

            alpha = min(
                255,
                int(elapsed / 3000 * 255)
            )

            fade_surface = pygame.Surface(
                (Screen.get_width(), Screen.get_height())
            )

            fade_surface.fill((255, 255, 255))

            fade_surface.set_alpha(alpha)

            Screen.blit(fade_surface, (0, 0))

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

def DesertVillage(player, game_data):
    # ================= INIT =================
    player.can_attack = False
    if game_data.get("Scene_Back"):
        player.set_position(778, -40)
        game_data["Scene_Back"] = False
    else:
        player.set_position(-40, 362)

    pygame.mixer.music.stop()

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    pygame.mixer.music.load("Musics/DesertVillage.mp3")
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1, fade_ms=2000)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/Second Boss/DesertVillage.tmx",
        pixelalpha=True
    )

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= SAVE POINT =================
    save_point = SavePoint("DesertVillage_save")

    chest = Chest(
        96,
        544,
        "desert_chest_1"
    )

    chest.set_loot(make_bow())
    chest.load_state(game_data)

    # ================= UI =================
    MenuButton = Button(
        "Graphics/MenuButton.png",
        "Graphics/Hovered_MenuButton.png",
        (20, 680),
        size=(164, 66)
    )

    regular_buttons = pygame.sprite.Group(MenuButton)

    # ================= COLLISION =================
    walls = [
        save_point.get_rect(),
        chest.hitbox
    ]

    Spikes = []

    ice_rects = []

    Change_Scene = []

    Change_Scene_1 = []

    save_message_timer = 0
    save_message_text = ""

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Spike"):
        Spikes.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(pygame.Rect(obj.x * SCALE, obj.y * SCALE, obj.width * SCALE, obj.height * SCALE))

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(pygame.Rect(obj.x * SCALE, obj.y * SCALE, obj.width * SCALE, obj.height * SCALE))

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        freeze_world = ui_open

        keys = pygame.key.get_pressed()

        near_save_point = save_point.is_near(player)

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= UI BUTTON =================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MenuButton.is_clicked(mouse_pos):
                    click.play()
                    return "menu"

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    if chest.state == "opened":
                        chest.close_ui()

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                # ===== SAVE SYSTEM =====
                if event.key == pygame.K_p and near_save_point:
                    save_game(
                        player,
                        "DesertVillage",
                        game_data,
                        save_point.save_point_id
                    )
                    save_message_timer = 120
                    save_message_text = "Progress saved."

                if event.key == pygame.K_r and near_save_point:
                    return reset_save_data(player, game_data)

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)

            chest.update(player)

            for rect in Spikes:
                if player.get_rect().colliderect(rect):
                    player.take_hit(1)

        if chest.give_loot:

            if chest.loot_item:
                inventory.add_item(chest.loot_item)

            game_data["looted_chests"].add(
                chest.chest_id
            )

            chest.give_loot = False

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        Screen.blit(SF, (0, 0))

        chest.draw(Screen)

        save_point.draw(Screen, near_save_point)

        player.draw(Screen)

        if chest.state == "opened":
            chest.draw_loot_ui(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        regular_buttons.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                    return "DesertMaze"

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.fadeout(1000)
                game_data["Scene_Back"] = True
                return "IroHome"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

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

            return respawn_from_save(player, game_data)


        pygame.display.update()
        clock.tick(60)

    pygame.mixer.music.stop()
    pygame.mixer.stop()

def DesertMaze(player, game_data):
    # ================= INIT =================
    player.can_attack = True

    if game_data["Scene_Back"]:
        player.set_position(992, -32)
        game_data["Scene_Back"] = False
    else:
        player.set_position(778, 660)

    last_arrow_time = 0
    last_melee_time = 0

    inventory = game_data["inventory"]
    inventory_ui = InventoryUI(inventory, player)

    click = pygame.mixer.Sound("Musics/Hover2.mp3")
    click.set_volume(0.2)

    arrow1 = pygame.mixer.Sound("SoundEffects/Arrow1.mp3")
    arrow1.set_volume(0.05)

    arrow_hit = pygame.mixer.Sound("SoundEffects/Arrow_hit.mp3")
    arrow_hit.set_volume(0.05)

    melee_sounds = [
        pygame.mixer.Sound(f"SoundEffects/Melee{i}.mp3")
        for i in range(1, 4)
    ]
    for s in melee_sounds:
        s.set_volume(0.1)

    Screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    arrow_images = load_arrow_images()
    melee_images = load_melee_images()

    arrows = []
    melee_weapons = []

    skeletons = []

    """skeletons.append(SkeletonSoldier(544, 192))
    skeletons.append(SkeletonSoldier(832, 192))
    skeletons.append(SkeletonSoldier(544, 416))
    skeletons.append(SkeletonSoldier(832, 416))
    skeletons.append(SkeletonSoldier(544, 640))
    skeletons.append(SkeletonSoldier(832, 640))"""

    chest = Chest(
        0,
        0,
        "desert_maze_chest"
    )

    chest.set_loot(make_chest_2())

    chest.load_state(game_data)

    chest1 = Chest(
        928,
        576,
        "desert_maze_chest_1"
    )

    chest1.set_loot(make_hands_2())

    chest1.load_state(game_data)

    chest2 = Chest(
        1248,
        288,
        "desert_maze_chest_2"
    )

    chest2.set_loot(make_head_2())

    chest2.load_state(game_data)

    chest3 = Chest(
        0,
        736,
        "desert_maze_chest_3"
    )

    chest3.set_loot(make_legs_2())

    chest3.load_state(game_data)

    chest4 = Chest(
        992,
        256,
        "maze_chest_4"
    )

    chest4.set_loot(make_sword_1())

    chest4.load_state(game_data)

    # ================= MAP =================
    tiled_map = pytmx.load_pygame(
        "Maps/Second Boss/DesertMaze.tmx",
        pixelalpha=True
    )

    SCALE = 2

    b1 = pygame.Surface(
        (
            tiled_map.width * tiled_map.tilewidth * SCALE,
            tiled_map.height * tiled_map.tileheight * SCALE
        )
    ).convert_alpha()

    def draw_map(surface):
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        tile = pygame.transform.scale(
                            tile,
                            (
                                tiled_map.tilewidth * SCALE,
                                tiled_map.tileheight * SCALE
                            )
                        )
                        surface.blit(tile, (
                            x * tiled_map.tilewidth * SCALE,
                            y * tiled_map.tileheight * SCALE
                        ))
        return surface

    SF = draw_map(b1)

    # ================= COLLISION =================
    walls = []

    walls.append(chest.hitbox)
    walls.append(chest1.hitbox)
    walls.append(chest2.hitbox)
    walls.append(chest3.hitbox)
    walls.append(chest4.hitbox)

    ice_rects = []

    Change_Scene = []

    Change_Scene_1 = []

    save_message_timer = 0
    save_message_text = ""

    fade_surface = pygame.Surface((1280, 768))
    fade_surface.fill((255, 255, 255))

    fade_alpha = 0
    fading = False
    fade_start = 0

    for obj in tiled_map.get_layer_by_name("collision"):
        walls.append(
            pygame.Rect(
                obj.x * SCALE,
                obj.y * SCALE,
                obj.width * SCALE,
                obj.height * SCALE
            )
        )

    for obj in tiled_map.get_layer_by_name("Change_Scene"):
        Change_Scene.append(pygame.Rect(obj.x * SCALE, obj.y * SCALE, obj.width * SCALE, obj.height * SCALE))

    for obj in tiled_map.get_layer_by_name("Change_Scene_1"):
        Change_Scene_1.append(pygame.Rect(obj.x * SCALE, obj.y * SCALE, obj.width * SCALE, obj.height * SCALE))

    # ================= GAME LOOP =================
    Game_active = True

    while Game_active:

        # ================= STATE =================
        now = pygame.time.get_ticks()

        ui_open = inventory_ui.open
        chest_open = (
                chest.state == "opened"
                or
                chest1.state == "opened"
                or
                chest2.state == "opened"
                or
                chest3.state == "opened"
                or
                chest4.state == "opened"
        )

        freeze_world = ui_open or chest_open or fading

        keys = pygame.key.get_pressed()

        # ================= EVENTS =================
        for event in pygame.event.get():

            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # ================= KEY INPUT =================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f and inventory_ui.open:
                    inventory_ui.handle_use(player, game_data["inventory"])

                if event.key == pygame.K_f:

                    if chest.state == "opened":
                        chest.close_ui()
                    if chest1.state == "opened":
                        chest1.close_ui()
                    if chest2.state == "opened":
                        chest2.close_ui()
                    if chest3.state == "opened":
                        chest3.close_ui()
                    if chest4.state == "opened":
                        chest4.close_ui()

                # ===== INVENTORY =====
                if event.key == pygame.K_i:
                    inventory_ui.open = not inventory_ui.open

                if inventory_ui.open:
                    if event.key == pygame.K_LEFT:
                        inventory_ui.move_cursor(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        inventory_ui.move_cursor(1, 0)
                    if event.key == pygame.K_UP:
                        inventory_ui.move_cursor(0, -1)
                    if event.key == pygame.K_DOWN:
                        inventory_ui.move_cursor(0, 1)

                # ===== COMBAT =====
                if not freeze_world:

                    if (
                            event.key == pygame.K_e
                            and player.bow
                            and now - last_arrow_time > player.bow.cooldown
                    ):
                        x, y = player.get_center()
                        arrows.append(Arrow(x, y, player.direction, arrow_images))
                        arrow1.play()
                        last_arrow_time = now
                        player.bow_cooldown = player.bow.cooldown * 0.06
                        player.max_bow_cooldown = player.bow.cooldown

                    if event.key == pygame.K_q:

                        if player.weapon is None:
                            continue

                        if now - last_melee_time >= player.weapon.cooldown:
                            x, y = player.get_center()

                            melee_weapons.append(
                                MeleeWeapon(
                                    x,
                                    y,
                                    player.direction,
                                    melee_images
                                )
                            )

                            random.choice(melee_sounds).play()

                            last_melee_time = now

        # ================= UPDATE =================
        if not freeze_world:
            player.move(keys, walls, ice_rects)
            chest.update(player)
            chest1.update(player)
            chest2.update(player)
            chest3.update(player)
            chest4.update(player)

            for sk in skeletons:
                sk.move(player, walls)

                for weapon in melee_weapons:

                    for skeleton in skeletons:
                        for arrow in skeleton.arrows[:]:

                            if weapon.attack_rect.colliderect(arrow.get_rect()):
                                arrow.active = False
                                skeleton.arrows.remove(arrow)

                    if weapon.hit_enemy(sk) and sk.alive:

                        damage = 0

                        if player.weapon:
                            damage = player.weapon.attack

                        sk.hit(damage)

                for arrow in arrows:

                    if sk.alive and arrow.hit_enemy(sk.get_rect()):

                        damage = 0

                        if player.bow:
                            damage = player.bow.damage

                        sk.hit(damage)

                        arrows.remove(arrow)

                        arrow_hit.play()

                        break

        if chest.give_loot:

            if chest.loot_item:
                inventory.add_item(chest.loot_item)

            game_data["looted_chests"].add(
                chest.chest_id
            )

            chest.give_loot = False

        if chest1.give_loot:

            if chest1.loot_item:
                inventory.add_item(chest1.loot_item)

            game_data["looted_chests"].add(
                chest1.chest_id
            )

            chest1.give_loot = False

        if chest2.give_loot:

            if chest2.loot_item:
                inventory.add_item(chest2.loot_item)

            game_data["looted_chests"].add(
                chest2.chest_id
            )

            chest2.give_loot = False

        if chest3.give_loot:

            if chest3.loot_item:
                inventory.add_item(chest3.loot_item)

            game_data["looted_chests"].add(
                chest3.chest_id
            )

            chest3.give_loot = False

        if chest4.give_loot:

            if chest4.loot_item:
                inventory.add_item(chest4.loot_item)

            game_data["looted_chests"].add(
                chest4.chest_id
            )

            chest4.give_loot = False

        for arrow in arrows[:]:
            if not arrow.update() or arrow.off_screen(1280, 768):
                arrows.remove(arrow)

        for weapon in melee_weapons[:]:
            if not weapon.update():
                melee_weapons.remove(weapon)

        Screen.blit(SF, (0, 0))

        chest.draw(Screen)
        chest1.draw(Screen)
        chest2.draw(Screen)
        chest3.draw(Screen)
        chest4.draw(Screen)

        for sk in skeletons:
            sk.draw(Screen)

        player.draw(Screen)

        if chest.state == "opened":
            chest.draw_loot_ui(Screen)

        if chest1.state == "opened":
            chest1.draw_loot_ui(Screen)

        if chest2.state == "opened":
            chest2.draw_loot_ui(Screen)

        if chest3.state == "opened":
            chest3.draw_loot_ui(Screen)

        if chest4.state == "opened":
            chest4.draw_loot_ui(Screen)

        for arrow in arrows:
            arrow.draw(Screen)

        for weapon in melee_weapons:
            weapon.draw(Screen)

        if inventory_ui.open:
            inventory_ui.draw(Screen)

        if save_message_timer > 0:
            draw_save_message(Screen, save_message_text)

            save_message_timer -= 1

        for rect in Change_Scene_1:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.stop()
                game_data["Scene_Back"] = True
                return "DesertVillage"

        for rect in Change_Scene:
            if player.get_rect().colliderect(rect):
                pygame.mixer.music.stop()
                return "DesertVillage"

        player.draw_health_bar(Screen)
        player.draw_stamina_bar(Screen)
        if player.can_attack:
            player.draw_weapon_cooldowns(Screen)

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

            return respawn_from_save(player, game_data)

        pygame.display.update()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.mixer.stop()

player = Player(spawn_x=297, spawn_y=389)

inventory = Inventory(cols=6, rows=3)

game_data = {
    "loaded_position": False,
    "looted_chests": set(),
    "npc_gift_given": False,
    "npc_gift": False,
    "Scene_Back": False,
    "inventory": inventory,
    "scene": menu,
    "MazeSolved": False,
    "Boss1": False,
    "Boss2": False,
    "Boss3": False,
}

current_scene = "menu"

while True:

    if current_scene == "menu":
        current_scene = menu(player, game_data)

    elif current_scene == "first_scene":
        current_scene = first_scene(player, game_data)

    elif current_scene == "second_scene":
        current_scene = second_scene(player, game_data)

    elif current_scene == "eldermoor_scene":
        current_scene = eldermoor_scene(player, game_data)

    elif current_scene == "Maze":
        current_scene = Maze(player, game_data)

    elif current_scene == "SnowVillage":
        current_scene = SnowVillage(player, game_data)

    elif current_scene == "IroHouse":
        current_scene = IroHouse(player, game_data)

    elif current_scene == "IroHome":
        current_scene = IroHome(player, game_data)

    elif current_scene == "InHouse":
        current_scene = InHouse(player, game_data)

    elif current_scene == "Maze_Solved":
        current_scene = Maze_Solved(player, game_data)

    elif current_scene == "First_Boss":
        current_scene = First_Boss(player, game_data)

    elif current_scene == "DesertVillage":
        current_scene = DesertVillage(player, game_data)

    elif current_scene == "DesertMaze":
        current_scene = DesertMaze(player, game_data)

    elif current_scene == "quit":
        break

pygame.quit()

