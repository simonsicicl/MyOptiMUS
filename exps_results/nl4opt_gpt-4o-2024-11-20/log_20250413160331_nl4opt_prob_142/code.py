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
Experiment1Count = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Experiment1Count")
Experiment2Count = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Experiment2Count")

# Ensure the number of experiment 1 is non-negative
model.addConstr(Experiment1Count >= 0, name="non_negative_experiment1")

# Add non-negativity constraint for Experiment2Count
model.addConstr(Experiment2Count >= 0, name="non_negativity_experiment2")

# Adding a constraint to ensure total red liquid usage does not exceed available red liquid
model.addConstr(
    Experiment1Count * Red1 + Experiment2Count * Red2 <= TotalRed,
    name="red_liquid_limit"
)

# Adding total blue liquid usage constraint
model.addConstr((Blue1 * Experiment1Count) + (Blue2 * Experiment2Count) <= TotalBlue, name="total_blue_liquid_usage")

# Add smelly gas limit constraint
model.addConstr(Smelly1 * Experiment1Count + Smelly2 * Experiment2Count <= MaxSmelly, name="smelly_gas_limit")

# Add constraint for total red liquid usage
model.addConstr(Red1 * Experiment1Count + Red2 * Experiment2Count <= TotalRed, name="red_liquid_limit")

# Add constraint for total blue liquid usage
model.addConstr(Blue1 * Experiment1Count + Blue2 * Experiment2Count <= TotalBlue, name="blue_liquid_limit")

# Add constraint to limit the total smelly gas production
model.addConstr(Smelly1 * Experiment1Count + Smelly2 * Experiment2Count <= MaxSmelly, name="smelly_gas_limit")

# Set objective
model.setObjective(Green1 * Experiment1Count + Green2 * Experiment2Count, gp.GRB.MAXIMIZE)

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
