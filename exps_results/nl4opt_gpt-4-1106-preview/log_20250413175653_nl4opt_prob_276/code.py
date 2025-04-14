import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_276/data.json", "r") as f:
    data = json.load(f)

FibreSpinach = data["FibreSpinach"] # scalar parameter
IronSpinach = data["IronSpinach"] # scalar parameter
CaloriesSpinach = data["CaloriesSpinach"] # scalar parameter
FibreSoybeans = data["FibreSoybeans"] # scalar parameter
IronSoybeans = data["IronSoybeans"] # scalar parameter
CaloriesSoybeans = data["CaloriesSoybeans"] # scalar parameter
TotalFibre = data["TotalFibre"] # scalar parameter
TotalIron = data["TotalIron"] # scalar parameter
CupsOfSpinach = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CupsOfSpinach")
CupsOfSoybeans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CupsOfSoybeans")

# Constraint: Number of cups of spinach must be non-negative
model.addConstr(CupsOfSpinach >= 0, "non_negativity_spinach")

model.addConstr(CupsOfSoybeans >= 0, name="non_negativity_soybeans")

model.addConstr(CupsOfSpinach >= CupsOfSoybeans + 1, name="spinach_vs_soybeans")

# Total fibre intake constraint
model.addConstr(FibreSpinach * CupsOfSpinach + FibreSoybeans * CupsOfSoybeans >= TotalFibre, "total_fibre_intake")

# Ensure the total intake of iron from spinach and soybeans meets the minimum required iron intake
model.addConstr(IronSpinach * CupsOfSpinach + IronSoybeans * CupsOfSoybeans >= TotalIron, name="iron_intake_requirement")

# Set objective
model.setObjective(CupsOfSpinach * CaloriesSpinach + CupsOfSoybeans * CaloriesSoybeans, gp.GRB.MAXIMIZE)

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
