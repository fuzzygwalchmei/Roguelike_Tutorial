

class Entity:
    """
    A generic class for entities, both player and enemies
    """
    def __init__(self, x, y, char, colour):
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour

    def move(self, dx, dy):
        """
        Function to move an entity
        :param dx:
        :param dy:
        :return:
        """
        self.x += dx
        self.y += dy
