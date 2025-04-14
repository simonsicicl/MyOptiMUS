import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_236/data.json", "r") as f:
    data = json.load(f)

OrdersBike = data["OrdersBike"] # scalar parameter
EnergyBike = data["EnergyBike"] # scalar parameter
TipsBike = data["TipsBike"] # scalar parameter
OrdersScooter = data["OrdersScooter"] # scalar parameter
EnergyScooter = data["EnergyScooter"] # scalar parameter
TipsScooter = data["TipsScooter"] # scalar parameter
TotalShifts = data["TotalShifts"] # scalar parameter
TotalEnergy = data["TotalEnergy"] # scalar parameter
MinOrders = data["MinOrders"] # scalar parameter
MinScooterShifts = data["MinScooterShifts"] # scalar parameter
BikeShifts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BikeShifts")
ScooterShifts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ScooterShifts")

# Add non-negativity constraint for total shifts
model.addConstr(BikeShifts + ScooterShifts >= 0, name="non_negative_shifts")

# No additional code is required because the variable "BikeShifts" is already defined as non-negative (continuous variables in Gurobi are non-negative by default).

# No additional code needed since the variable "ScooterShifts" is defined with non-negativity by default through its continuous type.

# Add constraint to ensure the total number of shifts worked using bikes and scooters does not exceed the total available shifts
model.addConstr(BikeShifts + ScooterShifts <= TotalShifts, name="max_shift_constraint")

# Add energy usage constraint
model.addConstr(EnergyBike * BikeShifts + EnergyScooter * ScooterShifts <= TotalEnergy, name="energy_usage_limit")

# Add constraint for minimum required orders
model.addConstr(
    BikeShifts * OrdersBike + ScooterShifts * OrdersScooter >= MinOrders,
    name="min_order_requirement"
)

# Add constraint to ensure the number of scooter shifts meets the minimum required
model.addConstr(ScooterShifts >= MinScooterShifts, name="min_scooter_shifts")

# The variable "BikeShifts" is constrained to be non-negative by its definition as a non-negative continuous variable (vtype=gp.GRB.CONTINUOUS), so no additional constraint is needed.

# Add constraint for non-negative scooter shifts
model.addConstr(ScooterShifts >= 0, name="non_negative_scooter_shifts")

# Adding the constraint for total number of shifts
model.addConstr(BikeShifts + ScooterShifts <= TotalShifts, name="total_shifts_constraint")

# Add energy consumption constraint
model.addConstr(EnergyBike * BikeShifts + EnergyScooter * ScooterShifts <= TotalEnergy, name="energy_consumption")

# Add constraint to ensure the total orders delivered meet the minimum required orders
model.addConstr(
    BikeShifts * OrdersBike + ScooterShifts * OrdersScooter >= MinOrders,
    name="min_orders_constraint"
)

# Add minimum scooter shifts constraint
model.addConstr(ScooterShifts >= MinScooterShifts, name="min_scooter_shifts")

# Set objective
model.setObjective(TipsBike * BikeShifts + TipsScooter * ScooterShifts, gp.GRB.MAXIMIZE)

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
