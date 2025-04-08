import math


class Vector2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vector):
        return Vector2d(self.x + vector.x, self.y + vector.y)

    def __iadd__(self, vector):
        self.x += vector.x
        self.y += vector.y
        return self

    def __sub__(self, vector):
        return Vector2d(self.x - vector.x, self.y - vector.y)

    def __isub__(self, vector):
        self.x -= vector.x
        self.y -= vector.y
        return self

    def __mul__(self, vector):
        return Vector2d(self.x * vector.x, self.y * vector.y)

    def __imul__(self, vector):
        self.x *= vector.x
        self.y *= vector.y
        return self

    def __truediv__(self, vector):
        return Vector2d(self.x / vector.x, self.y / vector.y)

    def __itruediv__(self, vector):
        self.x /= vector.x
        self.y /= vector.y
        return self

    def __pow__(self, power, modulo=None):
        return Vector2d(self.x ** power, self.y ** power)

    def norm(self):
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length
        return self

    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self

    def cutLengthTo(self, length):
        mylength = self.length()
        if mylength != 0:
            self.x = length / mylength * self.x
            self.y = length / mylength * self.y

    def getAsList(self):
        return [self.x, self.y]

    def getAsTuple(self):
        return (self.x, self.y)

    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def notVector(self):
        return Vector2d(self.x * -1, self.y * -1)

    def vectorEnergy(self, energy):
        return Vector2d(self.x * energy, self.y * energy)

    def rotateVector(self, alfa):
        s = math.sin(alfa)
        c = math.cos(alfa)
        x = self.x
        y = self.y
        self.x = x * c - y * s
        self.y = x * s + y * c

    def copyVector(self):
        return Vector2d(self.x, self.y)

    @staticmethod
    def angleBetween(v1, v2, a360=False):
        forsin = v1.x * v2.y - v1.y * v2.x
        forcos = v1.x * v2.x + v1.y * v2.y
        a = v1.length()
        b = v2.length()
        if (a == 0 or b == 0):
            return 0
        sinAlfa = forsin / (a * b)
        cosAlfa = forcos / (a * b)
        if cosAlfa > 1:
            cosAlfa = 1
        elif cosAlfa < -1:
            cosAlfa = -1
        if sinAlfa < 0 and a360:
            return math.pi + math.pi - math.acos(cosAlfa)
        return math.acos(cosAlfa)


if __name__ == "__main__":
    v1 = Vector2d(100.0, 0.0)
    v1.rotateVector(3/2 * math.pi)
    print(v1.getAsList())
