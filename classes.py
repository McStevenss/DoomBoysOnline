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
        self.max_health = 175
        self.health = 175
        self.armor = 65
        game.weapon = Axe(game)

        self.resource_pool = 100
        self.resource_name = "Rage"
        self.resource_regen = 1
        self.resource_color = (255,99,99)

class Druid(Player):
    def __init__(self, game):
        super().__init__(game)
        # Add additional attributes or behavior specific to the Warrior class
        self.attack_power = 10
        self.max_health = 100
        self.health = 100
        self.armor = 25
        game.weapon = HealingSpell(game)
        healing_spell = Heal(game,self)
        regenerate = Regenerate(game,self)
        bear_form = Bear_Form(game,self)
        self.spells = [healing_spell, regenerate, bear_form]

        self.resource_pool = 100
        self.resource_name = "Mana"
        self.resource_regen = 1
        self.resource_color = (0,0,255)

class Rogue(Player):
    def __init__(self, game):
        super().__init__(game)
        # Add additional attributes or behavior specific to the Warrior class
        self.attack_power = 10
        self.max_health = 75
        self.health = 75
        self.armor = 35

        game.weapon = Dagger(game)
        speed_spell = Speed(game,self)
        self.spells = [speed_spell]
        self.path="/resources/sprites/players/Rogue"

        self.resource_pool = 100
        self.resource_name = "Energy"
        self.resource_regen = 4
        self.resource_color = (0,0,255)


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

        healing_spell = Heal(game, network_player=self)
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
        self.original_stat = 123
        self.new_stat = 321
        self.network_player = network_player
        self.effect_started = 0

    def set_effect(self):
        if self.player and self.effect_started == 0:
            print("set default effect on player")
            self.effect_started = time.time()
        if self.network_player and self.effect_started == 0:
            print("set default effect on network_player")
            self.effect_started = time.time()

    def get_effect_duration_left(self):
        if self.player:
            time_left = self.duration - (time.time() - self.effect_started)
        
        return round(time_left,2)
    
    def remove_effect(self):
        #player.stat = self.original_stat
        pass


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

class Fast(Effect):
    def __init__(self, player:Player):
        super().__init__(player)
        self.name = "Speed effect"
        self.duration = 4
        self.hud_icon_path = "resources/icons/bear_form.png"
        self.original_stat = player.speed

    def set_effect(self):
        if self.player:
            self.effect_started = time.time()
            self.player.speed = self.original_stat * 2
            print("buff is ",self.player.speed)

    def remove_effect(self):
        if self.player:
            self.player.speed = self.original_stat
    


class Heal(Spell):
    def __init__(self, game, player:Druid = None, network_player: network_Druid = None):
        super().__init__(spell_path="resources/icons/Lesser_Heal.png")
        self.name="Lesser Heal"
        self.damage = 0
        self.cost = 10
        self.player = player
        self.network_player = network_player
        self.game = game

    def cast(self):
        if self.player:
            self.player.health +=10
            self.game.weapon = HealingSpell(self.game)
            self.player.armor = DRUID_BASE_ARMOR

        if self.network_player:
            self.network_player.change_player_model("resources/sprites/players/Druid")

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
            self.game.armor = 65
        if self.network_player:
            self.network_player.change_player_model("resources/sprites/players/Bear_Form")
        

class Regenerate(Spell):
    def __init__(self, game, player:Druid = None, network_player: network_Druid = None):
        super().__init__(spell_path="resources/icons/Regenerate.png")
        self.name="Regenerate"
        self.damage = 0
        self.cost = 10
        self.player = player
        self.network_player = network_player
        self.game = game

    def cast(self):
        if self.player:
            self.player.regenerate = True
            self.game.weapon = HealingSpell(self.game)
            self.player.armor = DRUID_BASE_ARMOR

        if self.network_player:
            self.network_player.change_player_model("resources/sprites/players/Druid")

class Speed(Spell):
    def __init__(self, game, player:Rogue):
        super().__init__(spell_path="resources/icons/poison.png")
        self.name="Speed"
        self.damage = 0
        self.cost = 10
        self.duration = 5
        self.player = player
        self.speed = self.player.speed
        self.game = game

    def cast(self):   
        fast_buff = Fast(self.player)
        fast_buff.set_effect()
        self.player.effects.append(fast_buff)
