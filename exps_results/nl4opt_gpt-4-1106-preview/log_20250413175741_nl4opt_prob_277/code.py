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
MechanicalKeyboards = model.addVar(vtype=gp.GRB.INTEGER, name="MechanicalKeyboards")
StandardKeyboards = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StandardKeyboards")

# Since MechanicalKeyboards is already defined as an integer variable, no code is needed to enforce non-negativity
# The Gurobi optimizer automatically enforces the non-negative domain for integer variables

# The number of standard keyboards produced must be non-negative
model.addConstr(StandardKeyboards >= 0, name="non_negative_standard_keyboards")

# Add minimum production constraint for standard keyboards
model.addConstr(StandardKeyboards >= MinStandard, name="min_standard_keyboards")

# Add constraint for total plastic use for mechanical and standard keyboards
model.addConstr(PlasticPerMechanical * MechanicalKeyboards + PlasticPerStandard * StandardKeyboards <= TotalPlastic, "TotalPlasticConstraint")

# Add constraint for solder usage
model.addConstr(SolderPerMechanical * MechanicalKeyboards + SolderPerStandard * StandardKeyboards <= TotalSolder, name="solder_usage")

# Add constraint to maintain the specified ratio of mechanical keyboards to standard keyboards
model.addConstr(MechanicalKeyboards == RatioMechanicalStandard * StandardKeyboards, name="ratio_mechanical_standard")

# Ensure the use of plastic does not exceed the total available
model.addConstr(PlasticPerMechanical * MechanicalKeyboards + PlasticPerStandard * StandardKeyboards <= TotalPlastic, name="plastic_limit")

# Ensure the use of solder does not exceed the total available
model.addConstr(SolderPerMechanical * MechanicalKeyboards + SolderPerStandard * StandardKeyboards <= TotalSolder, name="solder_usage_constraint")

# Ensure at least a minimum number of standard keyboards are produced
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
