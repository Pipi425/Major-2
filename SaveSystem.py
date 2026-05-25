from Inventory import Item
from SavePoint import SAVE_POINTS

SAVE_FILE = "save.txt"


def make_sword():
    return Item(
        "Sword",
        "Items/Item01.png",
        "A sharp blade that deal 1 damage per slash",
        "weapon"
    )


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

    if data == {}:
        return None

    return data


def save_game(player, current_scene, game_data, save_point_id=None):
    scene = current_scene
    x = int(player.x)
    y = int(player.y)

    if save_point_id in SAVE_POINTS:
        point = SAVE_POINTS[save_point_id]
        scene = point["scene"]
        x = point["spawn_x"]
        y = point["spawn_y"]

    file = open(SAVE_FILE, "w")

    file.write("scene=" + scene + "\n")
    file.write("x=" + str(x) + "\n")
    file.write("y=" + str(y) + "\n")
    file.write("health=" + str(player.health) + "\n")

    if player.weapon is None:
        file.write("weapon=None\n")
    else:
        file.write("weapon=" + player.weapon.name + "\n")

    file.write("chest_looted=" + str(game_data["chest_looted"]) + "\n")

    file.close()

    print("Game saved")


def apply_save_data(player, game_data, save_data):
    player.set_position(
        int(save_data["x"]),
        int(save_data["y"])
    )

    player.health = int(save_data["health"])
    player.hp = player.health

    player.dead = False
    player.hit = False

    if save_data["weapon"] == "Sword":
        player.weapon = make_sword()
    else:
        player.weapon = None

    if save_data["chest_looted"] == "True":
        game_data["chest_looted"] = True
    else:
        game_data["chest_looted"] = False

    game_data["loaded_position"] = True

    return save_data["scene"]


def respawn_from_save(player, game_data):
    save_data = load_game()

    if save_data is not None:
        return apply_save_data(player, game_data, save_data)

    player.health = player.max_health
    player.hp = player.health
    player.dead = False
    player.hit = False
    player.set_position(297, 389)

    game_data["loaded_position"] = True

    return "first_scene"


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
    game_data["chest_looted"] = False
    game_data["reset_message"] = True

    print("Save reset")

    return "first_scene"