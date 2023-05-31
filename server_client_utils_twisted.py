from twisted.internet import reactor, protocol
from twisted.internet.protocol import ClientFactory
import asyncore
import random
import pickle
import time
from player import *
from player_list import *
from network_player import *

import pickle
import select
import json

class ClientProtocol(protocol.Protocol):
    player = None
    playerList = None
    game = None
    def __init__(self, player, playerList, game):
        self.player = player
        self.playerList = playerList
        self.game = game

    def connectionMade(self):
        #self.sendData(['new_player', self.player.playerID, self.player.name, self.player.class_id])
        print("Connected to the game server")
        self.factory.client_instance = self

    def dataReceived(self, data):
        # Handle the received data
        gameEvent = pickle.loads(data)
        handle_connection(self.game, self.game.player, self.game.player_list, gameEvent)

    def connectionLost(self, reason):
        print("Disconnected from the game server")

    def sendData(self, data):
        self.transport.write(pickle.dumps(data))

def handle_game_event(game_event, player, player_list):
    print("recieved",game_event)

class EchoClientFactory(protocol.ClientFactory):
    protocol = ClientProtocol

    def __init__(self, player, player_list, game):
        self.player = player
        self.player_list = player_list
        self.client_instance = None
        self.game = game

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed:', reason.getErrorMessage())

    def clientConnectionLost(self, connector, reason):
        print('Connection lost:', reason.getErrorMessage())

    def buildProtocol(self, addr):
        protocol_instance = self.protocol(self.player, self.player_list, self.game)
        protocol_instance.factory = self
        return protocol_instance
    
    def sendData(self, data):
        if self.client_instance and self.client_instance.transport:
            print("Factory got data")
            self.client_instance.sendData(pickle.dumps(data))
        else:
            print("Cannot send data. Connection not established.")

def connect_to_server(address, game):
    client_factory = EchoClientFactory(game.player,game.player_list, game)
    game.clientConnection = client_factory
    reactor.connectTCP(address, 4321, client_factory)

def close_connection(client_connection):
    if client_connection and client_connection.protocol and client_connection.protocol.transport:
        client_connection.protocol.transport.loseConnection()




def handle_connection(game, player: Player, playerList: player_list, gameEvent):

    playerList = game.player_list_object
    #print("GE", gameEvent)
    if gameEvent[0] == 'id update':
        gameEvent.pop(0)
        playerid = gameEvent[0]
        print("Your player id:", playerid)
        player.set_player_id(playerid)
        gameEvent.pop(0)

        #Handle existing players
        if gameEvent[0][0] == 'existing_players': 
            gameEvent[0].pop(0)
            for player_data in gameEvent[0]:
                if player_data[0] != playerid:
                    playerId = player_data[0]
                    playerName = player_data[1]
                    player_x, player_y = player_data[2], player_data[3]
                    player_class = player_data[4]
                    player_hp = player_data[5]
                    angle = player_data[6]
                    existing_player = network_player(game,playerId,player_class,playerName, player_x,player_y,angle,health=player_hp)
                    playerList.add_player(existing_player, playerId)

        game.send_message(['new_player', playerid, player.name ,player.class_id])

    if gameEvent[0] == 'remove_player':
        print("trying to remove player", gameEvent[1])
        new_player_list = playerList.get_players()

        print("list", new_player_list)
        del new_player_list[gameEvent[1]]
        playerList.set_playerList(new_player_list)

    if gameEvent[0] == 'damaged_player':
        damaged_player_id = gameEvent[1]
        damage = gameEvent[2]
        if player.playerID != damaged_player_id:
            print("damaged player", damaged_player_id)
            print("player list", playerList)
            updated_player_list = playerList.get_players()
            updated_player_list[gameEvent[1]].health -= damage
            playerList.set_playerList(updated_player_list)
        else:
            print("You took damage!")
            if player.health - damage < 0:
                player.health = 0
            else:
                player.health -= damage

    if gameEvent[0] == 'new_player':
        playerId = gameEvent[1]
        playerName = gameEvent[2]
        playerClass = gameEvent[3]

        #only update network players)
        if playerId != player.playerID:       
            #New player connected, construct new player
            new_Player = network_player(game, playerId, playerClass ,playerName, 1.5, 5, 0, False, 100, 0, path='resources/sprites/npc/soldier/')
            #Register new player in list
            playerList.add_player(player=new_Player, id=playerId)
            print(f"New player | ID:{playerId} Name:{playerName} Class:{playerClass}")

    if gameEvent[0] == 'player_locations':
        gameEvent.pop(0)
        Player_list = playerList.get_players()

        #loop through each player location
        for player_data in gameEvent:
            #playerid, player_list[playerid].name ,x, y, player_list[playerid].Class, health, angle])
            if player_data[0] != player.playerID:
                Player_list[player_data[0]].x = player_data[2]
                Player_list[player_data[0]].y = player_data[3]
                Player_list[player_data[0]].name = player_data[1]
                Player_list[player_data[0]].health = player_data[5]
                Player_list[player_data[0]].angle = player_data[6]

        
        playerList.set_playerList(Player_list)

def updatePlayerOnServer(game, player: Player):
    if player.hasMoved == True:
        game.send_message(['position_update', player.playerID, player.x, player.y, player.health, player.angle])
        player.hasMoved = False
        player.prevx = player.x
        player.prevy = player.y
        player.prevAngle = player.angle




# def send_test_data(client_protocol):
#     print("trying to send")
#     if client_protocol.transport:
#         print("sending")
#         client_protocol.sendData("Test")