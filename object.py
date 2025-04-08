from vector2d import Vector2d
#from cell import Cell

class Object:
    def __init__(self, data: dict, allow_for_player=False):
        self.pos: Vector2d = Vector2d(data["px"], data["py"])
        self.vel: Vector2d = Vector2d(data["vx"], data["vy"])
        self.speed: float = data["speed"]
        self.mass: float = data["mass"]
        self.radius: float = data["radius"]
        self.size: Vector2d = Vector2d(data["width"], data["height"])
        self.bitmap: str = data["bitmap"]
        self.bitmap2: str = f"{data['bitmap']}_weak"
        self.bitmap3: str = f"{data['bitmap']}_god"
        self.bitmap4: str = f"{data['bitmap']}_god_left"
        self.static: bool = data["static"]
        self.number_of_frames: int = data["number_of_frames"]
        self.forces: list[Vector2d] = []
        self.allow_for_player = allow_for_player
        self.frame: int = 0
        self.timee: float = 0.0
        self.cant_move_time = 0.0
        self.v: int = 0
        self.cell = None

    def update(self, dtime: float):
        self.cant_move_time -= dtime
        if self.cant_move_time < 0:
            self.cant_move_time = 0.0
        if not self.static and self.cant_move_time == 0.0:
            for force in self.forces:
                self.vel += force
            self.forces.clear()
            self.pos += self.vel * Vector2d(dtime, dtime)

    def getSprite(self, dtime: float):
        if self.vel.x > 0:
            self.v = 0
        elif self.vel.x < 0:
            self.v = 1
        elif self.vel.y > 0:
            self.v = 2
        elif self.vel.y < 0:
            self.v = 3
        self.timee += dtime
        if self.timee > 60:
            self.frame += 1
            self.timee = 0.0
        if self.frame >= self.number_of_frames:
            self.frame = 0
        return self.bitmap, self.frame + 7 * self.v

    def getSprite3(self, dtime: float):
        if self.vel.x > 0:
            self.v = 0
        elif self.vel.x < 0:
            self.v = 1
        elif self.vel.y > 0:
            self.v = 2
        elif self.vel.y < 0:
            self.v = 3
        self.timee += dtime
        if self.timee > 60:
            self.frame += 1
            self.timee = 0.0
        if self.frame >= self.number_of_frames:
            self.frame = 0
        return self.bitmap3, self.frame + 7 * self.v

    def getSprite4(self, dtime: float):
        if self.vel.x > 0:
            self.v = 0
        elif self.vel.x < 0:
            self.v = 1
        elif self.vel.y > 0:
            self.v = 2
        elif self.vel.y < 0:
            self.v = 3
        self.timee += dtime
        if self.timee > 60:
            self.frame += 1
            self.timee = 0.0
        if self.frame >= self.number_of_frames:
            self.frame = 0
        return self.bitmap4, self.frame + 7 * self.v

    def getSprite2(self, dtime: float):
        return self.bitmap2, self.frame
