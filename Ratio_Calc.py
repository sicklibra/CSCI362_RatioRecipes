import json
# import Recipe #also includes ingredient class.

#Global variables for conversions
G2LB=453.5924 # Grams to 1lb
OZ2LB=16  #Ounces to 1lb
G2KG2MG=1000  #1k g/kg 1k mg/g

def saveRecipe(instring):
    jDict=loadRecipe(instring)
    #precondition is that json values match exactly, and 
    inRecipe=makeRecipe(jDict)
    return inRecipe.ratJason()

def getRecipe(instring):
    jDict=loadRecipe(instring)
    inrecipe=makeRecipe(jDict)
    return inrecipe.wtJson()

'''If we are updating/iterating a recipe, I will return a pk of -1 this will signal 
on the front end, that the key for this recipe needs to be new and the parent key needs to be 
updated to the key of the recipe just iterated.'''
def updateRecipe(instring):
    jDict=loadRecipe(instring)
    inrecipe= makeRecipe(jDict)
    inrecipe.pk="-1"

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