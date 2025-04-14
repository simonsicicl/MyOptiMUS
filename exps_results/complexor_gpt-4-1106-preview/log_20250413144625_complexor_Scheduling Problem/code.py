import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/Scheduling Problem/data.json", "r") as f:
    data = json.load(f)

NumRestaurants = data["NumRestaurants"] # scalar parameter
NumEmployees = data["NumEmployees"] # scalar parameter
NumShifts = data["NumShifts"] # scalar parameter
NumSkills = data["NumSkills"] # scalar parameter
Demand = np.array(data["Demand"]) # ['NumRestaurants', 'NumShifts', 'NumSkills']
EmployeeSkills = np.array(data["EmployeeSkills"]) # ['NumEmployees', 'NumSkills']
SkillPreference = np.array(data["SkillPreference"]) # ['NumEmployees', 'NumSkills']
ShiftAvailability = np.array(data["ShiftAvailability"]) # ['NumEmployees', 'NumShifts']
UnfulfilledPositionWeight = data["UnfulfilledPositionWeight"] # scalar parameter
EmployeeAssignedRestaurantShift = model.addVars(NumEmployees, NumRestaurants, NumShifts, vtype=gp.GRB.BINARY, name="EmployeeAssignedRestaurantShift")
SkillCoverage = model.addVars(NumSkills, NumRestaurants, NumShifts, vtype=gp.GRB.BINARY, name="SkillCoverage")

# Ensure exactly NumEmployees employees are assigned
employee_assignment_constraint = gp.quicksum(EmployeeAssignedRestaurantShift[e, r, j] for e in range(NumEmployees) for r in range(NumRestaurants) for j in range(NumShifts))
model.addConstr(employee_assignment_constraint == NumEmployees, name="exact_employee_assignment")

# Each employee can only be assigned to one shift at one restaurant at a time
for i in range(NumEmployees):
    for k in range(NumShifts):
        model.addConstr(gp.quicksum(EmployeeAssignedRestaurantShift[i, j, k] for j in range(NumRestaurants)) <= 1, name=f"unique_shift_assignment_{i}_{k}")

# Each restaurant must have the required number of skilled employees for each shift
for k in range(NumSkills):
    for r in range(NumRestaurants):
        for s in range(NumShifts):
            model.addConstr(
                gp.quicksum(EmployeeAssignedRestaurantShift[e,r,s] * EmployeeSkills[e,k] 
                            for e in range(NumEmployees)) >= Demand[r,s,k],
                name=f"skill_demand_r{r}_s{s}_k{k}"
            )

# Skill demand constraints for each restaurant shift
for r in range(NumRestaurants):
    for t in range(NumShifts):
        for s in range(NumSkills):
            model.addConstr(gp.quicksum(EmployeeAssignedRestaurantShift[e, r, t] * EmployeeSkills[e, s]
                                        for e in range(NumEmployees)) >= Demand[r, t, s],
                            name=f"skill_demand_r{r}_t{t}_s{s}")

EmployeeAssignedRestaurantShift = model.addVars(NumEmployees, NumRestaurants, NumShifts, vtype=gp.GRB.BINARY, name='EmployeeAssignedRestaurantShift')

# Ensure SkillCoverage is the sum of EmployeeAssignedRestaurantShift for employees with the required skills
for r in range(NumRestaurants):
    for s in range(NumShifts):
        for k in range(NumSkills):
            model.addConstr(
                (SkillCoverage[k, r, s] == gp.quicksum(EmployeeSkills[e, k] * EmployeeAssignedRestaurantShift[e, r, s]
                                                       for e in range(NumEmployees))),
                name=f"skill_coverage_r{r}_s{s}_k{k}"
            )

# Add a new set of variables for unfulfilled demand
UnfulfilledDemand = model.addVars(NumRestaurants, NumShifts, NumSkills, name="UnfulfilledDemand")

# Set objective
model.setObjective(
    gp.quicksum(
        EmployeeAssignedRestaurantShift[e, r, s] *
        gp.quicksum(EmployeeSkills[e, k] * SkillPreference[e, k] for k in range(NumSkills))
        for e in range(NumEmployees) for r in range(NumRestaurants) for s in range(NumShifts)
    ) + UnfulfilledPositionWeight *
      gp.quicksum(UnfulfilledDemand[r, s, k]
        for r in range(NumRestaurants) for s in range(NumShifts) for k in range(NumSkills)),
    gp.GRB.MINIMIZE
)

# Add constraints to ensure unfulfilled demand variables are correct
for r in range(NumRestaurants):
    for s in range(NumShifts):
        for k in range(NumSkills):
            model.addConstr(
                UnfulfilledDemand[r, s, k] >= Demand[r, s, k] - gp.quicksum(SkillCoverage[k, r, s] for e in range(NumEmployees) if EmployeeSkills[e, k] == 1),
                name="UnfulfilledDemandCons_{}_{}_{}".format(r, s, k)
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
