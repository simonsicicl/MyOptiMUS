import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_158/data.json", "r") as f:
    data = json.load(f)

SmallBusCapacity = data["SmallBusCapacity"] # scalar parameter
LargeBusCapacity = data["LargeBusCapacity"] # scalar parameter
MinStudents = data["MinStudents"] # scalar parameter
MaxLargeBusProportion = data["MaxLargeBusProportion"] # scalar parameter
SmallBuses = model.addVar(vtype=gp.GRB.INTEGER, name="SmallBuses")
LargeBuses = model.addVar(vtype=gp.GRB.INTEGER, name="LargeBuses")

# Add non-negativity constraint for the SmallBuses variable
model.addConstr(SmallBuses >= 0, name="non_negativity_small_buses")

# Add non-negativity constraint for the number of large buses
model.addConstr(LargeBuses >= 0, name="non_negativity_large_buses")

# Add constraint to ensure the minimum number of students transported
model.addConstr(SmallBuses * SmallBusCapacity + LargeBuses * LargeBusCapacity >= MinStudents, 
                name="MinStudentsConstraint")

# Large buses constraint: The number of large buses cannot exceed a certain proportion of the total number of buses
model.addConstr(LargeBuses <= MaxLargeBusProportion * (SmallBuses + LargeBuses), name="large_buses_proportion")

# Ensure that the minimum number of students are transported
model.addConstr(SmallBuses * SmallBusCapacity + LargeBuses * LargeBusCapacity >= MinStudents, name="min_students_transported")

# Ensure that the number of large buses does not exceed the specified maximum proportion
model.addConstr(LargeBuses <= MaxLargeBusProportion * (SmallBuses + LargeBuses), name="max_large_buses_proportion")

# Set objective
model.setObjective(SmallBuses + LargeBuses, gp.GRB.MINIMIZE)

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
