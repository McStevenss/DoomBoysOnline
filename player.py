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
        self.max_health = PLAYER_MAX_HEALTH
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
        self.speed = 0.004
        self.font_small = pg.font.Font('freesansbold.ttf', 25)

        self.resource_pool = 100
        self.resource_name = "Mana"
        self.resource_regen = 1
        self.resource_color = (0,0,255)
        self.max_resource = 100

        self.armor = 1
        self.spells = []
        self.active_spell = None
        self.effects = []
        
        self.regenerate = False
        self.totalRegenerated = 0

        self.poison = False
        self.totalPoisoned = 0
        

    def recover_health(self):
        if self.check_health_recovery_delay() and self.regenerate and self.health < self.max_health:
            self.health += 2
            self.totalRegenerated += 2
        
        if self.totalRegenerated > 25:
            self.regenerate = False
            self.totalRegenerated = 0

    def recover_resource(self):
        if self.check_health_recovery_delay() and self.resource_pool < self.max_resource:
            self.resource_pool += self.resource_regen

    def poison_tick(self):
        if self.check_health_recovery_delay() and self.poison:
            self.health -= 2
            self.totalPoisoned += 2
        
        if self.totalPoisoned > 25:
            self.poison = False
            self.totalPoisoned = 0

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

        #calculate damage from armor reduction
        dmg_multiplier = damage / (damage + self.armor)
        actual_damage = damage * dmg_multiplier
        self.health -= int(actual_damage)
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                #self.game.sound.shotgun.play()
                #self.game.send_message(['attacked',self.playerID])

                #Use weapon
                if not self.game.weapon.isSpell:
                    self.game.weapon.weaponSound.play()
                    self.shot = True
                    self.game.weapon.reloading = True

    def get_effect_durations(self):
        for effect in self.effects:
            duration_left = effect.get_effect_duration_left()
            if duration_left <= 0:
                effect.remove_effect()
                self.effects.remove(effect)

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        
        speed = self.speed * self.game.delta_time
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

    def execute_player_actions(self,event):
        #Check spells
        if event.type == pg.KEYUP and event.key == pg.K_1:
            if len(self.spells) >= 1:
                print("Cast spell", self.spells[0].name)

                self.active_spell = self.spells[0]
                self.game.send_message(['cast_spell', self.playerID, 0])

                self.active_spell.cast()
                #Animate weapon after spell is cast
                self.game.weapon.weaponSound.play()
                self.shot = True
                self.game.weapon.reloading = True

        if event.type == pg.KEYUP and event.key == pg.K_2:
            if len(self.spells) >= 2:
                print("Cast spell", self.spells[1].name)

                self.active_spell = self.spells[1]
                self.game.send_message(['cast_spell', self.playerID, 1])
                #Animate weapon after spell is cast
                self.active_spell.cast()
                self.resource_pool - self.active_spell.cost
                self.game.weapon.weaponSound.play()
                self.shot = True
                self.game.weapon.reloading = True

        if event.type == pg.KEYUP and event.key == pg.K_3:
            if len(self.spells) >= 3:
                print("Cast spell", self.spells[2].name)

                self.active_spell = self.spells[2]
                self.game.send_message(['cast_spell', self.playerID, 2])

                #Animate weapon after spell is cast
                self.active_spell.cast()
                self.game.weapon.weaponSound.play()
                self.shot = True
                self.game.weapon.reloading = True

        if event.type == pg.KEYUP and event.key == pg.K_4:
            if len(self.spells) >= 4:
                print("Cast spell", self.spells[3].name)

                self.active_spell = self.spells[3]
                self.game.send_message(['cast_spell', self.playerID, 3])

                #Animate weapon after spell is cast
                self.active_spell.cast()
                self.game.weapon.weaponSound.play()
                self.shot = True
                self.game.weapon.reloading = True



    def actionbar(self):
        y_slot = 2
        white = (255, 255, 255)
        #action bar
        pg.draw.rect(self.game.screen, (135,135, 135), (0, HEIGHT- HEIGHT//y_slot, 325, 100))


        #spell 1
        for i, spell in enumerate(self.spells):
            
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
        self.recover_resource()
        self.actionbar()
        self.get_effect_durations()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)