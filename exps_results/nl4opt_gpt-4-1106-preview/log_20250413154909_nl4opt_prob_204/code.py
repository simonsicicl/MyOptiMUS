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
GlassesOfMilk = model.addVar(vtype=gp.GRB.INTEGER, name="GlassesOfMilk")
PlatesOfVeg = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PlatesOfVeg")

# Constraint: Total calcium intake from milk and vegetables must be at least C units
model.addConstr(CalciumMilk * GlassesOfMilk + CalciumVeg * PlatesOfVeg >= C, name="calcium_intake")

# Ensure total iron from milk and vegetables is at least I units
model.addConstr(IronMilk * GlassesOfMilk + IronVeg * PlatesOfVeg >= I, name="iron_requirement")

# Add constraint to ensure the number of glasses of milk consumed is non-negative
model.addConstr(GlassesOfMilk >= 0, name="glasses_of_milk_non_negative")

model.addConstr(PlatesOfVeg >= 0, name="non_negativity_veg")

# Ensure that the calcium requirement is met
model.addConstr(CalciumMilk * GlassesOfMilk + CalciumVeg * PlatesOfVeg >= C, name="calcium_requirement")

# Ensure that the iron requirement is met constraint
model.addConstr(IronMilk * GlassesOfMilk + IronVeg * PlatesOfVeg >= I, name="iron_requirement")

# Set objective
model.setObjective(CostMilk * GlassesOfMilk + CostVeg * PlatesOfVeg, gp.GRB.MINIMIZE)

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
