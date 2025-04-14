import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_126/data.json", "r") as f:
    data = json.load(f)

EyeMachine1 = data["EyeMachine1"] # scalar parameter
FootMachine1 = data["FootMachine1"] # scalar parameter
EyeMachine2 = data["EyeMachine2"] # scalar parameter
FootMachine2 = data["FootMachine2"] # scalar parameter
WaterMachine1 = data["WaterMachine1"] # scalar parameter
WaterMachine2 = data["WaterMachine2"] # scalar parameter
TotalWater = data["TotalWater"] # scalar parameter
MinEyeCream = data["MinEyeCream"] # scalar parameter
MinFootCream = data["MinFootCream"] # scalar parameter
TimeMachine1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeMachine1")
TimeMachine2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeMachine2")

# Eye cream production constraint
model.addConstr(EyeMachine1 * TimeMachine1 + EyeMachine2 * TimeMachine2 >= MinEyeCream, name="min_eye_cream_requirement")

# Add constraint for minimum total amount of foot cream production
model.addConstr(FootMachine1 * TimeMachine1 + FootMachine2 * TimeMachine2 >= MinFootCream, "min_foot_cream_production")

# Add non-negativity constraint for time spent on Machine 1
model.addConstr(TimeMachine1 >= 0, name="non_negativity_TimeMachine1")

# Add non-negativity constraint for time spent on Machine 2
model.addConstr(TimeMachine2 >= 0, name="non_negativity_TimeMachine2")

# Constraint for the minimum requirement of eye cream production
model.addConstr(EyeMachine1 * TimeMachine1 + EyeMachine2 * TimeMachine2 >= MinEyeCream, name="min_eye_cream_requirement")

# Constraint for the minimum requirement of foot cream production
model.addConstr(FootMachine1 * TimeMachine1 + FootMachine2 * TimeMachine2 >= MinFootCream, name="min_foot_cream_requirement")

# Add distilled water usage constraint
model.addConstr(WaterMachine1 * TimeMachine1 + WaterMachine2 * TimeMachine2 <= TotalWater, name="total_water_usage")

# Set objective
model.setObjective(TimeMachine1 + TimeMachine2, gp.GRB.MINIMIZE)

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
