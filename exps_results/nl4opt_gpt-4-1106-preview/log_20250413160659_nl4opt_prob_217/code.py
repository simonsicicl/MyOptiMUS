import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_217/data.json", "r") as f:
    data = json.load(f)

PctCatPawFirst = data["PctCatPawFirst"] # scalar parameter
PctGoldSharkFirst = data["PctGoldSharkFirst"] # scalar parameter
PctCatPawSecond = data["PctCatPawSecond"] # scalar parameter
PctGoldSharkSecond = data["PctGoldSharkSecond"] # scalar parameter
TotalCatPaw = data["TotalCatPaw"] # scalar parameter
TotalGoldShark = data["TotalGoldShark"] # scalar parameter
ProfitFirstMix = data["ProfitFirstMix"] # scalar parameter
ProfitSecondMix = data["ProfitSecondMix"] # scalar parameter
CatPawFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CatPawFirstMix")
GoldSharkFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoldSharkFirstMix")
CatPawSecondMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CatPawSecondMix")
TotalFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalFirstMix")
TotalSecondMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalSecondMix")
GoldSharkSecondMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoldSharkSecondMix")

model.addConstr(CatPawFirstMix >= 0, name="nonnegativity_catpaw")

# Add constraint for non-negativity of the amount of gold shark snacks in the first mix
model.addConstr(GoldSharkFirstMix >= 0, "GoldSharkFirstMix_non_negative")

# Constraint: Amount of cat paw snacks in the second mix must be non-negative
model.addConstr(CatPawSecondMix >= 0, name="cat_paw_second_mix_non_negative")

model.addConstr(GoldSharkSecondMix >= 0, name="GoldSharkSecondMix_nonneg")

# Constraint: Total amount of cat paw snacks used in both mixes must not exceed the total available kg of cat paw snacks
model.addConstr(CatPawFirstMix + CatPawSecondMix <= TotalCatPaw, "cat_paw_snack_limit")

model.addConstr(GoldSharkFirstMix + GoldSharkSecondMix <= TotalGoldShark, "gold_shark_mix_constraint")

# The percentages of cat paw and gold shark snacks in the first snack mix must match the specified values
total_mix = CatPawFirstMix + GoldSharkFirstMix
model.addConstr(CatPawFirstMix == PctCatPawFirst * total_mix, name="pct_cat_paw_first_mix")
model.addConstr(GoldSharkFirstMix == PctGoldSharkFirst * total_mix, name="pct_gold_shark_first_mix")

# Define specific percentage constraints for the second snack mix
model.addConstr(CatPawSecondMix == PctCatPawSecond * TotalSecondMix, name="cat_paw_percentage_constraint")
model.addConstr(GoldSharkSecondMix == PctGoldSharkSecond * TotalSecondMix, name="gold_shark_percentage_constraint")

# Relate GoldSharkFirstMix to CatPawFirstMix with respect to their percentage compositions
model.addConstr(GoldSharkFirstMix == (CatPawFirstMix / PctCatPawFirst) * PctGoldSharkFirst, name="mix_relation")

# Relation between the first mix and its percentage composition of gold shark snacks
GoldSharkFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoldSharkFirstMix")
CatPawFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CatPawFirstMix")
PctGoldSharkFirst = data["PctGoldSharkFirst"] # scalar parameter

model.addConstr(GoldSharkFirstMix == PctGoldSharkFirst * (GoldSharkFirstMix + CatPawFirstMix), name="gold_shark_composition")

# Relation between the second mix and its percentage composition of gold shark snacks constraint
model.addConstr(GoldSharkSecondMix == PctGoldSharkSecond * (GoldSharkSecondMix + CatPawSecondMix / PctCatPawSecond), name="GoldSharkSecondMix_Composition")

# Constraint for the sum of cat paw and gold shark snacks in the first mix to equal the total amount for the first mix
model.addConstr(CatPawFirstMix + GoldSharkFirstMix == TotalFirstMix, name="percentage_constraint_first_mix")

# Percentage constraints for the first mix converted to linear form
model.addConstr(CatPawFirstMix == PctCatPawFirst * TotalFirstMix, name="CatPawFirstMix_constraint")
model.addConstr(GoldSharkFirstMix == PctGoldSharkFirst * TotalFirstMix, name="GoldSharkFirstMix_constraint")

# Constraint for the total amount in the second mix to equal the sum of cat paw and gold shark snacks in the second mix
model.addConstr(TotalSecondMix == CatPawSecondMix + GoldSharkSecondMix, name="mix_equality_constraint")

model.addConstr(CatPawFirstMix + CatPawSecondMix <= TotalCatPaw, "total_cat_paw_snacks_constraint")

model.addConstr(GoldSharkFirstMix + GoldSharkSecondMix <= TotalGoldShark, "gold_shark_mix_constraint")

# Constraint for the amount of cat paw snacks in the first mix to be 20% of its total amount
model.addConstr(CatPawFirstMix == PctCatPawFirst * TotalFirstMix, name="cat_paw_first_mix_constraint")

# Constraint for the amount of gold shark snacks in the first mix
GoldSharkFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoldSharkFirstMix")
TotalFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalFirstMix")
PctGoldSharkFirst = 0.8

model.addConstr(GoldSharkFirstMix == PctGoldSharkFirst * TotalFirstMix, "gold_shark_ratio_constraint")

# Constraint for the amount of cat paw snacks in the second mix to be 35% of its total amount
model.addConstr(CatPawSecondMix == PctCatPawSecond * TotalSecondMix, "pct_catpaw_second_mix")

# Constraint for the amount of gold shark snacks in the second mix to be 65% of its total amount
model.addConstr(GoldSharkSecondMix == PctGoldSharkSecond * TotalSecondMix, name="gold_shark_second_mix_constraint")

# Define objective function
model.setObjective(ProfitFirstMix * TotalFirstMix + ProfitSecondMix * TotalSecondMix, gp.GRB.MAXIMIZE)

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
