
class Tile:
    """
    A tile on a map
    The tile may or may not be block and may or may not block sight
    """
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        # By default, if a tile is blocked, then it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight
        self.explored = False
