from settings import *
import pygame as pg
import math
from collections import deque
import os

class BasePlayer:
    def __init__(self, game):
        self.path='resources/sprites/players/Druid/'
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')
        self.playerID = 0
        self.name = "default"
        self.game = game
        #self.x, self.y = PLAYER_POS
        self.x, self.y = self.game.map.spawnX, self.game.map.spawnY
        self.angle = PLAYER_ANGLE
        self.angleDeg = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.alive = True
        self.class_Id = 0 #DEFAULT CLASS
        self.dx, self.dy = 0,0


    def get_images(self, path):
        images = deque()
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + '/' + file_name).convert_alpha()
                images.append(img)
        return images

class Player(BasePlayer):
    def __init__(self, game):
        super().__init__(game)
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        self.class_id = 0
        # diagonal movement correction
        self.diag_move_corr = 1 / math.sqrt(2)
        self.prevx = 0
        self.prevy = 0
        self.prevAngle = 0
        self.hasMoved = True
        self.prevDx, self.prevDy = 0,0
        self.font_small = pg.font.Font('freesansbold.ttf', 25)
        self.spells = []
        

    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True
    
    def set_player_id(self, id):
        self.playerID = id

    def set_player_class(self,classId):
        self.class_id = classId

    def set_player_name(self, name):
        self.name = name

    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                self.game.weapon.weaponSound.play()
                #self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True
                self.game.send_message(['attacked',self.playerID])

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

        self.dx, self.dy = dx, dy
        if self.x != self.prevx or self.y != self.prevy or self.prevDx != self.dx or self.prevDy != self.dy:
            self.hasMoved = True

        self.check_wall_collision(dx, dy)

        #FOR KEY MOVEMENTS
        # if keys[pg.K_LEFT]:
        #     self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # if keys[pg.K_RIGHT]:
        #     self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.angle %= math.tau

    def execute_player_actions(self,game,event):
        #Check spells
        if event.type == pg.KEYUP and event.key == pg.K_1:
            print("Cast spell one!")
            try:
                print("Spell", self.spells[0].name)
                self.spells[0].cast()
            except:
                print("no spell")

        if event.type == pg.KEYUP and event.key == pg.K_2:
            print("Cast spell two!")
            try:
                print("Spell", self.spells[1].name)
                self.spells[1].cast()
            except:
                print("no spell")

        if event.type == pg.KEYUP and event.key == pg.K_3:
            print("Cast spell three!")
            try:
                print("Spell", self.spells[2].name)
                self.spells[2].cast()
            except:
                print("no spell")

        if event.type == pg.KEYUP and event.key == pg.K_4:
            print("Cast spell four!")
            try:
                print("Spell", self.spells[3].name)
            except:
                print("no spell")



    def actionbar(self):
        y_slot = 2
        white = (255, 255, 255)
        spells = 4
        #action bar
        pg.draw.rect(self.game.screen, (255, 0, 0), (0, HEIGHT- HEIGHT//y_slot, 325, 100))


        #spell 1
        for i in range(spells):
            
            pg.draw.rect(self.game.screen, (0, 255, 0), (25+75*i, HEIGHT- HEIGHT//y_slot + 25, 50, 50))
            if i < len(self.spells):
                self.game.screen.blit(self.spells[i].hud_icon, (25+75*i, HEIGHT- HEIGHT//y_slot + 25))
            text = self.font_small.render(f"{i+1}", True, white)
            self.game.screen.blit(text,(25+85*i, HEIGHT- HEIGHT//y_slot + 75))


    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def draw(self):
        pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100),
                    (self.x * 100 + WIDTH * math.cos(self.angle),
                     self.y * 100 + WIDTH * math. sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

        if self.angle != self.prevAngle:
            self.hasMoved = True

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()
        self.actionbar()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)