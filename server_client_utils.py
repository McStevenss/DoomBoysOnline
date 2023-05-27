import socket
import asyncore
import random
import pickle
import time
from player import *
from network_player import *
from player_list import *

import pickle
import select
import socket

BUFFERSIZE = 20480


def connect_to_server(address):
    try:
        print("Connecting to gameworld...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, 4321))
    except:
        print("Failed to connect to server....")

    return s

def handle_connection(game, player: Player, s, playerList: player_list):
    ins, outs, ex = select.select([s], [], [], 0)
    for inm in ins: 
        gameEvent = pickle.loads(inm.recv(BUFFERSIZE))


        # if gameEvent[0] == 'heartbeat':
        #    continue

        if gameEvent[0] == 'id update':
            playerid = gameEvent[1]

            print("Your player id:", playerid)
            player.set_player_id(playerid)

            #Tell other players a new player has connected
            s.send(pickle.dumps(['new_player', playerid, player.name ,player.class_id]))

        if gameEvent[0] == 'existing_players':
            gameEvent.pop(0)
            for player_data in gameEvent:
               playerId = player_data[0]
               playerName = player_data[1]
               player_x, player_y = player_data[2], player_data[3]
               player_class = player_data[4]
               player_hp = player_data[5]
               angle = player_data[6]
               existing_player = network_player(game,playerId,player_class,playerName, player_x,player_y,angle,health=player_hp)
               playerList.add_player(existing_player, playerId)

        if gameEvent[0] == 'remove_player':
            #removing unresponsive players
            new_player_list = playerList.get_players()
            del new_player_list[gameEvent[1]]
            playerList.set_playerList(new_player_list)

        if gameEvent[0] == 'new_player':
            playerId = gameEvent[1]
            playerName = gameEvent[2]
            playerClass = gameEvent[3]
            print(f"New player | ID:{playerId} Name:{playerName} Class:{playerClass}")
            #only update network players
            if playerId != player.playerID:
                
                #New player connected, construct new player
                new_Player = network_player(game, playerId, playerClass ,playerName, 1.5, 5, 0, False, 100, 0, path='resources/sprites/npc/soldier/')
                #Register new player in list
                print(f"New player connected! ID:{playerId} Name:{playerName}")
                playerList.add_player(player=new_Player, id=playerId)

        if gameEvent[0] == 'player_locations':
            gameEvent.pop(0)
            Player_list = playerList.get_players()

            #loop through each player location
            for player_data in gameEvent:
                if player_data[0] != player.playerID:
                    if player_data[0] not in Player_list:
                        new_player = network_player(game,  player_data[0], player_data[2] ,player_data[1], 1.5, 5, 0, False, 100, 0, path='resources/sprites/npc/soldier/')
                        Player_list[player_data[0]] = new_player
                    else:
                        Player_list[player_data[0]].x = player_data[1]
                        Player_list[player_data[0]].y = player_data[2]

            
            playerList.set_playerList(Player_list)







def updatePlayerOnServer(s, player: Player):
    if player.hasMoved == True:
        s.send(pickle.dumps(['position_update', player.playerID, player.x, player.y, player.health, player.angle]))
        player.hasMoved = False
        player.prevx = player.x
        player.prevy = player.y
