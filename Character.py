
import math
import random

#---------------------------------------------------------------------------------------------------------
# Character special skills class
#---------------------------------------------------------------------------------------------------------
class Skill:
    """
    Each skill has cooldown time
    """
    def __init__(self, name, cooldown, description="", target_self=False):
        self.name = name
        self.cooldown = cooldown
        self.current_cd = 0
        self.description = description
        self.target_self = target_self

    def execute(self, user, target):
        """
        Specific logic in child class
        """
        pass
#---------------------------------------------------------------------------------------------------------
# --- 6 specific skills subclass below ---
#---------------------------------------------------------------------------------------------------------
class Special_1(Skill):
    def __init__(self): super().__init__("Overload", 3, "Dealt 30 direct damage.")
    def execute(self, user, target):
        dmg = target.take_damage(30)
        user.gain_exp(dmg, is_attack=True)
        target.gain_exp(dmg, is_attack=False)
        if target.last_defended:
            return f"{target.name} defended! {user.name}'s Overload dealt only {dmg} damage."
        return f"{user.name} released Overload! {target.name} took {dmg} damage."

class Special_2(Skill):
    def __init__(self): super().__init__("Healing Magic", 3, "Recovered 20 HP.", target_self=True)
    def execute(self, user, target):
        old_hp = user.hp
        user.hp = min(user.max_hp, user.hp + 20)
        heal = user.hp - old_hp
        user.gain_exp(heal, is_attack=True)
        return f"{user.name} activated Healing Magic! Recovered {heal} HP."

class Special_3(Skill):
    def __init__(self): super().__init__("Fire Arrow", 3, "Damage equal to 20% of target HP.")
    def execute(self, user, target):
        damage = max(1, int(target.hp * 0.2))
        dmg = target.take_damage(damage)
        user.gain_exp(dmg, is_attack=True)
        target.gain_exp(dmg, is_attack=False)
        if target.last_defended:
            return f"{target.name} defended! {user.name}'s Fire Arrow dealt only {dmg} damage."
        return f"{user.name} shot Fire Arrow! Dealt {dmg} damage."

class Special_4(Skill):
    def __init__(self): super().__init__("Sonic Bark", 3, "Random massive damage.")
    def execute(self, user, target):
        dmg = target.take_damage(random.randint(20, 40))
        user.gain_exp(dmg, is_attack=True)
        target.gain_exp(dmg, is_attack=False)
        if target.last_defended:
            return f"{target.name} defended! {user.name}'s Sonic Bark dealt only {dmg} damage."
        return f"{user.name} barked! Dealt {dmg} damage."

class Special_5(Skill):
    def __init__(self): super().__init__("Assult Riffle", 3, "1.5x ATK damage.")
    def execute(self, user, target):
        dmg = target.take_damage(int(user.atk * 1.5))
        user.gain_exp(dmg, is_attack=True)
        target.gain_exp(dmg, is_attack=False)
        if target.last_defended:
            return f"{target.name} defended! {user.name}'s Assult Riffle dealt {dmg} damage."
        return f"{user.name} raided! Dealt {dmg} massive damage."

class Special_6(Skill):
    def __init__(self): super().__init__("Recovery Magic", 3, "Heal 15 HP and +1 ATK.", target_self=True)
    def execute(self, user, target):
        old_hp = user.hp
        user.hp = min(user.max_hp, user.hp + 15)
        user.atk += 1
        heal = user.hp - old_hp
        user.gain_exp(heal, is_attack=True)
        return f"{user.name} used Recovery Magic! Healed {heal} HP and powered up!"

#---------------------------------------------------------------------------------------------------------
# Character class
#---------------------------------------------------------------------------------------------------------
SHAKE_DURATION = 1000

class Character:
    """
    The class includes battle actions, exp/level-up logic, cooldowns,
    and the display animation state used by template.py.
    """
    def __init__(self, name, max_hp, atk_range, dfn_range, skill_pack=None):
        self.name = name
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.atk = self._stat_value(atk_range)
        self.dfn = self._stat_value(dfn_range)
        self.defense = self.dfn
        self.level = 1
        self.leve = self.level
        self.exp = 0
        self.epx = 0

        self.is_defensing = False
        self.defending = False
        self.last_defended = False

        self.skill = None if isinstance(skill_pack, str) else skill_pack
        self.special_type = skill_pack if isinstance(skill_pack, str) else "skill"
        self._special_cooldown = 0

        # Sprite display size - set after construction via create_new_game.
        self.sprite_w = 80
        self.sprite_h = 80

        # Animation state.
        self.images = {}
        self.current_action = "base"
        self.shake_timer = 0

    def _stat_value(self, value):
        if isinstance(value, (tuple, list)):
            return random.randint(value[0], value[1])
        return value

    @property
    def special_cooldown(self):
        if self.skill is not None:
            return self.skill.current_cd
        return self._special_cooldown

    @special_cooldown.setter
    def special_cooldown(self, value):
        if self.skill is not None:
            self.skill.current_cd = value
        else:
            self._special_cooldown = value

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.last_defended = self.defending or self.is_defensing
        if self.defending or self.is_defensing:
            damage = damage // 2
        actual_damage = max(0, damage)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def attack_target(self, target):
        damage = self.atk - target.defense + random.randint(-5, 10)
        damage = max(1, damage)
        actual_damage = target.take_damage(damage)
        self.gain_exp(actual_damage, is_attack=True)
        target.gain_exp(actual_damage, is_attack=False)
        return actual_damage

    def make_attack(self, target):
        return self.attack_target(target)

    def defend(self):
        self.defending = True
        self.is_defensing = True

    def stop_defending(self):
        self.defending = False
        self.is_defensing = False
        self.last_defended = False

    def use_special(self, target):
        if self.special_cooldown > 0:
            return None

        if self.skill is not None:
            result_text = self.skill.execute(self, target)
        elif self.special_type == "damage":
            damage = self.atk + random.randint(10, 20)
            actual_damage = target.take_damage(damage)
            self.gain_exp(actual_damage, is_attack=True)
            target.gain_exp(actual_damage, is_attack=False)
            if target.last_defended:
                result_text = f"{target.name} defended! {self.name}'s SPECIAL dealt only {actual_damage} damage!"
            else:
                result_text = f"{self.name} used SPECIAL and dealt {actual_damage} damage!"
        elif self.special_type == "heal":
            heal_amount = random.randint(15, 25)
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + heal_amount)
            actual_heal = self.hp - old_hp
            self.gain_exp(actual_heal, is_attack=True)
            result_text = f"{self.name} used SPECIAL and healed {actual_heal} HP!"
        else:
            result_text = f"{self.name} has no SPECIAL ready."

        cooldown = self.skill.cooldown if self.skill is not None else 3
        self.special_cooldown = cooldown
        return result_text

    def gain_exp(self, damage, is_attack):
        if is_attack:
            self.exp += damage
        else:
            base_gain = self.dfn
            if damage > 10:
                base_gain *= 1.2
            elif damage <= 0:
                base_gain *= 1.5
            self.exp += int(base_gain)

        while self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.atk += 5
            self.dfn += 3
            self.defense = self.dfn

        self.leve = self.level
        self.epx = self.exp
        return self.level, self.exp

    def reduce_cooldown(self):
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

    def reduce_cd(self):
        self.reduce_cooldown()

    def trigger_action(self, action):
        self.current_action = action
        self.shake_timer = SHAKE_DURATION

    def update(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_timer = 0
                self.current_action = "base"

    def shake_offset(self):
        if self.shake_timer <= 0:
            return 0
        progress = self.shake_timer / SHAKE_DURATION
        return int(math.sin(progress * math.pi * 6) * 6 * progress)
#---------------------------------------------------------------------------------------------------------
#Subclass for player and enemy in order to distinguish player and enemy
#---------------------------------------------------------------------------------------------------------
class Player(Character):
    """be player"""
    def __init__(self, name, max_hp, atk_range, dfn_range, skill_pack):
        super().__init__(name, max_hp, atk_range, dfn_range, skill_pack)
        self.type = "Player"

class Enemy(Character):
    """be enemy"""
    def __init__(self, name, max_hp, atk_range, dfn_range, skill_pack):
        super().__init__(name, max_hp, atk_range, dfn_range, skill_pack)
        self.type = "Enemy"
