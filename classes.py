from player import *
from weapon import *
from network_player import *
import time

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
    
def get_player_models():

    warrior_model = "resources/sprites/players/Knight"
    rogue_model = "resources/sprites/players/Rogue"
    druid_model = "resources/sprites/players/Druid"
    bear_form_model = "resources/sprites/players/Bear_Form"
    player_model_paths = {"warrior": warrior_model, "rogue":rogue_model, "druid":druid_model, "bear_form":bear_form_model}
    return player_model_paths

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
        healing_spell = Heal()
        regenerate = Regenerate(game,self)
        bear_form = Bear_Form(game,self)
        self.spells = [healing_spell, regenerate, bear_form]

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

        healing_spell = Heal()
        regenerate = Regenerate(game, network_player=self)
        bear_form = Bear_Form(game, network_player=self)
        self.spells = [healing_spell, regenerate, bear_form]

class network_Warrior(network_player):
    def __init__(self,game, playerId, name):
        super().__init__(game, playerID=playerId, name=name, path="resources/sprites/players/Knight")
        self.attack_power = 10
        self.health = 175
        self.animation_time = 150


class Spell():
    def __init__(self, spell_path="resources/icons/bear_form.png"):
        self.name = "Unnamed Spell"
        self.damage = 0
        self.cost = 0
        self.hud_icon = self.get_texture(spell_path)

    def cast(self):
        print("CASTED DEFAULT SPELL")

    @staticmethod
    def get_texture(path, res=(50, 50)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

#Effect takes player because it will essentially only affect the local player on each session
class Effect():
    def __init__(self, player:Player = None, network_player:network_player = None):
        self.name = "Unnamed Effect"
        self.duration = 10
        self.hud_icon_path = ""
        self.player = player
        self.network_player = network_player
        self.effect_started = 0

    def set_effect(self):
        if self.player and self.effect_started == 0:
            print("set default effect on player")
            self.effect_started = time.time()
        if self.network_player and self.effect_started == 0:
            print("set default effect on network_player")
            self.effect_started = time.time()


class Heal(Effect):
    def __init__(self):
        super().__init__()
        self.name = "Unnamed Effect"
        self.duration = 0
        self.hud_icon_path = ""

    def set_effect(self):
        if self.player:
            self.player.health += 50
        if self.network_player:
            #TODO: SEND SERVER MESSAGE TO HEAL PLAYER
            self.network_player.health += 50
    


class Heal(Spell):
    def __init__(self):
        super().__init__()
        self.name="Heal"
        self.damage = 0
        self.cost = 10

class Bear_Form(Spell):
    def __init__(self, game, player:Druid = None, network_player: network_Druid = None):
        super().__init__(spell_path="resources/icons/bear_form.png")
        self.name="Bear Form"
        self.damage = 0
        self.cost = 10
        self.player = player
        self.network_player = network_player
        self.game = game

    def cast(self):
        print("player", self.player, "network_player", self.network_player)
        if self.player:
            self.game.weapon = Bear_Claw(self.game)
        if self.network_player:
            self.network_player.change_player_model("resources/sprites/players/Bear_Form")
        

class Regenerate(Spell):
    def __init__(self, game, player:Druid = None, network_player: network_Druid = None):
        super().__init__(spell_path="resources/icons/poison.png")
        self.name="Regenerate"
        self.damage = 0
        self.cost = 10
        self.player = player
        self.network_player = network_player
        self.game = game

    def cast(self):
        if self.player:
            print("added hp")
            self.player.health +=10
            self.game.weapon = HealingSpell(self.game)

        if self.network_player:
            self.network_player.change_player_model("resources/sprites/players/Druid")
        
