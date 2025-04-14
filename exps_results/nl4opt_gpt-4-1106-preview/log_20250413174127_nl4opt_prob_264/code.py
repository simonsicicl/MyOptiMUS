import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_264/data.json", "r") as f:
    data = json.load(f)

SpecializedRate = data["SpecializedRate"] # scalar parameter
CommonRate = data["CommonRate"] # scalar parameter
SpecializedCharge = data["SpecializedCharge"] # scalar parameter
CommonCharge = data["CommonCharge"] # scalar parameter
MinimumImages = data["MinimumImages"] # scalar parameter
MinimumSpecializedProportion = data["MinimumSpecializedProportion"] # scalar parameter
SpecializedImagesAnnotated = model.addVar(vtype=gp.GRB.INTEGER, name="SpecializedImagesAnnotated")
CommonImagesAnnotated = model.addVar(vtype=gp.GRB.INTEGER, name="CommonImagesAnnotated")

# No code needed since the variable 'SpecializedImagesAnnotated' is already defined as non-negative by setting its type to INTEGER.
# Gurobi's default lower bound for integer variables is 0, which satisfies the given constraint.

# Add non-negativity constraint on the number of images annotated by the common company
model.addConstr(CommonImagesAnnotated >= 0, name="non_negative_common_images")

# No content to place here for model variables as they are already appropriately defined above

# Add constraint to ensure that at least a minimum proportion of the work is allocated to the specialized company
model.addConstr(SpecializedImagesAnnotated >= MinimumSpecializedProportion * (SpecializedImagesAnnotated + CommonImagesAnnotated), name="min_specialized_proportion")

# Define the objective function
TotalCost = (SpecializedImagesAnnotated / SpecializedRate) * SpecializedCharge + \
            (CommonImagesAnnotated / CommonRate) * CommonCharge

# Set the objective
model.setObjective(TotalCost, gp.GRB.MINIMIZE)

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
