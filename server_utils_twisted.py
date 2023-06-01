import socket
import asyncore
import random
import pickle
import time

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


def broadcast_to_clients(message,outgoing, player_list):
    remove = []

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

def handle_message_twisted(connections, message, outgoing, player_list):      
    update = None
    
    #Tell players that a player moved
    if message[0] == 'position_update':
        playerid = message[1]
        x = message[2]
        y = message[3]
        health = message[4]
        angle = message[5]
        dx = message[6]
        dy = message[7]

        player_list[playerid].x = x
        player_list[playerid].y = y
        player_list[playerid].health = health
        player_list[playerid].angle = angle
        message[0] = 'player_locations'
        update = [message[0]]
        update.append([playerid, player_list[playerid].name ,x, y, player_list[playerid].Class, health, angle, dx, dy])

    #Tell players a certain player got damaged
    if message[0] == 'damaged_player':
        damaged_player_id = message[1]
        damage = message[2]
        damaging_player_id = message[3]
        player_list[damaged_player_id].health = player_list[damaged_player_id].health - damage
        update = message

    #Tell players that a new player has joined
    if message[0] == 'new_player':
        print("New player joined!")
        playerid = message[1]
        playerName = message[2]
        playerClass = message[3]

        # if playerid not in player_list:
        player_list[playerid] = Player(playerid,playerName,playerClass)

        update = message

    #Tell players that one player just performed an attack
    if message[0] == 'attacked':      
        playerid = message[1]
        update = message

    if update == None:
        print("unknown command:", message)

    if update != None:
        for connection in connections.keys():
            connection.sendData(update)
    # for i,id in outgoing:

    #     try:
    #         i.send(pickle.dumps(update))
    #     except Exception:
    #         if id in player_list:
    #             remove.append(i)
    #         continue

    #     for r in remove:
    #         outgoing.remove(r)


    return player_list
