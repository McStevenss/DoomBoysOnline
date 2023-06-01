from player import *
from weapon import *
from network_player import *

#print("Please choose class: [0] Druid, [1] Rogue, [2] Warrior")
def get_class(class_id, game):
    if class_id == 0:
        return Druid(game)
    if class_id == 1:
        return Rogue(game)
    if class_id == 2:
        return Warrior(game)
    
    else:
        return Player(game)
    
def get_class_network(game, playerId, class_Id, name):
    if class_Id == 0:
        print("network druid")
        return network_Druid(game, playerId, name)
    if class_Id == 1:
        print("network_Rogue ")
        return network_Rogue(game, playerId, name)
    if class_Id == 2:
        print("network_Warrior ")
        return network_Warrior(game, playerId, name)
    
    else:
        return network_player(game, class_Id=class_Id)


class Warrior(Player):
    def __init__(self, game):
        super().__init__(game)
        # Add additional attributes or behavior specific to the Warrior class
        self.attack_power = 10
        self.health = 175
        game.weapon = Axe(game)


class Druid(Player):
    def __init__(self, game):
        super().__init__(game)
        # Add additional attributes or behavior specific to the Warrior class
        self.attack_power = 10
        self.health = 100
        game.weapon = HealingSpell(game)

class Rogue(Player):
    def __init__(self, game):
        super().__init__(game)
        # Add additional attributes or behavior specific to the Warrior class
        self.attack_power = 10
        self.health = 75
        game.weapon = Dagger(game)
        self.path="/resources/sprites/players/Rogue"


class network_Rogue(network_player):
    def __init__(self, game, playerId, name):
        super().__init__(game, playerID=playerId, name=name, path="resources/sprites/players/Rogue")
        self.attack_power = 10
        self.health = 75
        #self.path="/resources/sprites/players/Rogue"

class network_Druid(network_player):
    def __init__(self, game, playerId, name):
        super().__init__(game, playerID=playerId, name=name, path="resources/sprites/players/Druid")
        self.attack_power = 10
        self.health = 100

class network_Warrior(network_player):
    def __init__(self,game, playerId, name):
        super().__init__(game, playerID=playerId, name=name, path="resources/sprites/players/Knight")
        self.attack_power = 10
        self.health = 175
        self.animation_time = 150
        