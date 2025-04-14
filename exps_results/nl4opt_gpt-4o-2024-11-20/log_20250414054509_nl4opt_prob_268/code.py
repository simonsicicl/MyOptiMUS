import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_268/data.json", "r") as f:
    data = json.load(f)

TimeInVivoPrep = data["TimeInVivoPrep"] # scalar parameter
TimeInVivoExec = data["TimeInVivoExec"] # scalar parameter
TimeExVivoPrep = data["TimeExVivoPrep"] # scalar parameter
TimeExVivoExec = data["TimeExVivoExec"] # scalar parameter
RadiationInVivo = data["RadiationInVivo"] # scalar parameter
RadiationExVivo = data["RadiationExVivo"] # scalar parameter
MaxTimePrep = data["MaxTimePrep"] # scalar parameter
MaxTimeExec = data["MaxTimeExec"] # scalar parameter
NumInVivo = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumInVivo")
NumExVivo = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumExVivo")

# Add constraint for non-negativity of NumInVivo
model.addConstr(NumInVivo >= 0, name="non_negativity_NumInVivo")

# No additional code needed since the variable "NumExVivo" is defined with non-negativity by default through Gurobi's constraints for continuous variables (lower bound is 0).

# Add total preparation time constraint
model.addConstr(NumInVivo * TimeInVivoPrep + NumExVivo * TimeExVivoPrep <= MaxTimePrep, name="total_prep_time_constraint")

# Add execution time constraint
model.addConstr(
    NumInVivo * TimeInVivoExec + NumExVivo * TimeExVivoExec <= MaxTimeExec,
    name="execution_time_constraint"
)

# Add preparation time constraint
model.addConstr(NumInVivo * TimeInVivoPrep + NumExVivo * TimeExVivoPrep <= MaxTimePrep, name="preparation_time_constraint")

# Add constraint for total execution time
model.addConstr(
    TimeInVivoExec * NumInVivo + TimeExVivoExec * NumExVivo <= MaxTimeExec,
    name="total_execution_time_constraint"
)

# Set objective
model.setObjective(RadiationInVivo * NumInVivo + RadiationExVivo * NumExVivo, gp.GRB.MINIMIZE)

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
