from equipment_slots import EquipmentSlots


class Equipment:
    def __init__(self, main_hand=None, off_hand=None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    @property
    def max_hp_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equipable:
            bonus += self.main_hand.equipable.max_hp_bonus

        if self.off_hand and self.off_hand.equipable:
            bonus += self.off_hand.equipable.max_hp_bonus

        return bonus

    @property
    def power_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equipable:
            bonus += self.main_hand.equipable.power_bonus

        if self.off_hand and self.off_hand.equipable:
            bonus += self.off_hand.equipable.power_bonus

        return bonus

    @property
    def defense_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equipable:
            bonus += self.main_hand.equipable.defense_bonus

        if self.off_hand and self.off_hand.equipable:
            bonus += self.off_hand.equipable.defense_bonus

        return bonus

    def toggle_equip(self, equipable_entity):
        results = []

        slot = equipable_entity.equipable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equipable_entity:
                self.main_hand = None
                results.append({'unequipped': equipable_entity})
            else:
                if self.main_hand:
                    results.append({'unequipped': self.main_hand})

                self.main_hand = equipable_entity
                results.append({'equipped': equipable_entity})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equipable_entity:
                self.off_hand = None
                results.append({'unequipped': equipable_entity})
            else:
                if self.off_hand:
                    results.append({'unequipped': self.off_hand})

                self.off_hand = equipable_entity
                results.append({'equipped': equipable_entity})

        return results