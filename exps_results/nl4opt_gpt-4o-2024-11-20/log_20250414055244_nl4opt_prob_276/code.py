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
NumberOfCupsSpinach = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCupsSpinach")
NumberOfCupsSoybeans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCupsSoybeans")

# Add non-negativity constraint for NumberOfCupsSpinach
model.addConstr(NumberOfCupsSpinach >= 0, name="non_negativity_spinach")

# The non-negativity constraint is inherently satisfied as the variable "NumberOfCupsSoybeans" is defined with type CONTINUOUS, which is non-negative by default.

# Add constraint: Number of cups of spinach must exceed the number of cups of soybeans by at least 1
model.addConstr(NumberOfCupsSpinach >= NumberOfCupsSoybeans + 1, name="SpinachExceedsSoybeans")

# Add fibre constraint
model.addConstr(
    FibreSpinach * NumberOfCupsSpinach + FibreSoybeans * NumberOfCupsSoybeans >= TotalFibre,
    name="fibre_constraint"
)

# Adding the constraint for total iron intake
model.addConstr(
    IronSpinach * NumberOfCupsSpinach + IronSoybeans * NumberOfCupsSoybeans >= TotalIron,
    name="total_iron_intake"
)

# Add constraint for total fibre consumption
model.addConstr(FibreSpinach * NumberOfCupsSpinach + FibreSoybeans * NumberOfCupsSoybeans >= TotalFibre, name="fibre_requirement")

# Add constraint for minimum required milligrams of iron
model.addConstr(
    NumberOfCupsSpinach * IronSpinach + NumberOfCupsSoybeans * IronSoybeans >= TotalIron,
    name="minimum_iron_requirement"
)

# Set objective
model.setObjective(CaloriesSpinach * NumberOfCupsSpinach + CaloriesSoybeans * NumberOfCupsSoybeans, gp.GRB.MAXIMIZE)

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
