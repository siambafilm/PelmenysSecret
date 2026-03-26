from pygame import Surface, Rect
class Character:
    def __init__(self, name: str, dialog_picture: Surface, rect: Rect):
        self.name = name
        self.dialog_picture = dialog_picture
        self.rect = rect