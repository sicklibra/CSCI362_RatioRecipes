import json

class Recipe:
    def __init__(self, name, description, ingredients, notes):
        self.name=name
        self.description=description
        self.ingredients=ingredients
        self.notes=notes

class Ingredient:
    def __init__(self, ingin):
        self.what=ingin.get("name")
        try:
            self.weight=ingin.get("weight")
            self.unit=ingin.get('unit')
        except:
            self.weight='na'
            self.ratio=ingin('ratio')
        self.convert()

    def convert(self):
        if self.weight=='na':
            try:
              self.ratio = int(self.ratio)
            except:
                return 'please pass in a dictionary item!'


    