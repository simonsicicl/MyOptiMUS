import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_271/data.json", "r") as f:
    data = json.load(f)

NorthernInjectionsRate = data["NorthernInjectionsRate"] # scalar parameter
NorthernCreamRate = data["NorthernCreamRate"] # scalar parameter
WesternInjectionsRate = data["WesternInjectionsRate"] # scalar parameter
WesternCreamRate = data["WesternCreamRate"] # scalar parameter
NorthernPlasticRate = data["NorthernPlasticRate"] # scalar parameter
WesternPlasticRate = data["WesternPlasticRate"] # scalar parameter
TotalPlastic = data["TotalPlastic"] # scalar parameter
MinInjections = data["MinInjections"] # scalar parameter
MinCream = data["MinCream"] # scalar parameter
NorthernFactoryHours = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NorthernFactoryHours")
WesternFactoryHours = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WesternFactoryHours")

# Total plastic usage constraint for northern and western factories
model.addConstr(NorthernPlasticRate * NorthernFactoryHours + WesternPlasticRate * WesternFactoryHours <= TotalPlastic, name="total_plastic_usage")

# Add constraint for minimum total grams of anti-itch injections produced by both factories
model.addConstr(NorthernFactoryHours * NorthernInjectionsRate + WesternFactoryHours * WesternInjectionsRate >= MinInjections, name="min_injections_requirement")

# Constraint for the minimum requirement of topical cream production
model.addConstr(NorthernCreamRate * NorthernFactoryHours + WesternCreamRate * WesternFactoryHours >= MinCream, "min_cream_requirement")

model.addConstr(NorthernFactoryHours >= 0, name="non_negative_hours")

model.addConstr(WesternFactoryHours >= 0, "WesternFactoryHours_non_negative")

# Set objective
model.setObjective(NorthernFactoryHours + WesternFactoryHours, gp.GRB.MINIMIZE)

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
