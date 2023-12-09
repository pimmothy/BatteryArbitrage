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
solar_data = [0, 0, 0.1, 0.3, 0.5, 0.7, 1, 0.7, 0.5, 0.3, 0.1, 0, 0]

#System parameters
p_battery = 2 #The maximum capacity of the battery.
t_battery = 3 #The total discharge time on total capacity of the battery.
p_solar = 4
connection_battery_control = 2 #The maximum capacity of the connection between battery & control.
connection_grid_control = 2 #The maximum grid connection. 
connection_solar_control = 4 #The connection between solar panels and the controller. 
connection_load_control = 4 #The connection between the load and the controller. 

# Add network busses
network.add("Bus", "ControlBus", x=0, y=0) #This bus is where everything is attached to.
network.add("Bus", "BatteryBus", x=0, y=1) #This bus is responsible for the battery.
network.add("Bus", "GridBus", x=1, y=0) #This bus is responsible for the interaction with the grid.
network.add("Bus", "SolarBus", x=-1, y=0) #This bus is responsible for the interaction with solar panels.
network.add("Bus", "LoadBus", x=0, y=-1) #This bus is responsible for the interaction with the load.
network.snapshots = range(len(epex_prices))

#%%
### ADD GRID ###
# Grid link
network.add("Link",
            "ControlToGridLink",
            bus0="ControlBus",
            bus1="GridBus",
            p_nom=connection_grid_control,                #The grid connection for the energy system. 
            efficiency = 1,
            marginal_cost = 0,
            p_min_pu = -1)

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


### ADD BATTERY ###
# Add battery
network.add("Store",
            "Battery",
            bus="BatteryBus",
            e_nom = p_battery * t_battery)


# Charging link
network.add("Link",
            "ControlToBatteryLink",
            bus0="ControlBus",
            bus1="BatteryBus",
            p_nom=connection_battery_control,              #The maximum capacity of charge/discharge of the battery. 
            efficiency = 1,
            marginal_cost = 0)


# Discharging link
network.add("Link",
            "BatteryToControl",
            bus0="BatteryBus",
            bus1="ControlBus",
            p_nom=connection_battery_control,              #The maximum capacity of charge/discharge of the battery. 
            efficiency = 1,
            marginal_cost = 0)


### ADD SOLAR ###
# Grid link
network.add("Link",
            "SolarToControl", #One direction, solar can only give electricity.
            bus0="SolarBus",
            bus1="ControlBus",
            p_nom=connection_solar_control,                #The grid connection for the energy system. 
            efficiency = 1,
            marginal_cost = 0)

# Add a solar panel generator.
network.add("Generator",
            "Solar",
            bus="SolarBus",
            p_nom = p_solar,
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

df_battery
#%%
#plt.plot(network.stores_t.p, label="Battery")
# Plot the network
fig, ax = plt.subplots(figsize=(8, 6))

for bus_name, (x, y) in network.buses.loc[:, ["x", "y"]].iterrows():
    ax.annotate(bus_name, (x, y), textcoords="offset points", xytext=(0, 5), zorder=10, ha='center', fontsize=8)

network.plot(ax=ax, bus_sizes=0.02, link_widths=1)
plt.show()

# %%
