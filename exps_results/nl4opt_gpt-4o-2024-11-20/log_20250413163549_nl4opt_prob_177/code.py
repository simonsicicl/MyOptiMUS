import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_177/data.json", "r") as f:
    data = json.load(f)

Tc = data["Tc"] # scalar parameter
Cc = data["Cc"] # scalar parameter
Ratio = data["Ratio"] # scalar parameter
MinCorn = data["MinCorn"] # scalar parameter
CornByTractors = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CornByTractors")
NumberOfTractors = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfTractors")
CornByCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CornByCars")
NumberOfCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCars")

# Add constraint for tractor capacity regarding corn
model.addConstr(CornByTractors <= NumberOfTractors * Tc, name="tractor_corn_capacity")

# Add constraint to ensure total weight transported by cars does not exceed their total capacity
model.addConstr(CornByCars <= NumberOfCars * Cc, name="car_capacity_constraint")

# Add constraint to ensure the number of cars used is at least Ratio times the number of tractors used
model.addConstr(NumberOfCars >= Ratio * NumberOfTractors, name="min_cars_constraint")

# Add constraint to ensure at least MinCorn kg of corn is sent to the city
model.addConstr(CornByTractors + CornByCars >= MinCorn, name="min_corn_constraint")

# No code is needed because the non-negativity constraint is automatically enforced due to the default non-negative domain of continuous variables in Gurobi.

# The variable "NumberOfCars" already has a non-negative domain since it is defined with CONTINUOUS type.
# No additional constraints are needed to ensure non-negativity.

# Non-negativity constraint for CornByCars
model.addConstr(CornByCars >= 0, name="non_negativity_CornByCars")

# Change the variable "NumberOfCars" type to integer since it is defined as count
NumberOfCars.vtype = gp.GRB.INTEGER

# Add constraint for transporting minimum corn weight
model.addConstr(CornByTractors + CornByCars >= MinCorn, name="min_corn_shipment")

# Add constraint to ensure the amount of corn transported by tractors does not exceed their total capacity
model.addConstr(CornByTractors <= Tc * NumberOfTractors, name="corn_transport_constraint")

# Add constraint: The amount of corn transported by cars cannot exceed 
# the car capacity multiplied by the number of cars used.
model.addConstr(CornByCars <= Cc * NumberOfCars, name="corn_transport_capacity")

# Add constraint ensuring the number of cars used is greater than or equal to the ratio times the number of tractors used
model.addConstr(NumberOfCars >= Ratio * NumberOfTractors, name="cars_tractors_ratio")

# Set objective
model.setObjective(NumberOfTractors + NumberOfCars, gp.GRB.MINIMIZE)

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
