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
outgoing = []

class Player:
  def __init__(self, playerID, name = "Noname", Class = 0, x = 1.5, y=5,health= 100, angle = 0):
    self.playerID = playerID
    self.name = name
    self.x = x 
    self.y = y
    self.Class = Class
    self.health = health
    self.angle = angle

global player_list
player_list = {}

def updateWorld(message):
  global player_list
  global outgoing
  arr = pickle.loads(message)

  playerid = arr[1]
  if playerid == 0: return

  updated_player_list = handle_message(arr, outgoing ,player_list)

  player_list = updated_player_list

#Lobby server
class MainServer(asyncore.dispatcher):
  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('', port))
    self.listen(10)
    self.last_heartbeat_time = time.time()
    self.heartbeat_interval = 15 # Heartbeat interval in seconds

  def handle_accept(self):
    #Whats supposed to happen when a new connection joins
    conn, addr = self.accept()
    print('Connection address:' + addr[0] + " " + str(addr[1]))
    playerid = random.randint(1000, 1000000)
    player = Player(playerid)
    player_list[playerid] = player
    outgoing.append((conn,playerid))
    conn.send(pickle.dumps(['id update', playerid]))
    player_object_list = []
    for key in player_list:
      player = player_list[key]
      player_object = []
      player_object.append([player.playerID ,player.name, player.x, player.y, player.Class, player.health, player.angle])
      player_object_list.append(player_object)

    existing_player_data = ['existing_players']
    existing_player_data.append(player_object_list)
    print(player_object_list)
    conn.send(pickle.dumps(existing_player_data))
    SecondaryServer(conn)


  def send_heartbeat(self):
    current_time = time.time()
    disconnected_players= []
    if current_time - self.last_heartbeat_time >= self.heartbeat_interval:

          for conn, playerid in outgoing:
              try:
                conn.send(pickle.dumps(['heartbeat']))
              except:
                self.last_heartbeat_time = current_time
                disconnected_players.append(playerid)
                print("Cant contact player", playerid, "removing connection...")
                outgoing.remove((conn,playerid))
                del player_list[playerid]
                print(f"players left: {len(player_list)}")

    for conn, playerid in outgoing:
      for i in range(len(disconnected_players)):
        conn.send(pickle.dumps(['remove_player', playerid]))

    


#Game server
class SecondaryServer(asyncore.dispatcher_with_send):
  def __init__(self, conn):
      asyncore.dispatcher_with_send.__init__(self, conn)
      self.last_heartbeat_time = time.time()

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
    server.send_heartbeat()
#asyncore.loop()