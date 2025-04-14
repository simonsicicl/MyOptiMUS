import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_101/data.json", "r") as f:
    data = json.load(f)

ProteinAlpha = data["ProteinAlpha"] # scalar parameter
SugarAlpha = data["SugarAlpha"] # scalar parameter
CaloriesAlpha = data["CaloriesAlpha"] # scalar parameter
ProteinOmega = data["ProteinOmega"] # scalar parameter
SugarOmega = data["SugarOmega"] # scalar parameter
CaloriesOmega = data["CaloriesOmega"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MaxPropOmega = data["MaxPropOmega"] # scalar parameter
NumberAlphaDrinks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberAlphaDrinks")
NumberOmegaDrinks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOmegaDrinks")

# No additional code needed since the variable "NumberAlphaDrinks" is defined with non-negativity by default through Gurobi's constraints for continuous variables (min. bound is 0).

# NumberOmegaDrinks is already defined as a non-negative continuous variable, no additional constraint is needed as it is implicitly satisfied.

# Add constraint to ensure drinks provide at least MinProtein grams of protein
model.addConstr(
    ProteinAlpha * NumberAlphaDrinks + ProteinOmega * NumberOmegaDrinks >= MinProtein,
    name="protein_requirement"
)

# Add minimum calorie constraint
model.addConstr(
    CaloriesAlpha * NumberAlphaDrinks + CaloriesOmega * NumberOmegaDrinks >= MinCalories,
    name="min_calorie_requirement"
)

# Add constraint to ensure the number of omega brand drinks is limited to the permissible proportion relative to alpha brand drinks
model.addConstr(
    NumberOmegaDrinks <= (MaxPropOmega / (1 - MaxPropOmega)) * NumberAlphaDrinks,
    name="limit_omega_proportion"
)

# Add minimum protein intake constraint
model.addConstr(ProteinAlpha * NumberAlphaDrinks + ProteinOmega * NumberOmegaDrinks >= MinProtein, name="min_protein_intake")

# Add calorie intake constraint
model.addConstr(
    CaloriesAlpha * NumberAlphaDrinks + CaloriesOmega * NumberOmegaDrinks >= MinCalories,
    name="min_calorie_requirement"
)

# Add constraint to ensure Omega drinks do not exceed the maximum proportion of all drinks consumed
model.addConstr(NumberOmegaDrinks <= (MaxPropOmega / (1 - MaxPropOmega)) * NumberAlphaDrinks, name="omega_drinks_proportion")

# Set objective
model.setObjective(SugarAlpha * NumberAlphaDrinks + SugarOmega * NumberOmegaDrinks, gp.GRB.MINIMIZE)

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
