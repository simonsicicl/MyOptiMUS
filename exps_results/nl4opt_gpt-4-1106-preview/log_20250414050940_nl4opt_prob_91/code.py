import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_91/data.json", "r") as f:
    data = json.load(f)

ItemsAMadePerDay = data["ItemsAMadePerDay"] # scalar parameter
ElectricityA = data["ElectricityA"] # scalar parameter
ItemsBMadePerDay = data["ItemsBMadePerDay"] # scalar parameter
ElectricityB = data["ElectricityB"] # scalar parameter
MinItems = data["MinItems"] # scalar parameter
MaxElectricity = data["MaxElectricity"] # scalar parameter
MaxPercentB = data["MaxPercentB"] # scalar parameter
MinMachineA = data["MinMachineA"] # scalar parameter
NumMachineA = model.addVar(vtype=gp.GRB.INTEGER, name="NumMachineA")
NumMachineB = model.addVar(vtype=gp.GRB.INTEGER, name="NumMachineB")
TotalElectricityA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalElectricityA")
TotalElectricityB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalElectricityB")

ItemsAMadePerDay = data["ItemsAMadePerDay"]  # scalar parameter
ItemsBMadePerDay = data["ItemsBMadePerDay"]  # scalar parameter
MinItems = data["MinItems"]  # scalar parameter

model.addConstr(ItemsAMadePerDay * NumMachineA + ItemsBMadePerDay * NumMachineB >= MinItems, name="min_daily_production")

# Total electricity consumption constraint
model.addConstr(NumMachineA * ElectricityA + NumMachineB * ElectricityB <= MaxElectricity, name="total_electricity_consumption")

# Constraint for the number of machine B being at most MaxPercentB percent of the total number of machines
model.addConstr(NumMachineB <= MaxPercentB * (NumMachineA + NumMachineB), name="max_percent_machine_B")

# Add constraint to ensure the number of Machine A used is at least the minimum
model.addConstr(NumMachineA >= MinMachineA, "min_machines_A")

# Constraint: Total electricity used by machine A is at most the product of ElectricityA and NumMachineA
model.addConstr(TotalElectricityA <= ElectricityA * NumMachineA, name="TotalElectricity_A_Constraint")

# Add constraint for total electricity used by machine B
model.addConstr(TotalElectricityB <= ElectricityB * NumMachineB, name="total_electricity_machine_B")

# Set objective
model.setObjective(NumMachineA + NumMachineB, gp.GRB.MINIMIZE)

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
