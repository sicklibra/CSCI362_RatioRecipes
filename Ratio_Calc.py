import json
# import Recipe #also includes ingredient class.

#Global variables for conversions
G2LB=453.5924 # Grams to 1lb
OZ2LB=16  #Ounces to 1lb
G2KG2MG=1000  #1k g/kg 1k mg/g

def saveRecipe(instring):
    jDict=loadRecipe(instring)
    #precondition is that json values match exactly, and are in weight format.  
    inRecipe=makeRecipe(jDict)
    return inRecipe.ratJason()

def getRecipe(instring):
    jDict=loadRecipe(instring)
    recipe=makeRecipe(jDict)
    return recipe.wtJson()

'''If we are updating/iterating a recipe, I will return a pk of -1 this will signal 
on the front end, that the key for this recipe needs to be new and the parent key needs to be 
updated to the key of the recipe just iterated.'''
def updateRecipe(instring):
    jDict=loadRecipe(instring)
    inrecipe= makeRecipe(jDict)
    inrecipe.pk="-1"
    return inrecipe.ratJson()

# If you send this one with the ratio json string, the function will return the updated wt 
def changeWt(instring):
    jDict=loadRecipe(instring)
    inrecipe= makeRecipe(jDict)
    return inrecipe.wtJson()

#send the weight string here and the system will conduct the calculations
def changeUnit(instring, newUnit):
    jDict=loadRecipe(instring)
    recipe= makeRecipe(jDict)
    if recipe.unit== newUnit:
        return recipe.ratJson()
    elif recipe.unit== 'g':
        if newUnit== 'kg':
            metricConv(recipe, 'up', 1)
        elif newUnit== 'mg':
            metricConv(recipe, 'down', 1)
        else:
            met2imp(recipe, recipe.unit, newUnit)
    elif recipe.unit== 'lb':
        if newUnit != 'oz':
            imp2met(recipe, recipe.unit, newUnit)
        else:
            oz2lb(recipe, 'down')
    elif recipe.unit == 'oz':
        if newUnit != 'lb':
            imp2met(recipe, recipe.unit, newUnit)
        else:
            oz2lb(recipe, 'up')
    elif recipe.unit=='kg':
        if newUnit=='g':
            metricConv(recipe, 'down', 1)
        elif newUnit == 'mg':
            metricConv(recipe, 'down', 2)
        else:
            met2imp(recipe, recipe.unit, newUnit)
    elif recipe.unit=='mg':
        if newUnit== 'g':
            metricConv(recipe, 'up', 1)
        elif newUnit=='kg':
            metricConv(recipe, 'up', 2)
        else:
            met2imp(recipe, recipe.unit, newUnit)   

    return recipe.ratJson()


def gtolb(recipe, direction):
    # up is for grams to lbs
    if direction=='up':
        for ing in recipe.wtingredients:
            ing.wt=ing.wt/G2LB
    else:
        for ing in recipe.wtingredients:
            ing.wt=ing.wt*G2LB

def metricConv(recipe, direction, jumps):
    conv=jumps*G2KG2MG
    if direction=='up':
        for ing in recipe.wtingredients:
            ing.wt=ing.wt*conv
    else:
        for ing in recipe.wtingredients:
            ing.wt= ing.wt/conv

def oz2lb(recipe, direciton):
    # up is for oz to lbs
    if direciton== 'up':
        for ing in recipe.wtingredients:
            ing.wt = ing.wt/OZ2LB
    elif direciton == 'down':
        for ing in recipe.wtingredients:
            ing.wt == ing.wt * OZ2LB

def gtooz(recipe,):
    gtolb(recipe, 'up')
    oz2lb(recipe, 'down')

def met2imp(recipe, inunit, outunit):
    # Converts to grams
    if inunit=='kg':
        metricConv(recipe, 'down', 1)
    elif inunit=='mg':
        metricConv(recipe, 'up', 1)

    #once in grams will convert to lbs
    gtolb(recipe, 'up')
    # if in oz required, will convert to oz from lbs
    if outunit== 'oz':
        oz2lb(recipe, 'down')

def imp2met(recipe, inunit, outunit):
    #convert to grams
    if inunit=='lb':
        gtolb(recipe, 'down')
    elif inunit=='oz':
        oz2lb(recipe, 'up')
        gtolb(recipe, 'down')
    # now in grams check if kg or mg
    if outunit=='kg':
        metricConv(recipe, 'up', 1)
    elif outunit== 'mg':
        metricConv(recipe, 'down', 1)
        

def makeRecipe(inDict):
    return Recipe(inDict['name'], inDict['description'], inDict['ingredients'], inDict['notes'],inDict['unit'], inDict['totwt'], inDict['parentkey'])



def loadRecipe(instring):
    return json.loads(instring)


'''This next section is for the conversion logic if we are changin units. The ratios and weights will 
be easily updated by passing in updated weight variables. because the re'''
class RatIngredient:
    def __init__(self, name, ratio):
        self.what=name
        self.ratio=ratio


class WtIngredient:
    def __init__(self, name, wt):
        self.what=name
        self.wt=wt
        

class Recipe:
    
    def __init__(self, name, description, ingredients, notes, units, totwt, parentKey):
        self.name=name
        self.description=description
        self.totwt = totwt
        self.ratingredients = self.getRatIngredients(ingredients)
        self.wtingredients = self.getWtIngredients(ingredients)
        self.notes=notes
        self.unit=units
        self.pk=parentKey
        
    # def getTotWt(self, inglst):
    #     if self.totwt == null:
    #         total=0
    #         for i in inglst:
    #             total+=float(i['weight'])
    #         return total        

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
        return round(ratio * self.totwt, 2) 

    def toDict(self, type):
        if type=='rat':
            ingType = self.ratingredients
        elif type == 'wt':
            ingType = self.wtingredients
        else:
            print('passed wrong variable')
        return {'name':self.name, 'description':self.description, 'ingredients':ingType, 'notes':self.notes, 'units':self.units, 'totwt':self.totwt, 'parentKey':self.pk}    

    def ratJson(self):
        ratdict=self.toDict('rat')
        return json.dump(ratdict)
    
    def wtJson(self):
        wtDict=self.toDict('wt')
        return json.dump(wtDict)

# if __name__ == "__main__":
#     getjsonstring()