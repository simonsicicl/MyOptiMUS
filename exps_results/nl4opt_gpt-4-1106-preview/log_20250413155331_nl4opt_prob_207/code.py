import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_207/data.json", "r") as f:
    data = json.load(f)

TimePrintingGraph = data["TimePrintingGraph"] # scalar parameter
TimeScanningGraph = data["TimeScanningGraph"] # scalar parameter
TimePrintingMusic = data["TimePrintingMusic"] # scalar parameter
TimeScanningMusic = data["TimeScanningMusic"] # scalar parameter
MaxTimePrinting = data["MaxTimePrinting"] # scalar parameter
MaxTimeScanning = data["MaxTimeScanning"] # scalar parameter
ProfitGraph = data["ProfitGraph"] # scalar parameter
ProfitMusic = data["ProfitMusic"] # scalar parameter
GraphPaperReamsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GraphPaperReamsProduced")
MusicPaperReamsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MusicPaperReamsProduced")

# Non-negativity constraint for the number of reams of graph paper produced
model.addConstr(GraphPaperReamsProduced >= 0, name="graph_paper_non_negativity")

# Non-negativity constraint for the number of reams of music paper produced
model.addConstr(MusicPaperReamsProduced >= 0, name="reams_non_negative")

# Add time constraint for graph paper printing
model.addConstr(TimePrintingGraph * GraphPaperReamsProduced <= MaxTimePrinting, name="time_limit_printing_machine")

# Add constraint for the total time spent on the scanning machine for all graph paper
model.addConstr(TimeScanningGraph * GraphPaperReamsProduced <= MaxTimeScanning, name="time_scanning_constraint")

# Add constraint for maximum available time on the printing machine
model.addConstr(TimePrintingGraph * GraphPaperReamsProduced + TimePrintingMusic * MusicPaperReamsProduced <= MaxTimePrinting, name="max_time_printing")

# Add maximum available time constraint on the scanning machine
model.addConstr(TimeScanningGraph * GraphPaperReamsProduced + TimeScanningMusic * MusicPaperReamsProduced <= MaxTimeScanning, name="max_time_scanning")

# Define the objective function
model.setObjective(ProfitGraph * GraphPaperReamsProduced + ProfitMusic * MusicPaperReamsProduced, gp.GRB.MAXIMIZE)

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
