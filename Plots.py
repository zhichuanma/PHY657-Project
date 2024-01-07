import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Func import *
from main import Cost_Calculating

df = pd.read_csv("./database/Weekly_data.csv")
Price = df['Price (EUR/MWhe)']


costs = Cost_Calculating(50, '350bar', time_scale = 'Weekly')
C_max = max(costs[1])
time_periods = df["Datetime (Local)"]

# print(C_max/2)
# print(costs)

# Create a figure and a set of subplots
fig, ax1 = plt.subplots()

# Plotting the first curve
color = 'tab:red'
ax1.set_xlabel('time')
ax1.set_ylabel('C', color=color)
ax1.plot(time_periods, costs, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Instantiate a second axes that shares the same x-axis
ax2 = ax1.twinx()  

# Plotting the second curve
color = 'tab:blue'
ax2.set_ylabel('Price', color=color)  # we already handled the x-label with ax1
ax2.plot(time_periods, Price, color=color)
ax2.tick_params(axis='y', labelcolor=color)

# Adding titles and grid
plt.title('elec_price & C')
ax1.grid(True)

# Show the plot
plt.show()