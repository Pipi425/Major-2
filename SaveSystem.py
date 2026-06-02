from Inventory import Item
from Inventory import Weapon
from Inventory import Armor
from Inventory import Consumable
from Inventory import Misc
from SavePoint import SAVE_POINTS

SAVE_FILE = "save.txt"


# =========================
# ITEM FACTORY (扩展用)
# =========================
def make_sword():
    return Weapon(
        "Sword",
        "Items/Sword.png",
        "A sharp blade that deal 1 damage per slash",
        1
    )
def make_key():
    return Misc(
        "Key",
        "Items/Key.png",
        "The Key to unlock the path to the Storm's Genesis",
    )

# 👉 统一物品生成（关键：以后只改这里）
def create_item_by_name(name):
    registry = {
        "Sword": make_sword,
        "Key": make_key,

    }

    if name in registry:
        return registry[name]()
    return None


# =========================
# LOAD SAVE FILE
# =========================
def load_game():
    try:
        file = open(SAVE_FILE, "r")
    except:
        return None

    data = {}

    for line in file:
        line = line.strip()

        if "=" in line:
            key, value = line.split("=")
            data[key] = value

    file.close()

    if not data:
        return None

    return data


# =========================
# SAVE GAME
# =========================
def save_game(player, current_scene, game_data, save_point_id=None):
    scene = current_scene
    x = int(player.x)
    y = int(player.y)

    # save point override
    if save_point_id in SAVE_POINTS:
        point = SAVE_POINTS[save_point_id]
        scene = point["scene"]
        x = point["spawn_x"]
        y = point["spawn_y"]

    file = open(SAVE_FILE, "w")

    file.write(f"scene={scene}\n")
    file.write(f"x={x}\n")
    file.write(f"y={y}\n")
    file.write(f"health={player.health}\n")

    # weapon
    if player.weapon is None:
        file.write("weapon=None\n")
    else:
        file.write(f"weapon={player.weapon.name}\n")

    # flags
    looted_chests = game_data.get("looted_chests", set())

    file.write(
        "looted_chests=" +
        ",".join(looted_chests) +
        "\n"
    )

    file.write(f"npc_gift_given={game_data.get('npc_gift_given', False)}\n")
    file.write(f"npc_gift={game_data.get('npc_gift', False)}\n")
    file.write(f"Scene_Back={game_data.get('Scene_Back', False)}\n")
    file.write(f"House_Out={game_data.get('House_Out', False)}\n")
    file.write(f"MazeSolved={game_data.get('MazeSolved', False)}\n")
    file.write(f"Boss1={game_data.get('Boss1', False)}\n")
    file.write(f"Boss2={game_data.get('Boss2', False)}\n")
    file.write(f"Boss3={game_data.get('Boss3', False)}\n")

    # =========================
    # INVENTORY SAVE (grid)
    # =========================
    inventory = game_data.get("inventory")

    item_names = []

    if inventory:
        for row in inventory.grid:
            for item in row:
                if item is not None:
                    item_names.append(item.name)

    file.write("inventory=" + ",".join(item_names) + "\n")

    file.close()

    print("Game saved")


# =========================
# APPLY SAVE DATA
# =========================
def apply_save_data(player, game_data, save_data):

    player.set_position(
        int(save_data["x"]),
        int(save_data["y"])
    )

    player.health = int(save_data["health"])
    player.hp = player.health
    player.dead = False
    player.hit = False

    # weapon（已升级）
    weapon_name = save_data.get("weapon", "None")
    player.weapon = create_item_by_name(weapon_name)

    # flags
    raw_chests = save_data.get("looted_chests", "")

    if raw_chests:
        game_data["looted_chests"] = set(
            raw_chests.split(",")
        )
    else:
        game_data["looted_chests"] = set()

    game_data["npc_gift_given"] = save_data.get("npc_gift_given", "False") == "True"
    game_data["npc_gift"] = save_data.get("npc_gift", "False") == "True"
    game_data["Scene_Back"] = save_data.get("Scene_Back", "False") == "True"
    game_data["House_Out"] = save_data.get("House_Out", "False") == "True"
    game_data["scene"] = save_data["scene"]
    game_data["MazeSolved"] = save_data.get("MazeSolved", "False") == "True"

    game_data["Boss1"] = save_data.get("Boss1", "False") == "True"
    game_data["Boss2"] = save_data.get("Boss2", "False") == "True"
    game_data["Boss3"] = save_data.get("Boss3", "False") == "True"

    # =========================
    # INVENTORY LOAD
    # =========================
    inventory = game_data["inventory"]
    inventory.clear()

    raw_items = save_data.get("inventory", "")

    if raw_items:
        for name in raw_items.split(","):
            item = create_item_by_name(name)
            if item:
                inventory.add_item(item)

    game_data["loaded_position"] = True

    return save_data["scene"]


# =========================
# RESPAWN
# =========================
def respawn_from_save(player, game_data):
    save_data = load_game()

    if save_data:
        return apply_save_data(player, game_data, save_data)

    player.health = player.max_health
    player.hp = player.health
    player.dead = False
    player.hit = False
    player.set_position(297, 389)

    game_data["loaded_position"] = True

    return "first_scene"


# =========================
# RESET SAVE
# =========================
def reset_save_data(player, game_data):
    file = open(SAVE_FILE, "w")
    file.close()

    player.health = player.max_health
    player.hp = player.health
    player.weapon = None
    player.dead = False
    player.hit = False
    player.set_position(297, 389)

    game_data["loaded_position"] = True
    game_data["looted_chests"] = set()
    game_data["npc_gift_given"] = False
    game_data["npc_gift"] = False
    game_data["Scene_Back"] = False
    game_data["House_Out"] = False
    game_data["MazeSolved"] = False

    game_data["Boss1"] = False
    game_data["Boss2"] = False
    game_data["Boss3"] = False

    game_data["inventory"].clear()

    print("Save reset")

    return "first_scene"