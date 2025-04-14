import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_187/data.json", "r") as f:
    data = json.load(f)

FerryCapacity = data["FerryCapacity"] # scalar parameter
RailCapacity = data["RailCapacity"] # scalar parameter
MinRailToFerryRatio = data["MinRailToFerryRatio"] # scalar parameter
MinCornBoxes = data["MinCornBoxes"] # scalar parameter
FerryTrips = model.addVar(vtype=gp.GRB.INTEGER, name="FerryTrips")
LightRailTrips = model.addVar(vtype=gp.GRB.INTEGER, name="LightRailTrips")
TotalBoxesByFerry = model.addVar(vtype=gp.GRB.INTEGER, name="TotalBoxesByFerry")
TotalBoxesByLightRail = model.addVar(vtype=gp.GRB.INTEGER, name="TotalBoxesByLightRail")

# Since the variable FerryTrips is already defined as an integer variable, we only need to add the non-negativity constraint
model.addConstr(FerryTrips >= 0, name="non_negative_ferry_trips")

# Add constraint for non-negative number of light rail trips
model.addConstr(LightRailTrips >= 0, name="non_negative_LightRailTrips")

# Constraint for the maximum number of boxes transported by ferry
model.addConstr(TotalBoxesByFerry <= FerryTrips * FerryCapacity, name="ferry_capacity_constraint")

# Constraint: Each light rail trip can only carry up to RailCapacity boxes
model.addConstr(TotalBoxesByLightRail <= LightRailTrips * RailCapacity, name="rail_capacity_constraint")

# Constraint: Number of light rail trips must be at least MinRailToFerryRatio times the number of ferry trips
model.addConstr(LightRailTrips >= MinRailToFerryRatio * FerryTrips, name="min_rail_to_ferry_ratio")

# Add constraint to ensure at least MinCornBoxes boxes of corn must be sent
model.addConstr(TotalBoxesByFerry + TotalBoxesByLightRail >= MinCornBoxes, name="min_corn_boxes")

# Ensure the minimum ratio of light rail trips to ferry trips is met
model.addConstr(LightRailTrips >= MinRailToFerryRatio * FerryTrips, name="MinRatio_LightRailToFerry")

# Ensure the total number of boxes transported by ferry meets its capacity constraint
model.addConstr(TotalBoxesByFerry == FerryTrips * FerryCapacity, name="ferry_capacity_constraint")

# Constraint to ensure the total number of boxes by light rail meets its capacity
model.addConstr(TotalBoxesByLightRail == LightRailTrips * RailCapacity, name="TotalBoxesByLightRailCapacity")

# Ensure the total number of boxes of corn transported meets the minimum requirement
model.addConstr(TotalBoxesByFerry + TotalBoxesByLightRail >= MinCornBoxes, name="min_corn_boxes_requirement")

# Set the objective function
model.setObjective(FerryTrips + LightRailTrips, gp.GRB.MINIMIZE)

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
