#%%
import pypsa
import pandas as pd
import matplotlib.pyplot as plt

#%%
# Create a PyPSA network
network = pypsa.Network()

# Add prices for generation
epex_prices = [0, 2, 4, 8, 10, 8, 6, 4, 2, 0, 2, 4, 8]
intra_prices = [-3, 1, 5, -12, 6, 3, 1, -4, 8, 3, 2, 1, 7]
solar_data = [0, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 0]
# Add network busses
network.add("Bus", "GridBus")
network.add("Bus", "BatteryBus")
network.snapshots = range(len(epex_prices))

#%%
# Add a generator that mimics the epex prices
network.add("Generator",
            "EPEXGenerator",
            bus="GridBus",
            p_nom_extendable = True,
            marginal_cost=epex_prices)  # Operational cost is the electricity price

# Add a generator that mimics the intra-day prices
network.add("Generator",
            "IntraGenerator",
            bus="GridBus",
            p_nom_extendable = True,
            marginal_cost=intra_prices)  # Operational cost is the electricity price


# Add a load to make it all work. give a high load, to ensure there is always enough generation. 
network.add("Load",
            "SampleLoad",
            bus="GridBus",
            p_set = [1000] * len(epex_prices))


# Add battery
network.add("Store",
            "Battery",
            bus="BatteryBus",
            e_nom = 6)


# Charging link
network.add("Link",
            "GridToBatteryLink",
            bus0="GridBus",
            bus1="BatteryBus",
            p_nom=2,                #The maximum capacity of charge/discharge of the battery. 
            efficiency = 1,
            marginal_cost = 0)


# Discharging link
network.add("Link",
            "BatteryToGridLink",
            bus0="BatteryBus",
            bus1="GridBus",
            p_nom=2,                #The maximum capacity of charge/discharge of the battery. 
            efficiency = 1,
            marginal_cost = 0)

# Add solar panels
network.add("Generator",
            "Solar",
            bus="BatteryBus",
            p_nom = 10,
            p_max_pu = solar_data)

#%%
# Run the PyPSA linear optimal power flow (lopf) to optimize arbitrage strategy
network.optimize(solver_name="glpk")  # Use the linear optimal power flow

#%%
df_battery = network.stores_t.p.copy()
df_battery['intra_power'] = network.generators_t.p['IntraGenerator'] - 1000
df_battery['intra_power'][df_battery['intra_power'] == -1000] = 0
df_battery['intra_prices'] = intra_prices
df_battery['intra_income'] = df_battery['intra_power'] * -df_battery['intra_prices'] 

df_battery['epex_power'] = network.generators_t.p['EPEXGenerator'] - 1000
df_battery['epex_power'][df_battery['epex_power'] == -1000] = 0
df_battery['epex_prices'] = epex_prices
df_battery['epex_income'] = df_battery['epex_power'] * -df_battery['epex_prices'] 

df_battery['total_income'] = (df_battery['epex_income'] + df_battery['intra_income']).cumsum()
df_battery[['intra_power', 'intra_prices']].plot()
# Calculate the amount obtained from EPEX and from intra day generator.

df_battery
#%%
#plt.plot(network.stores_t.p, label="Battery")
network.plot()

#%%