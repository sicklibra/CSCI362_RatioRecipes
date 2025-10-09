import json
# import Recipe #also includes ingredient class.

#Global variables for conversions
G2LB=453.5924 # Grams to 1lb
OZ2LB=16  #Ounces to 1lb
G2KG2MG=1000  #1k g/kg 1k mg/g

def saveRecipe(instring):
    jDict=json.loads(instring)
    #precondition is that json values match exactly, and 
    inRecipe=Recipe(jDict['name'], jDict['description'], jDict['ingredients'], jDict['notes'],jDict['unit'])


def loadRecipe(instring):
    return json.loads(instring)



class RatIngredient:
    def __init__(self, name, ratio):
        self.what=name
        self.ratio=ratio

class WtIngredient:
    def __init__(self, name, wt):
        

class Recipe:
    
    def __init__(self, name, description, ingredients, notes, units):
        self.name=name
        self.description=description
        self.totwt = self.getTotWt(ingredients)
        self.ratingredients = self.getRatIngredients(ingredients)
        self.wtingredients = self.getWtIngredients(ingredients)
        self.notes=notes
        self.unit=units
        
    def getTotWt(inglst):
        total=0
        for i in inglst:
            total+=float(i['weight'])
        return total        

    def getRat(self, wt):
        return round(wt /self.totwt, 4)


    def getRatIngredients(self, inglst):
        ingredients=[]
        if 'ratio' in inglst[1].keys():
           for i in inglst:
               ing=RatIngredient(i['name'], float(i['ratio']))
               ingredients.append(ing)

        elif 'weight' in inglst[1].keys:
            for i in inglst:
                ing=WtIngredient(i['name'], self.getRat(i['weight']))
                ingredients.append(ing)

        else:
            print('Json string likely incorrect')

        return ingredients  
    
    def getWtIngredients(self, inglst):
        ingredients=[]
        if 'weight' in inglst[1].keys():
           for i in inglst:
               ing=WtIngredient(i['name'], float(i['weight']))
               ingredients.append(ing)

        elif 'Ratio' in inglst[1].keys:
            for i in inglst:
                ing=RatIngredient(i['name'], self.getWt(i['ratio']))
                ingredients.append(ing)

        else:
            print('Json string likely incorrect')

        return ingredients  

    def getWt(self, ratio):
        return round(ratio*self.totwt, 2)      

    


# if __name__ == "__main__":
#     getjsonstring()