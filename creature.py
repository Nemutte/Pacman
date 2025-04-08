from object import Object


class Creature:
    def __init__(self, object: Object, spawn_point=None, health=1, team=0, points=0):
        self.object: Object = object
        self.move_time: float = 0
        self.health: int = health
        self.points: int = points
        self.team: int = team
        self.god_mod: bool = False
        self.god_mod_time: float = 0.0
        self.spawn_point = spawn_point
        self.death_time: float = 0.0

    def update(self, dtime):
        if self.god_mod:
            self.god_mod_time -= dtime
            if self.god_mod_time <= 0.0:
                self.god_mod = False
                self.god_mod_time = 0.0
