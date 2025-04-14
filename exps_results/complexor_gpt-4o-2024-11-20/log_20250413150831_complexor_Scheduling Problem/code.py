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
Assignment = model.addVars(NumEmployees, NumRestaurants, NumShifts, vtype=gp.GRB.BINARY, name="Assignment")
SkillMatch = model.addVars(NumEmployees, NumRestaurants, NumShifts, NumSkills, vtype=gp.GRB.BINARY, name="SkillMatch")
UnfulfilledPositions = model.addVars(NumRestaurants, NumShifts, NumSkills, vtype=gp.GRB.CONTINUOUS, name="UnfulfilledPositions")

# Add a constraint to enforce that exactly NumEmployees assignments are made across all employees, restaurants, and shifts
model.addConstr(
    gp.quicksum(Assignment[e, r, s] for e in range(NumEmployees) for r in range(NumRestaurants) for s in range(NumShifts)) == NumEmployees,
    name="exactly_NumEmployees_assigned"
)

# Add constraint ensuring each employee can only be assigned to one shift at one restaurant at a time
for e in range(NumEmployees):
    model.addConstr(
        gp.quicksum(Assignment[e, r, s] for r in range(NumRestaurants) for s in range(NumShifts)) <= 1, 
        name=f"Employee_Assignment_Limit_{e}"
    )

# Add constraints to ensure the total number of employees assigned to each shift in each restaurant meets the skill demand
for r in range(NumRestaurants):
    for s in range(NumShifts):
        for k in range(NumSkills):
            model.addConstr(
                gp.quicksum(
                    Assignment[e, r, s] * EmployeeSkills[e, k] for e in range(NumEmployees)
                ) >= Demand[r, s, k],
                name=f"skill_demand_r{r}_s{s}_k{k}"
            )

# Add skill contribution constraints
for r in range(NumRestaurants):
    for s in range(NumShifts):
        for k in range(NumSkills):
            model.addConstr(
                gp.quicksum(SkillMatch[e, r, s, k] for e in range(NumEmployees)) >= Demand[r, s, k],
                name=f"skill_contribution_r{r}_s{s}_k{k}"
            )

# Add constraints to ensure that SkillMatch is valid only if an employee is assigned to a shift
for e in range(NumEmployees):
    for r in range(NumRestaurants):
        for s in range(NumShifts):
            for k in range(NumSkills):
                model.addConstr(SkillMatch[e, r, s, k] <= Assignment[e, r, s], name=f"SkillMatch_validity_e{e}_r{r}_s{s}_k{k}")

# Add constraints to ensure SkillMatch is 0 if the assigned employee does not possess the required skill
for e in range(NumEmployees):
    for r in range(NumRestaurants):
        for s in range(NumShifts):
            for k in range(NumSkills):
                model.addConstr(SkillMatch[e, r, s, k] <= EmployeeSkills[e, k], name=f"SkillMatch_constraint_{e}_{r}_{s}_{k}")

# Add SkillMatch constraints for ensuring proper assignment and skill compatibility
for e in range(NumEmployees):
    for r in range(NumRestaurants):
        for s in range(NumShifts):
            for k in range(NumSkills):
                model.addConstr(SkillMatch[e, r, s, k] >= Assignment[e, r, s] + EmployeeSkills[e, k] - 1, 
                                name=f"SkillMatchConstr_e{e}_r{r}_s{s}_k{k}")

# Add constraints to calculate UnfulfilledPositions for all restaurants, shifts, and skills
for r in range(NumRestaurants):
    for s in range(NumShifts):
        for k in range(NumSkills):
            model.addConstr(
                UnfulfilledPositions[r, s, k] == Demand[r, s, k] - gp.quicksum(SkillMatch[e, r, s, k] for e in range(NumEmployees)), 
                name=f"UnfulfilledPositions_calc_r{r}_s{s}_k{k}"
            )

# Add SkillMatch consistency constraints
for e in range(NumEmployees):
    for r in range(NumRestaurants):
        for s in range(NumShifts):
            for k in range(NumSkills):
                model.addConstr(SkillMatch[e, r, s, k] <= EmployeeSkills[e, k] * Assignment[e, r, s], 
                                name=f"SkillMatch_consistency_e{e}_r{r}_s{s}_k{k}")

# Add non-negativity constraints for UnfulfilledPositions
for r in range(NumRestaurants):
    for s in range(NumShifts):
        for k in range(NumSkills):
            model.addConstr(UnfulfilledPositions[r, s, k] >= 0, name=f"non_negativity_UnfulfilledPositions_r{r}_s{s}_k{k}")

# Set objective
model.setObjective(
    gp.quicksum(
        UnfulfilledPositions[r, s, k] * UnfulfilledPositionWeight
        for r in range(NumRestaurants)
        for s in range(NumShifts)
        for k in range(NumSkills)
    )
    +
    gp.quicksum(
        Assignment[e, r, s] * (1 - SkillPreference[e, k]) * EmployeeSkills[e, k]
        for e in range(NumEmployees)
        for r in range(NumRestaurants)
        for s in range(NumShifts)
        for k in range(NumSkills)
    ),
    gp.GRB.MINIMIZE
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
