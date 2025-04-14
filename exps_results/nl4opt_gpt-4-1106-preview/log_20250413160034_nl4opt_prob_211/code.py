import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_211/data.json", "r") as f:
    data = json.load(f)

Dlaminate = data["Dlaminate"] # scalar parameter
Dcarpet = data["Dcarpet"] # scalar parameter
Dtotal = data["Dtotal"] # scalar parameter
Claminate = data["Claminate"] # scalar parameter
Ccarpet = data["Ccarpet"] # scalar parameter
Plaminate = data["Plaminate"] # scalar parameter
Pcarpet = data["Pcarpet"] # scalar parameter
LaminateProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LaminateProduced")
CarpetProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CarpetProduced")

# Produce at least Dlaminate square feet of laminate planks per week constraint
model.addConstr(LaminateProduced >= Dlaminate, name="min_laminate_production")

# Ensure production meets minimum demand for carpets
model.addConstr(CarpetProduced >= Dcarpet, name="min_demand_carpets")

# Add the constraint for minimum total production of laminate planks and carpets per week.
model.addConstr(LaminateProduced + CarpetProduced >= Dtotal, name="min_total_demand")

# Production capacity constraint for laminate planks
model.addConstr(LaminateProduced <= Claminate, name="production_capacity")

# Add production limit constraint for carpets
model.addConstr(CarpetProduced <= Ccarpet, name="prod_limit_carpets")

# Add constraint to ensure laminate produced per week is non-negative
model.addConstr(LaminateProduced >= 0, name="non_negative_laminate_produced")

# Add constraint to ensure carpet produced is non-negative
model.addConstr(CarpetProduced >= 0, name="non_negative_carpet_produced")

# Minimum expected demand for laminate planks constraint
model.addConstr(LaminateProduced >= Dlaminate, name="demand_laminate")

# Ensure the minimum expected demand for carpets is met
model.addConstr(CarpetProduced >= Dcarpet, name="min_demand_carpets")

# Cannot exceed the maximum production capacity for laminate planks
model.addConstr(LaminateProduced <= Claminate, name="max_production_capacity")

# Add maximum production capacity constraint for carpets
model.addConstr(CarpetProduced <= Ccarpet, name="max_production_capacity")

# Add constraint to meet the minimum total amount of products to be shipped per week
model.addConstr(LaminateProduced + CarpetProduced >= Dtotal, "Min_Total_Production")

# Define the objective function
model.setObjective(Plaminate * LaminateProduced + Pcarpet * CarpetProduced, gp.GRB.MAXIMIZE)

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
