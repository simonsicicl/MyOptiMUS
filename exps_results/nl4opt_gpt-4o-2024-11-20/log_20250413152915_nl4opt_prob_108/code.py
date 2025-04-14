import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_108/data.json", "r") as f:
    data = json.load(f)

MedicinalIngredientsRegular = data["MedicinalIngredientsRegular"] # scalar parameter
RehydrationProductRegular = data["RehydrationProductRegular"] # scalar parameter
MedicinalIngredientsPremium = data["MedicinalIngredientsPremium"] # scalar parameter
RehydrationProductPremium = data["RehydrationProductPremium"] # scalar parameter
TotalMedicinalIngredients = data["TotalMedicinalIngredients"] # scalar parameter
TotalRehydrationProduct = data["TotalRehydrationProduct"] # scalar parameter
MinRegularBatches = data["MinRegularBatches"] # scalar parameter
PeopleTreatedRegular = data["PeopleTreatedRegular"] # scalar parameter
PeopleTreatedPremium = data["PeopleTreatedPremium"] # scalar parameter
RegularBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularBatches")
PremiumBatches = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PremiumBatches")

# The constraint RegularBatches >= 0 is automatically satisfied since the variable RegularBatches is defined with default domain constraints in gurobipy (non-negative for continuous variables)

# No additional code needed since PremiumBatches is already defined as a non-negative (continuous) variable. The constraint is implicitly satisfied.

# Adding constraint to ensure total medicinal ingredients used do not exceed available total
model.addConstr(RegularBatches * MedicinalIngredientsRegular <= TotalMedicinalIngredients, name="medicinal_ingredient_constraint")

# Add constraint to ensure total rehydration product used for regular batches does not exceed availability
model.addConstr(RegularBatches * RehydrationProductRegular <= TotalRehydrationProduct, name="rehydration_product_limit")

# Add constraint to ensure RegularBatches is less than PremiumBatches by at least 1
model.addConstr(RegularBatches <= PremiumBatches - 1, name="regular_vs_premium_batches")

# Add constraint to ensure RegularBatches is at least MinRegularBatches
model.addConstr(RegularBatches >= MinRegularBatches, name="min_regular_batches")

# Add constraint on the total use of medicinal ingredients
model.addConstr(
    RegularBatches * MedicinalIngredientsRegular + PremiumBatches * MedicinalIngredientsPremium <= TotalMedicinalIngredients,
    name="medicinal_ingredients_constraint"
)

# Add constraint on the total use of rehydration product
model.addConstr(
    RegularBatches * RehydrationProductRegular + PremiumBatches * RehydrationProductPremium <= TotalRehydrationProduct,
    name="rehydration_product_constraint"
)

# Add minimum production constraint for regular batches
model.addConstr(RegularBatches >= MinRegularBatches, name="min_production_regular_batches")

# No additional code needed for non-negativity, as Gurobi variables are non-negative by default unless explicitly set otherwise.

# Set objective
model.setObjective(PeopleTreatedRegular * RegularBatches + PeopleTreatedPremium * PremiumBatches, gp.GRB.MAXIMIZE)

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
