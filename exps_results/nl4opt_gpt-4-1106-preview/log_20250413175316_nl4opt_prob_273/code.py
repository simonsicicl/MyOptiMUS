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
CamelCaravans = model.addVar(vtype=gp.GRB.INTEGER, name="CamelCaravans")
DesertTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="DesertTrucks")

model.addConstr(CamelCaravans >= 0, name="non_negative_caravans")

# Add non-negativity constraint for the number of desert trucks
model.addConstr(DesertTrucks >= 0, name="nonnegativity_desert_trucks")

# Ensure total units delivered by camel caravans and desert trucks meet or exceed GoodsTotal
model.addConstr(CamelCaravans * UnitsCamel + DesertTrucks * UnitsTruck >= GoodsTotal, name="delivery_capacity")

# Ensure that the total units of goods delivered meet or exceed GoodsTotal
model.addConstr(CamelCaravans * UnitsCamel + DesertTrucks * UnitsTruck >= GoodsTotal, "goods_delivery_constraint")

# Objective: Minimize the total time spent
objective = CamelCaravans * TimeCamel + DesertTrucks * TimeTruck
model.setObjective(objective, gp.GRB.MINIMIZE)

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
