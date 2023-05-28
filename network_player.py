from settings import *
import pygame as pg
import math
import os
from collections import deque
from player import *

class network_player:
    def __init__(self, game, playerID=0, classId=0 ,name="Noname", x=0, y=0, angle=0, shot=False, health=100, rel=0, path='resources/sprites/npc/soldier/'):
        
        self.path = path
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')
        self.imagePath = 'resources/sprites/npc/soldier/0.png'
        self.image = pg.image.load(self.imagePath).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.playerID = playerID
        self.name = name
        self.game = game
        self.x = x
        self.y = y
        self.screenPos = (0,0)
        self.angle = angle #PLAYER_ANGLE
        self.angle_range = {}
        self.shot = shot
        self.health = health
        self.rel = rel
        self.frame_counter = 0
        self.alive = True
        self.death_images = 0
        self.classId = classId
        self.time_prev = pg.time.get_ticks()
        self.SPRITE_SCALE = 0.8
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.SPRITE_HEIGHT_SHIFT = 0.25
        self.ray_cast_value = False
        self.player_hit_event = pg.event.Event(self.game.player_hit_event,data=self.playerID)
        # diagonal movement correction
        self.diag_move_corr = 1 / math.sqrt(2)


    def set_player_id(self, id):
        print("Set network player id to ", id)
        self.playerID = id

    def get_player_id(self):
        return self.playerID
    
    def kill_Player(self):
        self.alive=False
    
    def revive_Player(self):
        self.alive=True

    def set_player_pos(self, cord):
        x,y = cord
        self.x = x
        self.y = y
    
    def set_player_health(self, hp):
        self.health = hp

    def set_player_name(self,name):
        self.name = name

    def set_player_angle(self, angle):
        self.angle = angle

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.image = self.idle_images
    
    def get_images(self, path):
        images = deque()
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + '/' + file_name).convert_alpha()
                images.append(img)
        return images
    
    def update(self):
        self.get_sprite()
        self.ray_cast_value = self.ray_cast_player_to_network_player()
        self.check_hit_in_player()
    
    def get_sprite_direction(self):
        sprite_directions = {
        #FRONT
        self.idle_images[0]: (157.5, 202.5),
        #LEFT_FRONT
        self.idle_images[1]: (202.5, 247.5),
        #LEFT_SIDE
        self.idle_images[2]: (247.5, 292.5),
        #LEFT BACK
        self.idle_images[3]: (292.5, 337.5),
        #BACK
        self.idle_images[4]: (337.5, 22.5),
        #RIGHT BACK
        self.idle_images[5]: (22.5, 67.5),
        #RIGHT
        self.idle_images[6]: (67.5, 112.5),
        #FRONT RIGHT
        self.idle_images[7]: (112.5, 157.5)
        
        }
        return sprite_directions
    
    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    
    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj

        image = pg.transform.scale(self.image, (proj_width, proj_height))

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = self.screen_x - self.sprite_half_width, HALF_HEIGHT - proj_height // 2 + height_shift

        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos, self))
        self.screenPos = pos
    
    def get_sprite(self):
        player = self.game.player

        dx = self.x - player.x
        dy = self.y - player.y
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        delta = self.theta - player.angle
        if (dx > 0 and player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        local_player_angle = math.degrees(self.game.player.angle)
        network_player_angle = math.degrees(self.angle)
        angle_difference = (network_player_angle - local_player_angle) % 360

        min_difference = float("inf")
        #closest_direction = None
        sprite_directions = self.get_sprite_direction()
        for direction, angle_range in sprite_directions.items():
            lower_bound, upper_bound = angle_range
            difference = abs(angle_difference - lower_bound)
            if difference < min_difference:
                min_difference = difference
                self.image = direction


        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()

    
    def ray_cast_player_to_network_player(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False
    
    def check_hit_in_player(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                pg.event.post(self.player_hit_event)


    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    