"""
Shotgun users can heal teammates with their spades
One possible improvement could be to double healing done to crouching players
"""

from pyspades.constants import SHOTGUN_WEAPON, MELEE_KILL

HEAL_RATE = 5 # Health healed per hit

def apply_script(protocol, connection, config):
    class MedicConnection(connection):
        def __init__(self, *arg, **kw):
            connection.__init__(self, *arg, **kw)

        def on_hit(self, hit_amount, hit_player, type, grenade):
            if (type == MELEE_KILL
            and self.team == hit_player.team
            and self.weapon == SHOTGUN_WEAPON):
                hit_player.set_hp(hit_player.hp + HEAL_RATE, type = MELEE_KILL)
                if (hit_player.hp >= 100): # If the target has full health
                     connection.send_chat(self.name + ' is all healed up!')
            return connection.on_hit(self, hit_amount, hit_player,
                type, grenade)

    return protocol, MedicConnection
