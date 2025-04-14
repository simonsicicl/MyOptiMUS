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
NumberOfInVivoExperiments = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfInVivoExperiments")
NumberOfExVivoExperiments = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfExVivoExperiments")

# Since NumberOfInVivoExperiments is already defined as an integer variable, 
# we only need to add the non-negativity constraint
model.addConstr(NumberOfInVivoExperiments >= 0, "num_in_vivo_non_negative")

# Since NumberOfExVivoExperiments is already ensured to be an integer variable, 
# we only need to add a constraint to ensure it is non-negative.
model.addConstr(NumberOfExVivoExperiments >= 0, "non_negative_ex_vivo_experiments")

# Add constraint for the total preparation time for all experiments
model.addConstr(NumberOfInVivoExperiments * TimeInVivoPrep +
                NumberOfExVivoExperiments * TimeExVivoPrep <= MaxTimePrep,
                name="max_preparation_time")

# Add constraint for maximum allowed execution time
model.addConstr(TimeInVivoExec * NumberOfInVivoExperiments + TimeExVivoExec * NumberOfExVivoExperiments <= MaxTimeExec, name="max_execution_time")

# Objective function
model.setObjective(RadiationInVivo * NumberOfInVivoExperiments + RadiationExVivo * NumberOfExVivoExperiments, gp.GRB.MINIMIZE)

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
