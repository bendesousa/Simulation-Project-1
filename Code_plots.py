import random
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Parameters
AVG_SPEED = 20
Termination = 100
Rider_arrival_rate = 30
Driver_arrival_rate = 3

#########Random Simulation
#Classes
class Rider:
    def __init__(self, r_id, time):
        self.id = r_id
        self.request_time = time
        self.origin = (random.uniform(0,20), random.uniform(0,20))
        self.destination = (random.uniform(0,20), random.uniform(0,20))
        self.pickup_time = None
        self.dropoff_time = None
        self.patience_deadline = time + random.expovariate(5)

class Driver:
    def __init__(self, d_id, time):
        self.id = d_id
        self.location = (random.uniform(0,20), random.uniform(0,20))
        self.offline_time = time + random.uniform(5,8)
        self.available = True
        self.income = 0
        
        self.arrival_time = time
        self.busy_time = 0

#Helper Functions
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def travel_time(dist):
    mean_time = dist / AVG_SPEED
    return random.uniform(0.8 * mean_time, 1.2 * mean_time)

#Matching function
def attempt_match():
    global idle_drivers, waiting_riders, TNOW
    while idle_drivers and waiting_riders:
        #FIFO
        rider = waiting_riders.pop(0)
        B1[rider.id] = 0  # mark as matched
        #Find closest driver
        driver = min(idle_drivers, key=lambda d: distance(d.location, rider.origin))
        idle_drivers.remove(driver)
        driver.available = False
        B2[driver.id] = 0  # mark as matched
        #Travel distance to pickup
        d = distance(driver.location, rider.origin)
        pickup_time = TNOW + travel_time(d)
        EC[3].append((pickup_time, rider.id, driver.id))
        match[rider.id] = driver.id

#System State
TNOW = 0
Q =0

drivers= {}
riders = {}

X1=[]   #X coordinate of customers
Y1=[]   #Y coordinate of customers
X2=[]   #X coordinate of drivers
Y2=[]   #Y coordinate of drivers

#Indices of which taxis/customers are looking for a match
B1=[]   #Customers
B2=[]   #Taxis

#indices of taxis corresponding to each customer
#index in the i_th place is the taxi for the i_th customer
match=[]

idle_drivers = []
waiting_riders = []

next_driver_id = 0
next_rider_id = 0

#Event calendar
# EC[0] = next rider arrival
# EC[1] = list of rider impatience times
# EC[2] = next driver arrival
# EC[3] = list of pickup times
# EC[4] = list of dropoff times
# EC[5] = list of driver offline times
# EC[6] = termination time
EC = [0, [], 0, [], [], [], Termination]
EC[0] = random.expovariate(Rider_arrival_rate)
EC[2] = random.expovariate(Driver_arrival_rate)

#Times and total riders currently in the system
system_rider_times=[]
system_rider_counts=[]
current_riders=0

#Times and total riders in the system who left due to impatience
rider_abandonments_times=[]
rider_abandonments_counts=[]
current_abandonments=0

#Times and total drivers currently in the system
system_driver_times=[]
system_driver_counts=[]
current_drivers=0

#Times each rider was waiting
waiting_times=[]

#Times each driver was resting
resting_times = []

#Simulation Loop
while TNOW < Termination:
    #Identify next event
    TNEXT = EC[0]
    event  = 'rider_arrival'
    
    if EC[1] and min(EC[1])[0] < TNEXT:
        TNEXT = min(EC[1])[0]
        event  = 'abandon'

    if EC[2] < TNEXT:
        TNEXT = EC[2]
        event  = 'driver_arrival'    

    if EC[3] and min(EC[3])[0] < TNEXT:
        TNEXT = min(EC[3])[0]
        event  = 'pickup'

    if EC[4] and min(EC[4])[0] < TNEXT:
        TNEXT = min(EC[4])[0]
        event  = 'dropoff'

    if EC[5] and min(EC[5])[0] < TNEXT:
        TNEXT = min(EC[5])[0]
        event  = 'driver_offline'

    if EC[6] < TNEXT:
        TNEXT = EC[6]
        event  = 'termination'

    TNOW = TNEXT

    #Event handling
    if event == 'rider_arrival':
        #Creating the rider
        r = Rider(next_rider_id, TNOW)
        riders[next_rider_id] = r
        waiting_riders.append(r)
        #Starting location
        X1.append(r.origin[0])
        Y1.append(r.origin[1])
        B1.append(1)
        match.append(None)
        #Abandonment time
        EC[1].append((r.patience_deadline, next_rider_id))
        #Updating the EC
        next_rider_id += 1
        EC[0] = TNOW + random.expovariate(30)
        attempt_match()
        
        current_riders += 1
        system_rider_times.append(TNOW)
        system_rider_counts.append(current_riders)
    
    elif event == "abandon":
        event = min(EC[1])
        EC[1].remove(event)
        #Assinging time and rider to event
        _, r_id = event
        #If pickup time is not at TNOW
        if riders[r_id].pickup_time is None:
            if any(r.id == r_id for r in waiting_riders):
                B1[r_id] = 0
                #Removing abandoning rider from the waiting list
                waiting_riders = [r for r in waiting_riders if r.id != r_id]
            
                current_riders -= 1
                system_rider_times.append(TNOW)
                system_rider_counts.append(current_riders)
                
                current_abandonments += 1
                rider_abandonments_times.append(TNOW)
                rider_abandonments_counts.append(current_abandonments)

    elif event == "driver_arrival":
        #Creating the driver
        d = Driver(next_driver_id, TNOW)
        drivers[next_driver_id] = d
        #Starting location
        X2.append(d.location[0])
        Y2.append(d.location[1])
        B2.append(1)
        #Adding to idle list
        idle_drivers.append(d)
        #Adding their offline time
        EC[5].append((d.offline_time, next_driver_id))
        next_driver_id += 1
        Q += 1
        #Updating the event calendar
        EC[2] = TNOW + random.expovariate(3)
        attempt_match()
        
        current_drivers += 1
        system_driver_times.append(TNOW)
        system_driver_counts.append(current_drivers)

    elif event == "pickup":
        event = min(EC[3])
        EC[3].remove(event)
        #Assinging the correct driver and rider to the event
        _, r_id, d_id = event
        r = riders[r_id]
        d = drivers[d_id]
        r.pickup_time = TNOW
        #Setting the trip distance
        trip_dist = distance(r.origin, r.destination)
        t_dropoff = TNOW + travel_time(trip_dist)
        #Updating the event calendar
        EC[4].append((t_dropoff, r_id, d_id, trip_dist))
        
        waiting_times.append(TNOW - r.request_time)
    
    elif event == "dropoff":
        event = min(EC[4])
        EC[4].remove(event)
        #Matching ids, time and distance to the event
        _, r_id, d_id, dist = event
        r = riders[r_id]
        d = drivers[d_id]
        r.dropoff_time = TNOW
        
        d.busy_time+=TNOW-r.pickup_time
        
        #Calculating financials
        fare = 3 + 2*dist
        cost = 0.2*dist
        d.income += (fare - cost)
        #Updating driver status and location
        d.location = r.destination
        B2[d_id] = 1
        idle_drivers.append(d)
        attempt_match()
        
        current_riders -= 1
        system_rider_times.append(TNOW)
        system_rider_counts.append(current_riders)

    elif event == 'driver_offline':
        #Taking the first event in the list of driver offline times
        event = min(EC[5])
        EC[5].remove(event)
        _, d_id = event
        #Updating driver status
        B2[d_id] = 0
        #Removing driver from idle list if they are in it
        idle_drivers = [drv for drv in idle_drivers if drv.id != d_id]
        
        current_drivers -= 1
        system_driver_times.append(TNOW)
        system_driver_counts.append(current_drivers)

    elif event == "termination":
        break

#Results
#Calculating which riders were served and which abandoned based on pickup and dropoff times
served = [r for r in riders.values() if r.dropoff_time]
abandoned = [r for r in riders.values() if r.pickup_time is None]

# Rider financials
total_revenue = 0
for r in served:
    trip_dist = distance(r.origin, r.destination)
    fare = 3 + 2*trip_dist
    total_revenue += fare
avg_revenue_per_rider = total_revenue / len(served) if served else 0

# Driver financials
total_driver_income = sum(d.income for d in drivers.values())
avg_net_income_per_driver = total_driver_income / len(drivers) if drivers else 0

# Additional metrics
abandonment_rate = len(abandoned)/len(riders) if riders else 0
revenue_per_hour = total_revenue / Termination

print("Total Riders:", len(riders))
print("Served Riders:", len(served))
print("Abandoned Riders:", len(abandoned))
print(f"Rider abandonment rate: {abandonment_rate*100:.2f}%")
print(f"Total revenue: £{total_revenue:.2f}")
print(f"Average revenue per served rider: £{avg_revenue_per_rider:.2f}")
print(f"Total driver income: £{total_driver_income:.2f}")
print(f"Average net income per driver: £{avg_net_income_per_driver:.2f}")
print(f"Revenue per hour of simulation: £{revenue_per_hour:.2f}")

#Make plots
plt.figure()
plt.step(system_rider_times, system_rider_counts, where='post')
plt.xlabel("Time")
plt.ylabel("Number of Customers in System")
plt.title("Customers in System Over Time")
plt.show()

plt.figure()
plt.step(rider_abandonments_times, rider_abandonments_counts, where='post')
plt.xlabel("Time")
plt.ylabel("Number of Customers who abandon")
plt.title("Abandonments from the System Over Time")
plt.show()

plt.figure()
plt.hist(waiting_times, bins=50)
plt.xlabel("Rider Waiting Time for Pickup")
plt.ylabel("Number of Riders")
plt.title("Distribution of Rider Waiting Times")
plt.show()

plt.figure()
plt.step(system_driver_times, system_driver_counts, where='post')
plt.xlabel("Time")
plt.ylabel("Number of Drivers in System")
plt.title("Drivers in System Over Time")
plt.show()

driver_incomes = [d.income for d in drivers.values()]
plt.figure()
plt.hist(driver_incomes, bins=len(driver_incomes))
plt.xlabel("Driver Net Income (£)")
plt.ylabel("Number of Drivers")
plt.title("Number of Drivers by Income Level")
plt.show()

for d in drivers.values():
    active_time=d.offline_time-d.arrival_time
    rest_time=active_time-d.busy_time
    if rest_time>=0:
        resting_times.append(rest_time)
        
plt.figure()
plt.hist(resting_times, bins=50)
plt.xlabel("Driver Resting Time")
plt.ylabel("Number of Drivers")
plt.title("Distribution of Driver Resting Time")
plt.show()

# #########Data Driven Simulation
# # Data Preparation
# rider_df  = pd.read_excel("riders.xlsx")
# driver_df = pd.read_excel("drivers.xlsx")

# def parse_location(loc_string):
#     x, y = loc_string.strip("()").split(",")
#     return (float(x), float(y))

# class Rider:
#     def __init__(self, r_id, row):
#         self.id = r_id
#         self.request_time = row["request_time"]
#         self.origin = parse_location(row["pickup_location"])
#         self.destination = parse_location(row["dropoff_location"])

#         # Use the actual data for pickup/dropoff
#         self.pickup_time = None if pd.isna(row["pickup_time"]) else row["pickup_time"]
#         self.dropoff_time = None if pd.isna(row["dropoff_time"]) else row["dropoff_time"]

#         # Use the status in the data
#         self.status = row["status"]

# class Driver:
#     def __init__(self, d_id, row):
#         self.id = d_id
#         self.location = parse_location(row["initial_location"])
#         self.available_time = row["arrival_time"]
#         self.offline_time = row["offline_time"]
#         self.available = True
#         self.income = 0

# #Helper Functions
# def distance(a, b):
#     return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# #System State

# drivers= {}
# riders = {}

# X1=[]   #X coordinate of customers
# Y1=[]   #Y coordinate of customers
# X2=[]   #X coordinate of drivers
# Y2=[]   #Y coordinate of drivers

# #Indices of which taxis/customers are looking for a match
# B1=[]   #Customers
# B2=[]   #Taxis

# for i, row in rider_df.iterrows():
#     if str(row["status"]).strip().lower() == "pickup-scheduled":
#         continue  # Skip riders who haven't started
#     r = Rider(i, row)
#     riders[i] = r
#     X1.append(r.origin[0])
#     Y1.append(r.origin[1])
#     B1.append(1)

# for i, row in driver_df.iterrows():
#     d = Driver(i, row)
#     drivers[i] = d
#     X2.append(d.location[0])
#     Y2.append(d.location[1])
#     B2.append(1)

# # Map dataset status to KPIs
# served_statuses = ["dropoff-scheduled", "dropped-off"]
# abandoned_statuses = ["abandoned"]

# served = [r for r in riders.values() if str(r.status).strip().lower() in served_statuses]
# abandoned = [r for r in riders.values() if str(r.status).strip().lower() in abandoned_statuses]
# # Rider financials
# total_revenue = 0
# for r in served:
#     trip_dist = distance(r.origin, r.destination)
#     fare = 3 + 2 * trip_dist
#     total_revenue += fare
# avg_revenue_per_rider = total_revenue / len(served) if served else 0

# # Rider waiting time
# waiting_times = [r.pickup_time - r.request_time for r in served if r.pickup_time]
# avg_waiting_time = sum(waiting_times)/len(waiting_times) if waiting_times else 0

# # Driver financials
# # Assign income only for served trips
# total_driver_income = sum((3 + 2 * distance(r.origin, r.destination)) * 0.8 for r in served)
# avg_net_income_per_driver = total_driver_income / len(drivers) if drivers else 0

# # Driver earnings per hour
# driver_hours = [(d.offline_time - d.available_time) for d in drivers.values()]
# avg_earnings_per_hour = total_driver_income / sum(driver_hours) if sum(driver_hours) > 0 else 0

# # Fairness (income variability)
# incomes = [d.income for d in drivers.values()]
# fairness = np.std(incomes) if incomes else 0

# # Additional metrics
# abandonment_rate = len(abandoned) / len(riders) if riders else 0
# revenue_per_hour = total_revenue / Termination

# #Results
# print("Total Riders:", len(riders))
# print("Served Riders:", len(served))
# print("Abandoned Riders:", len(abandoned))
# print(f"Rider abandonment rate: {abandonment_rate*100:.2f}%")
# print(f"Average rider waiting time: {avg_waiting_time:.2f}")
# print(f"Total revenue: £{total_revenue:.2f}")
# print(f"Average revenue per served rider: £{avg_revenue_per_rider:.2f}")
# print(f"Total driver income: £{total_driver_income:.2f}")
# print(f"Average net income per driver: £{avg_net_income_per_driver:.2f}")
# print(f"Average earnings per driver per hour: £{avg_earnings_per_hour:.2f}")
# print(f"Driver income fairness (std dev): £{fairness:.2f}")
# print(f"Revenue per hour of simulation: £{revenue_per_hour:.2f}")

# #Make plots
# plt.figure()
# plt.hist(waiting_times, bins=50)
# plt.xlabel("Rider Waiting Time")
# plt.ylabel("Number of Riders")
# plt.title("Distribution of Rider Waiting Times")
# plt.show()

# plt.figure()
# plt.hist(incomes, bins=50)
# plt.xlabel("Driver Net Income (£)")
# plt.ylabel("Number of Drivers")
# plt.title("Distribution of Driver Incomes")
# plt.show()
