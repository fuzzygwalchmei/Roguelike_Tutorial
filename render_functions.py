import tcod as libtcod

def render_all(con, entities, screen_width, screen_height):
    """
    draw all entities in the list
    :param con:
    :param entities:
    :param screen_width:
    :param screen_height:
    :return:
    """
    for entity in entities:
        draw_entity(con, entity)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    libtcod.console_set_default_foreground(con, entity.colour)
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    """
    Erase the character that is represented by this object
    :param con:
    :param entity:
    :return:
    """
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)