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
#from server_client_utils import *
from player_list import *
from server_client_utils_twisted import *
from classes import *

import pickle
import select
import socket
import json

BUFFERSIZE = 2048

print("Welcome to DOOM-boys-Online!")
print("Please choose class: [0] Druid, [1] Rogue, [2] Warrior")
player_class = input("Class:")

classes = ["Druid", "Rogue", "Warrior"]
player_class = int(player_class) % len(classes)
print("You chose:", classes[player_class])

player_name = input("Whats your name name:")
print("Welcome", player_name)

Player_list = player_list()

serverAddr = '127.0.0.1'
if len(sys.argv) == 2:
  serverAddr = sys.argv[1]

# s = connect_to_server(serverAddr)

#Jag tror att game objektet inte blir uppdaterat efter 

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.player = None
        self.global_event = pg.USEREVENT + 0
        self.player_hit_event = pg.USEREVENT + 1
        self.player_list = Player_list.get_players()
        self.player_list_object = Player_list
        pg.time.set_timer(self.global_event, 40)
        self.clientConnection = None
        self.isConnected = False
        self.map = Map(self)
        self.new_game()
 

    def new_game(self):
       # self.player = Player(self)
        self.player = get_class(player_class,self)
        self.player.set_player_name(player_name)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.player.set_player_class(player_class)
        #self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        self.clientConnection = None
        #connect_to_server(serverAddr,self)
        #pg.mixer.music.play(-1)

    def send_message(self, message):
        if self.clientConnection and self.clientConnection.client_instance:      
            self.clientConnection.client_instance.sendData(message)   
        else:
            print("Not connected to the server yet. Message not sent.")

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update(self.player_list)
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'FPS:{self.clock.get_fps() :.1f}, Playername: {player_name}, Class: {player_class}')


        #print("playerList:", len(self.player_list))
        #self.send_message("Hey lmao")
        reactor.iterate()

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()

        #HUD
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        self.global_trigger = False
        should_exit = False


        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                #s.send(pickle.dumps(['remove_player', self.player.playerID]))
                self.send_message(['remove_player', self.player.playerID])
                close_connection(self.clientConnection)
                should_exit = True  # Set the flag to exit the game

            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

            if event.type == self.player_hit_event:
                self.send_message(['damaged_player', event.data, self.weapon.damage, self.player.playerID])
                print("Network player hit:", event.data, "dmg:", self.weapon.damage)

            self.player.execute_player_actions(self,event)

        if should_exit:
            reactor.stop()
            os._exit(1)


    def run(self):
        #self.player = Player(self)
        while True:
            #Networking
            #handle_connection(self, self.player, s, Player_list)
            updatePlayerOnServer(self, self.player)

            # if self.clientConnection != None:

            
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    reactor.callWhenRunning(connect_to_server,serverAddr, game)
    reactor.callWhenRunning(game.run)
    reactor.run()
    
