from gurobipy import *
# import pandas as pd
# import matplotlib.pyplot as plt
# import math
# from functions import get_results, plot_resulting_routes, read_data

model = Model ('Assignment1')


# ---- Parameters ----
# Characteristics
productname                = ('airfryers', 'breadmakers', 'coffeemakers')
holding_costs_finished     = (800, 1500, 500)            # euro / 1000 products
holding_costs_packaged     = (1000, 1000, 1000)          # euro / 1000 products

productionstep             = ('molding', 'assembling', 'finishing', 'packaging')                   
time_airfryers             = (0.6, 0.8, 0.1, 2.5)        # hours / 1000 products
time_breadmachines         = (1.2, 0.5, 2.0, 2.5)        # hours / 1000 products
time_coffeemakers          = (0.5, 0.1, 0.1, 2.5)        # hours / 1000 products
capacity                   = (80, 100, 100, 250)         # hours

month                      = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')              
demand_airfryer            = (10, 20, 25, 30, 50, 70, 10, 12, 10, 200.2, 20.0, 14.8)    # 1000 products
demand_breadmachines       = (11, 13, 12, 11, 10, 10, 10, 12, 11, 10.0, 50.4, 10.6)     # 1000 products
demand_coffeemakers        = (10, 20, 50, 10, 20, 50, 10, 20, 50, 10.0, 20.0, 55.5)     # 1000 products
demand = {
    ("airfryers"): [10, 20, 25, 30, 50, 70, 10, 12, 10, 200.2, 20.0, 14.8],
    ("breadmachines"): [11, 13, 12, 11, 10, 10, 10, 12, 11, 10.0, 50.4, 10.6],
    ("coffeemakers"): [10, 20, 50, 10, 20, 50, 10, 20, 50, 10.0, 20.0, 55.5]
}

# demand = {(10, 20, 25, 30, 50, 70, 10, 12, 10, 200.2, 20.0, 14.8)
#          (11, 13, 12, 11, 10, 10, 10, 12, 11, 10.0, 50.4, 10.6)
#          (10, 20, 50, 10, 20, 50, 10, 20, 50, 10.0, 20.0, 55.5) 
#    }
# ---- Sets ----

P = range(len(productname))               # set of products
O = range(len(productionstep))            # set of production steps
M = range(len(month))                     # set of months

# ---- Variables ----

# Decision Variable x(i,j) (cargo of type in in compartment j)
X1 = {}                             # number of products of type p for operation o in month m
for m in M:
    for p in P:
        for o in range(1,4):
            X1[m,p,o] = model.addVar (lb = 0, vtype = GRB.CONTINUOUS, name = 'X1[' + str(m) + ',' + str(p) + ',' + str(o) +  ']')
        
X2 = {}
for m in M:
    for p in P:
        for o in O:
            X2[m,p,o] = model.addVar (lb = 0, vtype = GRB.CONTINUOUS, name = 'X2[' + str(m) + ',' + str(p) + ',' + str(o) +  ']')

W1 = {}
for m in M:
    for p in P:
        for o in O:
            W1[m,p,o] = model.addVar (lb = 0, vtype = GRB.CONTINUOUS, name = 'W1[' + str(m) + ',' + str(p) + ',' + str(o) +  ']')                            

W2 = {}   
for m in M:
    for p in P:
        for o in O:
            W2[m,p,o] = model.addVar (lb = 0, vtype = GRB.CONTINUOUS, name = 'W2[' + str(m) + ',' + str(p) + ',' + str(o) +  ']')


# Integrate new variables
model.update ()


# ---- Objective Function ----

model.setObjective (quicksum ((holding_costs_finished[p] * W1[m,p,o])+(holding_costs_packaged[p] * W2[m,p,o]) for m in M for p in P for o in O) )
model.modelSense = GRB.MINIMIZE
model.update ()

# ---- Constraints ----

# Constraints 1: demand constraint
con1 = {}
for m in M:
    for p in P:
        con1[m,p] = model.addConstr(quicksum (X2[m,p,o] + W2[m,p,o] for o in O) >= demand[m])
     
# Constraints 2: capacity constraint
con2 = {}
for o in range (1,4):
     con2[o] = model.addConstr(quicksum (time[p, o / 1000] * X1[m,p,o] for m in M for p in P) <= capacity[o])

# Constraints 3: inventory balance constraint packaged products
con3 = {}
for p in P:
    for m in M:
        if m == 1:
            con3[p,m] = model.addConstr(W2[p, m] == W2[p, m-1] + X2[m,p,o] + X1[m-1,p,o] - demand[p,m])
           
# Constraints 4: inventory balance constraint finished products
con4 = {}
for p in P:
    for m in M:
        if m == 1:
            con4[p,m] = model.addConstr(W1[p, m] == X1[m,p,o]) 
                                        
# Constraint 5, 6, 7, 8: non-negativity constraint
con5 = {}
for p in P:
    for m in M:
        for o in O:
            con5[p,o,m] = model.addConstr(X1[m,p,o] >= 0)
            
con6 = {}
for p in P:
    for m in M:
        for o in O:
            con6[p,o,m] = model.addConstr(X2[m,p,o] >= 0)

con7 = {}
for p in P:
    for m in M:
        for o in O:
            con7[p,o,m] = model.addConstr(W1[m,p,o] >= 0)
            
con8 = {}
for p in P:
    for m in M:
        for o in O:
            con8[p,o,m] = model.addConstr(W2[m,p,o] >= 0)
        

# ---- Solve ----

model.setParam( 'OutputFlag', True) # silencing gurobi output or not
model.setParam ('MIPGap', 0);       # find the optimal solution
model.write("output.lp")            # print the model in .lp format file

model.optimize ()


# --- Print results ---
print ('\n--------------------------------------------------------------------\n')
    
if model.status == GRB.Status.OPTIMAL: # If optimal solution is found
    print ("Optimal Objective Value:", model.objVal)

    for p in P:
        for m in M:
            print(f"X_{p}_{m}: {X[p, m].x}")
  

else:
    print ('\nNo feasible solution found')

print ('\nREADY\n')

