import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_227/data.json", "r") as f:
    data = json.load(f)

SubsoilWater = data["SubsoilWater"] # scalar parameter
TopsoilWater = data["TopsoilWater"] # scalar parameter
TotalBags = data["TotalBags"] # scalar parameter
MinTopsoil = data["MinTopsoil"] # scalar parameter
MaxTopsoilProportion = data["MaxTopsoilProportion"] # scalar parameter
NumberOfSubsoilBags = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSubsoilBags")
NumberOfTopsoilBags = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTopsoilBags")

# The variable NumberOfSubsoilBags is already ensured to be non-negative by its definition.
# Hence, no additional constraint is required.

# Ensure that the number of bags of topsoil is non-negative and meets minimum requirement
model.addConstr(NumberOfTopsoilBags >= 0, name="NonNegativityTopsoilBags")
model.addConstr(NumberOfTopsoilBags >= MinTopsoil, name="MinRequirementTopsoilBags")

# Total number of subsoil and topsoil bags constraint
model.addConstr(NumberOfSubsoilBags + NumberOfTopsoilBags <= TotalBags, name="total_bags_constraint")

# Add constraint to ensure that at least the minimum number of topsoil bags are used
model.addConstr(NumberOfTopsoilBags >= MinTopsoil, name="min_topsoil_bags")

# Constraint: Topsoil bags cannot exceed a certain proportion of the total bags of soil
model.addConstr(NumberOfTopsoilBags <= MaxTopsoilProportion * (NumberOfSubsoilBags + NumberOfTopsoilBags), 
                name="topsoil_proportion_constraint")

# Add constraint: The number of bags of topsoil cannot exceed the maximum proportion allowed of the total number of bags
model.addConstr(NumberOfTopsoilBags <= MaxTopsoilProportion * TotalBags, "topsoil_proportion_limit")

# Ensure the number of bags of topsoil meets the minimum requirement
model.addConstr(NumberOfTopsoilBags >= MinTopsoil, name="min_topsoil_requirement")

# Add constraint for the total number of subsoil and topsoil bags available
model.addConstr(NumberOfSubsoilBags + NumberOfTopsoilBags <= TotalBags, name="soil_bags_limit")

# Define the objective function
model.setObjective(SubsoilWater * NumberOfSubsoilBags + TopsoilWater * NumberOfTopsoilBags, gp.GRB.MINIMIZE)

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
