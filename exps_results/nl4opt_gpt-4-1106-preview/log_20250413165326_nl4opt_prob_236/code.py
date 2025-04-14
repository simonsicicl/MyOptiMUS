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
BikeShifts = model.addVar(vtype=gp.GRB.INTEGER, name="BikeShifts")
ScooterShifts = model.addVar(vtype=gp.GRB.INTEGER, name="ScooterShifts")

# Add constraint to ensure the total number of shifts is non-negative
model.addConstr(BikeShifts + ScooterShifts >= 0, name="non_negative_shifts")

# The number of bike shifts worked in a month must be non-negative
model.addConstr(BikeShifts >= 0, name="non_negative_bike_shifts")

# No code needed since the variable 'ScooterShifts' is already defined as non-negative by setting the variable type to INTEGER

# Total number of shifts constraint
model.addConstr(BikeShifts + ScooterShifts <= TotalShifts, name="total_shifts_limit")

# Total energy used by all shifts must not exceed the available total energy
model.addConstr(EnergyBike * BikeShifts + EnergyScooter * ScooterShifts <= TotalEnergy, name="total_energy")

# Add constraint for minimum orders
model.addConstr(BikeShifts * OrdersBike + ScooterShifts * OrdersScooter >= MinOrders, name="min_orders")

# Ensure the number of scooter shifts meets the minimum requirement
model.addConstr(ScooterShifts >= MinScooterShifts, name="min_scooter_shifts")

# Constrain the total number of shifts to not exceed the total available shifts per month
model.addConstr(BikeShifts + ScooterShifts <= TotalShifts, name="total_shift_constraint")

# Energy consumption constraint
model.addConstr(EnergyBike * BikeShifts + EnergyScooter * ScooterShifts <= TotalEnergy, name="total_energy_constraint")

# The total orders delivered must meet or exceed the minimum order requirement
model.addConstr(OrdersBike * BikeShifts + OrdersScooter * ScooterShifts >= MinOrders, name="min_order_requirement")

# Constraint: The number of scooter shifts must meet or exceed the minimum scooter shift requirement
model.addConstr(ScooterShifts >= MinScooterShifts, name="min_scooter_shifts_req")

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
