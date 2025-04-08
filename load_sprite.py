
import pygame


def getImage(sheet, frame, width, height, colour):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), area=(width * frame, 0, width, height))
    # image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(colour)
    return image

def loadSprites():
    sprites: list[list[pygame.image]]
    invisible_color = (255, 255, 255)
    # player idle 1
    img = pygame.image.load("./src/player/player_idle.png")
    animation: list[pygame.image] = []
    for i in range(5):
        animation.append(getImage(img, i, 47, 62, invisible_color))
    sprites.append(animation)

    # player move 2
    img = pygame.image.load("./src/player/player_move.png")
    animation: list[pygame.image] = []
    for i in range(5):
        animation.append(getImage(img, i, 47, 62, invisible_color))
    sprites.append(animation)

    # player death 3
    img = pygame.image.load("./src/player/player_death.png")
    animation: list[pygame.image] = []
    for i in range(5):
        animation.append(getImage(img, i, 47, 62, invisible_color))
    sprites.append(animation)

    # player corps 4
    img = pygame.image.load("./src/player/player_corps.png")
    animation: list[pygame.image] = []
    for i in range(5):
        animation.append(getImage(img, i, 47, 62, invisible_color))
    sprites.append(animation)

    # player cast spell 5
    img = pygame.image.load("./src/player/player_cast_spell.png")
    animation: list[pygame.image] = []
    for i in range(10):
        animation.append(getImage(img, i, 47, 62, invisible_color))
    sprites.append(animation)

    # player ult 6
    img = pygame.image.load("./src/player/player_ult.png")
    animation: list[pygame.image] = []
    for i in range(10):
        animation.append(getImage(img, i, 500, 500, invisible_color))
    sprites.append(animation)

    return sprites
