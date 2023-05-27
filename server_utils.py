import socket
import asyncore
import random
import pickle
import time

from network_player import *
from player import *

class Player:
  def __init__(self, playerID, name = "Noname", Class = 0, x = 1.5, y=5,health= 100, angle = 0):
    self.playerID = playerID
    self.name = name
    self.x = x 
    self.y = y
    self.Class = Class
    self.health = health
    self.angle = angle


def handle_message(message, outgoing, player_list):
    #FUNCTION RETURNS UPDATE MESSAGE
    remove = []
    #update position/world if game event is pos update
    if message[0] == 'position_update':
        playerid = message[1]
        x = message[2]
        y = message[3]
        health = message[4]
        angle = message[5]

        player_list[playerid].x = x
        player_list[playerid].y = y
        player_list[playerid].health = health
        player_list[playerid].angle = angle
        message[0] = 'player_locations'

    if message[0] == 'new_player':
        playerid = message[1]
        playerName = message[2]
        playerClass = message[3]

        if playerid not in player_list:
            player_list[playerid] = Player(playerid,playerName,playerClass)

        update = message


    for i,id in outgoing:

        if message[0] != 'new_player':
            update = [message[0]]

        for key, value in player_list.items():
            update.append([value.playerID, value.x, value.y, value.Class, value.health, value.angle])

        print(f"sent: {update}")
        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        for r in remove:
            outgoing.remove(r)
    return player_list
