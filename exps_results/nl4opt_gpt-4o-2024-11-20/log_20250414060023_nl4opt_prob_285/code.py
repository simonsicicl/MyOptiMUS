import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_285/data.json", "r") as f:
    data = json.load(f)

WideCapacity = data["WideCapacity"] # scalar parameter
NarrowCapacity = data["NarrowCapacity"] # scalar parameter
WideGarbage = data["WideGarbage"] # scalar parameter
NarrowGarbage = data["NarrowGarbage"] # scalar parameter
MaxWideTrails = data["MaxWideTrails"] # scalar parameter
MaxCapacity = data["MaxCapacity"] # scalar parameter
WideTrails = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WideTrails")
NarrowTrails = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NarrowTrails")
VisitorsWide = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VisitorsWide")
VisitorsNarrow = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VisitorsNarrow")

# Adding constraint: The number of wide trails must be non-negative
model.addConstr(WideTrails >= 0, name="non_negative_constraint_WideTrails")

# Non-negativity constraint for NarrowTrails
model.addConstr(NarrowTrails >= 0, name="non_negativity_NarrowTrails")

# Add constraint to ensure total visitors from wide trails does not exceed WideCapacity multiplied by WideTrails
model.addConstr(VisitorsWide <= WideCapacity * WideTrails, name="wide_trails_capacity")

# Add constraint to ensure total number of visitors from narrow trails does not exceed capacity of all narrow trails combined
model.addConstr(VisitorsNarrow <= NarrowCapacity * NarrowTrails, name="narrow_trail_capacity")

# Add constraint for maximum number of wide trails
model.addConstr(WideTrails <= MaxWideTrails, name="max_wide_trails_constraint")

# Add constraint to ensure total visitors do not exceed maximum capacity
model.addConstr(VisitorsWide + VisitorsNarrow <= MaxCapacity, name="visitors_capacity")

# Change the variable WideTrails to integer type
WideTrails.vtype = gp.GRB.INTEGER

# Change the variable NarrowTrails to have integer integrality since it is defined to be an integer
NarrowTrails.vtype = gp.GRB.INTEGER

# Ensure VisitorsWide is non-negative
model.addConstr(VisitorsWide >= 0, name="non_negative_visitorswide_constraint")

# Add constraint to ensure total wide-trail visitors do not exceed the sum of wide trail capacities
model.addConstr(VisitorsWide <= WideTrails * WideCapacity, name="wide_trail_capacity")

# Add constraint to ensure total narrow-trail visitors do not exceed total capacities
model.addConstr(VisitorsNarrow <= NarrowTrails * NarrowCapacity, name="narrow_trail_capacity_constraint")

# Set objective
model.setObjective(WideGarbage * WideTrails + NarrowGarbage * NarrowTrails, gp.GRB.MINIMIZE)

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
