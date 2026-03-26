import pygame as pg
from character import Character

class Replique:
    def __init__(self, character: Character, text: str):
        self.character = character
        self.text = text

class ChoiseStep:
    def __init__(self, choices: list, replicsAfter: list):
        self.choices = choices
        self.replicsAfter = replicsAfter