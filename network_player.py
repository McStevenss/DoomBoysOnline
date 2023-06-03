from settings import *
import pygame as pg
import math
import os
from collections import deque
from player import *

class network_player(BasePlayer):
    def __init__(self, game, playerID=0, class_Id=0 ,name="Noname", x=0, y=0, angle=0, shot=False, health=100, rel=0, path='resources/sprites/players/Druid/'):
        super().__init__(game)
        self.playerID = playerID
        self.name = name
        self.x, self.y = x,y
        self.prevX = self.x
        self.prevY = self.y
        self.class_Id= class_Id
        self.game = game
        self.path = path
        self.attack_images = self.get_animation(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_animation(self.path + '/pain')
        self.walk_images = self.get_animation(self.path + '/walk')
        self.imagePath = 'resources/sprites/npc/soldier/0.png'
        self.image = pg.image.load(self.imagePath).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.playerID = playerID #
        self.screenPos = (0,0)
        self.angle = angle #PLAYER_ANGLE
        self.angle_range = {}
        self.shot = shot
        self.health = health
        self.rel = rel
        self.frame_counter = 0
        self.alive = True
        self.hasAttacked = False
        self.hasMoved = False
        self.pain = False
        self.death_images = 0
        self.time_prev = pg.time.get_ticks()
        self.SPRITE_SCALE = 0.8
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.SPRITE_HEIGHT_SHIFT = 0.25
        self.ray_cast_value = False
        self.ray_cast_range = 0
        self.player_hit_event = pg.event.Event(self.game.player_hit_event,data=self.playerID)
        self.animation_time = 90
        self.animation_trigger = False
        self.animation_time_prev = pg.time.get_ticks()

        self.attack_animation_time_prev = pg.time.get_ticks()
        self.attack_animation_trigger = False
        self.attack_frame_counter = 0
        self.spells = []

    def change_player_model(self, model_path="resources/sprites/players/Rogue"):
        self.path = model_path
        self.attack_images = self.get_animation(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_animation(self.path + '/pain')
        self.walk_images = self.get_animation(self.path + '/walk')

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

    def animate_pain(self, angle_difference):
        player_direction = self.get_player_direction(angle_difference)

        if self.pain and self.animation_trigger:
            self.pain_images[player_direction].rotate(-1)
            self.image = self.pain_images[player_direction][0]
            self.frame_counter += 1
            
        elif self.frame_counter > len(self.pain_images[player_direction]) * 12 - 1:
            self.pain = False
            self.frame_counter = 0   

    def animate(self):
        local_player_angle = math.degrees(self.game.player.angle)
        network_player_angle = math.degrees(self.angle)
        angle_difference = (network_player_angle - local_player_angle) % 360

        if self.hasAttacked:
            self.animate_attack(angle_difference)
            return
        
        if self.hasMoved:
            self.animate_walking(angle_difference)
            return
        
        if self.pain:
            self.animate_pain(angle_difference)
            return

        #default anim
        self.animate_idle(angle_difference)
        
    def animate_walking(self, angle_difference):
        player_direction = self.get_player_direction(angle_difference)

        if self.animation_trigger and self.animation_trigger:
            self.walk_images[player_direction].rotate(-1)
            self.image = self.walk_images[player_direction][0]
            self.frame_counter += 1
            
        elif self.frame_counter > len(self.walk_images[player_direction]) - 1:
            self.hasMoved = False
            self.frame_counter = 0

    def animate_attack(self, angle_difference):

        player_direction = self.get_player_direction(angle_difference)

        if self.hasAttacked and self.attack_animation_trigger: #and self.frame_counter < len(self.attack_images) - 1:
            self.attack_images[player_direction].rotate(-1)
            self.image = self.attack_images[player_direction][0]
            self.attack_frame_counter += 1
        elif self.attack_frame_counter > len(self.attack_images[player_direction]) - 1:
            self.hasAttacked = False
            self.attack_frame_counter = 0

    def animate_idle(self, angle_difference):
            player_direction = self.get_player_direction(angle_difference)
            self.image = self.idle_images[player_direction]
            
    def get_images(self, path):
        images = deque()
        print(path)
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + '/' + file_name).convert_alpha()
                images.append(img)
        return images
    
    def get_animation(self, path):
        walk_images = {i: deque() for i in range(8)}

        for walk_direction in os.listdir(path):
            walk_dir_path = os.path.join(path, walk_direction)

            for image in os.listdir(walk_dir_path):
                img_path = os.path.join(path, walk_direction,image)
                if os.path.isfile(img_path):
                    if int(walk_direction) == 1:
                        img = pg.image.load(img_path).convert_alpha()
                        flipped_image = pg.transform.flip(img, True, False)
                        walk_images[7].append(flipped_image)
                    if int(walk_direction) == 2:
                        img = pg.image.load(img_path).convert_alpha()
                        flipped_image = pg.transform.flip(img, True, False)
                        walk_images[6].append(flipped_image)
                    if int(walk_direction) == 3:
                        img = pg.image.load(img_path).convert_alpha()
                        flipped_image = pg.transform.flip(img, True, False)
                        walk_images[5].append(flipped_image)
                    
                    img = pg.image.load(img_path).convert_alpha()
                    walk_images[int(walk_direction)].append(img)
        return walk_images
    
    def checkIfMoved(self):
        if self.prevX != self.x and self.prevY != self.y:
            self.hasMoved = True
            self.prevX = self.x
            self.prevY = self.y
    
    def update(self):
        self.get_sprite()
        self.check_animation_time()
        self.check_attack_animation_time()
        self.animate()
        self.checkIfMoved()
        self.ray_cast_value, self.ray_cast_range = self.ray_cast_player_to_network_player()
        self.check_hit_in_player()
        #self.animate_attack()    
    
    def execute_network_player_spell(self,spellIndex):
        self.spells[spellIndex].cast()



    def get_player_direction(self, angle_difference):
        # Define the angle ranges for each direction
        direction_ranges = {
            0: (180,225), #Back
            1: (225,270), #Back Left
            2: (270,315), #Left
            3: (315,360), #Left Front
            4: (0,45),    #Front
            5: (45,90),    #Front Right
            6: (90,135),   #Right
            7: (135,180)   #Back Right
        }
        min_difference = float("inf")
        network_player_direction = 0 #0 default
        for direction, (lower_bound, upper_bound) in direction_ranges.items():
            difference = abs(angle_difference - lower_bound)
            if difference < min_difference:
                     min_difference = difference
                     network_player_direction = direction
        return network_player_direction  # Default direction (Front)
    
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

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()
    
    def ray_cast_player_to_network_player(self):
        if self.game.player.map_pos == self.map_pos:
            return True, 0

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
            return True, player_dist
        return False, player_dist
    
    def check_hit_in_player(self):
        if self.ray_cast_value and self.game.player.shot and self.ray_cast_range < self.game.weapon.weapon_range:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:

                self.pain = True
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                pg.event.post(self.player_hit_event)


    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True


    def check_attack_animation_time(self):
        self.attack_animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.attack_animation_time_prev > self.animation_time:
            self.attack_animation_time_prev = time_now
            self.attack_animation_trigger = True

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    