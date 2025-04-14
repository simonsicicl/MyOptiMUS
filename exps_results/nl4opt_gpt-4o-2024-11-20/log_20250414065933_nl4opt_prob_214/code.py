import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_214/data.json", "r") as f:
    data = json.load(f)

B = data["B"] # scalar parameter
Pbasketball = data["Pbasketball"] # scalar parameter
Phorse = data["Phorse"] # scalar parameter
Psoccer = data["Psoccer"] # scalar parameter
Rbasketball = data["Rbasketball"] # scalar parameter
Rhorse = data["Rhorse"] # scalar parameter
Rsoccer = data["Rsoccer"] # scalar parameter
Pmax = data["Pmax"] # scalar parameter
MoneyBasketball = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MoneyBasketball")
MoneyHorse = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MoneyHorse")
MoneySoccer = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MoneySoccer")
TotalMoneySpent = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMoneySpent")

# Add budget constraint
model.addConstr(MoneyBasketball + MoneyHorse + MoneySoccer <= B, name="budget_constraint")

# Add non-negativity constraint for MoneyBasketball
model.addConstr(MoneyBasketball >= 0, name="non_negative_MoneyBasketball")

# Non-negativity constraint for MoneyHorse
model.addConstr(MoneyHorse >= 0, name="non_negativity_MoneyHorse")

# Add non-negativity constraint for MoneySoccer
model.addConstr(MoneySoccer >= 0, name="non_negativity_MoneySoccer")

# Add constraint for maximum average probability of losing money
model.addConstr(
    (Pbasketball * MoneyBasketball / B) + 
    (Phorse * MoneyHorse / B) + 
    (Psoccer * MoneySoccer / B) <= Pmax, 
    name="max_avg_losing_probability"
)

# Add budget constraint
model.addConstr(MoneyBasketball + MoneyHorse + MoneySoccer <= B, name="budget_constraint")

# Add weighted average probability of losing constraint
model.addConstr(
    Pbasketball * MoneyBasketball + Phorse * MoneyHorse + Psoccer * MoneySoccer <= TotalMoneySpent * Pmax,
    name="weighted_average_probability"
)

# Add constraint ensuring total money spent is the sum of money spent on basketball, horse racing, and soccer
model.addConstr(TotalMoneySpent == MoneyBasketball + MoneyHorse + MoneySoccer, name="total_money_spent")

# Set objective
model.setObjective((MoneyBasketball * Rbasketball + MoneyHorse * Rhorse + MoneySoccer * Rsoccer) / 3, gp.GRB.MAXIMIZE)

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
