import os
import shelve
from map_objects.game_map import  GameMap


def save_game(player, entities, game_map, message_log, game_state):
    with shelve.open('savegame.dat', 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['game_map'] = game_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state


def load_game():
    if not os.path.isfile('savegame.dat'):
        raise FileNotFoundError

    with shelve.open('savegame.dat', 'r') as datafile:
        player_index = datafile['player_index']
        entities = datafile['entities']
        game_map = datafile['game_map']
        message_log = datafile['message_log']
        game_state = datafile['game_state']

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state
