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

        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))
    
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



    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        num_key_pressed = -1
        if keys[pg.K_w]:
            num_key_pressed += 1
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            num_key_pressed += 1
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            num_key_pressed += 1
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            num_key_pressed += 1
            dx += -speed_sin
            dy += speed_cos

        # diag move correction
        if num_key_pressed:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr

        self.check_wall_collision(dx, dy)

        # if keys[pg.K_LEFT]:
        #     self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # if keys[pg.K_RIGHT]:
        #     self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.angle %= math.tau


    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    