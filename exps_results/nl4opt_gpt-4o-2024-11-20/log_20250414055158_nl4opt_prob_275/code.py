import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_275/data.json", "r") as f:
    data = json.load(f)

TimeA = data["TimeA"] # scalar parameter
TimeB = data["TimeB"] # scalar parameter
MaxRatioAtoB = data["MaxRatioAtoB"] # scalar parameter
MinUnitsA = data["MinUnitsA"] # scalar parameter
MinTotalUnits = data["MinTotalUnits"] # scalar parameter
UnitsA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="UnitsA")
UnitsB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="UnitsB")

# Add non-negativity constraint for UnitsA
model.addConstr(UnitsA >= 0, name="non_negativity_UnitsA")

# The variable UnitsB is already defined with the non-negativity constraint as it is a continuous variable with no lower bound added.

# Add constraint ensuring UnitsA is at most MaxRatioAtoB times UnitsB
model.addConstr(UnitsA <= MaxRatioAtoB * UnitsB, name="chemical_ratio_constraint")

# Add constraint ensuring at least MinUnitsA units of chemical A are in the mixer
model.addConstr(UnitsA >= MinUnitsA, name="min_units_A")

# Add constraint to ensure the total units in the mixer satisfy the minimum requirement
model.addConstr(UnitsA + UnitsB >= MinTotalUnits, name="mixer_min_total_units")

# Add minimum quantity constraint for chemical A
model.addConstr(UnitsA >= MinUnitsA, name="min_quantity_chemical_A")

# Add constraint to ensure the total units of chemicals A and B meet the minimum requirement
model.addConstr(UnitsA + UnitsB >= MinTotalUnits, name="min_total_units_constraint")

# Add constraint for the ratio of UnitsA to UnitsB
model.addConstr(UnitsA <= MaxRatioAtoB * UnitsB, name="ratio_constraint_A_to_B")

# Set objective
model.setObjective((TimeA * UnitsA) + (TimeB * UnitsB), gp.GRB.MINIMIZE)

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
