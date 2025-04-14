import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_116/data.json", "r") as f:
    data = json.load(f)

AcneFactory1 = data["AcneFactory1"] # scalar parameter
AntibacterialFactory1 = data["AntibacterialFactory1"] # scalar parameter
AcneFactory2 = data["AcneFactory2"] # scalar parameter
AntibacterialFactory2 = data["AntibacterialFactory2"] # scalar parameter
BaseGelFactory1 = data["BaseGelFactory1"] # scalar parameter
BaseGelFactory2 = data["BaseGelFactory2"] # scalar parameter
TotalBaseGel = data["TotalBaseGel"] # scalar parameter
MinAcneCream = data["MinAcneCream"] # scalar parameter
MinAntibacterialCream = data["MinAntibacterialCream"] # scalar parameter
HoursFactory1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursFactory1")
HoursFactory2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursFactory2")

# Add constraint to ensure total base gel usage does not exceed available supply
model.addConstr(
    HoursFactory1 * BaseGelFactory1 + HoursFactory2 * BaseGelFactory2 <= TotalBaseGel,
    name="base_gel_supply"
)

# Add constraint ensuring total acne cream production meets the minimum required amount
model.addConstr(AcneFactory1 * HoursFactory1 + AcneFactory2 * HoursFactory2 >= MinAcneCream, name="min_acne_cream_production")

# Add constraint for minimum production of anti-bacterial cream
model.addConstr(AntibacterialFactory1 * HoursFactory1 + AntibacterialFactory2 * HoursFactory2 >= MinAntibacterialCream, name="min_antibacterial_production")

# No additional code needed since non-negativity is ensured by the default lower bound of 0 in gurobipy variables.

# Add non-negativity constraint for HoursFactory2
model.addConstr(HoursFactory2 >= 0, name="non_negativity_HoursFactory2")

# Adding minimum production requirement for acne cream
model.addConstr(
    HoursFactory1 * AcneFactory1 + HoursFactory2 * AcneFactory2 >= MinAcneCream,
    name="min_acne_cream_production"
)

# Add constraint for meeting the minimum requirement of anti-bacterial cream production
model.addConstr(
    HoursFactory1 * AntibacterialFactory1 + HoursFactory2 * AntibacterialFactory2 >= MinAntibacterialCream,
    name="min_antibacterial_production"
)

# Add base gel consumption constraint
model.addConstr(
    HoursFactory1 * BaseGelFactory1 + HoursFactory2 * BaseGelFactory2 <= TotalBaseGel,
    name="base_gel_consumption"
)

# Set objective
model.setObjective(HoursFactory1 + HoursFactory2, gp.GRB.MINIMIZE)

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
