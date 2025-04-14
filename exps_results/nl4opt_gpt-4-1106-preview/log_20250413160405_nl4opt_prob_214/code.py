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
MoneySpentBasketball = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MoneySpentBasketball")
MoneySpentHorse = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MoneySpentHorse")
MoneySpentSoccer = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MoneySpentSoccer")

# Constraint: Total money spent on all bets should not exceed the available budget B
model.addConstr(MoneySpentBasketball + MoneySpentHorse + MoneySpentSoccer <= B, "budget_constraint")

# Constraint for non-negative money spent on basketball betting
model.addConstr(MoneySpentBasketball >= 0, name="non_negative_MoneySpentBasketball")

# MoneySpentHorse should be non-negative
model.addConstr(MoneySpentHorse >= 0, name="constraint_non_negative_MoneySpentHorse")

# Constraint: Money spent on soccer should be non-negative
model.addConstr(MoneySpentSoccer >= 0, name="non_negative_betting")

# Add a constraint for the average chance of losing money on bets
model.addConstr((MoneySpentBasketball * Pbasketball + MoneySpentHorse * Phorse + MoneySpentSoccer * Psoccer) <= Pmax * (MoneySpentBasketball + MoneySpentHorse + MoneySpentSoccer), name="max_loss_probability")

# Ensure that the total money spent does not exceed the available budget
model.addConstr(MoneySpentBasketball + MoneySpentHorse + MoneySpentSoccer <= B, name="budget_constraint")

AverageLossProbability = model.addVar(vtype=gp.GRB.CONTINUOUS, name='AverageLossProbability')
model.addConstr(MoneySpentBasketball * Pbasketball +
                 MoneySpentHorse * Phorse +
                 MoneySpentSoccer * Psoccer <=
                 AverageLossProbability * (MoneySpentBasketball + MoneySpentHorse + MoneySpentSoccer),
                name='max_avg_probability_loss')
model.addConstr(AverageLossProbability <= Pmax, name='avg_probability_loss_max')


# Define the objective function for maximizing the average payout
average_payout = (MoneySpentBasketball * Rbasketball + MoneySpentHorse * Rhorse + MoneySpentSoccer * Rsoccer) / 3
model.setObjective(average_payout, gp.GRB.MAXIMIZE)

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
