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
BasketballsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="BasketballsProduced")
FootballsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="FootballsProduced")

# Define the constraint for total materials used for basketballs and footballs
model.addConstr(MaterialBasketball * BasketballsProduced + MaterialFootball * FootballsProduced <= TotalMaterial, name="material_usage")

# Add labor hours constraint for producing basketballs and footballs
model.addConstr(HourBasketball * BasketballsProduced + HourFootball * FootballsProduced <= TotalHours, name="labor_hours")

# Ensure there are at least BasketballFootballRatio times as many basketballs as footballs
model.addConstr(BasketballsProduced >= BasketballFootballRatio * FootballsProduced, name="MinRatioBasketballsToFootballs")

# Add constraint to ensure produced footballs are at least as many as MinFootballs
model.addConstr(FootballsProduced >= MinFootballs, name="min_footballs_produced_constraint")

# Add non-negativity constraint for basketballs produced
model.addConstr(BasketballsProduced >= 0, name="nonnegativity_basketballs")

# Add non-negativity constraint for footballs produced
model.addConstr(FootballsProduced >= 0, name="nonnegativity_footballs")

# Add constraint for the total units of materials used should be less than or equal to the total available units of materials
model.addConstr(MaterialBasketball * BasketballsProduced + MaterialFootball * FootballsProduced <= TotalMaterial, name="material_usage")

# Add labor hours constraint
model.addConstr(HourBasketball * BasketballsProduced + HourFootball * FootballsProduced <= TotalHours, name="labor_hours_constraint")

# Add the constraint for the minimum ratio of basketballs to footballs produced
model.addConstr(BasketballsProduced >= BasketballFootballRatio * FootballsProduced, name="min_basketball_football_ratio")

# Ensure the number of footballs produced is greater than or equal to the minimum required
model.addConstr(FootballsProduced >= MinFootballs, name="min_footballs_produced")

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
