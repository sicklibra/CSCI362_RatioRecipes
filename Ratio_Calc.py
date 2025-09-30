import json

class RatioCalc:
    G2LB=453.5924 # Grams to 1lb
    OZ2LB=16  #Ounces to 1lb
    G2KG2MG=1000  #1k g/kg 1k mg/g
    name='' 
    description=''
    ingredients=[]
    notes=''
    def __init__(self, jsonstr):
        
