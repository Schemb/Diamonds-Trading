# Diamonds-Trading

## ROUND 2
## Orchids
When sunlight is less than 7 hours in a day, production will go down by 4% for every 10 minute difference. 
When sunlight > 7, production stays the same.

When the humidity levels are outside the range of 60-80%, production will fall 2% for every 5% humidity change.

Storage - must pay 0.1 seashells per orchid **per timestep**

In the submission logs, sunlight is decreasing throughout the duration of the trading period. This may be beacuse the submission logs only calculate a small fraction of the trading period (only having 100,000 timesteps instead of 1M) 

(1) change the prediction model using sunlight humidity
(2) find the difference in timestamp