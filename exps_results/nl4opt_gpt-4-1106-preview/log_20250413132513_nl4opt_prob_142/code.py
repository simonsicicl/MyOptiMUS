import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_142/data.json", "r") as f:
    data = json.load(f)

Red1 = data["Red1"] # scalar parameter
Blue1 = data["Blue1"] # scalar parameter
Green1 = data["Green1"] # scalar parameter
Smelly1 = data["Smelly1"] # scalar parameter
Red2 = data["Red2"] # scalar parameter
Blue2 = data["Blue2"] # scalar parameter
Green2 = data["Green2"] # scalar parameter
Smelly2 = data["Smelly2"] # scalar parameter
TotalRed = data["TotalRed"] # scalar parameter
TotalBlue = data["TotalBlue"] # scalar parameter
MaxSmelly = data["MaxSmelly"] # scalar parameter
NumberOfExperiment1 = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfExperiment1")
NumberOfExperiment2 = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfExperiment2")

# Since NumberOfExperiment1 is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfExperiment1 >= 0, name="non_negativity_NumberOfExperiment1")

# Add constraint for non-negativity of the number of times experiment 2 is conducted
model.addConstr(NumberOfExperiment2 >= 0, name="exp2_non_negative")

# Add constraint for total units of red liquid used in experiments
model.addConstr(Red1 * NumberOfExperiment1 + Red2 * NumberOfExperiment2 <= TotalRed, name="red_liquid_usage")

# Add constraint for total units of blue liquid used in experiments
model.addConstr(Blue1 * NumberOfExperiment1 + Blue2 * NumberOfExperiment2 <= TotalBlue, name="blue_liquid_usage")

# Constraint for the total units of smelly gas from all experiments
model.addConstr(Smelly1 * NumberOfExperiment1 + Smelly2 * NumberOfExperiment2 <= MaxSmelly, name="max_smelly_gas")

# Set objective
model.setObjective(Green1 * NumberOfExperiment1 + Green2 * NumberOfExperiment2, gp.GRB.MAXIMIZE)

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
