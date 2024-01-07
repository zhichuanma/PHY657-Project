import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def consumption_cal(V_max, Material, type):
    if type == '350bar':
        df = pd.read_csv('./database/Material_consumption_350bar.csv', index_col= 0)
    if type == '700bar':
        df = pd.read_csv('./database/Material_consumption_700bar.csv', index_col= 0)
    
    model = LinearRegression()
    x = np.array(df.loc['Size of the tank']).reshape((-1,1))
    y = np.array(df.loc[Material])
    model.fit(x, y)

    # Get the slope (beta_1) and y-intercept (beta_0)
    slope = model.coef_
    intercept = model.intercept_
    '''
    # Predicting values
    y_pred = model.predict(x)

    # Plotting
    plt.scatter(x, y, color='blue')
    plt.plot(x, y_pred, color='red')
    plt.title('Linear Regression')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
    '''
    return slope * V_max + intercept

#print(consumption_cal(10, 'Aluminium', '350bar'))

def cost_material_cal(V_max, type):
    if type == '350bar':
        df_price = pd.read_csv('./database/Material_price_350bar.csv', index_col= 0)
    if type == '700bar':
        df_price = pd.read_csv('./database/Material_price_700bar.csv', index_col= 0)
    cost = 0
    for index, row in df_price.iterrows():
        if index == 'Size of the tank':
            continue
        cost = cost + df_price['Price (in USD per kg)'][index] * consumption_cal(V_max, index, type)
    return cost

def cost_total_cal(V_max, type):
    df_cost_frac = pd.read_csv('./database/Cost_frac.csv', index_col= 0)
    cost_total = {'Compressed Vessel': 0, 'Regulator': 0, 'Valves': 0, 'Other BOP': 0, 'Final Assembly & Inspectation': 0}
    cost_total['Compressed Vessel'] = cost_material_cal(V_max, type)
    # Material cost
    for key in cost_total:
        if key == 'Final Assembly & Inspectation':
            continue
        cost_total[key] = cost_total['Compressed Vessel']/df_cost_frac['Material']['Compressed Vessel'] * df_cost_frac.loc[key, 'Material']
    
    # Processing cost
    Compressed_Vessel_process = cost_total['Compressed Vessel'] * 0.04
    cost_total['Compressed Vessel'] = cost_total['Compressed Vessel'] + Compressed_Vessel_process
    cost_total['Final Assembly & Inspectation'] = Compressed_Vessel_process / df_cost_frac.loc['Compressed Vessel', 'processing'] * df_cost_frac.loc['Final Assembly & Inspectation', 'processing']

    return cost_total
    