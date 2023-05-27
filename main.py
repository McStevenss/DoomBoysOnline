from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from server_client_utils import *
from player_list import *

import pickle
import select
import socket

BUFFERSIZE = 2048

print("Welcome to DOOM-boys-Online!")
print("Please choose class: [0] Archer, [1] Knight, [2] Healer, [3] Mage")
player_class = input("Class:")
player_class = int(player_class)


classes = ["Archer", "Knight", "Healer", "Mage"]

player_class = player_class % len(classes)

print("You chose:", classes[player_class])

print("Whats your name:")
player_name = input("Name:")
print("Welcome", player_name)


serverAddr = '127.0.0.1'
if len(sys.argv) == 2:
  serverAddr = sys.argv[1]

s = connect_to_server(serverAddr)

Player_list = player_list()

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()
 

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        self.player.set_player_class(player_class)
        self.player.set_player_name(player_name)
        pg.mixer.music.play(-1)

    def update(self):
        self.player.update()
        self.raycasting.update()
        test = Player_list.get_players()
        self.object_handler.update(Player_list.get_players())
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()

        #HUD
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        #self.player = Player(self)
        while True:
            #Networking
            handle_connection(self, self.player, s, Player_list)
            updatePlayerOnServer(s, self.player)

            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
