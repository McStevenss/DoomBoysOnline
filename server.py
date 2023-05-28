import socket
import asyncore
import random
import pickle
import time
from server_utils import handle_message
import threading


BUFFERSIZE = 512
HEARTBEAT_INTERVAL = 5

global outgoing
global client_Servers
global player_list
global g_player_id

outgoing = []
client_Servers= {}
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



def updateWorld(message):
  global player_list
  global outgoing
  arr = pickle.loads(message)

  updated_player_list = handle_message(arr, outgoing ,player_list)

  player_list = updated_player_list

def generate_existing_players(player_list):
    existing_player_data = ['existing_players']
    for key in player_list:
      player = player_list[key]
      existing_player_data.append([player.playerID ,player.name, player.x, player.y, player.Class, player.health, player.angle])

    return existing_player_data

#Lobby server
class MainServer(asyncore.dispatcher):

  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('', port))
    self.listen(10)
    self.last_heartbeat_time = time.time()
    self.heartbeat_interval = 5 # Heartbeat interval in seconds

  def handle_accept(self):
    global g_player_id

    #Whats supposed to happen when a new connection joins
    conn, addr = self.accept()
    print('Connection address:' + addr[0] + " " + str(addr[1]))
    playerid = g_player_id
    
    player = Player(playerid)
    player_list[playerid] = player
    outgoing.append((conn,playerid))


    #Generate already connected players.
    existing_player_data = generate_existing_players(player_list)
    conn.send(pickle.dumps(['id update', playerid,existing_player_data]))
    
    g_player_id = g_player_id + 1
    client_Servers[playerid]= SecondaryServer(conn)


#Game server
class SecondaryServer(asyncore.dispatcher_with_send):
  def __init__(self, conn):
      asyncore.dispatcher_with_send.__init__(self, conn)
      self.last_heartbeat_time = time.time()
      self.heartbeat_interval = 5

  def handle_read(self):
      received_data = self.recv(BUFFERSIZE)
      if received_data:
          # Update the game with data
          updateWorld(received_data)
      else:
          self.close()

server= MainServer(4321)
print("Server Started...")
while True:
    asyncore.loop(timeout=0.1, count=1)
