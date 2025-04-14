import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/BlendingProblem/data.json", "r") as f:
    data = json.load(f)

AlloysOnMarket = data["AlloysOnMarket"] # scalar parameter
RequiredElements = data["RequiredElements"] # scalar parameter
CompositionDataPercentage = np.array(data["CompositionDataPercentage"]) # ['RequiredElements', 'AlloysOnMarket']
DesiredBlendPercentage = np.array(data["DesiredBlendPercentage"]) # ['RequiredElements']
AlloyPrice = np.array(data["AlloyPrice"]) # ['AlloysOnMarket']
QuantityUsed = model.addVars(AlloysOnMarket, vtype=gp.GRB.CONTINUOUS, name="QuantityUsed")
MarketAvailability = model.addVars(AlloysOnMarket, vtype=gp.GRB.CONTINUOUS, name="MarketAvailability")

# Add non-negativity constraints for the quantity of each alloy used
for i in range(AlloysOnMarket):
    model.addConstr(QuantityUsed[i] >= 0, name="non_negativity_alloy_{}".format(i))

# Add constraints to ensure that final blend meets required percentages for each of the RequiredElements
for i in range(RequiredElements):
    model.addConstr(
        gp.quicksum(CompositionDataPercentage[i,j] * QuantityUsed[j] for j in range(AlloysOnMarket)) == 
        DesiredBlendPercentage[i] * gp.quicksum(QuantityUsed[j] for j in range(AlloysOnMarket)), 
        name=f"element_percentage_{i}"
    )

# Market availability constraints for each alloy
for i in range(AlloysOnMarket):
    model.addConstr(QuantityUsed[i] <= MarketAvailability[i], name=f"market_availability_{i}")

# Matching actual blend percentage to desired blend percentage for each required element
for j in range(RequiredElements):
    model.addConstr(
        gp.quicksum(CompositionDataPercentage[j, i] * QuantityUsed[i] for i in range(AlloysOnMarket)) == 
        DesiredBlendPercentage[j] * gp.quicksum(QuantityUsed[i] for i in range(AlloysOnMarket)),
        name=f"blend_percentage_match_element_{j}"
    )

# Set objective
model.setObjective(gp.quicksum(AlloyPrice[i] * QuantityUsed[i] for i in range(AlloysOnMarket)), gp.GRB.MINIMIZE)

# Optimize model
model.optimize()


# Get model status
status = model.status

obj_val = None
# check whether the model is infeasible, has infinite solutions, or has an optimal solution
if status == gp.GRB.INFEASIBLE:
    obj_val = "infeasible"
elif status == gp.GRB.INF_OR_UNBD:
    obj_val = "infeasible or unbounded"
elif status == gp.GRB.UNBOUNDED:
    obj_val = "unbounded"
elif status == gp.GRB.OPTIMAL:
    obj_val = model.objVal
