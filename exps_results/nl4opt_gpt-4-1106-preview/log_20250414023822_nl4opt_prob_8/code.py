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
ClothingInvestment = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ClothingInvestment")
TechInvestment = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TechInvestment")

# Add constraint to ensure ClothingInvestment is at least a certain ratio of TechInvestment
model.addConstr(ClothingInvestment >= InvestmentRatio * TechInvestment, name="investment_ratio_constraint")

# Ensure TechInvestment is non-negative
TechInvestment_lb = model.addConstr(TechInvestment >= 0, name="TechInvestment_non_negative")

# Add constraint for non-negative clothing investment
model.addConstr(ClothingInvestment >= 0, name="non_negative_investment")

# Constraint: Jacob can invest at most MaxTechInvestment in the tech company
model.addConstr(TechInvestment <= MaxTechInvestment, name="max_tech_investment")

# Total investment constraint: investment in clothing and tech companies must equal total investment
model.addConstr(ClothingInvestment + TechInvestment == TotalInvestment, name="total_investment_constraint")

model.addConstr(ClothingInvestment + TechInvestment <= TotalInvestment, name="investment_limit")

# Add constraint for investment in clothing company to be at least four times that of the tech company
model.addConstr(ClothingInvestment >= 4 * TechInvestment, name="investment_ratio_constraint")

# Constraint: The investment in the tech company can't exceed the maximum allowed investment
model.addConstr(TechInvestment <= MaxTechInvestment, name="max_tech_investment_constraint")

# Set the objective function
model.setObjective(ClothingInvestment * ReturnRateClothing + TechInvestment * ReturnRateTech, gp.GRB.MAXIMIZE)

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
