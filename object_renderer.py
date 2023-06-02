import pygame as pg
from settings import *
from classes import *

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 90
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)

        self.font = pg.font.Font('freesansbold.ttf', 32)



    def draw(self):
        self.draw_background()
        self.render_game_objects()
        #self.draw_player_health()
        self.draw_HUD()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        
        for i in range(len(list_objects)):

            if len(list_objects[i]) != 4:
                depth, image, pos = list_objects[i]

                self.screen.blit(image, pos)
            else:
                depth, image, pos, player = list_objects[i]
                if depth < 11:
                    green = (0, 255, 0)
                    text = self.font.render(f'{player.name}', True, green)
                    textRect = text.get_rect()

                    proj = SCREEN_DIST / player.norm_dist * player.SPRITE_SCALE
                    proj_width, proj_height = proj * player.IMAGE_RATIO, proj

                    textRect.center = (player.screenPos[0] + proj_width // 2, player.screenPos[1] + proj_height)
                    self.screen.blit(text,textRect)

                self.screen.blit(image, pos)


    def draw_HUD(self):
        self.draw_health()

    def draw_health(self):
        green = (255, 0, 0)
        text = self.font.render(f'Health: {self.game.player.health}', True, green)
        textRect = text.get_rect()   
        self.screen.blit(text,(textRect.x, textRect.y + HEIGHT - 50))


    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)


    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
            6: self.get_texture('resources/textures/city/door.png'),
            7: self.get_texture('resources/textures/city/mosswall_window.png'),
            8: self.get_texture('resources/textures/city/mosswall.png'),
            9: self.get_texture('resources/textures/city/stonewall.png'),
            10: self.get_texture('resources/textures/fort/wall1.png'),
            11: self.get_texture('resources/textures/fort/wall2.png'),
            12: self.get_texture('resources/textures/fort/wall3.png'),
            13: self.get_texture('resources/textures/mudhut/mud_door.png'),
            14: self.get_texture('resources/textures/mudhut/mud_wall.png'),
            15: self.get_texture('resources/textures/mudhut/mud_window.png')
        }