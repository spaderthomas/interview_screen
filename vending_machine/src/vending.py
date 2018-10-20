#!/usr/bin/env python

notes = '''
You can find assumptions I've made inline by searching for @assume
'''

import json
from pathlib import Path
import sys

inventory = json.loads(open(sys.argv[1]).read())
transactions = json.loads(open(sys.argv[2]).read())

results = []

for trans in transactions:
    # @assume well-formed data. 
    item = inventory[trans["name"]]
    cents_cost = int(item["price"] * 100)
    result = {}

    # Determine amount the customer paid
    cents_paid = 0
    for coin in trans["funds"]:
        cents_paid += coin
        
    # Two cases where no product delivered + give all change back, which share code
    # 1: There is no product left
    # 2: The customer didn't add enough money
    if (item["quantity"] is 0) or (cents_paid < cents_cost):
        result["product_delivered"] = False
        result["change"] = [coin for coin in trans["funds"]]
        results.append(result)
        continue
    # Customer overpaid. Deliver item, return some change.
    elif cents_paid > cents_cost:
        amount_owed = cents_paid - cents_cost
        coins_paid = sorted([coin for coin in trans["funds"]])
        coins_returned = []

        # Simple change-giving algorithm: Always give the largest coin you can
        # @assume infinite amounts of each kind of change.
        while amount_owed is not 0:
            if (amount_owed >= 25):
                coins_returned.append(25)
                amount_owed -= 25
                continue
            elif (amount_owed >= 10):
                coins_returned.append(10)
                amount_owed -= 10
                continue
            elif (amount_owed >= 5):
                coins_returned.append(5)
                amount_owed -= 5
                continue
            elif (amount_owed >= 1):
                coins_returned.append(1)
                amount_owed -= 1
                continue
                
        result["product_delivered"] = True
        result["change"] = coins_returned
        results.append(result)
        item["quantity"] -= 1
        continue
    # Customer paid exactly. Deliver item and give no change
    elif cents_paid is cents_cost:
        result["product_delivered"] = True
        result["change"] = []
        results.append(result)
        item["quantity"] -= 1
        continue

# Make sure to dump into a JSON string, since Python dict syntax != JSON syntax
print(json.dumps(results))
