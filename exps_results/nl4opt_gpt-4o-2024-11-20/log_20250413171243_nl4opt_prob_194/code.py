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
PeopleAssignedSmallTrucks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PeopleAssignedSmallTrucks")
PeopleAssignedLargeTrucks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PeopleAssignedLargeTrucks")
SmallTrucksUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallTrucksUsed")
LargeTrucksUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeTrucksUsed")

# The non-negativity constraint is inherently satisfied as the variable PeopleAssignedSmallTrucks is defined as continuous, which defaults to being non-negative in Gurobi. Thus, no additional code is needed.

# No additional code needed; non-negativity is enforced as the variable "PeopleAssignedLargeTrucks" is defined with a lower bound of 0 by default in Gurobi (continuous variables are non-negative by default unless explicitly stated otherwise through bounds).

# Add constraint to ensure that the total number of people assigned to small and large trucks does not exceed TotalPeople
model.addConstr(PeopleAssignedSmallTrucks + PeopleAssignedLargeTrucks <= TotalPeople, name="people_assignment_limit")

# Add constraint for minimum number of small trucks used
model.addConstr(SmallTrucksUsed >= MinSmallTrucks, name="min_small_trucks")

# Add constraint to ensure that at least MinLargeTrucks large trucks are used
model.addConstr(LargeTrucksUsed >= MinLargeTrucks, name="min_large_trucks")

# Add constraint relating PeopleAssignedSmallTrucks to SmallTrucksUsed
model.addConstr(PeopleAssignedSmallTrucks == SmallTrucksUsed * PeopleSmallTruck, name="relate_small_trucks_to_people")

# Add constraint to ensure total assigned people do not exceed available people
model.addConstr(
    PeopleSmallTruck * SmallTrucksUsed + PeopleLargeTruck * LargeTrucksUsed <= TotalPeople,
    name="limit_total_people"
)

# Add constraint to ensure the number of small trucks used meets the minimum requirement
model.addConstr(SmallTrucksUsed >= MinSmallTrucks, name="min_small_trucks_requirement")

# Add constraint to ensure the number of large trucks used meets or exceeds the minimum required
model.addConstr(LargeTrucksUsed >= MinLargeTrucks, name="min_large_trucks")

# Add proportion constraint to ensure ratio of small trucks to large trucks
model.addConstr(SmallTrucksUsed >= TruckProportion * LargeTrucksUsed, name="truck_proportion_constraint")

# Set objective
model.setObjective(
    CapacitySmallTruck * SmallTrucksUsed + CapacityLargeTruck * LargeTrucksUsed, 
    gp.GRB.MAXIMIZE
)

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
