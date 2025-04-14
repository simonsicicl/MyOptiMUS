import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_222/data.json", "r") as f:
    data = json.load(f)

StrawberryProfit = data["StrawberryProfit"] # scalar parameter
SugarProfit = data["SugarProfit"] # scalar parameter
MaxStrawberryDemand = data["MaxStrawberryDemand"] # scalar parameter
MaxSugarDemand = data["MaxSugarDemand"] # scalar parameter
MaxProductionCapacity = data["MaxProductionCapacity"] # scalar parameter
StrawberryCookiesProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StrawberryCookiesProduced")
SugarCookiesProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SugarCookiesProduced")

# Non-negativity constraint for the number of strawberry cookies produced
model.addConstr(StrawberryCookiesProduced >= 0, name="non_negativity_StrawberryCookiesProduced")

# Non-negativity constraint for the SugarCookiesProduced variable
model.addConstr(SugarCookiesProduced >= 0, name="non_negativity_sugar_cookies")

# Add constraint for strawberry cookie production not exceeding maximum demand
model.addConstr(StrawberryCookiesProduced <= MaxStrawberryDemand, name="MaxStrawberryCookiesConstraint")

# Add constraint to ensure sugar cookies produced do not exceed maximum demand
model.addConstr(SugarCookiesProduced <= MaxSugarDemand, name="max_sugar_demand")

# Add constraint for maximum production capacity
model.addConstr(StrawberryCookiesProduced + SugarCookiesProduced <= MaxProductionCapacity, 
                name="max_production_capacity")

# Add demand constraint for strawberry cookies
model.addConstr(StrawberryCookiesProduced <= MaxStrawberryDemand, name="strawberry_demand_constraint")

# Add demand constraint for sugar cookies
model.addConstr(SugarCookiesProduced <= MaxSugarDemand, name="sugar_cookie_demand")

# Add production capacity constraint
model.addConstr(StrawberryCookiesProduced + SugarCookiesProduced <= MaxProductionCapacity, name="production_capacity")

# Non-negativity constraint for strawberry cookies
model.addConstr(StrawberryCookiesProduced >= 0, name="non_negativity_StrawberryCookies")

# The non-negativity constraint for SugarCookiesProduced is already enforced by the variable's non-negative domain in Gurobi (default for continuous variables).

# Set objective
model.setObjective(StrawberryProfit * StrawberryCookiesProduced + SugarProfit * SugarCookiesProduced, gp.GRB.MAXIMIZE)

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
