import json
import pandas as pd
 
# Opening JSON file
f = open('../../data/intent/intents.json')
intent = json.load(f)
intent = intent['intents']

print(f"Total number of intents: {len(intent)}")

# check out some of the questions
intent[0:5]