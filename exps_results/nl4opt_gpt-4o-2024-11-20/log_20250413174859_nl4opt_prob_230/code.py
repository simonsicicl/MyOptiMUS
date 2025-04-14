import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_230/data.json", "r") as f:
    data = json.load(f)

Tc = data["Tc"] # scalar parameter
Td = data["Td"] # scalar parameter
Pmin = data["Pmin"] # scalar parameter
Dmin = data["Dmin"] # scalar parameter
CalciumPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CalciumPills")
VitaminDPills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VitaminDPills")

# Add non-negativity and calcium-vs-vitamin D constraints
model.addConstr(CalciumPills >= 0, name="non_negative_calcium")
model.addConstr(CalciumPills >= VitaminDPills + 1, name="calcium_vs_vitamin_d")

# Adding constraints for non-negative vitamin D pills, minimum intake, and relative calcium dominance
model.addConstr(VitaminDPills >= 0, name="non_negative_vitamin_d")
model.addConstr(VitaminDPills >= Dmin, name="min_vitamin_d_intake")
model.addConstr(CalciumPills + VitaminDPills >= Pmin, name="min_total_pills")
model.addConstr(CalciumPills >= VitaminDPills + 1, name="calcium_dominance")

# Add constraint for the minimum total number of pills
model.addConstr(CalciumPills + VitaminDPills >= Pmin, name="min_pills_constraint")

# Add constraint to ensure the number of vitamin D pills taken is at least Dmin
model.addConstr(VitaminDPills >= Dmin, name="min_vitamin_d_pills")

# Add constraint: CalciumPills must be strictly greater than VitaminDPills
model.addConstr(CalciumPills >= VitaminDPills + 1, name="calcium_vs_vitaminD")

# Add constraint ensuring total number of pills meets the minimum requirement
model.addConstr(CalciumPills + VitaminDPills >= Pmin, name="min_pills_constraint")

# Add constraint ensuring the minimum consumption of vitamin D pills in a month
model.addConstr(VitaminDPills >= Dmin, name="min_vitamin_d_pills")

# Ensure variables are integers to apply the strict inequality constraint properly
CalciumPills.vtype = gp.GRB.INTEGER
VitaminDPills.vtype = gp.GRB.INTEGER

# Add the constraint: CalciumPills >= VitaminDPills + 1
model.addConstr(CalciumPills >= VitaminDPills + 1, name="CalciumPills_greater_than_VitaminDPills")

# Set objective
model.setObjective(Tc * CalciumPills + Td * VitaminDPills, gp.GRB.MINIMIZE)

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
