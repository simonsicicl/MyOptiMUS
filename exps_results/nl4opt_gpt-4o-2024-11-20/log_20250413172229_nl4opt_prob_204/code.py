import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_204/data.json", "r") as f:
    data = json.load(f)

C = data["C"] # scalar parameter
I = data["I"] # scalar parameter
CostMilk = data["CostMilk"] # scalar parameter
CalciumMilk = data["CalciumMilk"] # scalar parameter
IronMilk = data["IronMilk"] # scalar parameter
CostVeg = data["CostVeg"] # scalar parameter
CalciumVeg = data["CalciumVeg"] # scalar parameter
IronVeg = data["IronVeg"] # scalar parameter
MilkConsumed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MilkConsumed")
VegetablesConsumed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VegetablesConsumed")

# Add calcium intake constraint
model.addConstr(CalciumMilk * MilkConsumed + CalciumVeg * VegetablesConsumed >= C, name="calcium_intake_constraint")

# Add constraint for total iron requirement
model.addConstr(IronMilk * MilkConsumed + IronVeg * VegetablesConsumed >= I, name="iron_requirement")

# The non-negativity constraint for MilkConsumed is inherently satisfied as it is defined as a continuous variable in Gurobi, which is non-negative by default.

# No additional code is necessary as the non-negativity constraint is automatically handled by Gurobi for non-negative domain variables such as the continuous variable "VegetablesConsumed".

# Add calcium intake constraint
model.addConstr(
    MilkConsumed * CalciumMilk + VegetablesConsumed * CalciumVeg >= C,
    name="calcium_intake"
)

# Add constraint to ensure total iron intake meets the daily requirement
model.addConstr(IronMilk * MilkConsumed + IronVeg * VegetablesConsumed >= I, name="iron_intake_requirement")

# Add non-negativity constraint for MilkConsumed
model.addConstr(MilkConsumed >= 0, name="non_negativity_MilkConsumed")

# Adding non-negativity constraint for VegetablesConsumed
model.addConstr(VegetablesConsumed >= 0, name="non_negativity_constraint")

# Set objective
model.setObjective(CostMilk * MilkConsumed + CostVeg * VegetablesConsumed, gp.GRB.MINIMIZE)

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
