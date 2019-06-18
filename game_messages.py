import tcod as libtcod
import textwrap

class Message:
    def __init__(self, text, colour=libtcod.white):
        self.text = text
        self.colour = colour


class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # Split the message if required, amoung multiple lines
        new_msg_line = textwrap.wrap(message.text, self.width)

        for line in new_msg_line:
            # If the buffer is full, remove the first line to make room for the next one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line of the Message object, with the text and the colour
            self.messages.append(Message(line, message.colour))
