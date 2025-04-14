import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_143/data.json", "r") as f:
    data = json.load(f)

TotalMedicinalUnits = data["TotalMedicinalUnits"] # scalar parameter
LargePillMedicinalUnits = data["LargePillMedicinalUnits"] # scalar parameter
LargePillFillerUnits = data["LargePillFillerUnits"] # scalar parameter
SmallPillMedicinalUnits = data["SmallPillMedicinalUnits"] # scalar parameter
SmallPillFillerUnits = data["SmallPillFillerUnits"] # scalar parameter
MinimumLargePills = data["MinimumLargePills"] # scalar parameter
MinimumSmallPillsPercentage = data["MinimumSmallPillsPercentage"] # scalar parameter
NumberOfLargePills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfLargePills")
NumberOfSmallPills = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallPills")
TotalPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalPills")

# The number of large pills must be non-negative
model.addConstr(NumberOfLargePills >= 0, name="non_negativity_large_pills")

# Add non-negativity constraint for the number of small pills
model.addConstr(NumberOfSmallPills >= 0, name="non_negativity_small_pills")

# Add constraint for the total medicinal units used in large and small pills
model.addConstr(LargePillMedicinalUnits * NumberOfLargePills + SmallPillMedicinalUnits * NumberOfSmallPills <= TotalMedicinalUnits, "TotalMedicinalUnitsConstraint")

# Constraint for minimum required number of large pills
model.addConstr(NumberOfLargePills >= MinimumLargePills, name="min_large_pills")

# At least MinimumSmallPillsPercentage of the total number of pills must be small pills constraint
model.addConstr((1 - MinimumSmallPillsPercentage) * NumberOfSmallPills >= MinimumSmallPillsPercentage * NumberOfLargePills, "MinimumSmallPillsPercentage_Constraint")

# Ensure that the number of large pills produced meets the minimum required
model.addConstr(NumberOfLargePills >= MinimumLargePills, "min_large_pills")

# Constraint to ensure at least a certain percentage of the total pills produced should be small pills
model.addConstr(NumberOfSmallPills >= MinimumSmallPillsPercentage * TotalPills, name="min_small_pills_percentage")

# Define the total number of pills constraint
model.addConstr(TotalPills == NumberOfLargePills + NumberOfSmallPills, name="total_pills")

# Define the objective function
objective = NumberOfLargePills * LargePillFillerUnits + NumberOfSmallPills * SmallPillFillerUnits

# Set the objective in the model
model.setObjective(objective, gp.GRB.MINIMIZE)

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
