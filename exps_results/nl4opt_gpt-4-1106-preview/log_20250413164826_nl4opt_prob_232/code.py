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
NumCircularTables = model.addVar(vtype=gp.GRB.INTEGER, name="NumCircularTables")
NumRectangularTables = model.addVar(vtype=gp.GRB.INTEGER, name="NumRectangularTables")

# The number of circular tables must be non-negative
# Hence, there is no need to add an explicit constraint in Gurobi,
# as the variable is already defined with the correct domain being non-negative integers.

# The number of rectangular tables must be non-negative, so no constraint is needed as
# Gurobi variables are non-negative by default when the lower bound is not specified.
# Integers are assumed to be non-negative unless otherwise specified.

# Add constraint for the minimum number of participants
model.addConstr(NumCircularTables * ParticipantsCircular + NumRectangularTables * ParticipantsRectangular >= MinParticipants, name="min_participants")

# Constraint: Number of poster boards at circular and rectangular tables should meet the minimum requirement
model.addConstr(NumCircularTables * PosterBoardsCircular + NumRectangularTables * PosterBoardsRectangular >= MinPosterBoards, "min_poster_boards")

# Space used by all tables must not exceed the total available space for the science fair
model.addConstr(NumCircularTables * SpaceCircular + NumRectangularTables * SpaceRectangular <= TotalSpace, "total_space_constraint")

# Define Objective Function
model.setObjective(NumCircularTables * GuestsCircular + NumRectangularTables * GuestsRectangular, gp.GRB.MAXIMIZE)

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
