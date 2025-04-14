import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_168/data.json", "r") as f:
    data = json.load(f)

ScooterCapacity = data["ScooterCapacity"] # scalar parameter
RickshawCapacity = data["RickshawCapacity"] # scalar parameter
MaxRickshawProportion = data["MaxRickshawProportion"] # scalar parameter
MinVisitors = data["MinVisitors"] # scalar parameter
NumScooters = model.addVar(vtype=gp.GRB.INTEGER, name="NumScooters")
NumRickshaws = model.addVar(vtype=gp.GRB.INTEGER, name="NumRickshaws")

# The number of scooters must be non-negative
model.addConstr(NumScooters >= 0, name="non_negativity_scooters")

# No code needed as the variable is already defined with the proper type (INTEGER) and the non-negative constraint is implicit.
# Gurobi integer variables are non-negative by default unless specified otherwise.

# At most MaxRickshawProportion of the vehicles used can be rickshaws
model.addConstr(NumRickshaws <= MaxRickshawProportion * (NumRickshaws + NumScooters), name="MaxRickshawProportionConstraint")

# Add constraint to ensure at least MinVisitors are transported
model.addConstr(NumScooters * ScooterCapacity + NumRickshaws * RickshawCapacity >= MinVisitors, "min_visitors_requirement")

# Rearranged maximum proportion constraint for rickshaws
model.addConstr((1 - MaxRickshawProportion) * NumRickshaws <= MaxRickshawProportion * NumScooters, "MaxRickshawProportionConstraint")

# Ensure the minimum number of visitors are transported
model.addConstr(NumScooters * ScooterCapacity + NumRickshaws * RickshawCapacity >= MinVisitors, name="min_visitors")

# Limit the proportion of rickshaws to reduce pollution
model.addConstr(NumRickshaws <= MaxRickshawProportion * (NumScooters + NumRickshaws), name="limit_rickshaw_proportion")

# Set objective
model.setObjective(NumScooters, gp.GRB.MINIMIZE)

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
