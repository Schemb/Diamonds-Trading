from screeninfo import get_monitors
import re
import numpy
import matplotlib.pyplot as plt

# Open log file
file = open('visualise.log')

# Assign text to variable
Lines = file.readlines()

# Search for timestamps
timestamp = 'timestamp": '
for line in Lines:
    if timestamp in line:
      nTimestamp = line.split(timestamp,1)

# Log the greatest timestamp
totalTime = int(re.sub("[^0-9]", "",str(nTimestamp)))
print(totalTime)

# Create an array of all the timestamps
timestampsArray = []
for i in range(int(totalTime / 100)):
    timestampsArray.append(i * 100)

# Create an array for the amethyst profit margin
amethystProfitArray = []

# Search for amethyst profit margin
amethystProfit = "Current profit margin for AMETHYSTS is: "
for line in Lines:
    if str(amethystProfit) in line:
        amethystProfit = line.split(amethystProfit,1)
        #amethystProfitArray.append(10002)
        print(amethystProfit[1])

print(numpy.array(amethystProfitArray))

# Create graph
plt.plot([numpy.array(timestampsArray)], [numpy.array(amethystProfitArray)])
plt.xlabel('Timestamps')
plt.ylabel('Amethyst Profit Margins')
plt.show()

# Close log file
file.close()
