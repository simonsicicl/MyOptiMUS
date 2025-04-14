import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_219/data.json", "r") as f:
    data = json.load(f)

MinMath = data["MinMath"] # scalar parameter
MinEnglish = data["MinEnglish"] # scalar parameter
MaxMath = data["MaxMath"] # scalar parameter
MaxEnglish = data["MaxEnglish"] # scalar parameter
MinTotalWorkbooks = data["MinTotalWorkbooks"] # scalar parameter
ProfitMath = data["ProfitMath"] # scalar parameter
ProfitEnglish = data["ProfitEnglish"] # scalar parameter
MathWorkbooks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MathWorkbooks")
EnglishWorkbooks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="EnglishWorkbooks")

# Add constraint to ensure the number of math workbooks produced is at least MinMath
model.addConstr(MathWorkbooks >= MinMath, name="min_math_workbooks")

# Add constraint ensuring the number of math workbooks produced does not exceed MaxMath
model.addConstr(MathWorkbooks <= MaxMath, name="math_workbooks_constraint")

# Add constraint to ensure the production of English workbooks meets the minimum required
model.addConstr(EnglishWorkbooks >= MinEnglish, name="min_english_workbooks")

# Add constraint to limit English workbooks production to maximum allowed
model.addConstr(EnglishWorkbooks <= MaxEnglish, name="max_english_workbooks")

# Add constraint to ensure the total number of workbooks produced meets the minimum requirement
model.addConstr(MathWorkbooks + EnglishWorkbooks >= MinTotalWorkbooks, name="min_workbook_requirement")

# Add constraints to ensure MathWorkbooks production is within MinMath and MaxMath bounds
model.addConstr(MathWorkbooks >= MinMath, name="min_math_workbooks")
model.addConstr(MathWorkbooks <= MaxMath, name="max_math_workbooks")

# Add constraints to ensure English workbook production is within the minimum and maximum bounds
model.addConstr(MinEnglish <= EnglishWorkbooks, name="min_english_workbooks")
model.addConstr(EnglishWorkbooks <= MaxEnglish, name="max_english_workbooks")

# Add constraint to ensure total production meets the minimum contract requirement
model.addConstr(MathWorkbooks + EnglishWorkbooks >= MinTotalWorkbooks, name="min_total_workbooks_constraint")

# Set objective
model.setObjective(ProfitMath * MathWorkbooks + ProfitEnglish * EnglishWorkbooks, gp.GRB.MAXIMIZE)

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
