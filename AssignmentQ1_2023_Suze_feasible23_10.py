# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 21:15:51 2023

@author: suzev
"""

import gurobipy as gp
from gurobipy import GRB

model = gp.Model('Assignment1')

# ---- Parameters ----
# Characteristics
productname = ('airfryers', 'breadmakers', 'coffeemakers')
P = ('airfryers', 'breadmakers', 'coffeemakers')
holding_costs_finished = (800e-3, 1500e-3, 500e-3)  # euro / 1000 products
holding_costs_packaged = (1000e-3, 1000e-3, 1000e-3)  # euro / 1000 products

productionstep = ('molding', 'assembling', 'finishing', 'packaging')
O = ('molding', 'assembling', 'finishing', 'packaging')
# time_airfryers = (0.6, 0.8, 0.1, 2.5)  # hours / 1000 products
# time_breadmachines = (1.2, 0.5, 2.0, 2.5)  # hours / 1000 products
# time_coffeemakers = (0.5, 0.1, 0.1, 2.5)  # hours / 1000 products

time = {  # hour / 1000 products
    ('airfryers', 'molding'): 0.6e-3,
    ('breadmakers', 'molding'): 1.2e-3,
    ('coffeemakers', 'molding'): 0.5e-3,
    ('airfryers', 'assembling'): 0.8e-3,
    ('breadmakers', 'assembling'): 0.5e-3,
    ('coffeemakers', 'assembling'): 0.1e-3,
    ('airfryers', 'finishing'): 0.1e-3,
    ('breadmakers', 'finishing'): 2.0e-3,
    ('coffeemakers', 'finishing'): 0.1e-3,
    ('airfryers', 'packaging'): 2.5e-3,
    ('breadmakers', 'packaging'): 2.5e-3,
    ('coffeemakers', 'packaging'): 2.5e-3
}

capacity = {  # hour
    ('molding'): 80,
    ('assembling'): 100,
    ('finishing'): 100,
    ('packaging'): 250,
}
capacity = (80, 100, 100, 250)  # hours

month = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
# demand_airfryer = (10, 20, 25, 30, 50, 70, 10, 12, 10, 200.2, 20.0, 14.8)  # 1000 products
# demand_breadmachines = (11, 13, 12, 11, 10, 10, 10, 12, 11, 10.0, 50.4, 10.6)  # 1000 products
# demand_coffeemakers = (10, 20, 50, 10, 20, 50, 10, 20, 50, 10.0, 20.0, 55.5)  # 1000 products

demand = {
        ('Jan', 'airfryers'): 10e3, ('Jan', 'breadmakers'): 11e3, ('Jan', 'coffeemakers'): 10e3,
        ('Feb', 'airfryers'): 20e3, ('Feb', 'breadmakers'): 13e3, ('Feb', 'coffeemakers'): 20e3,
        ('Mar', 'airfryers'): 25e3, ('Mar', 'breadmakers'): 12e3, ('Mar', 'coffeemakers'): 50e3,
        ('Apr', 'airfryers'): 30e3, ('Apr', 'breadmakers'): 11e3, ('Apr', 'coffeemakers'): 10e3,
        ('May', 'airfryers'): 50e3, ('May', 'breadmakers'): 10e3, ('May', 'coffeemakers'): 20e3,
        ('Jun', 'airfryers'): 70e3, ('Jun', 'breadmakers'): 10e3, ('Jun', 'coffeemakers'): 50e3,
        ('Jul', 'airfryers'): 10e3, ('Jul', 'breadmakers'): 10e3, ('Jul', 'coffeemakers'): 10e3,
        ('Aug', 'airfryers'): 12e3, ('Aug', 'breadmakers'): 12e3, ('Aug', 'coffeemakers'): 20e3,
        ('Sep', 'airfryers'): 10e3, ('Sep', 'breadmakers'): 11e3, ('Sep', 'coffeemakers'): 50e3,
        ('Oct', 'airfryers'): 300.2e3, ('Oct', 'breadmakers'): 10.0e3, ('Oct', 'coffeemakers'): 10.0e3,
        ('Nov', 'airfryers'): 20.0e3, ('Nov', 'breadmakers'): 50.4e3, ('Nov', 'coffeemakers'): 20.0e3,
        ('Dec', 'airfryers'): 14.8e3, ('Dec', 'breadmakers'): 10.6e3, ('Dec', 'coffeemakers'): 55.5e3,
    }


# ---- Sets ----
M = range(len(month))  # set of months
P = range(len(productname))  # set of products
O = range(len(productionstep))  # set of production steps

# ---- Variables ----

# Decision Variable x(i,j) (cargo of type in in compartment j)
X1 = {}  # number of products of type p for operation o in month m
for m in M:
    for p in P:
        for o in O:
            X1[m, p, o] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name='X1[' + str(m) + ',' + str(p) + ',' + str(o) + ']')

# X2 = {}
# for m in M:
#     for p in P:
#         for o in O:
#             X2[m, p, o] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name='X2[' + str(m) + ',' + str(p) + ',' + str(o) + ']')

W1 = {}  # inventory finished
for m in M:
    for p in P:
        W1[m, p] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name='W1[' + str(m) + ',' + str(p) + ']')

W2 = {}  # inventory packaged
for m in M:
    for p in P:
        W2[m, p] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name='W2[' + str(m) + ',' + str(p) + ']')


# Integrate new variables
model.update()

# ---- Objective Function ----

model.setObjective(gp.quicksum(
    (holding_costs_finished[p] * W1[m, p]) + (holding_costs_packaged[p] * W2[m, p]) for m in M for p in P))
model.modelSense = GRB.MINIMIZE
model.update()

# ---- Constraints ----

# Constraints 1: demand constraint
# Constraints 1: demand constraint for each month and product
con1 = {}
for m in M:
    for p in P:
        con1[m, p] = model.addConstr(W2[m, p] >= demand[month[m], productname[p]])
    
# Constraints 2: capacity constraint for each production step
con2 = {}
con2[m, o] = model.addConstr(gp.quicksum(time[productname[p], productionstep[o]] * (X1[m, p, o]) for p in P) <= capacity[o])

# Constraints 3: Inventory balance constraint for finished products
con3 = {}
for p in P:
    for m in M:
        if m == 0:
            con3[p, m] = model.addConstr(W1[m, p] == (X1[m, p, 2] - X1[m, p, 3]))
        else:
            con3[p, m] = model.addConstr(W1[m, p] == (X1[m, p, 2] - X1[m, p, 3]))

# Constraints 4: Inventory balance constraint for packaged products
con4 = {}
for p in P:
    for m in M:
        if m == 0:
            con4[m, p] = model.addConstr(W2[m, p] == (X1[m, p, 3] - demand[month[m], productname[p]]))
        else:
            con4[m, p] = model.addConstr(W2[m, p] == ((W2[m - 1, p] + X1[m, p, 3] - demand[month[m], productname[p]])))


# Constraints 5: First three production steps in the same month
con5 = {}
for m in M:
    for p in P:
        con5[p, m, o] = model.addConstr(X1[m, p, 0] == X1[m, p, 1])
        con5[p, m, o] = model.addConstr(X1[m, p, 1] == X1[m, p, 2])


# ---- Solve ----

model.setParam( 'OutputFlag', True) # silencing gurobi output or not
model.setParam ('MIPGap', 0);       # find the optimal solution
model.write("output.lp")            # print the model in .lp format file

model.optimize ()


# --- Print results ---

production_schedule_finished = {}
production_schedule_packaged = {}

if model.status == GRB.Status.OPTIMAL:
    for p in P:
        for m in M:
            if isinstance(W1[m, p], gp.Var):
                production_schedule_finished[(month[m], productname[p])] = W1[m, p].x
            if isinstance(W2[m, p], gp.Var):
                production_schedule_packaged[(month[m], productname[p])] = W2[m, p].x

    # Now you can access the values as a dictionary
    print("\nProduction Schedule for Finished Products:")
    for (m, p), value in production_schedule_finished.items():
        print(f"{m} - {p}: {value}")

    print("\nProduction Schedule for Packaged Products:")
    for (m, p), value in production_schedule_packaged.items():
        print(f"{m} - {p}: {value}")

    print("\nOptimal Total Holding Costs:", model.objVal)
else:
    print('\nNo feasible solution found')


