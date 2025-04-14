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
ElectricJacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ElectricJacks")
GasPoweredJacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GasPoweredJacks")

# No additional code needed since the variable "ElectricJacks" is already defined with a lower bound of 0 by default as it is continuous.

# No code is needed for this constraint since the variable `GasPoweredJacks` is already defined with non-negativity implicitly handled by default (continuous variables in Gurobi are non-negative unless specified otherwise).

# Add constraint to ensure the number of electric jacks does not exceed the maximum allowed
model.addConstr(ElectricJacks <= MaxElectricJacks, name="electric_jacks_limit")

# Add constraint for total electricity usage of automatic electric jacks
model.addConstr(ElectricJacks * ElectricityPerJack <= MaxElectricity, name="electricity_usage_limit")

# Add constraint for gas usage by gas-powered car jacks
model.addConstr(GasPoweredJacks * GasPerJack <= MaxGas, name="max_gas_usage")

# Add constraint to limit the number of electric jacks
model.addConstr(ElectricJacks <= MaxElectricJacks, name="limit_electric_jacks")

# Add constraint to ensure total electricity usage by electric jacks does not exceed the maximum available electricity
model.addConstr(ElectricJacks * ElectricityPerJack <= MaxElectricity, name="electric_jack_constraint")

# Add constraint to ensure the total gas used by gas-powered jacks does not exceed the maximum available gas
model.addConstr(GasPoweredJacks * GasPerJack <= MaxGas, name="gas_limit_constraint")

# Set objective
model.setObjective(ElectricJacks * CarsPerHourElectric + GasPoweredJacks * CarsPerHourGas, gp.GRB.MAXIMIZE)

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
