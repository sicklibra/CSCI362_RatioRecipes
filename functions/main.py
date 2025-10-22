# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app
from firebase_admin import firestore as admin_firestore

# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=10)

# Initialize the Admin SDK so we can access Firestore with admin privileges
initialize_app()

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


@https_fn.on_request()
def save_and_scale_recipe(req: https_fn.Request) -> https_fn.Response:
    """
    Expects POST JSON:
    {
      "name": "Recipe name",
      "description": "...",
      "ingredients": [{"name":"flour","weight":200}, ...] or [{"name":"flour","ratio":0.5}, ...],
      "unit": "g",
      "totwt": 320,         # optional if weights provided
      "scale": 2.0          # numeric scale factor
    }

    Scales ingredient weights and saves a document to collection 'recipes'.
    """
    # CORS headers used by all responses
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

    try:
        # Handle CORS preflight
        if req.method == 'OPTIONS':
            # Always allow preflight requests
            return https_fn.Response('', status=204, headers=cors_headers)

        if req.method != "POST":
            return https_fn.Response(json.dumps({"error": "Only POST allowed"}), status=405, mimetype="application/json", headers=cors_headers)

        body = req.get_json(silent=True)
        if not body:
            return https_fn.Response(json.dumps({"error": "Missing or invalid JSON"}), status=400, mimetype="application/json", headers=cors_headers)

        name = body.get('name', '')
        description = body.get('description', '')
        unit = body.get('unit', 'g')
        scale = float(body.get('scale', 1.0))
        ingredients = body.get('ingredients', [])
        totwt = body.get('totwt', 0)

        # Determine if ingredients are weight-based or ratio-based
        scaled_ingredients = []
        if not isinstance(ingredients, list):
            return https_fn.Response(json.dumps({"error": "ingredients must be a list"}), status=400, mimetype="application/json")

        if len(ingredients) == 0:
            return https_fn.Response(json.dumps({"error": "no ingredients provided"}), status=400, mimetype="application/json", headers=cors_headers)

        first = ingredients[0]
        # Weight-based input
        if 'weight' in first:
            # ensure numeric weights
            for ing in ingredients:
                name_i = ing.get('name')
                wt = float(ing.get('weight', 0))
                scaled_wt = round(wt * scale, 4)
                scaled_ingredients.append({'name': name_i, 'weight': scaled_wt})
            # compute total weight
            total_weight = round(sum([i['weight'] for i in scaled_ingredients]), 4)

        # Ratio-based input (requires totwt)
        elif 'ratio' in first:
            if not totwt or float(totwt) == 0:
                return https_fn.Response(json.dumps({"error": "totwt required when sending ratios"}), status=400, mimetype="application/json")
            totwt = float(totwt) * float(scale)
            for ing in ingredients:
                name_i = ing.get('name')
                ratio = float(ing.get('ratio', 0))
                wt = round(ratio * totwt, 4)
                scaled_ingredients.append({'name': name_i, 'weight': wt, 'ratio': ratio})
            total_weight = round(totwt, 4)

        else:
            return https_fn.Response(json.dumps({"error": "ingredient objects must contain 'weight' or 'ratio'"}), status=400, mimetype="application/json", headers=cors_headers)

        # Prepare document to save
        doc = {
            'name': name,
            'description': description,
            'unit': unit,
            'ingredients': scaled_ingredients,
            'totwt': total_weight,
            'scale': scale
        }

        db = admin_firestore.client()
        ref = db.collection('recipes').add(doc)

        # Attempt to extract the document id from the add result
        doc_id = None
        try:
            if isinstance(ref, (list, tuple)) and len(ref) > 0:
                candidate = ref[0]
            else:
                candidate = ref
            doc_id = getattr(candidate, 'id', None) or getattr(candidate, 'document_id', None)
        except Exception:
            doc_id = None

        # Fallback: if add returned a write_result + ref tuple, try second element
        if not doc_id and isinstance(ref, (list, tuple)) and len(ref) > 1:
            doc_id = getattr(ref[1], 'id', None)

        response = {'id': doc_id, 'data': doc}
        return https_fn.Response(json.dumps(response), status=200, mimetype='application/json', headers=cors_headers)

    except Exception as e:
        return https_fn.Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json', headers=cors_headers)


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

        elif 'weight' in inglst[1].keys():
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

        elif 'Ratio' in inglst[1].keys():
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

# initialize_app()
#
#
# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello world!")