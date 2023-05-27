from settings import *
import pygame as pg
import math
from network_player import *




class player_list:

    player_list = {}

    def add_player(self, player: network_player, id):
        if id not in self.player_list:
            self.player_list[id] = player

    def get_players(self):
        return self.player_list
    
    def set_playerList(self, new_playerList):
        self.player_list = new_playerList


