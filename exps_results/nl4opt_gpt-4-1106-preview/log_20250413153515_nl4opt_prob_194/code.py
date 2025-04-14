import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_194/data.json", "r") as f:
    data = json.load(f)

PeopleSmallTruck = data["PeopleSmallTruck"] # scalar parameter
CapacitySmallTruck = data["CapacitySmallTruck"] # scalar parameter
PeopleLargeTruck = data["PeopleLargeTruck"] # scalar parameter
CapacityLargeTruck = data["CapacityLargeTruck"] # scalar parameter
TotalPeople = data["TotalPeople"] # scalar parameter
MinSmallTrucks = data["MinSmallTrucks"] # scalar parameter
MinLargeTrucks = data["MinLargeTrucks"] # scalar parameter
TruckProportion = data["TruckProportion"] # scalar parameter
NumberOfPeopleAssignedToSmallTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPeopleAssignedToSmallTrucks")
NumberOfPeopleAssignedToLargeTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfPeopleAssignedToLargeTrucks")
NumberOfSmallTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallTrucks")
NumberOfLargeTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeTrucks")

# Since the NumberOfPeopleAssignedToSmallTrucks variable is already initialized to be non-negative by default,
# there's no need to add an explicit constraint for it.

# In Gurobi, all variables are non-negative by default unless specified otherwise, thus no constraint needed here.

# Since NumberOfPeopleAssignedToLargeTrucks is already defined as an integer variable, no code needed to ensure non-negativity,
# as integer variables in Gurobi are non-negative by default unless specified otherwise.

# Add constraint: Total number of people for trucks cannot exceed the total available people
model.addConstr(NumberOfPeopleAssignedToSmallTrucks * PeopleSmallTruck + NumberOfPeopleAssignedToLargeTrucks * PeopleLargeTruck <= TotalPeople, "total_people_constraint")

# Ensure that at least the minimum number of small trucks is used
model.addConstr(NumberOfSmallTrucks >= MinSmallTrucks, name="min_small_trucks_constraint")

# Ensure that at least MinLargeTrucks large trucks are used
model.addConstr(NumberOfLargeTrucks >= MinLargeTrucks, name="min_large_trucks_constraint")

# Constraint: Total number of people assigned to small and large trucks should not exceed the total number of people available for shoveling snow
model.addConstr(NumberOfSmallTrucks * PeopleSmallTruck + NumberOfLargeTrucks * PeopleLargeTruck <= TotalPeople, "PeopleCapacityConstraint")

# Ensure the number of small trucks used is at least the minimum required
model.addConstr(NumberOfSmallTrucks >= MinSmallTrucks, name="min_small_trucks_required")

# Constraint: Number of large trucks used must be at least the minimum required
model.addConstr(NumberOfLargeTrucks >= MinLargeTrucks, name="min_large_trucks_required")

# Maintaining the proportion of the number of small trucks to large trucks
model.addConstr(NumberOfSmallTrucks >= TruckProportion * NumberOfLargeTrucks, name="truck_proportion_constraint")

# Set objective
model.setObjective(NumberOfSmallTrucks * CapacitySmallTruck + NumberOfLargeTrucks * CapacityLargeTruck, gp.GRB.MAXIMIZE)

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
