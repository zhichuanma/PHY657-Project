from pulp import *
import pandas as pd

df = pd.read_csv("./database/Weekly_data.csv")

# Define the time period
time_periods = df["Datetime (Local)"]

# Define parameters
'''
The eff_SOEC's and eff_SOFC'S units are both MWh/m^3
it means the quantity of electricity energy input in a return of 1 m^3 hydrogen gas,
taking into consideration of the efficiency
the desity of hydrogen: 0.08 kg/m^3
transfer efficiency: 90%
'''
# eff_SOEC = 39.82 * 0.08 * 0.9 * 0.001 #39.82's unit is kWh/kg
# eff_SOFC = 27 * 0.08 * 0.9 * 0.001 # 27's unit is kWh/kg
eff_SOEC = 1 #39.82's unit is kWh/kg
eff_SOFC = 1 # 27's unit is kWh/kg
V_max = 5
P_SOEC = 1
P_SOFC = 1 
Price = df['Price (EUR/MWhe)']
M = 1000
# Elementary features:

lp = LpProblem("Profit_making", LpMinimize)

# Define variables
x1 = {t: LpVariable(f"x1_{t}", cat="Binary") for t in time_periods}
x2 = {t: LpVariable(f"x2_{t}", cat="Binary") for t in time_periods}
E_in = {t: LpVariable(f"E_in_{t}",lowBound=0, cat="Continuous") for t in time_periods}
E_out = {t: LpVariable(f"E_out_{t}",lowBound=0, cat="Continuous") for t in time_periods}
C = {t: LpVariable(f"C_{t}", lowBound=0, cat="Continuous") for t in time_periods}
V = {t: LpVariable(f"V_{t}", cat="Continuous") for t in time_periods}

# Add the objective function
objective_function = 287.93 * V_max * 1.3 + lpSum(Price[t] * (E_in[t] - E_out[t]) for t in time_periods)
lp += objective_function

# Working mode rule
for t in time_periods:
    lp += x1[t] + x2[t] <= 1, f"working_mode_rule_t{t}"

# Power_limit1_rule
for t in time_periods:
   lp += E_in[t] <= P_SOEC * x1[t], f"Power_limit1_rule_t{t}"

# Power_limit2_rule
for t in time_periods:
   lp += E_out[t] <= P_SOFC * x2[t], f"Power_limit2_rule_t{t}"

# Initial_condition_rule
lp += C[time_periods[0]] == 0, f"Initial_condition_rule_t{t}"

# Cumulative_gas_rule
for t in time_periods:
   lp += V[t] == E_in[t]*eff_SOEC - E_out[t]*1/eff_SOFC

for t in time_periods:
    if t >= 1:
        lp += C[t] == C[t-1] + V[t-1], f"Cumulative_gas_rule_t{t}"

# Volume_constraint_rule
for t in time_periods:
   lp += C[t] <= V_max, f"Volume_constraint_rule_t{t}"

# Set a time limit
solver = PULP_CBC_CMD(timeLimit=1800)

# Solve the problem
lp.solve(solver)

# Print solver status
print("Solver Status:", LpStatus[lp.status])

# Print optimal values of decision variables
for t in time_periods:
    print(f"Time {t}: x1={pulp.value(x1[t])}, x2={pulp.value(x2[t])}, C={pulp.value(C[t])}, V={pulp.value(V[t])}, E_in={pulp.value(E_in[t])}, E_out={pulp.value(E_out[t])}")

# Print optimal objective value
print("Optimal Objective Value:", pulp.value(lp.objective))