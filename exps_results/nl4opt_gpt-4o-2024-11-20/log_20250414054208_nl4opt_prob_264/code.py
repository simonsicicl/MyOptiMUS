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
SpecializedImages = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SpecializedImages")
CommonImages = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CommonImages")
TotalImagesAnnotated = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalImagesAnnotated")

# No additional code is necessary as the non-negativity constraint is automatically handled by Gurobi for non-negative domain variables such as the `SpecializedImages` variable. Ensure the variable range is not modified elsewhere.

# Add non-negativity constraints for SpecializedImages and CommonImages
model.addConstr(SpecializedImages >= 0, name="non_negativity_SpecializedImages")
model.addConstr(CommonImages >= 0, name="non_negativity_CommonImages")

# Add constraint ensuring total annotated images are at least the minimum required
model.addConstr(SpecializedImages + CommonImages >= MinimumImages, 
                name="min_images_constraint")

# Add constraint ensuring at least MinimumSpecializedProportion of the total work is allocated to the specialized company
model.addConstr(SpecializedImages >= MinimumSpecializedProportion * TotalImagesAnnotated, name="specialized_work_proportion")

# Add constraint for minimum number of images to be annotated
model.addConstr(SpecializedImages + CommonImages >= MinimumImages, name="minimum_images_constraint")

# Add constraint to ensure the minimum proportion of images are allocated to the specialized company
model.addConstr(SpecializedImages >= MinimumSpecializedProportion * (SpecializedImages + CommonImages), name="min_proportion_specialized")

# Add constraint for TotalImagesAnnotated as the sum of SpecializedImages and CommonImages
model.addConstr(TotalImagesAnnotated == SpecializedImages + CommonImages, name="total_images_constraint")

# Adding the constraint to ensure the total number of annotated images meets or exceeds the minimum required
model.addConstr(SpecializedImages + CommonImages >= MinimumImages, name="min_images_constraint")

# Add constraint to ensure minimum specialized proportion
model.addConstr(SpecializedImages >= MinimumSpecializedProportion * TotalImagesAnnotated, name="min_specialized_proportion")

# Add constraint ensuring total number of images is the sum of images annotated by specialized and common companies
model.addConstr(TotalImagesAnnotated == SpecializedImages + CommonImages, name="total_images_constraint")

# Set objective
model.setObjective(SpecializedImages * (SpecializedCharge / SpecializedRate) + CommonImages * (CommonCharge / CommonRate), gp.GRB.MINIMIZE)

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
