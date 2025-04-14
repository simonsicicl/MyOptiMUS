import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_8/data.json", "r") as f:
    data = json.load(f)

TotalInvestment = data["TotalInvestment"] # scalar parameter
InvestmentRatio = data["InvestmentRatio"] # scalar parameter
MaxTechInvestment = data["MaxTechInvestment"] # scalar parameter
ReturnRateClothing = data["ReturnRateClothing"] # scalar parameter
ReturnRateTech = data["ReturnRateTech"] # scalar parameter
InvestmentClothing = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestmentClothing")
InvestmentTech = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestmentTech")

# Add constraint ensuring clothing investment is at least InvestmentRatio times the tech investment
model.addConstr(InvestmentClothing >= InvestmentRatio * InvestmentTech, name="clothing_investment_ratio")

# The variable InvestmentTech is already coded as a non-negative continuous variable, which inherently satisfies the non-negativity constraint defined in Gurobi.

# The non-negativity of InvestmentClothing is enforced by Gurobi's default non-negative domain for continuous variables. No additional constraint code is needed.

# Add the constraint that Jacob's investment in tech company must not exceed the maximum limit
model.addConstr(InvestmentTech <= MaxTechInvestment, name="tech_investment_limit")

# Add constraint to ensure the total investment equals the available investment
model.addConstr(InvestmentClothing + InvestmentTech == TotalInvestment, 
                name="investment_balance")

# Add budget constraint
model.addConstr(InvestmentClothing + InvestmentTech <= TotalInvestment, name="budget_constraint")

# Add constraint ensuring investment in clothing is at least InvestmentRatio times the investment in tech
model.addConstr(InvestmentClothing >= InvestmentRatio * InvestmentTech, name="clothing_investment_minimum")

# Add constraint to ensure tech investment does not exceed the maximum allowable investment
model.addConstr(InvestmentTech <= MaxTechInvestment, name="tech_investment_limit")

# Add non-negativity constraints for investments
model.addConstr(InvestmentClothing >= 0, name="non_negativity_InvestmentClothing")
model.addConstr(InvestmentTech >= 0, name="non_negativity_InvestmentTech")

# Set objective
model.setObjective(
    InvestmentClothing * ReturnRateClothing + InvestmentTech * ReturnRateTech, 
    gp.GRB.MAXIMIZE
)

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
