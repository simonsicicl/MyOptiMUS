import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_141/data.json", "r") as f:
    data = json.load(f)

ProteinTurkeyDinner = data["ProteinTurkeyDinner"] # scalar parameter
CarbsTurkeyDinner = data["CarbsTurkeyDinner"] # scalar parameter
FatTurkeyDinner = data["FatTurkeyDinner"] # scalar parameter
ProteinTunaSalad = data["ProteinTunaSalad"] # scalar parameter
CarbsTunaSalad = data["CarbsTunaSalad"] # scalar parameter
FatTunaSalad = data["FatTunaSalad"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
MinCarbs = data["MinCarbs"] # scalar parameter
MaxTurkeyDinnerProportion = data["MaxTurkeyDinnerProportion"] # scalar parameter
TurkeyDinners = model.addVar(vtype=gp.GRB.INTEGER, name="TurkeyDinners")
TunaSalads = model.addVar(vtype=gp.GRB.INTEGER, name="TunaSalads")

# Constraint: The number of turkey dinners must be non-negative
model.addConstr(TurkeyDinners >= 0, name="non_negative_turkey_dinners")

# Since the variable TunaSalads has already been defined as an integer variable, 
# the non-negativity constraint is implicitly applied.
# No further code needed to enforce TunaSalads >= 0.

# Add constraint to ensure the minimum total grams of protein
model.addConstr(ProteinTurkeyDinner * TurkeyDinners + ProteinTunaSalad * TunaSalads >= MinProtein, name="min_protein_requirement")

# Add constraint to ensure the total grams of carbs from meals is at least MinCarbs
model.addConstr(CarbsTurkeyDinner * TurkeyDinners + CarbsTunaSalad * TunaSalads >= MinCarbs, name="min_carbs")

# Ensure no more than MaxTurkeyDinnerProportion of the meals are turkey dinners
model.addConstr(TurkeyDinners <= MaxTurkeyDinnerProportion * (TurkeyDinners + TunaSalads), "MaxTurkeyDinnerProportionConstraint")

# Ensure minimum protein intake is met
model.addConstr(ProteinTurkeyDinner * TurkeyDinners + ProteinTunaSalad * TunaSalads >= MinProtein, name="min_protein_intake")

# Ensure minimum carbs intake is met
model.addConstr(CarbsTurkeyDinner * TurkeyDinners + CarbsTunaSalad * TunaSalads >= MinCarbs, name="min_carbs_intake")

# Limit the proportion of turkey dinners compared to the total number of meals constraint
model.addConstr(TurkeyDinners <= MaxTurkeyDinnerProportion * (TurkeyDinners + TunaSalads), name="max_turkey_dinner_proportion")

# Set objective
model.setObjective(FatTurkeyDinner * TurkeyDinners + FatTunaSalad * TunaSalads, gp.GRB.MINIMIZE)

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
