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
RefrigeratorsSold = model.addVar(vtype=gp.GRB.INTEGER, name="RefrigeratorsSold")
StovesSold = model.addVar(vtype=gp.GRB.INTEGER, name="StovesSold")

# Add constraint for non-negative refrigerators sold
model.addConstr(RefrigeratorsSold >= 0, name="non_negative_refrigerators_sold")

# The variable StovesSold is already non-negative due to its definition as an integer variable in Gurobi
# No additional constraints are needed to ensure non-negativity

# Add constraint for total mover time for all refrigerators sold
model.addConstr(RefrigeratorsSold * MoverTimeRefrigerator <= TotalMoverTime, name="total_mover_time")

# Add total setup time constraint for refrigerators
model.addConstr(RefrigeratorsSold * SetupTimeRefrigerator <= TotalSetupTime, name="total_setup_time")

# Add constraint for the total time used by movers for both refrigerators and stoves not exceeding total available time
model.addConstr(RefrigeratorsSold * MoverTimeRefrigerator + StovesSold * MoverTimeStove <= TotalMoverTime, "TotalMoverTimeConstraint")

# Total setup time constraint for refrigerators and stoves
model.addConstr(SetupTimeRefrigerator * RefrigeratorsSold + SetupTimeStove * StovesSold <= TotalSetupTime, name="total_setup_time")

# Constraint: The total mover time for refrigerators and stoves should not exceed the total available mover time
model.addConstr(MoverTimeRefrigerator * RefrigeratorsSold + MoverTimeStove * StovesSold <= TotalMoverTime, name="total_mover_time")

# Add constraint for the total setup time for refrigerators and stoves
model.addConstr(SetupTimeRefrigerator * RefrigeratorsSold + SetupTimeStove * StovesSold <= TotalSetupTime, name="total_setup_time")

# Define the objective function
objective = ProfitRefrigerator * RefrigeratorsSold + ProfitStove * StovesSold

# Set the objective
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
