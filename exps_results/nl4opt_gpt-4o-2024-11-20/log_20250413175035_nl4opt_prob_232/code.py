import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_232/data.json", "r") as f:
    data = json.load(f)

PosterBoardsCircular = data["PosterBoardsCircular"] # scalar parameter
ParticipantsCircular = data["ParticipantsCircular"] # scalar parameter
GuestsCircular = data["GuestsCircular"] # scalar parameter
PosterBoardsRectangular = data["PosterBoardsRectangular"] # scalar parameter
ParticipantsRectangular = data["ParticipantsRectangular"] # scalar parameter
GuestsRectangular = data["GuestsRectangular"] # scalar parameter
SpaceCircular = data["SpaceCircular"] # scalar parameter
SpaceRectangular = data["SpaceRectangular"] # scalar parameter
MinParticipants = data["MinParticipants"] # scalar parameter
MinPosterBoards = data["MinPosterBoards"] # scalar parameter
TotalSpace = data["TotalSpace"] # scalar parameter
NumberCircularTables = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberCircularTables")
NumberRectangularTables = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberRectangularTables")

# No code is needed: Gurobi variables by default have non-negativity constraints unless explicitly set otherwise.

# Number of rectangular tables is non-negative
model.addConstr(NumberRectangularTables >= 0, name="non_negative_constraint")

# Adding the constraint for total participants
model.addConstr(
    ParticipantsCircular * NumberCircularTables + ParticipantsRectangular * NumberRectangularTables >= MinParticipants,
    name="total_participants_constraint"
)

# Add constraint for minimum poster board requirements
model.addConstr(
    NumberCircularTables * PosterBoardsCircular + NumberRectangularTables * PosterBoardsRectangular >= MinPosterBoards,
    name="min_poster_boards"
)

# Add constraint for total space used by tables
model.addConstr(
    NumberCircularTables * SpaceCircular + NumberRectangularTables * SpaceRectangular <= TotalSpace,
    name="space_constraint"
)

# Add constraint for total space occupied by tables
model.addConstr(SpaceCircular * NumberCircularTables + SpaceRectangular * NumberRectangularTables <= TotalSpace, 
                name="space_constraint")

# Add constraint to ensure the tables can accommodate at least the minimum number of participants
model.addConstr(
    NumberCircularTables * ParticipantsCircular + NumberRectangularTables * ParticipantsRectangular >= MinParticipants,
    name="min_participants_constraint"
)

# Add constraint to ensure a minimum number of poster boards are accommodated
model.addConstr(
    PosterBoardsCircular * NumberCircularTables + 
    PosterBoardsRectangular * NumberRectangularTables >= MinPosterBoards,
    name="min_poster_boards"
)

# Set objective
model.setObjective(GuestsCircular * NumberCircularTables + GuestsRectangular * NumberRectangularTables, gp.GRB.MAXIMIZE)

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
