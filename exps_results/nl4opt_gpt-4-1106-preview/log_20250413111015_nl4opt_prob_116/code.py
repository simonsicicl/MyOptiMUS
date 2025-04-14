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

# Constraint: Total base gel used by both factories must not exceed the available base gel
model.addConstr(BaseGelFactory1 * HoursFactory1 + BaseGelFactory2 * HoursFactory2 <= TotalBaseGel, name="TotalBaseGelConstraint")

# Production constraint to meet minimum required units of acne cream
model.addConstr(AcneFactory1 * HoursFactory1 + AcneFactory2 * HoursFactory2 >= MinAcneCream, name="min_acne_cream_production")

# Total production of anti-bacterial cream must meet or exceed minimum required units
model.addConstr(HoursFactory1 * AntibacterialFactory1 + HoursFactory2 * AntibacterialFactory2 >= MinAntibacterialCream, "MinTotalAntibacterialCream")

# Constraint: Number of hours factory 1 operates must be non-negative
model.addConstr(HoursFactory1 >= 0, "Factory1_Hours_Nonnegative")

# Constraint: Number of hours factory 2 operates must be non-negative
model.addConstr(HoursFactory2 >= 0, "Factory2_Hours_Nonnegative")

# Ensure that the total production of acne cream meets the minimum requirement
model.addConstr(HoursFactory1 * AcneFactory1 + HoursFactory2 * AcneFactory2 >= MinAcneCream, name="min_acne_cream_production")

# Ensure that the total production of anti-bacterial cream meets the minimum requirement
model.addConstr(HoursFactory1 * AntibacterialFactory1 + HoursFactory2 * AntibacterialFactory2 >= MinAntibacterialCream, name="min_antibacterial_cream_requirement")

# Ensure the total usage of base gel does not exceed the available quantity
model.addConstr(HoursFactory1 * BaseGelFactory1 + HoursFactory2 * BaseGelFactory2 <= TotalBaseGel, "TotalBaseGelUsage")

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
