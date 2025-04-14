import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_277/data.json", "r") as f:
    data = json.load(f)

RatioMechanicalStandard = data["RatioMechanicalStandard"] # scalar parameter
PlasticPerMechanical = data["PlasticPerMechanical"] # scalar parameter
SolderPerMechanical = data["SolderPerMechanical"] # scalar parameter
PlasticPerStandard = data["PlasticPerStandard"] # scalar parameter
SolderPerStandard = data["SolderPerStandard"] # scalar parameter
MinStandard = data["MinStandard"] # scalar parameter
TotalPlastic = data["TotalPlastic"] # scalar parameter
TotalSolder = data["TotalSolder"] # scalar parameter
MechanicalKeyboards = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MechanicalKeyboards")
StandardKeyboards = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StandardKeyboards")

# Non-negativity constraint for the number of mechanical keyboards
model.addConstr(MechanicalKeyboards >= 0, name="non_negative_mechanical_keyboards")

# No code is needed: Gurobi variables by default have non-negativity constraints unless otherwise specified.

# Add minimum production constraint for standard keyboards
model.addConstr(StandardKeyboards >= MinStandard, name="min_standard_keyboards")

# Add constraint to ensure total plastic usage does not exceed available total plastic
model.addConstr(
    (PlasticPerMechanical * MechanicalKeyboards) + 
    (PlasticPerStandard * StandardKeyboards) 
    <= TotalPlastic, 
    name="plastic_usage_constraint"
)

# Add solder usage constraint
model.addConstr(
    MechanicalKeyboards * SolderPerMechanical + StandardKeyboards * SolderPerStandard <= TotalSolder,
    name="solder_usage_constraint"
)

# Add constraint to enforce ratio between mechanical and standard keyboards
model.addConstr(MechanicalKeyboards == RatioMechanicalStandard * StandardKeyboards, name="mechanical_standard_ratio")

# Add constraint to limit plastic usage
model.addConstr(PlasticPerMechanical * MechanicalKeyboards + PlasticPerStandard * StandardKeyboards <= TotalPlastic, 
                name="plastic_usage_limit")

# Add solder usage constraint
model.addConstr(SolderPerMechanical * MechanicalKeyboards + SolderPerStandard * StandardKeyboards <= TotalSolder, name="solder_usage")

# Ensure the number of standard keyboards meets the minimum requirement
model.addConstr(StandardKeyboards >= MinStandard, name="min_standard_keyboards")

# Set objective
model.setObjective(MechanicalKeyboards + StandardKeyboards, gp.GRB.MAXIMIZE)

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
