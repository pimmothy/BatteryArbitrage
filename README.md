# BatteryArbitrage


# TODO:
1. Immplement that the battery link from and to control together cannot surpass the total grid connection.
2. Implement transport tariffs
3. Improve on battery characteristics (efficiency). 
4. Implement a better strategy to determine added value of solar
    - The load must always be satisfied. When solar is given to the grid (via control) it receives the epex prices at that moment. If the solar panel deliver electricity to the battery, it avoid the costs of the grid. However, the solar energy could be sold to the grid for that price. However, the transport tarif is avoided this way. 
5. Include a load profile of a house.
6. Backtest potential revenue per day of a battery using real data
    - Implement real epex prices. 
    - Implement real intra-day prices.
    - Implement real imbalance prices.
7. Look into the added value of solar curtailment.

