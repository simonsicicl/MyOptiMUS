import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/54/data.json", "r") as f:
    data = json.load(f)

A = data["A"] # scalar parameter
Budget = data["Budget"] # scalar parameter
Costs = np.array(data["Costs"]) # ['A']
MaxClicks = np.array(data["MaxClicks"]) # ['A']
YoungClicks = np.array(data["YoungClicks"]) # ['A']
OldClicks = np.array(data["OldClicks"]) # ['A']
UniqueClicks = np.array(data["UniqueClicks"]) # ['A']
GoalYoung = data["GoalYoung"] # scalar parameter
GoalOld = data["GoalOld"] # scalar parameter
GoalUniqueYoung = data["GoalUniqueYoung"] # scalar parameter
GoalUniqueOld = data["GoalUniqueOld"] # scalar parameter
ClicksPurchased = model.addVars(A, vtype=gp.GRB.INTEGER, name="ClicksPurchased")
UniqueYoungClicks = model.addVars(A, vtype=gp.GRB.INTEGER, name="UniqueYoungClicks")

# Total cost constraint
total_cost_expr = gp.quicksum(Costs[a] * ClicksPurchased[a] for a in range(A))
model.addConstr(total_cost_expr <= Budget, name="TotalCostConstraint")

# Ensure each advertisement type does not exceed its maximum number of clicks
for a in range(A):
    model.addConstr(ClicksPurchased[a] <= MaxClicks[a], name=f"max_clicks_ad_type_{a}")

# Total young audience clicks goal constraint
young_clicks_expr = gp.quicksum(YoungClicks[a] * ClicksPurchased[a] for a in range(A))
model.addConstr(young_clicks_expr >= GoalYoung, name="young_audience_clicks_goal")

# Add constraint for achieving at least the goal for old audience clicks
old_clicks_constraint = gp.quicksum(OldClicks[a] * ClicksPurchased[a] for a in range(A)) >= GoalOld
model.addConstr(old_clicks_constraint, name="old_clicks_goal")

# Ensure the total number of unique young audience clicks meets the goal
model.addConstr(gp.quicksum(UniqueYoungClicks[a] for a in range(A)) >= GoalUniqueYoung, name="young_audience_goal")

# Add constraint for reaching at least the goal number of unique old audience clicks
old_clicks_sum = gp.quicksum(OldClicks[a] for a in range(A))
model.addConstr(old_clicks_sum >= GoalUniqueOld, name="unique_old_audience_clicks_goal")

# Add non-negativity constraints for the number of clicks from each advertisement type
for a in range(A):
    model.addConstr(0 <= ClicksPurchased[a], name='clicks_nonnegativity_{0}'.format(a))

# Unique young clicks for an ad type cannot exceed the total clicks purchased
for a in range(A):
    model.addConstr(UniqueYoungClicks[a] <= ClicksPurchased[a], name=f"unique_young_clicks_limit_{a}")

# Constraint to ensure unique young clicks for an ad type do not exceed young clicks from that ad type
for a in range(A):
    model.addConstr(UniqueYoungClicks[a] <= YoungClicks[a], name=f"unique_young_clicks_limit_{a}")

# Ensure the total cost does not exceed budget
total_cost = gp.quicksum(ClicksPurchased[a] * Costs[a] for a in range(A))
model.addConstr(total_cost <= Budget, name="budget_constraint")

# Ensure the number of clicks purchased does not exceed the maximum available clicks
for a in range(A):
    model.addConstr(ClicksPurchased[a] <= MaxClicks[a], name=f"max_clicks_{a}")

# Ensure that ClicksPurchased is at least UniqueYoungClicks for each advertisement type if the respective goal is specified
for a in range(A):
    model.addConstr(ClicksPurchased[a] >= UniqueYoungClicks[a], name="clicks_purchased_lb_ad_type_{}".format(a))

# Ensure the total number of unique young audience clicks meets the goal if specified
model.addConstr(gp.quicksum(UniqueYoungClicks[a] for a in range(A)) >= GoalUniqueYoung, name="YoungAudienceClicksGoal")

# Ensure the sum of unique clicks from all advertisement types is counted as the total number of clicks purchased.
for a in range(A):
    model.addConstr(ClicksPurchased[a] == UniqueClicks[a], name=f"clicks_count_{a}")

# Set objective
model.setObjective(gp.quicksum(ClicksPurchased[a] for a in range(A)), gp.GRB.MAXIMIZE)

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
