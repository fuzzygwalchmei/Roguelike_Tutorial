"""
Following tutorial:
http://rogueliketutorials.com/tutorials/tcod/
https://www.reddit.com/r/roguelikedev/comments/bz6s0j/roguelikedev_does_the_complete_roguelike_tutorial/

"""

import tcod as libtcod
import tcod.event

from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message
from input_handlers import handle_keys, handle_mouse
from entity import Entity, get_blocking_entities_at_location
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialise_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter


def main():
    # global variables
    screen_width = 80
    screen_height = 50
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    colours = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }

    # Set up characters and inventory
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component)
    entities = [player]

    # Fonts
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    # Initialise console
    libtcod.console_init_root(screen_width, screen_height, 'Fuzzle Roguelike', False)

    # Variables for console and display panel
    con = libtcod.console_new(screen_width, screen_height)
    panel = libtcod.console_new(screen_width, panel_height)

    # create game map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                      max_monsters_per_room, max_items_per_room)

    # Field of View
    fov_recompute = True
    fov_map = initialise_fov(game_map)

    # Create message log
    message_log = MessageLog(message_x, message_width, message_height)

    # Define inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None

    # Main gam loop to run until the window is closed
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        # Render everything to the screen
        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width,
                   screen_height, bar_width, panel_height, panel_y, mouse, colours, game_state)
        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        # Use imports and compare to the input handlers
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')

        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        # Perform requested action
        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
                else:
                    message_log.add_message(Message('The {0} is not here to pick up here.'.format(entity.name), libtcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'Targeting_cancelled': True})
            else:
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        # Print all accumulated messages via message keys
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('dropped_item')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = game_state
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

        # Perform enemy turn actions
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
