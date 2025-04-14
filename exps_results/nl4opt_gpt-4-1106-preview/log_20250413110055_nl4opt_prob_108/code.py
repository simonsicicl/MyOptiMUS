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
PremiumBatches = model.addVar(vtype=gp.GRB.INTEGER, name="PremiumBatches")

# The number of regular batches produced must be non-negative
model.addConstr(RegularBatches >= 0, name="non_negative_regular_batches")

# Add constraint to ensure the number of premium batches produced is non-negative
model.addConstr(PremiumBatches >= 0, name="non_negativity_premium_batches")

# Medicinal Ingredients constraints for regular batches
model.addConstr(MedicinalIngredientsRegular * RegularBatches <= TotalMedicinalIngredients, "medicinal_ingredients_regular")



# Constraint: The number of regular batches must be less than the number of premium batches
model.addConstr(RegularBatches <= PremiumBatches - 1, name="regular_less_than_premium")

# Constraint for minimum required regular batches production
model.addConstr(RegularBatches >= MinRegularBatches, name="min_regular_batches")

# Ensure that the total amount of medicinal ingredients used does not exceed the available amount
model.addConstr(
    MedicinalIngredientsRegular * RegularBatches + MedicinalIngredientsPremium * PremiumBatches <= TotalMedicinalIngredients,
    name="medicinal_ingredients_constraint"
)

# Ensure that the total amount of rehydration product used does not exceed the available amount
model.addConstr(RehydrationProductRegular * RegularBatches + RehydrationProductPremium * PremiumBatches <= TotalRehydrationProduct, "rehydration_product_constraint")

# Ensure that at least the minimum number of regular batches are produced
model.addConstr(RegularBatches >= MinRegularBatches, name="min_regular_batches")

# Define objective function
objective = PeopleTreatedRegular * RegularBatches + PeopleTreatedPremium * PremiumBatches

# Set objective
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
