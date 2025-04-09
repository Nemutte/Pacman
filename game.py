import random
import time

from vector2d import Vector2d
from object import Object
from maps import maps
from cell import Cell
from creature import Creature
from worm import Worm
import pygame
from copy import deepcopy

gravity: Vector2d = Vector2d(0.0, 0.0)
SCREEN_WIDTH: int = 1200
SCREEN_HEIGHT: int = 600
X_MAP_ON_SCREEN: int = 0
Y_MAP_ON_SCREEN: int = 0
NUMBER_OF_PLAYERS: int = 2

def RayVsRect(ray_origin: Vector2d, ray_dir: Vector2d, target: Object, contact_point: Vector2d, contact_normal: Vector2d, t_hit_near: float):
    if ray_dir.x == 0:
        return False
    if ray_dir.y == 0:
        return False

    t_near = (target.pos - ray_origin) / ray_dir
    t_far = (target.pos + target.size - ray_origin) / ray_dir

    tmp = 0.0
    if t_near.x > t_far.x:
        tmp = t_near.x
        t_near.x = t_far.x
        t_far.x = tmp
    if t_near.y > t_far.y:
        tmp = t_near.y
        t_near.y = t_far.y
        t_far.y = tmp

    if t_near.x > t_far.y or t_near.y > t_far.x:
        return False

    t_hit_near = max(t_near.x, t_near.y)
    t_hit_far = min(t_far.x, t_far.y)

    if t_hit_far < 0:
        return False

    contact_point = ray_origin + ray_dir * t_hit_near

    if t_near.x > t_near.y:
        if ray_dir.x < 0:
            contact_normal = Vector2d(1, 0)
        else:
            contact_normal = Vector2d(-1, 0)
    elif t_near.x < t_near.y:
        if ray_dir.y < 0:
            contact_normal = Vector2d(0, 1)
        else:
            contact_normal = Vector2d(0, -1)
    return True

def DynamicRectVsRect(inn: Object, target: Object, contact_point: Vector2d, contact_normal: Vector2d, contact_time: float, fElapsed_time: float):
    if inn.vel.x == 0 and inn.vel.y == 0:
        return False

    expanded_target: Object = deepcopy(target)
    expanded_target.pos = target.pos - inn.size / Vector2d(2.0, 2.0)
    expanded_target.size = target.size + inn.size

    ray_origin: Vector2d = inn.pos + inn.size / 2.0
    ray_dir: Vector2d = inn.vel * fElapsed_time
    if RayVsRect(ray_origin, ray_dir, expanded_target, contact_point, contact_normal, contact_time):
        if contact_time <= 1.0:
            return True
    return False

def solveDynamicCollisionBallVsBall(obj1: Object, obj2: Object):
    vector: Vector2d = obj2.pos - obj1.pos
    distance = vector.length()
    if distance == 0:
        distance = 0.000001
    # Normal
    nx = vector.x / distance
    ny = vector.y / distance

    # Target
    tx = -ny
    ty = nx

    # Dot Product Tangent
    dpTan1 = obj1.vel.x * tx + obj1.vel.y * ty
    dpTan2 = obj2.vel.x * tx + obj2.vel.y * ty

    # Dot Product Normal
    dpNorm1 = obj1.vel.x * nx + obj1.vel.y * ny
    dpNorm2 = obj2.vel.x * nx + obj2.vel.y * ny

    # Conversation of momentum in 1D
    m1 = (dpNorm1 * (obj1.mass - obj2.mass) + 2.0 * obj2.mass * dpNorm2) / (obj1.mass + obj2.mass)
    m2 = (dpNorm2 * (obj2.mass - obj1.mass) + 2.0 * obj1.mass * dpNorm1) / (obj1.mass + obj2.mass)

    obj1.vel.x = (tx * dpTan1 + nx * m1)
    obj1.vel.y = (ty * dpTan1 + ny * m1)
    obj2.vel.x = (tx * dpTan2 + nx * m2)
    obj2.vel.y = (ty * dpTan2 + ny * m2)

def solveDynamicCollisionBallVsRect(obj1: Object, obj2: Object, dtime: float):
    pass

def solveStaticCollisionBallVsBall(obj1: Object, obj2: Object, dtime: float):
    if_equal_zero = 0.0000001
    vector = obj2.pos - obj1.pos  # tworzymy vektor od obj1 do obj2
    distance = vector.length()

    l = obj1.radius + obj2.radius - distance  # długość odcinka pokrywania się kółek
    vector.cutLengthTo(l / 2 + if_equal_zero)  # skracamy wektor o połowe + bo przybliżena nie są dokładne
    if vector.length() == 0:
        vector.x = if_equal_zero
        vector.y = if_equal_zero
    obj2.pos += vector      # przesuwamy pbj2 o wektor
    vector.scale(-1)
    obj1.pos += vector  # przesuwamy obj1 o odwrucony wektor

def solveStaticCollisionBallVsRect(obj1: Object, obj2: Object):
    nearest_point: Vector2d = Vector2d(0, 0)
    nearest_point.x = max(obj2.pos.x, min(obj1.pos.x, obj2.pos.x + obj2.size.x))
    nearest_point.y = max(obj2.pos.y, min(obj1.pos.y, obj2.pos.y + obj2.size.y))
    ray_to_nearest: Vector2d = nearest_point - obj1.pos
    overlap: float = obj1.radius - ray_to_nearest.length()

    if ray_to_nearest.length() != 0:
        if overlap > 0:
            obj1.pos = obj1.pos - ray_to_nearest.norm().scale(overlap)
            return True
    return False

def solveStaticCollisionRectVsRect(obj1: Object, obj2: Object):
    pass

def collisionBallVsBall(obj1: Object, obj2: Object):
    distance = (obj1.pos - obj2.pos).length()
    if distance < obj1.radius + obj2.radius:
        return True
    else:
        return False

def collisionRectVsRect(obj1: Object, obj2: Object):
    return False

def findCollision(obj1: Object, obj2: Object, dtime: float):
    if obj1.radius != 0 and obj2.radius != 0:
        if collisionBallVsBall(obj1, obj2):
            solveStaticCollisionBallVsBall(obj1, obj2, dtime)
            return True
    if obj1.radius != 0 and obj2.radius == 0:
        if solveStaticCollisionBallVsRect(obj1, obj2):
            solveDynamicCollisionBallVsRect(obj1, obj2, dtime)
            return True
    if obj1.radius == 0 and obj2.radius != 0:
        if solveStaticCollisionBallVsRect(obj2, obj1):
            solveDynamicCollisionBallVsRect(obj2, obj1, dtime)
            return True
    if obj1.radius == 0 and obj2.radius == 0:
        if collisionRectVsRect(obj1, obj2):
            solveStaticCollisionRectVsRect(obj1, obj2)
            return True
    return False

def moveObjectToScene(object: Object):
    if not object.static:
        if object.pos.x > SCREEN_WIDTH:
            object.pos.x = 0
        elif object.pos.x < 0:
            object.pos.x = SCREEN_WIDTH
        if object.pos.y > SCREEN_HEIGHT:
            object.pos.y = 0
        elif object.pos.y < 0:
            object.pos.y = SCREEN_HEIGHT

def addForcesFromOutside(object: Object):
    mas: Vector2d = Vector2d(object.mass, object.mass)
    object.forces.append(gravity * mas)

def update(objects: list[Object], worms: list[Worm], creatures: list[Creature], spawn_point: Vector2d, mapp: int, world: list[list[Cell]], sounds: dict[str: pygame.mixer.Sound], dtime: float):
    # aktualizacja pozostawionego śladu przez gracza
    for w in world:
        for h in w:
            h.dtime += dtime
            if h.dtime > 0.016:
                h.dtime -= 0.016
                if h.traces.length() - 0.002 <= 0:
                    h.traces.x = 0
                    h.traces.y = 0
                else:
                    h.traces.cutLengthTo(h.traces.length() - 0.002)
    # aktualizowanie uchu graczy
    for i in range(NUMBER_OF_PLAYERS):
        addForcesFromOutside(creatures[i].object)
        creatures[i].object.update(dtime)
        if creatures[i].object.vel.length() != 0 and creatures[i].object.cell is not None:
            creatures[i].object.cell.traces = creatures[i].object.vel.copyVector().scale(1/creatures[i].object.vel.length())
        creatures[i].update(dtime)
        moveObjectToScene(creatures[i].object)
    # aktualizowanie ruchu duchów
    for creature in creatures[NUMBER_OF_PLAYERS:]:
        creature.death_time -= dtime
        if creature.death_time < 0:
            creature.death_time = 0
        addForcesFromOutside(creature.object)
        if creature.death_time == 0:
            AI(mapp, world, creature, creatures[:NUMBER_OF_PLAYERS], dtime)
            creature.object.update(dtime)
        moveObjectToScene(creature.object)

    # kolizja z ścianami
    for i in range(NUMBER_OF_PLAYERS):
        for obj2 in objects:
            if not obj2.allow_for_player:
                if findCollision(creatures[i].object, obj2, dtime):
                    pass
    for creature in creatures[NUMBER_OF_PLAYERS:]:
        for obj2 in objects:
            if findCollision(creature.object, obj2, dtime):
                pass

    # kolizja z innym graczem
    for i in range(NUMBER_OF_PLAYERS):
        for j in range(NUMBER_OF_PLAYERS):
            if creatures[i].team != creatures[j].team:
                if findCollision(creatures[i].object, creatures[j].object, dtime):
                    if creatures[i].god_mod:
                        pygame.mixer.Sound.play(sounds["player_death"])
                        creatures[j].object.cant_move_time += 6
                        creatures[j].object.pos = spawn_point.copyVector()
                    if creatures[j].god_mod:
                        pygame.mixer.Sound.play(sounds["player_death"])
                        creatures[i].object.cant_move_time += 6
                        creatures[i].object.pos = spawn_point.copyVector()
    # zbieranie robaków
    for i in range(NUMBER_OF_PLAYERS):
        for worm in worms:
            if findCollision(creatures[i].object, worm.object, dtime):
                worms.remove(worm)
                creatures[i].points += worm.points
                if worm.god_mod:
                    pygame.mixer.Sound.play(sounds["god_mod"])
                    creatures[i].god_mod = True
                    creatures[i].god_mod_time += 6.0
                else:
                    pygame.mixer.Sound.play(sounds["collecting_warm"])
    # kolizja z przeciwnikami
    for creature2 in creatures[NUMBER_OF_PLAYERS:]:
        for i in range(NUMBER_OF_PLAYERS):
            if creature2.death_time == 0.0:
                if findCollision(creatures[i].object, creature2.object, dtime):
                    if creatures[i].god_mod:
                        creature2.object.pos = creature2.spawn_point.copyVector()
                        creature2.death_time = 10.0
                        creatures[i].points += 20
                        pygame.mixer.Sound.play(sounds["creature_death"])
                    else:
                        creatures[i].health -= 1
                        if creatures[i].health <= 0:
                            creatures[i].object.pos = Vector2d(X_MAP_ON_SCREEN - 20, Y_MAP_ON_SCREEN - 20)
                        else:
                            creatures[i].object.pos = spawn_point.copyVector()
                        pygame.mixer.Sound.play(sounds["player_death"])
    for creature in creatures:
        moveCreatureFromCellToCell(creature, world)

def draw(screen, fonts,  fps: float, objects: list[Object], worms: list[Worm], creatures: list[Creature], world: list[list[Cell]], sprites: dict[str: list[pygame.image]], sounds: dict[str: pygame.mixer.Sound], dtime: float):
    information: list = []
    screen.fill((30, 30, 30))
    # rysowanie ścieszki
    # for idx, w in enumerate(world):
    #     for idy, h in enumerate(world[idx]):
    #         if h.traces.length() > 0:
    #             x = X_MAP_ON_SCREEN + 30 * idx
    #             y = Y_MAP_ON_SCREEN + 30 * idy
    #             pygame.draw.rect(screen, (200*h.traces.length(), 200*h.traces.length(), 200*h.traces.length()), pygame.Rect(x, y, 30, 30))
    #             pygame.draw.line(screen, (0, 255, 0), (x+15, y+15), (x+15+h.traces.x*15, y+15+h.traces.y*15), 2)
    # rysuj ściany
    for object in objects:
       sprite, frame = object.getSprite(dtime)
       screen.blit(sprites[sprite][frame], (round(object.pos.x), round(object.pos.y)))

    # rysuj robaki
    for worm in worms:
        sprite, frame = worm.object.getSprite(dtime)
        screen.blit(sprites[sprite][frame], (round(worm.object.pos.x - worm.object.radius),
                                                      round(worm.object.pos.y - worm.object.radius)))

    # rysuj graczy
    for i in range(NUMBER_OF_PLAYERS):
        if creatures[i].god_mod_time == 0.0:
            sprite, frame = creatures[i].object.getSprite(dtime)
            screen.blit(sprites[sprite][frame], (round(creatures[i].object.pos.x - creatures[i].object.radius),
                                                          round(creatures[i].object.pos.y - creatures[i].object.radius)))
        elif creatures[i].god_mod_time <= 2.0:
            sprite, frame = creatures[i].object.getSprite4(dtime)
            screen.blit(sprites[sprite][frame], (round(creatures[i].object.pos.x - creatures[i].object.radius),
                                                 round(creatures[i].object.pos.y - creatures[i].object.radius)))
        elif creatures[i].god_mod_time > 2.0:
            sprite, frame = creatures[i].object.getSprite3(dtime)
            screen.blit(sprites[sprite][frame], (round(creatures[i].object.pos.x - creatures[i].object.radius),
                                                 round(creatures[i].object.pos.y - creatures[i].object.radius)))

    # rysuj duchy
    for creature in creatures[NUMBER_OF_PLAYERS:]:
        god_mod_is_on: bool = False
        for i in range(NUMBER_OF_PLAYERS):
            if creatures[i].god_mod:
                god_mod_is_on = True
        if creature.death_time == 0:
            if god_mod_is_on:
                sprite, frame = creature.object.getSprite2(dtime)
                screen.blit(sprites[sprite][frame], (round(creature.object.pos.x - creature.object.radius),
                                                              round(creature.object.pos.y - creature.object.radius)))
            else:
                sprite, frame = creature.object.getSprite(dtime)
                screen.blit(sprites[sprite][frame], (round(creature.object.pos.x - creature.object.radius),
                                                          round(creature.object.pos.y - creature.object.radius)))
        else:
            dc = pygame.font.Font.render(fonts[2], f"{round(creature.death_time, 1)}", True, (255, 0, 0))
            screen.blit(dc, (creature.spawn_point.x - 7, creature.spawn_point.y - 7))

    #information.append(pygame.font.Font.render(fonts[0], f"fps: {fps}", True, (255, 255, 255)))
    for i in range(NUMBER_OF_PLAYERS):
        information.append(pygame.font.Font.render(fonts[0], f"Player: {i+1}", True, (255, 255, 255)))
        information.append(pygame.font.Font.render(fonts[0], f"Health: {creatures[i].health}", True, (255, 255, 255)))
        information.append(pygame.font.Font.render(fonts[0], f"Points: {creatures[i].points}", True, (255, 255, 255)))
    for info_idx, info in enumerate(information):
        if info_idx < 3:
            screen.blit(info, (150, 200 + info_idx * 29))
        else:
            screen.blit(info, (950, 200 + (info_idx-3) * 29))
    game_over = pygame.font.Font.render(fonts[1], f"Game Over", True, (255, 40, 40))
    steal_alive: bool = False
    for i in range(NUMBER_OF_PLAYERS):
        if creatures[i].health > 0:
            steal_alive = True
    if not steal_alive:
        screen.blit(game_over, (SCREEN_WIDTH/2 - game_over.get_width()/2, SCREEN_HEIGHT/2 - game_over.get_height()/2))
    pygame.display.flip()

def generateLevel(level: int,world: list[list[Cell]], objects: list[Object], worms: list[Worm], creatures: list[Creature]):
    wall_size: int = 30
    world.clear()
    width: int = len(maps[f"level{level}"][0])
    height: int = len(maps[f"level{level}"])
    global X_MAP_ON_SCREEN
    global Y_MAP_ON_SCREEN
    X_MAP_ON_SCREEN = SCREEN_WIDTH / 2 - width * wall_size/2
    Y_MAP_ON_SCREEN = SCREEN_HEIGHT / 2 - height * wall_size/2
    X = X_MAP_ON_SCREEN
    Y = Y_MAP_ON_SCREEN
    settings: dict = {"px": 0.0, "py": 0.0, "vx": 0.0, "vy": 0.0, "speed": 1.0, "mass": 10.0, "radius": 0.0,
                      "width": wall_size, "height": wall_size, "bitmap": "wall", "static": True,
                      "number_of_frames": 1}
    worm: dict = {"px": 0.0, "py": 0.0, "vx": 0.0, "vy": 0.0, "speed": 1.0, "mass": 10.0, "radius": 4.0,
                  "width": wall_size, "height": wall_size, "bitmap": "worm", "static": False,
                  "number_of_frames": 1}
    worm_big: dict = {"px": 0.0, "py": 0.0, "vx": 0.0, "vy": 0.0, "speed": 1.0, "mass": 10.0, "radius": 4.0,
                      "width": wall_size, "height": wall_size, "bitmap": "worm_big", "static": False,
                      "number_of_frames": 1}
    creature: dict = {"px": 0.0, "py": 0.0, "vx": 0.0, "vy": 0.0, "speed": 1.0,
                      "mass": 10.0, "radius": 12.0,
                      "width": 0.0, "height": 0.0, "bitmap": "ghost", "static": False,
                      "number_of_frames": 7}
    spawn_position: Vector2d = Vector2d(X + width / 2 * wall_size, Y + height / 2 * wall_size)
    object_player: dict = {"px": spawn_position.x, "py": spawn_position.y, "vx": 0.0, "vy": 0.0, "speed": 1.0,
                           "mass": 10.0, "radius": 12.0,
                           "width": 0.0, "height": 0.0, "bitmap": "player1", "static": False,
                           "number_of_frames": 7}
    for i in range(width):
        column: list[Cell] = []
        for j in range(height):
            cell = Cell(pos=(i, j))
            column.append(cell)
        world.append(column)
    if len(creatures) == 0:
        for i in range(NUMBER_OF_PLAYERS):
            object_player["bitmap"] = f"player{i+1}"
            cre = Creature(Object(object_player), team=i+1, health=2)
            cre.object.bitmap3 = f"player{i+1}_god"
            cre.object.bitmap4 = f"player{i+1}_god_left"
            cre.object.cell = world[int(width / 2)][int(height / 2)]
            creatures.append(cre)
            world[int(width / 2)][int(height / 2)].creatures.append(cre)
    for i in range(width):
        for j in range(height):
            cell = world[i][j]
            if maps[f"level{level}"][j][i] == 2:
                creature["px"] = X + wall_size * i + 15
                creature["py"] = Y + wall_size * j + 15
                cre = Creature(Object(creature), spawn_point=Vector2d(creature["px"], creature["py"]))
                cre.object.cell = cell
                creatures.append(cre)
                cell.creatures.append(cre)
            elif maps[f"level{level}"][j][i] == 1:
                settings["px"] = X + wall_size * i
                settings["py"] = Y + wall_size * j
                obj = Object(settings)
                obj.cell = cell
                objects.append(obj)
                cell.wall = obj
            elif maps[f"level{level}"][j][i] == 4:
                settings["px"] = X + wall_size * i
                settings["py"] = Y + wall_size * j
                settings["bitmap"] = "wall_a"
                obj = Object(settings, allow_for_player=True)
                obj.cell = cell
                objects.append(obj)
                cell.wall = obj
                settings["bitmap"] = "wall"
            elif maps[f"level{level}"][j][i] == 0:
                worm["px"] = X + wall_size * i + wall_size / 2
                worm["py"] = Y + wall_size * j + wall_size / 2
                wor = Worm(Object(worm))
                wor.object.cell = cell
                worms.append(wor)
                cell.worms.append(wor)
            elif maps[f"level{level}"][j][i] == 3:
                worm_big["px"] = X + wall_size * i + wall_size / 2 - 3
                worm_big["py"] = Y + wall_size * j + wall_size / 2 - 3
                wor = Worm(Object(worm_big), god_mod=True)
                wor.object.cell = cell
                worms.append(wor)
                cell.worms.append(wor)
    return spawn_position

def sortMoves(moves: list[Vector2d], chances: list[int]):
    tmp_v: Vector2d = Vector2d(0, 0)
    tmp = 0

    for _ in range(len(moves)):
        for i in range(1, len(moves)):
            if chances[i] > chances[i - 1]:
                tmp = chances[i]
                tmp_v = moves[i]
                chances[i] = chances[i - 1]
                moves[i] = moves[i - 1]
                chances[i - 1] = tmp
                moves[i - 1] = tmp_v

def AI(level: int, world: list[list[Cell]], creature: Creature, players: list[Creature], dtime):
    moves: list[Vector2d] = [Vector2d(130, 0),
                             Vector2d(-130, 0),
                             Vector2d(0, 130),
                             Vector2d(0, -130),
                          ]
    moves_weak: list[Vector2d] = [Vector2d(80, 0),
                             Vector2d(-80, 0),
                             Vector2d(0, 80),
                             Vector2d(0, -80),
                          ]
    allowed_moves: list[Vector2d] = []
    allowed_moves_chanse: list = []
    map_position: Vector2d = Vector2d(X_MAP_ON_SCREEN, Y_MAP_ON_SCREEN)
    god_mod_is_on = False
    for p in players:
        if p.god_mod:
            god_mod_is_on = True
    track: Vector2d = creature.object.cell.traces
    c_posx = creature.object.cell.x
    c_posy = creature.object.cell.y
    creature.move_time += dtime
    if creature.move_time >= 0.2:
        creature.move_time = 0
        # stworzenie lisy dostępnych ruchów
        if world[c_posx+1][c_posy].wall is None:
            if god_mod_is_on:
                allowed_moves.append(moves_weak[0])
            else:
                allowed_moves.append(moves[0])
        if world[c_posx-1][c_posy].wall is None:
            if god_mod_is_on:
                allowed_moves.append(moves_weak[1])
            else:
                allowed_moves.append(moves[1])
        if world[c_posx][c_posy+1].wall is None:
            if god_mod_is_on:
                allowed_moves.append(moves_weak[2])
            else:
                allowed_moves.append(moves[2])
        if world[c_posx][c_posy-1].wall is None:
            if god_mod_is_on:
                allowed_moves.append(moves_weak[3])
            else:
                allowed_moves.append(moves[3])

        # nadanie szansy na każdy ruch
        v = creature.object.vel
        v.scale(-1)
        for idx, amoves in enumerate(allowed_moves):
            # zmniejszenie szansy jeśli jest to droga w tył
            if amoves.x == v.x and amoves.y == v.y:
                allowed_moves_chanse.append(1)
            else:
                allowed_moves_chanse.append(50)
            if amoves.x > 0 and track.x > 0:
                if god_mod_is_on:
                    allowed_moves_chanse[idx] = 1
                else:
                    allowed_moves_chanse[idx] += 150
            elif amoves.x < 0 and track.x < 0:
                if god_mod_is_on:
                    allowed_moves_chanse[idx] = 1
                else:
                    allowed_moves_chanse[idx] += 150
            elif amoves.y > 0 and track.y > 0:
                if god_mod_is_on:
                    allowed_moves_chanse[idx] = 1
                else:
                    allowed_moves_chanse[idx] += 150
            elif amoves.y < 0 and track.y < 0:
                if god_mod_is_on:
                    allowed_moves_chanse[idx] = 1
                else:
                    allowed_moves_chanse[idx] += 150
        sortMoves(allowed_moves, allowed_moves_chanse)
        # jeśli znajdzie ślad gracza

        sum_of_chance: int = 0
        for n in allowed_moves_chanse:
            sum_of_chance +=n
        lottery = random.randint(1, sum_of_chance)
        for idx, amoves in enumerate(allowed_moves):
            if allowed_moves_chanse[idx] >= lottery:
                creature.object.vel = amoves
                break
            lottery -= allowed_moves_chanse[idx]

def getImage(sheet, frame, width, height, colour):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), area=(width * frame, 0, width, height))
    # image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(colour)
    return image

def loadSprites(sprites: dict[str: list[pygame.image]]):
    # player1
    player1_image = pygame.image.load("./src/player1.png")
    player1_list_sprites: list[pygame.image] = []
    for i in range(28):
        player1_list_sprites.append(getImage(player1_image, i, 24, 24, (0, 0, 0)))
    sprites["player1"] = player1_list_sprites

    player1_god_image = pygame.image.load("./src/player1_god.png")
    player1_god_list_sprites: list[pygame.image] = []
    for i in range(28):
        player1_god_list_sprites.append(getImage(player1_god_image, i, 24, 24, (0, 0, 0)))
    sprites["player1_god"] = player1_god_list_sprites

    player1_god_left_image = pygame.image.load("./src/player1_god_left.png")
    player1_god_left_list_sprites: list[pygame.image] = []
    for i in range(28):
        player1_god_left_list_sprites.append(getImage(player1_god_left_image, i, 24, 24, (0, 0, 0)))
    sprites["player1_god_left"] = player1_god_left_list_sprites

    # player2
    player2_image = pygame.image.load("./src/player2.png")
    player2_list_sprites: list[pygame.image] = []
    for i in range(28):
        player2_list_sprites.append(getImage(player2_image, i, 24, 24, (0, 0, 0)))
    sprites["player2"] = player2_list_sprites

    player2_god_image = pygame.image.load("./src/player2_god.png")
    player2_god_list_sprites: list[pygame.image] = []
    for i in range(28):
        player2_god_list_sprites.append(getImage(player2_god_image, i, 24, 24, (0, 0, 0)))
    sprites["player2_god"] = player2_god_list_sprites

    player2_god_left_image = pygame.image.load("./src/player2_god_left.png")
    player2_god_left_list_sprites: list[pygame.image] = []
    for i in range(28):
        player2_god_left_list_sprites.append(getImage(player2_god_left_image, i, 24, 24, (0, 0, 0)))
    sprites["player2_god_left"] = player2_god_left_list_sprites

    # worm
    worm_image = pygame.image.load("./src/worm.png")
    worm_list_sprites: list[pygame.image] = []
    for i in range(1):
        worm_list_sprites.append(getImage(worm_image, i, 14, 14, (0, 0, 0)))
    sprites["worm"] = worm_list_sprites

    # worm_big
    worm_big_image = pygame.image.load("./src/worm_big.png")
    worm_big_list_sprites: list[pygame.image] = []
    for i in range(1):
        worm_big_list_sprites.append(getImage(worm_big_image, i, 14, 14, (0, 0, 0)))
    sprites["worm_big"] = worm_big_list_sprites

    # ghost
    ghost_image = pygame.image.load("./src/ghost.png")
    ghost_list_sprites: list[pygame.image] = []
    for i in range(28):
        ghost_list_sprites.append(getImage(ghost_image, i, 24, 24, (0, 0, 0)))
    sprites["ghost"] = ghost_list_sprites

    # ghost_weak
    ghost_weak_image = pygame.image.load("./src/ghost_weak.png")
    ghost_weak_list_sprites: list[pygame.image] = []
    for i in range(28):
        ghost_weak_list_sprites.append(getImage(ghost_weak_image, i, 24, 24, (0, 0, 0)))
    sprites["ghost_weak"] = ghost_weak_list_sprites

    # wall
    wall_image = pygame.image.load("./src/wall.png")
    wall_list_sprites: list[pygame.image] = []
    for i in range(1):
        wall_list_sprites.append(getImage(wall_image, i, 30, 30, (0, 0, 0)))
    sprites["wall"] = wall_list_sprites

    # wall_a
    wall_a_image = pygame.image.load("./src/wall_a.png")
    wall_a_list_sprites: list[pygame.image] = []
    for i in range(1):
        wall_a_list_sprites.append(getImage(wall_a_image, i, 30, 30, (0, 0, 0)))
    sprites["wall_a"] = wall_a_list_sprites

def loadSounds(sounds: dict[str: pygame.mixer.Sound]):
    background_sound = pygame.mixer.Sound("./music/background_sound.mp3")
    background_sound.set_volume(0.3)
    collecting_warm_sound = pygame.mixer.Sound("./music/collecting_warm.mp3")
    collecting_warm_sound.set_volume(0.2)
    god_mod_sound = pygame.mixer.Sound("./music/god_mod.mp3")
    god_mod_sound.set_volume(0.2)
    player_death_sound = pygame.mixer.Sound("./music/player_death.wav")
    player_death_sound.set_volume(0.4)
    creature_death_sound = pygame.mixer.Sound("./music/creature_death.wav")
    creature_death_sound.set_volume(0.4)
    game_over_sound = pygame.mixer.Sound("./music/game_over.wav")
    game_over_sound.set_volume(0.5)

    sounds["background"] = background_sound
    sounds["collecting_warm"] = collecting_warm_sound
    sounds["god_mod"] = god_mod_sound
    sounds["player_death"] = player_death_sound
    sounds["creature_death"] = creature_death_sound
    sounds["game_over"] = game_over_sound

def moveCreatureFromCellToCell(creature: Creature, world: list[list[Cell]]):
    cell_size = 30
    x = creature.object.pos.x - X_MAP_ON_SCREEN
    y = creature.object.pos.y - Y_MAP_ON_SCREEN
    x = int(x/cell_size)
    y = int(y/cell_size)
    if len(world) > x >= 0 and len(world[0]) > y >= 0:
        if creature.object.cell is not None:
            creature.object.cell.creatures.remove(creature)
        world[x][y].creatures.append(creature)
        creature.object.cell = world[x][y]
    else:
        if creature.object.cell is not None:
            creature.object.cell.creatures.remove(creature)
        creature.object.cell = None


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    fonts: list[pygame.font.SysFont] = []
    fonts.append(pygame.font.SysFont("Calibri", 24))
    fonts.append(pygame.font.SysFont("Calibri", 74, bold=2))
    fonts.append(pygame.font.SysFont("Calibri", 15, bold=1))
    # zegar gry
    clock: pygame.time.Clock = pygame.time.Clock()
    # czy dziągle gramy
    run: bool = True
    # Grafiki
    sprites: dict[str: list[pygame.image]] = {}
    loadSprites(sprites)
    # Dźwięki
    sounds: dict[str: pygame.mixer.Sound] = {}
    loadSounds(sounds)
    # start muzyki
    pygame.mixer.Sound.play(sounds["background"], loops=-1)
    # mapa
    world: list[list[Cell]] = []

    level: int = 1
    max_level: int = 4
    game_over_played: bool = False
    objects: list[Object] = []
    worms: list[Worm] = []
    creatures: list[Creature] = []
    spawn_position = generateLevel(level, world, objects, worms, creatures)
    selected_object: Object = creatures[0].object

    dtime: float = 0.0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                creatures.clear()
                objects.clear()
                worms.clear()
                level = 1
                generateLevel(level, world, objects, worms, creatures)
                game_over_played = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                creatures[0].object.vel.y = -120
                creatures[0].object.vel.x = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                creatures[0].object.vel.y = 120
                creatures[0].object.vel.x = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                creatures[0].object.vel.x = -120
                creatures[0].object.vel.y = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                creatures[0].object.vel.x = 120
                creatures[0].object.vel.y = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if NUMBER_OF_PLAYERS == 1:
                    creatures[0].object.vel.y = -120
                    creatures[0].object.vel.x = 0
                elif NUMBER_OF_PLAYERS == 2:
                    creatures[1].object.vel.y = -120
                    creatures[1].object.vel.x = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if NUMBER_OF_PLAYERS == 1:
                    creatures[0].object.vel.y = 120
                    creatures[0].object.vel.x = 0
                elif NUMBER_OF_PLAYERS == 2:
                    creatures[1].object.vel.y = 120
                    creatures[1].object.vel.x = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                if NUMBER_OF_PLAYERS == 1:
                    creatures[0].object.vel.x = -120
                    creatures[0].object.vel.y = 0
                elif NUMBER_OF_PLAYERS == 2:
                    creatures[1].object.vel.x = -120
                    creatures[1].object.vel.y = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                if NUMBER_OF_PLAYERS == 1:
                    creatures[0].object.vel.x = 120
                    creatures[0].object.vel.y = 0
                elif NUMBER_OF_PLAYERS == 2:
                    creatures[1].object.vel.x = 120
                    creatures[1].object.vel.y = 0
        tick = clock.tick()
        dtime += tick
        draw_dtime = tick
        steal_alive: bool = False
        for i in range(NUMBER_OF_PLAYERS):
            if creatures[i].health > 0:
                steal_alive = True
        if not steal_alive and not game_over_played:
            pygame.mixer.Sound.play(sounds["game_over"])
            game_over_played = True
        while dtime > 16 and steal_alive:
            dtime -= 16
            if len(worms) != 0:
                update(objects, worms, creatures, spawn_position, level, world, sounds, 0.016)
            else: # kiedy skoncza sie robaki
                players: list = []
                for i in range(NUMBER_OF_PLAYERS):
                    player: Creature = creatures[i]
                    player.health += 2
                    player.object.pos = spawn_position.copyVector()
                    player.god_mod = False
                    player.object.vel.scale(0)
                    players.append(player)
                creatures.clear()
                for player in players:
                    creatures.append(player)
                objects.clear()
                if level < max_level:
                    level += 1
                generateLevel(level, world, objects, worms, creatures)
        fps = clock.get_fps()
        draw(screen, fonts, fps, objects, worms, creatures, world, sprites, sounds, draw_dtime)

    pygame.mixer.music.stop()
    pygame.quit()

