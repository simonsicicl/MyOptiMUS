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
AmountFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AmountFirstMix")
AmountSecondMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AmountSecondMix")
CatPawFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CatPawFirstMix")
GoldSharkFirstMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoldSharkFirstMix")
CatPawSecondMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CatPawSecondMix")
GoldSharkSecondMix = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GoldSharkSecondMix")

# Add non-negativity constraint for cat paw snacks in the first mix
model.addConstr(AmountFirstMix * PctCatPawFirst >= 0, name="non_negative_cat_paw_first_mix")

# No need to add a constraint since the product of a non-negative variable (AmountFirstMix) and a positive scalar (PctGoldSharkFirst = 0.8) already ensures non-negativity.

# Constraint to ensure AmountSecondMix is non-negative
model.addConstr(AmountSecondMix >= 0, name="non_negative_second_mix")

# Constraint to ensure the amount of gold shark snacks in the second snack mix is non-negative
model.addConstr(AmountSecondMix * PctGoldSharkSecond >= 0, name="non_negative_gold_shark_snacks")

# Add constraint for total cat paw snacks availability
model.addConstr(
    AmountFirstMix * PctCatPawFirst + AmountSecondMix * PctCatPawSecond <= TotalCatPaw,
    name="cat_paw_snacks_limit"
)

# Add constraint for total gold shark snacks used in both mixes
model.addConstr(
    PctGoldSharkFirst * AmountFirstMix + PctGoldSharkSecond * AmountSecondMix <= TotalGoldShark,
    name="gold_shark_snacks_limit"
)

# Add constraints for the first mix composition and total weight
model.addConstr(CatPawFirstMix == PctCatPawFirst * AmountFirstMix, name="cat_paw_first_mix_percentage")
model.addConstr(GoldSharkFirstMix == PctGoldSharkFirst * AmountFirstMix, name="gold_shark_first_mix_percentage")
model.addConstr(AmountFirstMix == CatPawFirstMix + GoldSharkFirstMix, name="amount_first_mix_total")

# Add constraints for the composition of the second mix
model.addConstr(CatPawSecondMix == PctCatPawSecond * AmountSecondMix, name="cat_paw_second_mix")
model.addConstr(GoldSharkSecondMix == PctGoldSharkSecond * AmountSecondMix, name="gold_shark_second_mix")

# Add constraint to ensure total usage does not exceed available stock
model.addConstr(CatPawFirstMix + CatPawSecondMix <= TotalCatPaw, name="total_cat_paw_snacks_constraint")

# Add constraint to ensure total gold shark snack usage does not exceed available stock
model.addConstr(
    GoldSharkFirstMix + GoldSharkSecondMix <= TotalGoldShark,
    name="gold_shark_snack_limit"
)

# Add constraint to ensure total weight of the second mix is consistent with its components
model.addConstr(AmountSecondMix == CatPawSecondMix + GoldSharkSecondMix, name="second_mix_weight_consistency")

# Add constraint to ensure the cat paw proportion in the first mix matches PctCatPawFirst
model.addConstr(CatPawFirstMix == PctCatPawFirst * AmountFirstMix, name="cat_paw_proportion_first_mix")

# Add constraint to ensure the gold shark proportion in the first mix matches PctGoldSharkFirst
model.addConstr(GoldSharkFirstMix == PctGoldSharkFirst * AmountFirstMix, name="gold_shark_proportion_first_mix")

# Add constraint to ensure the cat paw proportion in the second mix matches PctCatPawSecond
model.addConstr(CatPawSecondMix == PctCatPawSecond * AmountSecondMix, name="cat_paw_proportion_second_mix")

# Add constraint to ensure the gold shark proportion in the second mix matches PctGoldSharkSecond
model.addConstr(GoldSharkSecondMix == PctGoldSharkSecond * AmountSecondMix, name="gold_shark_proportion_second_mix")

# Add constraint to ensure the total kilograms of cat paw snacks used do not exceed availability
model.addConstr(CatPawFirstMix + CatPawSecondMix <= TotalCatPaw, name="cat_paw_snacks_availability")

# Add constraint to ensure the total kilograms of gold shark snacks used do not exceed availability
model.addConstr(GoldSharkFirstMix + GoldSharkSecondMix <= TotalGoldShark, name="gold_shark_snacks_availability")

# Set objective
model.setObjective(ProfitFirstMix * AmountFirstMix + ProfitSecondMix * AmountSecondMix, gp.GRB.MAXIMIZE)

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
