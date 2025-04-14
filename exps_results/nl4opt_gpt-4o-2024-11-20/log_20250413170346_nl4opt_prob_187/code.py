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
FerryTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FerryTrips")
RailTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RailTrips")
CornBoxesFerry = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CornBoxesFerry")
CornBoxesRail = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CornBoxesRail")

# Add constraints related to ferry and rail trips

# Non-negativity constraints
model.addConstr(FerryTrips >= 0, name="NonNegativity_FerryTrips")
model.addConstr(RailTrips >= 0, name="NonNegativity_RailTrips")

# Minimum ratio of rail trips to ferry trips
model.addConstr(RailTrips >= MinRailToFerryRatio * FerryTrips, name="RailToFerryRatio")

# Minimum boxes of corn to transport
model.addConstr(FerryTrips * FerryCapacity + RailTrips * RailCapacity >= MinCornBoxes, name="MinCornBoxes")

# The variable RailTrips is already coded as a continuous variable. No additional code is needed for non-negativity since Gurobi variables are non-negative by default unless specified otherwise.

# Add constraint to ensure total number of boxes transported by ferry is bounded by ferry capacity multiplied by trips
model.addConstr(CornBoxesFerry <= FerryTrips * FerryCapacity, name="ferry_capacity_constraint")

# Add constraint to ensure the number of boxes transported by rail is bounded by the total rail capacity
model.addConstr(CornBoxesRail <= RailTrips * RailCapacity, name="rail_capacity_constraint")

# Add constraint to ensure the number of rail trips is at least the ratio times the ferry trips
model.addConstr(RailTrips >= MinRailToFerryRatio * FerryTrips, name="rail_to_ferry_ratio")

# Adding the constraint for minimum total boxes of corn being delivered
model.addConstr(
    (FerryTrips * FerryCapacity) + (RailTrips * RailCapacity) >= MinCornBoxes, 
    name="min_corn_boxes_constraint"
)

# Add constraint to enforce the minimum ratio of rail trips to ferry trips
model.addConstr(RailTrips >= MinRailToFerryRatio * FerryTrips, name="min_ratio_rail_to_ferry")

# Add the constraint for minimum total number of boxes of corn transported
model.addConstr(FerryCapacity * FerryTrips + RailCapacity * RailTrips >= MinCornBoxes, name="min_corn_boxes_constraint")

# Non-negativity constraint for FerryTrips
model.addConstr(FerryTrips >= 0, name="non_negativity_FerryTrips")

# Add constraint relating CornBoxesFerry with FerryTrips and FerryCapacity
model.addConstr(CornBoxesFerry == FerryTrips * FerryCapacity, name="corn_boxes_ferry_constraint")

# Add constraint to ensure rail trips are at least the minimum ratio of ferry trips
model.addConstr(RailTrips >= MinRailToFerryRatio * FerryTrips, name="min_rail_to_ferry_ratio")

# Add constraint to ensure the total number of boxes of corn transported meets or exceeds the requirement
model.addConstr(FerryTrips * FerryCapacity + RailTrips * RailCapacity >= MinCornBoxes, name="corn_transport_requirement")

# Enforce the minimum ratio of light rail trips to ferry trips
model.addConstr(RailTrips >= MinRailToFerryRatio * FerryTrips, name="min_rail_to_ferry_ratio")

# Non-negativity constraints for FerryTrips and RailTrips
model.addConstr(FerryTrips >= 0, name="non_negativity_FerryTrips")
model.addConstr(RailTrips >= 0, name="non_negativity_RailTrips")

# Set objective
model.setObjective(FerryTrips + RailTrips, gp.GRB.MINIMIZE)

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
