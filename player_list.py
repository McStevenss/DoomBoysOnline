from settings import *
import pygame as pg
import math
import network_player




class player_list:

    player_list = {}

    def add_player(self, player: network_player, id):
        #refresh list
        new_list = self.get_players()
        new_list[id] = player
        self.set_playerList(new_list)
        print("Added new player")
    

    def get_players(self):
        return self.player_list
    
    def set_playerList(self, new_playerList):
        self.player_list = new_playerList


