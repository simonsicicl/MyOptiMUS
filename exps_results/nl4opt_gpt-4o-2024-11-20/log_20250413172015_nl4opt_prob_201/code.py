import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_201/data.json", "r") as f:
    data = json.load(f)

ProfitRefrigerator = data["ProfitRefrigerator"] # scalar parameter
ProfitStove = data["ProfitStove"] # scalar parameter
MoverTimeRefrigerator = data["MoverTimeRefrigerator"] # scalar parameter
MoverTimeStove = data["MoverTimeStove"] # scalar parameter
SetupTimeRefrigerator = data["SetupTimeRefrigerator"] # scalar parameter
SetupTimeStove = data["SetupTimeStove"] # scalar parameter
TotalMoverTime = data["TotalMoverTime"] # scalar parameter
TotalSetupTime = data["TotalSetupTime"] # scalar parameter
RefrigeratorsSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RefrigeratorsSold")
StovesSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StovesSold")

# Non-negativity constraint for the number of refrigerators sold
model.addConstr(RefrigeratorsSold >= 0, name="non_negative_refrigerators_sold")

# Adding constraint: The number of stoves sold is non-negative
model.addConstr(StovesSold >= 0, name="non_negative_stoves")

# Add total mover time constraint
model.addConstr(
    RefrigeratorsSold * MoverTimeRefrigerator + StovesSold * MoverTimeStove <= TotalMoverTime,
    name="total_mover_time_constraint"
)

# Add the total setup time constraint
model.addConstr(
    (RefrigeratorsSold * SetupTimeRefrigerator) + (StovesSold * SetupTimeStove) <= TotalSetupTime, 
    name="total_setup_time_constraint"
)

# Add constraint to limit total mover time
model.addConstr(
    RefrigeratorsSold * MoverTimeRefrigerator + StovesSold * MoverTimeStove <= TotalMoverTime,
    name="TotalMoverTimeConstraint"
)

# Add total setup time constraint
model.addConstr(RefrigeratorsSold * SetupTimeRefrigerator + StovesSold * SetupTimeStove <= TotalSetupTime, name="total_setup_time")

# Add mover time constraint
model.addConstr(
    MoverTimeRefrigerator * RefrigeratorsSold + MoverTimeStove * StovesSold <= TotalMoverTime,
    name="mover_time_constraint"
)

# Add setup time constraint ensuring total setup time does not exceed available time
model.addConstr(
    RefrigeratorsSold * SetupTimeRefrigerator + StovesSold * SetupTimeStove <= TotalSetupTime, 
    name="setup_time_constraint"
)

# Set objective
model.setObjective(ProfitRefrigerator * RefrigeratorsSold + ProfitStove * StovesSold, gp.GRB.MAXIMIZE)

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
