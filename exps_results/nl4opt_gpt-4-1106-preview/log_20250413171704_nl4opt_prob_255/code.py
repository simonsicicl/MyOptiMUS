import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_255/data.json", "r") as f:
    data = json.load(f)

CarsPerHourElectric = data["CarsPerHourElectric"] # scalar parameter
ElectricityPerJack = data["ElectricityPerJack"] # scalar parameter
CarsPerHourGas = data["CarsPerHourGas"] # scalar parameter
GasPerJack = data["GasPerJack"] # scalar parameter
MaxElectricJacks = data["MaxElectricJacks"] # scalar parameter
MaxElectricity = data["MaxElectricity"] # scalar parameter
MaxGas = data["MaxGas"] # scalar parameter
NumElectricJacks = model.addVar(vtype=gp.GRB.INTEGER, name="NumElectricJacks")
NumGasPoweredJacks = model.addVar(vtype=gp.GRB.INTEGER, name="NumGasPoweredJacks")

# Since the variable is defined as an INTEGER, it is implicitly non-negative. 
# No further constraint is needed.

# Constraint for non-negative number of gas-powered car jacks
model.addConstr(NumGasPoweredJacks >= 0, name="non_negative_gas_powered_jacks")

# Ensure that the number of automatic electric car jacks does not exceed the maximum available
model.addConstr(NumElectricJacks <= MaxElectricJacks, name="limit_electric_jacks")

# Constraint for the total electricity usage of automatic electric car jacks
model.addConstr(NumElectricJacks * ElectricityPerJack <= MaxElectricity, name="electricity_usage_limit")

# Total gas usage constraint for gas-powered car jacks
model.addConstr(NumGasPoweredJacks * GasPerJack <= MaxGas, name="total_gas_usage")

ElectricityPerJack = data["ElectricityPerJack"]  # scalar parameter
MaxElectricity = data["MaxElectricity"]  # scalar parameter
NumElectricJacks = model.addVar(vtype=gp.GRB.INTEGER, name="NumElectricJacks")
model.addConstr(ElectricityPerJack * NumElectricJacks <= MaxElectricity, name="max_electric_units_constraint")

# Constraint: Total gas units used by all gas-powered jacks should not exceed the maximum units of gas available per hour
model.addConstr(GasPerJack * NumGasPoweredJacks <= MaxGas, name="max_gas_usage")

# Add constraint for the maximum number of electric jacks
model.addConstr(NumElectricJacks <= MaxElectricJacks, name="Max_NumElectricJacks")

# Set objective
model.setObjective(CarsPerHourElectric * NumElectricJacks + CarsPerHourGas * NumGasPoweredJacks, gp.GRB.MAXIMIZE)

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
