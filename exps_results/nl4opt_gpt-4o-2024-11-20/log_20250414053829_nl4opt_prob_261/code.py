import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_261/data.json", "r") as f:
    data = json.load(f)

MotorcycleCapacity = data["MotorcycleCapacity"] # scalar parameter
MotorcyclePollution = data["MotorcyclePollution"] # scalar parameter
MotorcycleEarnings = data["MotorcycleEarnings"] # scalar parameter
SedanCapacity = data["SedanCapacity"] # scalar parameter
SedanPollution = data["SedanPollution"] # scalar parameter
SedanEarnings = data["SedanEarnings"] # scalar parameter
MaxMotorcycleProportion = data["MaxMotorcycleProportion"] # scalar parameter
MaxPollution = data["MaxPollution"] # scalar parameter
MinPeopleTransported = data["MinPeopleTransported"] # scalar parameter
NumberOfMotorcycles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfMotorcycles")
NumberOfSedans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSedans")

# NumberOfMotorcycles is already defined as a continuous variable which ensures it is non-negative.

# No code is needed because the non-negativity constraint is automatically enforced due to the default non-negative domain of continuous variables in Gurobi.

# Add constraint to ensure at most MaxMotorcycleProportion of the total number of vehicles are motorcycles
model.addConstr((1 - MaxMotorcycleProportion) * NumberOfMotorcycles <= MaxMotorcycleProportion * NumberOfSedans, name="motorcycle_proportion")

# Add pollution constraint: The total pollution from motorcycles and sedans must not exceed MaxPollution.
model.addConstr(MotorcyclePollution * NumberOfMotorcycles + SedanPollution * NumberOfSedans <= MaxPollution, 
                name="pollution_limit")

# Add constraint to ensure transportation of at least MinPeopleTransported people
model.addConstr(
    MotorcycleCapacity * NumberOfMotorcycles + SedanCapacity * NumberOfSedans >= MinPeopleTransported,
    name="min_people_transport_constraint"
)

# Add pollution constraint
model.addConstr(MotorcyclePollution * NumberOfMotorcycles + SedanPollution * NumberOfSedans <= MaxPollution, name="pollution_limit")

# Add total capacity constraint
model.addConstr(
    MotorcycleCapacity * NumberOfMotorcycles + SedanCapacity * NumberOfSedans >= MinPeopleTransported,
    name="total_capacity_constraint"
)

# Add a constraint to ensure the number of motorcycles does not exceed the maximum allowed proportion of the fleet
model.addConstr(
    NumberOfMotorcycles <= (MaxMotorcycleProportion / (1 - MaxMotorcycleProportion)) * NumberOfSedans,
    name="motorcycle_proportion_constraint"
)

# Set objective
model.setObjective(MotorcycleEarnings * NumberOfMotorcycles + SedanEarnings * NumberOfSedans, gp.GRB.MAXIMIZE)

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
