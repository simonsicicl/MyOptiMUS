import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/65/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
IsolateCentral = np.array(data["IsolateCentral"]) # ['N']
ScanCentral = np.array(data["ScanCentral"]) # ['N']
IsolateDistributed = np.array(data["IsolateDistributed"]) # ['N']
ScanDistributed = np.array(data["ScanDistributed"]) # ['N']
CentralCost = data["CentralCost"] # scalar parameter
DistributedCost = data["DistributedCost"] # scalar parameter
CentralMaxHours = data["CentralMaxHours"] # scalar parameter
DistributedMaxHours = data["DistributedMaxHours"] # scalar parameter
IsolateCentralDecision = model.addVars(N, vtype=gp.GRB.BINARY, name="IsolateCentralDecision")
IsolateDistributedDecision = model.addVars(N, vtype=gp.GRB.BINARY, name="IsolateDistributedDecision")
NumberOfCentralInterventions = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCentralInterventions")
NumberOfDistributedInterventions = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDistributedInterventions")

# Add constraint for maximum processing hours at the central system
central_system_constraint = gp.quicksum(IsolateCentralDecision[i] * IsolateCentral[i] for i in range(N))
model.addConstr(central_system_constraint <= CentralMaxHours, name="central_max_hours")

# Constraint for the total processing time of scanning interventions in the central system
model.addConstr(gp.quicksum(IsolateCentralDecision[i] * ScanCentral[i] for i in range(N)) <= CentralMaxHours, name="central_system_capacity")

# Add constraint for total processing time at the distributed system
total_processing_time = gp.quicksum(IsolateDistributedDecision[i] * IsolateDistributed[i] for i in range(N))
model.addConstr(total_processing_time <= DistributedMaxHours, name="distributed_processing_time")

# Add constraint for the maximum hours of operation for the distributed system
processing_time_constraint = gp.quicksum(IsolateDistributedDecision[i] * ScanDistributed[i] for i in range(N))
model.addConstr(processing_time_constraint <= DistributedMaxHours, name="max_distributed_hours_operation")

# Add constraint for total number of interventions for both systems to be equal to N
total_isolation_interventions = gp.quicksum(IsolateCentralDecision[i] + IsolateDistributedDecision[i] for i in range(N))
model.addConstr(total_isolation_interventions == N, name="total_interventions_constraint")

# No code needed because NumberOfCentralInterventions is derived from IsolateCentralDecision, which has already been defined as binary, thus it is non-negative and integer by definition.
# However, if we want to create an explicit variable for NumberOfCentralInterventions, we could sum the binary variables and ensure it's non-negative.
# Since NumberOfCentralInterventions is not explicitly defined yet, here is the code to define it and ensure it is non-negative and integer.

NumberOfCentralInterventions = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCentralInterventions")
model.addConstr(NumberOfCentralInterventions == gp.quicksum(IsolateCentralDecision[i] for i in range(N)), name="calculate_NumberOfCentralInterventions")
model.addConstr(NumberOfCentralInterventions >= 0, name="nonnegativity_NumberOfCentralInterventions")

# Since the variable IsolateDistributedDecision is already defined as binary,
# there is no need to explicitly add a constraint for non-negativity or integrality.
# Integrality and non-negativity are inherent properties of binary variables.
# However, if we need to count the number of interventions, we should create an auxiliary integer variable.

# Define an auxiliary integer variable for the total number of interventions
NumberOfDistributedInterventions = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDistributedInterventions")

# Add a constraint that equates the auxiliary variable with the sum of the binary decision variables
model.addConstr(NumberOfDistributedInterventions == gp.quicksum(IsolateDistributedDecision[n] for n in range(N)),
                name="total_distributed_interventions")

# Constraint for the total number of central system interventions
model.addConstr(NumberOfCentralInterventions == gp.quicksum(IsolateCentralDecision[i] for i in range(N)), name="TotalNumberOfCentralInterventions")

# Summation constraint for the total number of distributed system interventions
model.addConstr(NumberOfDistributedInterventions == gp.quicksum(IsolateDistributedDecision[i] for i in range(N)), 
                name="total_distributed_interventions")

# Add the constraint for maximum hours of operation for the central system
central_system_constraint = gp.quicksum((IsolateCentralDecision[i] * IsolateCentral[i] +
                                        IsolateCentralDecision[i] * ScanCentral[i])
                                        for i in range(N)) <= CentralMaxHours
model.addConstr(central_system_constraint, name="central_system_max_hours")

# Add a constraint for the sum of processing times in the distributed system
model.addConstr(
    gp.quicksum(IsolateDistributedDecision[i] * IsolateDistributed[i] + 
                IsolateDistributedDecision[i] * ScanDistributed[i]
                for i in range(N)) 
    <= DistributedMaxHours, 
    name="max_distributed_operation_hours")

# Set objective
model.setObjective(
    gp.quicksum(IsolateCentralDecision[i] * CentralCost for i in range(N)) +
    gp.quicksum(IsolateDistributedDecision[i] * DistributedCost for i in range(N)),
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
