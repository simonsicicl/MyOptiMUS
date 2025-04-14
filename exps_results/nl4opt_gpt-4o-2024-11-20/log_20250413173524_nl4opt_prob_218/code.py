import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_218/data.json", "r") as f:
    data = json.load(f)

ProfitRegular = data["ProfitRegular"] # scalar parameter
ProfitDeluxe = data["ProfitDeluxe"] # scalar parameter
DemandRegularMax = data["DemandRegularMax"] # scalar parameter
DemandDeluxeMax = data["DemandDeluxeMax"] # scalar parameter
SupplyTotalMax = data["SupplyTotalMax"] # scalar parameter
RegularTacosSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularTacosSold")
DeluxeTacosSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DeluxeTacosSold")

# Add demand, supply, and non-negativity constraints for taco sales
model.addConstr(RegularTacosSold <= DemandRegularMax, name="demand_regular_tacos")
model.addConstr(DeluxeTacosSold <= DemandDeluxeMax, name="demand_deluxe_tacos")
model.addConstr(RegularTacosSold + DeluxeTacosSold <= SupplyTotalMax, name="supply_total_limit")
model.addConstr(RegularTacosSold >= 0, name="non_negativity_regular_tacos")
model.addConstr(DeluxeTacosSold >= 0, name="non_negativity_deluxe_tacos")

# Add constraint to ensure the number of deluxe tacos sold is non-negative
model.addConstr(DeluxeTacosSold >= 0, name="non_negative_deluxe_tacos")

# Add the constraint that the number of regular tacos sold is at most the maximum demand for regular tacos
model.addConstr(RegularTacosSold <= DemandRegularMax, name="max_demand_regular_tacos")

# Add constraint for deluxe tacos
model.addConstr(DeluxeTacosSold <= DemandDeluxeMax, name="deluxe_tacos_demand_constraint")

# Add constraint ensuring total number of tacos sold is at most the supply limit
model.addConstr(RegularTacosSold + DeluxeTacosSold <= SupplyTotalMax, name="total_taco_supply_limit")

# Regular tacos maximum demand constraint
model.addConstr(RegularTacosSold <= DemandRegularMax, name="max_demand_regular_tacos")

# Add constraint to ensure deluxe tacos sold do not exceed maximum demand
model.addConstr(DeluxeTacosSold <= DemandDeluxeMax, name="deluxe_tacos_demand_limit")

# Add constraint for total tacos sold not exceeding supply limit
model.addConstr(RegularTacosSold + DeluxeTacosSold <= SupplyTotalMax, name="taco_supply_limit")

# The variable "RegularTacosSold" is already defined as non-negative due to its default lower bound (0) in Gurobi.
# No additional code is needed for this constraint.

# Add constraint to ensure the number of deluxe tacos sold is non-negative
model.addConstr(DeluxeTacosSold >= 0, name="non_negative_deluxe_tacos")

# Set objective
model.setObjective(ProfitRegular * RegularTacosSold + ProfitDeluxe * DeluxeTacosSold, gp.GRB.MAXIMIZE)

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
