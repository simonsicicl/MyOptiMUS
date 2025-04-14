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
NumberMachinesA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberMachinesA")
NumberMachinesB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberMachinesB")
ElectricityUsedB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ElectricityUsedB")
TotalMachinesUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMachinesUsed")

# Add constraint to ensure the total number of items produced by machines A and B meets the minimum required number of items per day  
model.addConstr(NumberMachinesA * ItemsAMadePerDay + NumberMachinesB * ItemsBMadePerDay >= MinItems, name="min_items_constraint")

# Add constraint for total electricity consumption
model.addConstr(
    NumberMachinesA * ElectricityA + NumberMachinesB * ElectricityB <= MaxElectricity,
    name="total_electricity_consumption"
)

# Add constraint ensuring NumberMachinesB is at most MaxPercentB percent of the total 
model.addConstr(NumberMachinesB <= (MaxPercentB / (1 - MaxPercentB)) * NumberMachinesA, name="limit_machine_B_percentage")

# Add constraint for minimum number of machine A
model.addConstr(NumberMachinesA >= MinMachineA, name="min_machines_constraint")

TotalElectricityA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalElectricityA")
model.addConstr(ElectricityA * NumberMachinesA >= TotalElectricityA, name="electricity_usage_machine_A")

# Add constraint to limit total electricity used by machine B
model.addConstr(ElectricityUsedB <= ElectricityB * NumberMachinesB, name="electricity_limit_B")

# Add constraint to define electricity used by machine B
model.addConstr(ElectricityUsedB == ElectricityB * NumberMachinesB, name="electricity_usage_B")

# Add production minimum constraint
model.addConstr(NumberMachinesA * ItemsAMadePerDay + NumberMachinesB * ItemsBMadePerDay >= MinItems, name="min_production_constraint")

# Add electricity usage constraint
model.addConstr(
    NumberMachinesA * ElectricityA + NumberMachinesB * ElectricityB <= MaxElectricity,
    name="electricity_limit"
)

# Add constraint to limit the percentage of type B machines
model.addConstr(NumberMachinesB <= MaxPercentB * TotalMachinesUsed, name="limit_percentage_B")

# Ensure at least a minimum number of machine A is used
model.addConstr(NumberMachinesA >= MinMachineA, name="min_machines_A")

# Add a constraint to define the total machines used as the sum of type A and type B machines
model.addConstr(NumberMachinesA + NumberMachinesB == TotalMachinesUsed, name="total_machines_constraint")

# Set objective
model.setObjective(NumberMachinesA + NumberMachinesB, gp.GRB.MINIMIZE)

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
