import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_96/data.json", "r") as f:
    data = json.load(f)

CocoaMilk = data["CocoaMilk"] # scalar parameter
MilkMilk = data["MilkMilk"] # scalar parameter
CocoaDark = data["CocoaDark"] # scalar parameter
MilkDark = data["MilkDark"] # scalar parameter
TotalCocoa = data["TotalCocoa"] # scalar parameter
TotalMilk = data["TotalMilk"] # scalar parameter
MilkDarkRatio = data["MilkDarkRatio"] # scalar parameter
TimeMilk = data["TimeMilk"] # scalar parameter
TimeDark = data["TimeDark"] # scalar parameter
NumberOfMilkChocolateBars = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMilkChocolateBars")
NumberOfDarkChocolateBars = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDarkChocolateBars")
TotalMilkUsedForMilkChocolateBars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMilkUsedForMilkChocolateBars")
TotalCocoaUsedForDarkChocolateBars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalCocoaUsedForDarkChocolateBars")
TotalMilkUsedForDarkChocolateBars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMilkUsedForDarkChocolateBars")

# Since the variable NumberOfMilkChocolateBars is already guaranteed to be non-negative by its definition as an integer variable in Gurobi, no additional constraint is needed.

# Since the variable NumberOfDarkChocolateBars has already been defined as an integer variable, 
# the non-negativity constraint is implicitly applied.
# Hence, no code is needed for this constraint.

# Constraint: Total used cocoa must not exceed the available cocoa units
model.addConstr(NumberOfMilkChocolateBars * CocoaMilk + NumberOfDarkChocolateBars * CocoaDark <= TotalCocoa, "cocoa_limit")

# Constraint: Total used milk is at most TotalMilk units
model.addConstr(MilkMilk * NumberOfMilkChocolateBars + MilkDark * NumberOfDarkChocolateBars <= TotalMilk, "Milk_Usage_Constraint")

# Add constraint for at least MilkDarkRatio times as many milk chocolate bars as dark chocolate bars
model.addConstr(NumberOfMilkChocolateBars >= MilkDarkRatio * NumberOfDarkChocolateBars, 
                name="milk_to_dark_ratio_constraint")

# Constrain the cocoa used for milk chocolate bars to be at most CocoaMilk times the number of milk chocolate bars
model.addConstr(CocoaMilk * NumberOfMilkChocolateBars >= TotalCocoa, name="cocoa_milk_usage")

# Add constraint for total units of milk used for milk chocolate bars
model.addConstr(TotalMilkUsedForMilkChocolateBars <= MilkMilk * NumberOfMilkChocolateBars, "milk_usage_constraint")

# Constraint: Total cocoa used for dark chocolate bars must not exceed CocoaDark times the number of dark chocolate bars
model.addConstr(TotalCocoaUsedForDarkChocolateBars <= CocoaDark * NumberOfDarkChocolateBars, name="cocoa_dark_chocolate_limit")

# Add constraint for the total units of milk used for dark chocolate bars
model.addConstr(TotalMilkUsedForDarkChocolateBars <= MilkDark * NumberOfDarkChocolateBars, "MilkForDarkChocolateConstraint")

# Define the objective function
model.setObjective(TimeMilk * NumberOfMilkChocolateBars + TimeDark * NumberOfDarkChocolateBars, gp.GRB.MINIMIZE)

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
