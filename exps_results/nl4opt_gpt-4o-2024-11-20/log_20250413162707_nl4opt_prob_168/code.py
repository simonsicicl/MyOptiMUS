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
ScootersCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ScootersCount")
RickshawsCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RickshawsCount")

# ScootersCount is already coded as a model variable. No additional code is required for non-negativity since Gurobi variables are non-negative by default unless explicitly set to allow negative values (lb < 0).

# Since the variable RickshawsCount is defined with non-negativity by default in Gurobi (continuous variables have their lower bound set to 0), no additional constraint needs to be added.

# Add constraint to ensure at most MaxRickshawProportion of vehicles are rickshaws
model.addConstr((1 - MaxRickshawProportion) * RickshawsCount <= MaxRickshawProportion * ScootersCount, name="max_rickshaw_proportion")

# Add constraint to ensure the total number of visitors transported by scooters and rickshaws meets or exceeds the minimum required
model.addConstr(ScooterCapacity * ScootersCount + RickshawCapacity * RickshawsCount >= MinVisitors, name="MinVisitorsConstraint")

# Add constraint ensuring combined carrying capacity meets minimum visitors
model.addConstr(ScooterCapacity * ScootersCount + RickshawCapacity * RickshawsCount >= MinVisitors, name="combined_capacity")

# Add constraint to limit the number of rickshaws based on the maximum proportion of total vehicles
model.addConstr(
    RickshawsCount <= (MaxRickshawProportion / (1 - MaxRickshawProportion)) * ScootersCount, 
    name="max_rickshaw_proportion"
)

# Set objective
model.setObjective(ScootersCount, gp.GRB.MINIMIZE)

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
