import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_273/data.json", "r") as f:
    data = json.load(f)

UnitsCamel = data["UnitsCamel"] # scalar parameter
TimeCamel = data["TimeCamel"] # scalar parameter
UnitsTruck = data["UnitsTruck"] # scalar parameter
TimeTruck = data["TimeTruck"] # scalar parameter
GoodsTotal = data["GoodsTotal"] # scalar parameter
NumberOfCamelCaravans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCamelCaravans")
NumberOfDesertTrucks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfDesertTrucks")

# The constraint is already defined inherently by the non-negative domain of the variable
# Since no additional code is needed, the variable's range is satisfied by its definition.

# The non-negativity of the "NumberOfDesertTrucks" variable is already ensured by defining it as a continuous variable with no lower bound constraint. No additional code is required.

# Ensure that the total units delivered by camel caravans and desert trucks meet or exceed GoodsTotal
model.addConstr(NumberOfCamelCaravans * UnitsCamel + NumberOfDesertTrucks * UnitsTruck >= GoodsTotal, name="delivery_requirement")

# Add constraint ensuring total goods transported meet or exceed GoodsTotal
model.addConstr(
    NumberOfCamelCaravans * UnitsCamel + NumberOfDesertTrucks * UnitsTruck >= GoodsTotal,
    name="total_goods_constraint"
)

# Variables are already defined and constraints are inherently ensured by their non-negativity (due to gp.GRB.CONTINUOUS type).

# Set objective
model.setObjective(NumberOfCamelCaravans * TimeCamel + NumberOfDesertTrucks * TimeTruck, gp.GRB.MINIMIZE)

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
