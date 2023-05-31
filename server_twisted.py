import socket
import asyncore
import random
import pickle
import time
#from server_utils import handle_message
from server_utils_twisted import handle_message_twisted

import threading

from twisted.internet import reactor, protocol
from twisted.protocols import basic
import json

BUFFERSIZE = 512
HEARTBEAT_INTERVAL = 5

global outgoing
global connections
global player_list
global g_player_id

outgoing = []
connections= {}
player_list = {}
g_player_id = 0




class Player:
  def __init__(self, playerID, name = "Noname", Class = 0, x = 1.5, y=5,health= 100, angle = 0):
    self.playerID = playerID
    self.name = name
    self.x = x 
    self.y = y
    self.Class = Class
    self.health = health
    self.angle = angle



def updateWorld(connections, message, player_list):
  #global player_list
  #global outgoing

  game_data = pickle.loads(message)
  updated_player_list = handle_message_twisted(connections, game_data, outgoing ,player_list)
  player_list = updated_player_list

def generate_existing_players(player_list):
    existing_player_data = ['existing_players']
    for key in player_list:
      player = player_list[key]
      existing_player_data.append([player.playerID ,player.name, player.x, player.y, player.Class, player.health, player.angle])

    return existing_player_data

from twisted.internet import protocol, reactor

class MainServer(protocol.Factory):
    global g_player_id
    global player_list
    global connections
    connections = {}
    player_id_counter = 0

    def __init__(self):
        # self.connections = {}
      print("server initialized!")

    def buildProtocol(self, addr):
      return SecondaryServer(self)

    def notifyPlayerDisconnected(self, player_id):
      # Handle the removal of the disconnected player
      print("Player", player_id, "has disconnected")
      if player_id in player_list:
          del player_list[player_id]
          for connection in connections.keys():
            connection.sendData(['remove_player', player_id])

    # def broadcastPlayerListUpdate(self):
    #   #self.send_message(['remove_player', self.player.playerID]
    #   player_data = [(player_id, player.name, player.x, player.y) for player_id, player in player_list.items()]
    #   message = ['player_list_update', player_data]

    #   for connection in self.connections.keys():
    #       connection.sendData(message)

    def generateExistingPlayers(self):
      return [(player_id, player.name, player.x, player.y) for player_id, player in self.player_list.items()]
    
    def parse_data(self,data):
      updateWorld(connections, data, player_list) 

class SecondaryServer(protocol.Protocol):
    global g_player_id
    global player_list
    global connections
    factory = None

    def __init__(self, factory):
      self.factory = factory

    def connectionMade(self):
      global g_player_id
      playerid = g_player_id
      
      player = Player(playerid)
      player_list[playerid] = player
      connections[self] = playerid
      g_player_id = g_player_id + 1
      print("A new player has connected with id:", g_player_id)

      existing_player_data = generate_existing_players(player_list)
      self.sendData(['id update', playerid,existing_player_data])

    def connectionLost(self, reason):
        player_id = connections.pop(self, None)
        print("Lost connection to player", player_id)
        if player_id is not None:
            self.factory.notifyPlayerDisconnected(player_id)
            for connection in connections.keys():
              connection.sendData(['remove_player', player_id])
            #self.sendData(['remove_player', player_id])

    def dataReceived(self, data):
        #print("Recieved data: ", pickle.loads(data.encode('utf-8')))
        self.factory.parse_data(data)
        #HANDLE DATA RECEIVED

    def sendData(self, data):
      self.transport.write(pickle.dumps(data))
    

# Create and start the server
factory = MainServer()
print("Server started...")
reactor.listenTCP(4321, factory)
reactor.run()

# # Create and start the server
# factory = MainServer()
# reactor.listenTCP(4321, factory)
# reactor.run()

# #Lobby server
# class MainServer(asyncore.dispatcher):

#   def __init__(self, port):
#     asyncore.dispatcher.__init__(self)
#     self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
#     self.bind(('', port))
#     self.listen(10)
#     self.last_heartbeat_time = time.time()
#     self.heartbeat_interval = 5 # Heartbeat interval in seconds

#   def handle_accept(self):
#     global g_player_id

#     #Whats supposed to happen when a new connection joins
#     conn, addr = self.accept()
#     print('Connection address:' + addr[0] + " " + str(addr[1]))
#     playerid = g_player_id
    
#     player = Player(playerid)
#     player_list[playerid] = player
#     outgoing.append((conn,playerid))


#     #Generate already connected players.
#     existing_player_data = generate_existing_players(player_list)
#     conn.send(pickle.dumps(['id update', playerid,existing_player_data]))
    
#     g_player_id = g_player_id + 1
#     client_Servers[playerid]= SecondaryServer(conn)


# #Game server
# class SecondaryServer(asyncore.dispatcher_with_send):
#   def __init__(self, conn):
#       asyncore.dispatcher_with_send.__init__(self, conn)
#       self.last_heartbeat_time = time.time()
#       self.heartbeat_interval = 5

#   def handle_read(self):
#       received_data = self.recv(BUFFERSIZE)
#       if received_data:
#           # Update the game with data
#           updateWorld(received_data)
#       else:
#           self.close()

# server= MainServer(4321)
# print("Server Started...")
# while True:
#     asyncore.loop(timeout=0.1, count=1)
