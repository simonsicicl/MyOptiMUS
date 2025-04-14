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
TimeMachine1Eye = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeMachine1Eye")
TimeMachine1Foot = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeMachine1Foot")
TimeMachine2Eye = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeMachine2Eye")
TimeMachine2Foot = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TimeMachine2Foot")

# Add constraint ensuring total eye cream production meets the minimum required amount
model.addConstr(
    TimeMachine1Eye * EyeMachine1 + TimeMachine2Eye * EyeMachine2 >= MinEyeCream,
    name="MinEyeCreamProduction"
)

# Add constraint for total production of foot cream being at least the minimum required amount
model.addConstr(FootMachine1 * TimeMachine1Foot + FootMachine2 * TimeMachine2Foot >= MinFootCream, name="min_foot_cream_requirement")

# Add non-negativity constraints for TimeMachine1Eye and TimeMachine1Foot
model.addConstr(TimeMachine1Eye >= 0, name="nonnegative_TimeMachine1Eye")
model.addConstr(TimeMachine1Foot >= 0, name="nonnegative_TimeMachine1Foot")

# Add non-negativity constraints for time spent on Machine 2
model.addConstr(TimeMachine2Eye >= 0, name="nonneg_TimeMachine2Eye")
model.addConstr(TimeMachine2Foot >= 0, name="nonneg_TimeMachine2Foot")

# Add constraint to ensure minimum production requirement for eye cream
model.addConstr(TimeMachine1Eye * EyeMachine1 + TimeMachine2Eye * EyeMachine2 >= MinEyeCream, name="min_eye_cream_production")

# Add constraint to ensure total production of foot cream meets the minimum requirement
model.addConstr(TimeMachine1Foot * FootMachine1 + TimeMachine2Foot * FootMachine2 >= MinFootCream, name="min_foot_cream_production")

# Add constraint to ensure total distilled water usage doesn't exceed available amount
model.addConstr(
    (TimeMachine1Eye + TimeMachine1Foot) * WaterMachine1 + 
    (TimeMachine2Eye + TimeMachine2Foot) * WaterMachine2 <= TotalWater, 
    name="water_usage_limit"
)

# Set objective
model.setObjective(TimeMachine1Eye + TimeMachine1Foot + TimeMachine2Eye + TimeMachine2Foot, gp.GRB.MINIMIZE)

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
