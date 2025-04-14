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
NumberOfSmallBuses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSmallBuses")
NumberOfLargeBuses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfLargeBuses")
TotalBuses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalBuses")

# The non-negativity constraint is inherently satisfied as the variable `NumberOfSmallBuses` is continuous, so no additional constraint is needed.

# No code is needed because non-negativity is inherent to continuous variables in Gurobi.

# Add total students transportation constraint
model.addConstr(NumberOfSmallBuses * SmallBusCapacity + NumberOfLargeBuses * LargeBusCapacity >= MinStudents, name="min_students_transportation")

# Add constraint to limit the proportion of large buses
model.addConstr((1 - MaxLargeBusProportion) * NumberOfLargeBuses <= MaxLargeBusProportion * NumberOfSmallBuses, 
                name="large_bus_proportion_limit")

# Add constraint to ensure the total number of students transported meets or exceeds the minimum required
model.addConstr(
    NumberOfSmallBuses * SmallBusCapacity + NumberOfLargeBuses * LargeBusCapacity >= MinStudents,
    name="min_students_transport"
)

# Add constraint to ensure the number of large buses does not exceed the allowed maximum proportion of total buses
model.addConstr(NumberOfLargeBuses <= MaxLargeBusProportion * TotalBuses, name="large_bus_limit")

# Add constraint enforcing the definition of TotalBuses
model.addConstr(TotalBuses == NumberOfSmallBuses + NumberOfLargeBuses, name="TotalBuses_definition")

# Set objective
model.setObjective(NumberOfSmallBuses + NumberOfLargeBuses, gp.GRB.MINIMIZE)

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
