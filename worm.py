from object import Object


class Worm:
    def __init__(self, object: Object, points=10, god_mod=False):
        self.object: Object = object
        self.points: int = points
        self.god_mod: bool = god_mod
