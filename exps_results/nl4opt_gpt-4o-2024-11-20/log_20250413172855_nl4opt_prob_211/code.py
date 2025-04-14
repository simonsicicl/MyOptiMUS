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

# Add constraint to ensure laminate production meets or exceeds minimum demand
model.addConstr(LaminateProduced >= Dlaminate, name="laminate_demand_constraint")

# Add flooring company production constraint
model.addConstr(CarpetProduced >= Dcarpet, name="minimum_carpet_production")

# Add constraint to ensure the total square feet of laminate and carpets produced meets or exceeds Dtotal
model.addConstr(LaminateProduced + CarpetProduced >= Dtotal, name="min_demand_constraint")

# Add laminate production capacity constraint
model.addConstr(LaminateProduced <= Claminate, name="laminate_production_capacity")

# Add carpet production limit constraint
model.addConstr(CarpetProduced <= Ccarpet, name="carpet_production_limit")

# The non-negativity constraint is automatically ensured due to the default non-negative domain of continuous variables in Gurobi.

# Ensure the number of square feet of carpets produced per week is non-negative
model.addConstr(CarpetProduced >= 0, name="non_negativity_CarpetProduced")

# Add constraint to ensure laminate production meets minimum demand
model.addConstr(LaminateProduced >= Dlaminate, name="min_demand_laminate")

# Ensure the production of carpets meets the minimum demand
model.addConstr(CarpetProduced >= Dcarpet, name="min_demand_constraint")

# Add constraint to ensure the total production meets the overall minimum demand
model.addConstr(LaminateProduced + CarpetProduced >= Dtotal, name="total_production_min_demand")

# Add constraint to ensure laminate production does not exceed capacity
model.addConstr(LaminateProduced <= Claminate, name="laminate_production_capacity")

# Add production capacity constraint
model.addConstr(CarpetProduced <= Ccarpet, name="carpet_production_capacity")

# Set objective
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
