from collections import defaultdict
import json
import os
import sys


class Item(dict):
    def __init__(self, ident, reference):
        self['ident'] = ident
        self['reference'] = reference
        # you can create objects like this.
        # worldmap.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), Position)
    

class Container(Item):
    """Containers are types of Items and can do everything an item can do."""
    def __init__(self, ident, reference):
        Item.__init__(self, ident, reference)
        self['contained_items'] = []
        self['opened'] = True
        # this plus all the contained items is how much the item weighs.
        self['base_weight'] = int(self['reference']['weight'])
        self['max_volume'] = int(self['reference']['volume'])
        self['contained_weight'] = 0
        self['contained_volume'] = 0

    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self['contained_items']:
            weight = weight + int(item['reference']['weight'])
        weight = weight + self['base_weight'] # add the base weight
        self['contained_weight'] = weight

    def add_item(self, item):
        # TODO: check right item type and container type (liquids go in liquid containers.)

        # check volume
        if int(item['reference']['volume']) + self['contained_volume'] < self['max_volume']:
            self['contained_items'].append(item)
            self.recalc_weight()
            print(' - added item to container successfully.')
            return True
        else:
            # TODO: send a message to the player that the container is full and they cannot do this.
            return False

    def remove_item(self, item):
        for item_to_check in self['contained_items'][:]:
            if item_to_check == item:
                self['contained_items'].remove(item_to_check)
                self.recalc_weight()
                return item # if we remove it then it needs to go somewhere. better return it so we can manage it.


class ItemManager:
    def __init__(self):
        self.ITEM_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/items/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    with open(root+'/'+file_data, encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if isinstance(value, list):
                                    self.ITEM_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.ITEM_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.ITEM_TYPES[item['ident']][key] = str(value)
                        except Exception:
                            raise Exception(f"!! couldn't parse: {item}.")
        print(f"Total ITEM_TYPES loaded: {len(self.ITEM_TYPES)}")

    def get_item(self, ident):
        return self.ITEM_TYPES[ident]

    def create_item(self, ident):
        if 'container_type' in self.ITEM_TYPES[ident]:
            return Container(ident, self.ITEM_TYPES[ident])
        else:
            return Item(ident, self.ITEM_TYPES[ident])
