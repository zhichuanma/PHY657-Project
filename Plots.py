from pulp import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from Func import *
df = pd.read_csv('./database/Weekly_data.csv')
Price = df['Price (EUR/MWhe)']
time_periods = df["Datetime (Local)"]
def Cost_Calculating(V_max, type, time_scale):
    if time_scale == 'Weekly':
        df = pd.read_csv("./database/Weekly_data.csv")

    elif time_scale == 'Monthly':
        df = pd.read_csv("./database/Monthly_data.csv")

    elif time_scale == 'Yearly':
        df = pd.read_csv("./database/Yearly_data.csv")

    else:
        print('wrong input')
        return 0
    
    # Calculate fixed cost firstly
    fixed_cost = cost_total_cal(V_max, type)
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
    eff_SOEC = 39.82 * 0.08 * 0.9  #39.82's unit is MWh/kg
    eff_SOFC = 27 * 0.08 * 0.9  # 27's unit is MWh/kg

    P_SOEC = 1 # MW
    P_SOFC = 1 # MW
    Price = df['Price (EUR/MWhe)']

    # Elementary features:

    lp = LpProblem("Cost_Calculating", LpMinimize)

    # Define variables
    x1 = {t: LpVariable(f"x1_{t}", cat="Binary") for t in time_periods}
    x2 = {t: LpVariable(f"x2_{t}", cat="Binary") for t in time_periods}
    E_in = {t: LpVariable(f"E_in_{t}",lowBound=0, cat="Continuous") for t in time_periods}
    E_out = {t: LpVariable(f"E_out_{t}",lowBound=0, cat="Continuous") for t in time_periods}
    C = {t: LpVariable(f"C_{t}", lowBound=0.05 * V_max, cat="Continuous") for t in time_periods}
    V = {t: LpVariable(f"V_{t}", cat="Continuous") for t in time_periods}

    # Add the objective function
    objective_function = fixed_cost + lpSum(Price[t] * (E_in[t] - E_out[t]) for t in time_periods)
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
    lp += C[time_periods[0]] == 0.05 * V_max, f"Initial_condition_rule_t{t}"

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
    solver = PULP_CBC_CMD(timeLimit=20)

    # Solve the problem
    lp.solve(solver)

    # Print solver status
    print("Solver Status:", LpStatus[lp.status])

    # Print optimal values of decision variables
    
    C_temp = []

    for t in time_periods:
        C_temp.append(pulp.value(C[t]))
        print(f"Time {t}: x1={pulp.value(x1[t])}, x2={pulp.value(x2[t])}, C={pulp.value(C[t])}, V={pulp.value(V[t])}, E_in={pulp.value(E_in[t])}, E_out={pulp.value(E_out[t])}")

    # Print optimal objective value
    print("Optimal Objective Value:", pulp.value(lp.objective))
    return C_temp

costs = Cost_Calculating(1.5, '350bar', 'Weekly')

# Plotting
fig, ax1 = plt.subplots(figsize=(15, 7))  # Set the figure size as desired

# Plot Costs on the primary y-axis
cost_line, = ax1.plot(time_periods, costs, 'b-o', label='Volume in tank (m³)', markersize=5, linewidth=2)  # Blue color with circle markers
ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Volume in tank (m³)', color='b')
ax1.tick_params('y', colors='b')
ax1.set_xticks(time_periods[::4])  # Set x-ticks to every fourth hour for clarity
ax1.set_xticklabels(time_periods[::4], rotation=45, ha='right')  # Rotate x-axis labels for better visibility

# Create a second y-axis for Prices
ax2 = ax1.twinx()
price_line, = ax2.plot(time_periods, Price, 'r-s', label='Price (EUR/MWhe)', markersize=5, linewidth=2)  # Red color with square markers
ax2.set_ylabel('Price (EUR/MWhe)', color='r')
ax2.tick_params('y', colors='r')

# Add grid to the plot for better readability
ax1.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# Set plot title with a font size
ax1.set_title('Hydrogen Volume in the Tank and Price over Time', fontsize=16)

# Add legend
lines = [cost_line, price_line]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc='best', framealpha=1)

# Adjust layout to prevent clipping of labels and ensure everything fits
fig.tight_layout()

# Show the plot
plt.show()