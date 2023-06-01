import math

# game settings
RES = WIDTH, HEIGHT = 1280, 720
# RES = WIDTH, HEIGHT = 1920, 1080
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 0

PLAYER_POS = 1.5, 5  # mini_map
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100

MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

FLOOR_COLOR = (112, 110, 109)

FOV = math.pi / 2
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# def load_wall_textures(self):
#     return {
#         1: self.get_texture('resources/textures/1.png'),
#         2: self.get_texture('resources/textures/2.png'),
#         3: self.get_texture('resources/textures/3.png'),
#         4: self.get_texture('resources/textures/4.png'),
#         5: self.get_texture('resources/textures/5.png'),
#         6: self.get_texture('resources/textures/city/door.png'),
#         7: self.get_texture('resources/textures/city/mosswall_window.png'),
#         8: self.get_texture('resources/textures/city/mosswall.png'),
#         9: self.get_texture('resources/textures/city/stonewall.png'),
#         10: self.get_texture('resources/textures/fort/wall1.png'),
#         11: self.get_texture('resources/textures/fort/wall2.png'),
#         12: self.get_texture('resources/textures/fort/wall3.png'),
#         13: self.get_texture('resources/textures/mudhut/mud_door.png'),
#         14: self.get_texture('resources/textures/mudhut/mud_wall.png'),
#         15: self.get_texture('resources/textures/mudhut/mud_window.png'),

#     }

#CITY TILES
city_door = (127,0,1)
city_mosswall_window = (150,0,1)
city_mosswall = (255,0,1)
city_stonewall = (75,0,1)

#FORT TILES
fort_wall_1 = (0,25,2)
fort_wall_2 = (0,50,2)
fort_wall_3 = (0,75,2)

#MUDHUT TILES
mudhut_door = (1,0,25)
mudhut_wall = (1,0,50)
mudhut_window = (1,0,75)


#DEFAULT TILES
floorColor = (255,255,255)
wallColor = (0,0,0)

COLOR_TO_TEXTURE = {
    floorColor: False,
    wallColor: 5,
    city_door: 6,
    city_mosswall_window: 7,
    city_mosswall: 8,
    city_stonewall: 9,
    fort_wall_1: 10,
    fort_wall_2: 11,
    fort_wall_3: 12,
    mudhut_door: 13,
    mudhut_wall: 14,
    mudhut_window: 15
    }