import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_267/data.json", "r") as f:
    data = json.load(f)

MaterialBasketball = data["MaterialBasketball"] # scalar parameter
HourBasketball = data["HourBasketball"] # scalar parameter
MaterialFootball = data["MaterialFootball"] # scalar parameter
HourFootball = data["HourFootball"] # scalar parameter
TotalMaterial = data["TotalMaterial"] # scalar parameter
TotalHours = data["TotalHours"] # scalar parameter
BasketballFootballRatio = data["BasketballFootballRatio"] # scalar parameter
MinFootballs = data["MinFootballs"] # scalar parameter
BasketballsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BasketballsProduced")
FootballsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FootballsProduced")

# Add material usage constraint
model.addConstr(
    MaterialBasketball * BasketballsProduced + MaterialFootball * FootballsProduced <= TotalMaterial,
    name="material_usage_constraint"
)

# Add total labor hour constraint
model.addConstr(
    BasketballsProduced * HourBasketball + FootballsProduced * HourFootball <= TotalHours,
    name="total_labor_hour_constraint"
)

# Add constraint ensuring basketballs produced are at least BasketballFootballRatio times footballs produced
model.addConstr(BasketballsProduced >= BasketballFootballRatio * FootballsProduced, name="basketball_football_ratio")

# Add constraint to ensure the number of footballs produced is at least MinFootballs
model.addConstr(FootballsProduced >= MinFootballs, name="min_footballs_produced")

# Adding constraint: The number of basketballs produced cannot be negative
model.addConstr(BasketballsProduced >= 0, name="non_negative_constraint")

# The variable "FootballsProduced" already has non-negativity implicitly enforced due to its default lower bound (0) in the Gurobi continuous variable declaration. No additional constraint is required.

# Add constraint to ensure total material usage does not exceed available material
model.addConstr(
    BasketballsProduced * MaterialBasketball + FootballsProduced * MaterialFootball <= TotalMaterial,
    name="material_usage_constraint"
)

# Add labor hour usage constraint
model.addConstr(
    BasketballsProduced * HourBasketball + FootballsProduced * HourFootball <= TotalHours, 
    name="labor_hours_constraint"
)

# Add minimum production constraint for footballs
model.addConstr(FootballsProduced >= MinFootballs, name="min_footballs_production")

# Add product mix ratio constraint
model.addConstr(BasketballsProduced >= BasketballFootballRatio * FootballsProduced, name="product_mix_ratio")

# Set objective
model.setObjective(BasketballsProduced + FootballsProduced, gp.GRB.MAXIMIZE)

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
