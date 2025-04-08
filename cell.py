from creature import Creature
from worm import Worm
from object import Object
from vector2d import Vector2d


class Cell:
    def __init__(self, pos: tuple = (-1, -1)):
        self.x = pos[0]
        self.y = pos[1]
        self.size = 30
        self.players: list[Creature] = []
        self.creatures: list[Creature] = []
        self.worms: list[Worm] = []
        self.wall: Object = None
        self.traces: Vector2d = Vector2d(0, 0)
        self.dtime: float= 0.0
