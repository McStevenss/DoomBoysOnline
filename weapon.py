from sprite_object import *
import pygame as pg

#resources/sprites/weapon/heal/0.png
class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/shotgun/0.png', scale=0.4, animation_time=90):

        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        # self.images = deque(
        #     [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
        #      for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50
        self.weapon_range = 999999
        self.weaponSound = pg.mixer.Sound("resources/sound/" + 'shotgun.wav')

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()


class HealingSpell(Weapon):
    def __init__(self, game):
        super().__init__(game, path="resources/sprites/weapon/heal/0.png", animation_time= 50)
        self.scale = 3
        self.images = deque(
            [pg.transform.scale(img, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))
             for img in self.images])
        self.weapon_pos = (0, HEIGHT - self.images[0].get_height())

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50

        self.weaponSound = pg.mixer.Sound("resources/sound/" + 'MAGIC02.wav')

class Dagger(Weapon):
    def __init__(self, game):
        super().__init__(game, path="resources/sprites/weapon/dagger/0.png")
        self.scale = 3
        self.images = deque(
            [pg.transform.scale(img, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))
             for img in self.images])
        self.weapon_pos = (WIDTH - self.images[0].get_width() * 1.5, HEIGHT - self.images[0].get_height())

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50

        self.weapon_range = 1
        self.weaponSound = pg.mixer.Sound("resources/sound/" + 'SWING03.wav')


class Axe(Weapon):
    def __init__(self, game):
        super().__init__(game, path="resources/sprites/weapon/axe/0.png")
        self.scale = 3
        scaled_images = deque()
        for img in self.images:
            scaled_img = pg.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            scaled_images.append(scaled_img)
        
        self.images = scaled_images
        self.weapon_pos = (WIDTH - self.images[0].get_width() - 125 , HEIGHT - self.images[0].get_height())

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50
        self.weapon_range = 1.5
        self.weaponSound = pg.mixer.Sound("resources/sound/" + 'SWING04.wav')

class Bow(Weapon):
    def __init__(self, game):
        super().__init__(game, path="resources/sprites/weapon/bow/0.png", animation_time= 50)
        self.scale = 3

        scaled_images = deque()

        for img in self.images:
            scaled_img = pg.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            scaled_images.append(scaled_img)
        
        self.images = scaled_images
        self.weapon_pos = (WIDTH - self.images[0].get_width() - 125 , HEIGHT - self.images[0].get_height())

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50

        self.weapon_range = 10
        self.weaponSound = pg.mixer.Sound("resources/sound/" + 'ARROW01.wav')
        #self.crosshairImage = self.get_images("resources/sprites/weapon/crosshair/")
        self.crosshair = self.crosshairImage = pg.image.load("resources/sprites/weapon/crosshair/0.png").convert_alpha()
        self.crosshair = pg.image.load("resources/sprites/weapon/crosshair/0.png").convert_alpha()

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)
        self.game.screen.blit(self.crosshair, (WIDTH//2,HEIGHT//2))




class Bear_Claw(Weapon):
    def __init__(self, game):
        super().__init__(game, path="resources/sprites/weapon/bear_form/0.png", animation_time= 160)      
        self.scale = 3
        # self.images = deque(
        #     [pg.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
        #     for img in self.images])
        scaled_images = deque()
        for img in self.images:
            scaled_img = pg.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            scaled_images.append(scaled_img)
        
        self.images = scaled_images
        
        self.weapon_pos = (WIDTH - self.images[0].get_width() * 1.2, HEIGHT - self.images[0].get_height())

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50
        self.weaponSound = pg.mixer.Sound("resources/sound/" + 'MNSTER19.wav')
        self.weapon_range = 10