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
NumTurkeyDinners = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumTurkeyDinners")
NumTunaSalad = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumTunaSalad")
TotalMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMeals")
TotalMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMeals")

# Add non-negativity constraint for NumTurkeyDinners
model.addConstr(NumTurkeyDinners >= 0, name="non_negativity_NumTurkeyDinners")

# Ensure the number of tuna salad sandwiches is non-negative
model.addConstr(NumTunaSalad >= 0, name="tuna_salad_non_negative")

# Add protein intake constraint
model.addConstr(
    ProteinTurkeyDinner * NumTurkeyDinners + ProteinTunaSalad * NumTunaSalad >= MinProtein,
    name="min_protein_constraint"
)

# Add constraint for minimum required carbs from Turkey Dinners and Tuna Salad Sandwiches
model.addConstr(
    NumTurkeyDinners * CarbsTurkeyDinner + NumTunaSalad * CarbsTunaSalad >= MinCarbs,
    name="min_carbs_requirement"
)

# Add constraint to ensure at most MaxTurkeyDinnerProportion of meals are turkey dinners
model.addConstr(NumTurkeyDinners <= MaxTurkeyDinnerProportion * TotalMeals, name="turkey_dinner_proportion")

# Add constraint to ensure TotalMeals is the sum of NumTurkeyDinners and NumTunaSalad
model.addConstr(TotalMeals == NumTurkeyDinners + NumTunaSalad, name="total_meals_constraint")

# Add protein intake constraint
model.addConstr(ProteinTurkeyDinner * NumTurkeyDinners + ProteinTunaSalad * NumTunaSalad >= MinProtein, name="protein_requirement")

# Add constraint to ensure minimum required carbs intake
model.addConstr(NumTurkeyDinners * CarbsTurkeyDinner + NumTunaSalad * CarbsTunaSalad >= MinCarbs, name="min_carbs_constraint")

# Add constraint to enforce the limit on turkey dinner proportions
model.addConstr(NumTurkeyDinners <= MaxTurkeyDinnerProportion * TotalMeals, name="turkey_dinner_limit")

# Add constraint to define TotalMeals as the sum of NumTurkeyDinners and NumTunaSalad
model.addConstr(TotalMeals == NumTurkeyDinners + NumTunaSalad, name="total_meals_definition")

# Set objective
model.setObjective(FatTurkeyDinner * NumTurkeyDinners + FatTunaSalad * NumTunaSalad, gp.GRB.MINIMIZE)

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
