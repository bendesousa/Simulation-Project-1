import random
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# #Parameters
AVG_SPEED = 20
Termination = 100
Rider_arrival_rate = 30
Driver_arrival_rate = 3
Rider_patience_rate = 5

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
        self.patience_deadline = time + random.expovariate(Rider_patience_rate)

class Driver:
    def __init__(self, d_id, time):
        self.id = d_id
        self.location = (random.uniform(0,20), random.uniform(0,20))
        # self.online_time = time
        self.arrival_time = time  
        self.offline_time = time + random.uniform(5,8)
        self.available = True
        self.income = 0
        self.busy_time = 0
        # self.busy_start = None

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
        # driver.available = TNOW
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
        EC[0] = TNOW + random.expovariate(Rider_arrival_rate)
        attempt_match()

        current_riders += 1
        system_rider_times.append(TNOW)
        system_rider_counts.append(current_riders)
    
    elif event == "abandon":
        event = min(EC[1])
        EC[1].remove(event)
        #Assigning time and rider to event
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
        EC[2] = TNOW + random.expovariate(Driver_arrival_rate)
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
        # d.busy_time += TNOW - d.busy_start
        # d.busy_start = None
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

# rider time stats
total_system_t = 0
total_waiting_t = 0
for r in riders.values():
    if r.pickup_time is None:
        total_system_t += r.patience_deadline - r.request_time
        total_waiting_t += r.patience_deadline - r.request_time
    elif r.dropoff_time is None:
        total_system_t += Termination - r.request_time
        total_waiting_t += r.pickup_time - r.request_time
    else:
        total_system_t += r.dropoff_time - r.request_time
        total_waiting_t += r.pickup_time - r.request_time
rider_satisfaction_score = 100 * (1 - (total_waiting_t/total_system_t))

# Driver financials
total_driver_income = sum(d.income for d in drivers.values())
avg_net_income_per_driver = total_driver_income / len(drivers) if drivers else 0
total_driver_worktime = sum(d.offline_time - d.arrival_time for d in drivers.values())
avg_hourly_driver_income = np.mean([d.income / (d.offline_time - d.arrival_time) for d in drivers.values()])
range_hourly_driver_income = max(d.income / (d.offline_time - d.arrival_time) for d in drivers.values()) - min(d.income / (d.offline_time - d.arrival_time) for d in drivers.values())
avg_break_time = np.mean([
    (d.offline_time - d.arrival_time - d.busy_time) /
    (d.offline_time - d.arrival_time)
    for d in drivers.values()
])
driver_satisfaction_score = avg_hourly_driver_income + (avg_hourly_driver_income * avg_break_time) - range_hourly_driver_income

# Additional metrics
abandonment_rate = len(abandoned)/len(riders) if riders else 0
revenue_per_hour = total_revenue / Termination

print("----- Given Parameters Random Simulation -----")
print("Total Riders:", len(riders))
print("Served Riders:", len(served))
print("Abandoned Riders:", len(abandoned))
print(f"Rider abandonment rate: {abandonment_rate*100:.2f}%")
print(f"Total revenue: £{total_revenue:.2f}")
print(f"Average revenue per served rider: £{avg_revenue_per_rider:.2f}")
print(f"Total driver income: £{total_driver_income:.2f}")
print(f"Average net income per driver: £{avg_net_income_per_driver:.2f}")
print(f"Revenue per hour of simulation: £{revenue_per_hour:.2f}")
print(f"Rider Satisfaction Score {rider_satisfaction_score:.3f}")
print(f"Driver Satisfaction Score: {driver_satisfaction_score:.3f}")
print(f"Avg Driver Income/hr: £{avg_hourly_driver_income}")
print(f"Max Driver Income/hr: £{max(d.income / (d.offline_time - d.arrival_time) for d in drivers.values())}")
print(f"Min Driver Income/hr: £{min(d.income / (d.offline_time - d.arrival_time) for d in drivers.values())}")
print(f"Avg Driver Break Time: {avg_break_time}")

#Make plots
plt.figure()
plt.step(system_rider_times, system_rider_counts, where='post')
plt.xlabel("Time")
plt.ylabel("Number of Customers in System")
plt.title("Customers in System Over Time")
plt.savefig('customers_in_system.png')
plt.show()

plt.figure()
plt.step(rider_abandonments_times, rider_abandonments_counts, where='post')
plt.xlabel("Time")
plt.ylabel("Number of Customers who abandon")
plt.title("Abandonments from the System Over Time")
plt.savefig('abandonments_over_time.png')
plt.show()

plt.figure()
plt.hist(waiting_times, bins=50)
plt.xlabel("Rider Waiting Time for Pickup")
plt.ylabel("Number of Riders")
plt.title("Distribution of Rider Waiting Times")
plt.savefig('waiting_times.png')
plt.show()

plt.figure()
plt.step(system_driver_times, system_driver_counts, where='post')
plt.xlabel("Time")
plt.ylabel("Number of Drivers in System")
plt.title("Drivers in System Over Time")
plt.savefig('drivers_in_system.png')
plt.show()

driver_incomes = [d.income for d in drivers.values()]
plt.figure()
plt.hist(driver_incomes, bins=len(driver_incomes))
plt.xlabel("Driver Net Income (£)")
plt.ylabel("Number of Drivers")
plt.title("Number of Drivers by Income Level")
plt.savefig('driver_incomes.png')
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
plt.title("Adjusted Distribution of Driver Resting Time")
plt.savefig('resting_times.png')
plt.show()

# #########Deterministic Simulation
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

# # Results
# served = [r for r in riders.values() if str(r.status).strip().lower() in served_statuses]
# abandoned = [r for r in riders.values() if str(r.status).strip().lower() in abandoned_statuses]

# # Rider financials
# total_revenue = 0
# for r in served:
#     trip_dist = distance(r.origin, r.destination)
#     fare = 3 + 2*trip_dist
#     total_revenue += fare
# avg_revenue_per_rider = total_revenue / len(served) if served else 0

# # rider time stats
# # total_system_t = 0
# # total_waiting_t = 0
# # for r in riders.values():
# #     if r.pickup_time is None:
# #         total_system_t += r.patience_deadline - r.request_time
# #         total_waiting_t += r.patience_deadline - r.request_time
# #     elif r.dropoff_time is None:
# #         total_system_t += Termination - r.request_time
# #         total_waiting_t += r.pickup_time - r.request_time
# #     else:
# #         total_system_t += r.dropoff_time - r.request_time
# #         total_waiting_t += r.pickup_time - r.request_time
# # rider_satisfaction_score = 100 * (1 - (total_waiting_t/total_system_t))

# # Driver financials
# # total_driver_income = sum(d.income for d in drivers.values())
# # avg_net_income_per_driver = total_driver_income / len(drivers) if drivers else 0
# # total_driver_worktime = sum(d.offline_time - d.available_time for d in drivers.values())
# # avg_hourly_driver_income = np.mean([d.income / (d.offline_time - d.available_time) for d in drivers.values()])
# # range_hourly_driver_income = max(d.income / (d.offline_time - d.available_time) for d in drivers.values()) - min(d.income / (d.offline_time - d.available_time) for d in drivers.values())
# # avg_break_time = np.mean([
# #     (d.offline_time - d.available_time - d.busy_time) /
# #     (d.offline_time - d.available_time)
# #     for d in drivers.values()
# # ])
# # driver_satisfaction_score = avg_hourly_driver_income + (avg_hourly_driver_income * avg_break_time) - range_hourly_driver_income

# # Additional metrics
# abandonment_rate = len(abandoned)/len(riders) if riders else 0
# revenue_per_hour = total_revenue / Termination

# waiting_times = []
# for r in riders.values():
#     if r.status in served_statuses:
#         waiting_times.append(r.pickup_time - r.request_time)
        
# rider_abandonments_times = []
# rider_abandonments_counts = []
# count = 0
# for r in riders.values():
#     if str(r.status).strip().lower() == "abandoned":
#         count += 1
#         rider_abandonments_times.append(r.request_time)
#         rider_abandonments_counts.append(count)
        

# # Results
# print("----- Data-Driven Simulation -----")
# print("Total Riders:", len(riders))
# print("Served Riders:", len(served))
# print("Abandoned Riders:", len(abandoned))
# print(f"Rider abandonment rate: {abandonment_rate*100:.2f}%")
# print(f"Total revenue: £{total_revenue:.2f}")
# print(f"Average revenue per served rider: £{avg_revenue_per_rider:.2f}")
# # print(f"Total driver income: £{total_driver_income:.2f}")
# # print(f"Average net income per driver: £{avg_net_income_per_driver:.2f}")
# print(f"Revenue per hour of simulation: £{revenue_per_hour:.2f}")
# # print(f"Rider Satisfaction Score {rider_satisfaction_score:.3f}")
# # print(f"Driver Satisfaction Score: {driver_satisfaction_score:.3f}")
# # print(f"Avg Driver Income/hr: £{avg_hourly_driver_income}")
# # print(f"Max Driver Income/hr: £{max(d.income / (d.offline_time - d.available_time) for d in drivers.values())}")
# # print(f"Min Driver Income/hr: £{min(d.income / (d.offline_time - d.available_time) for d in drivers.values())}")
# #print(f"Avg Driver Break Time: {avg_break_time}")

# # Plots
# #Make plots
# events = []    
# for r in riders.values():
#     events.append((r.request_time, 1))

#     if str(r.status).strip().lower() == "abandoned":
#         events.append((r.request_time, -1))
#     elif r.dropoff_time is not None:
#         events.append((r.dropoff_time, -1))
#     else:
#         events.append((Termination, 0))
        
# events.sort()

# system_rider_times = []
# system_rider_counts = []
# count = 0
# for t, change in events:
#     count += change
#     system_rider_times.append(t)
#     system_rider_counts.append(count)
# plt.figure()
# plt.step(system_rider_times, system_rider_counts, where='post')
# plt.xlabel("Time")
# plt.ylabel("Number of Customers in System")
# plt.title("Customers in System Over Time")
# plt.savefig('deterministic_customers_in_system.png')
# plt.show()

# plt.figure()
# plt.step(rider_abandonments_times, rider_abandonments_counts, where='post')
# plt.xlabel("Time")
# plt.ylabel("Number of Customers who abandon")
# plt.title("Abandonments from the System Over Time")
# plt.savefig('deterministic_abandonments_over_time.png')
# plt.show()

# plt.figure()
# plt.hist(waiting_times, bins=50)
# plt.xlabel("Rider Waiting Time for Pickup")
# plt.ylabel("Number of Riders")
# plt.title("Distribution of Rider Waiting Times")
# plt.savefig('deterministic_waiting_times.png')
# plt.show()

# driver_events = []
# for d in drivers.values():
#     driver_events.append((d.available_time, 1))
#     driver_events.append((d.offline_time, -1))

# driver_events.sort()

# system_driver_times = []
# system_driver_counts = []
# count = 0
# for t, change in driver_events:
#     count += change
#     system_driver_times.append(t)
#     system_driver_counts.append(count)
# plt.figure()
# plt.step(system_driver_times, system_driver_counts, where='post')
# plt.xlabel("Time")
# plt.ylabel("Number of Drivers in System")
# plt.title("Drivers in System Over Time")
# plt.savefig('deterministic_drivers_in_system.png')
# plt.show()

# # driver_incomes = [d.income for d in drivers.values()]
# # plt.figure()
# # plt.hist(driver_incomes, bins=len(driver_incomes))
# # plt.xlabel("Driver Net Income (£)")
# # plt.ylabel("Number of Drivers")
# # plt.title("Number of Drivers by Income Level")
# # plt.savefig('deterministic_driver_incomes.png')
# # plt.show()

# # resting_times = []
# # for d in drivers.values():
# #     active_time=d.offline_time-d.available_time
# #     rest_time=active_time-d.busy_time
# #     if rest_time>=0:
# #         resting_times.append(rest_time)

# # plt.figure()
# # plt.hist(resting_times, bins=50)
# # plt.xlabel("Driver Resting Time")
# # plt.ylabel("Number of Drivers")
# # plt.title("Adjusted Distribution of Driver Resting Time")
# # plt.savefig('deterministic_resting_times.png')
# # plt.show()




##########Input-Analyzed Simulation
# #Parameters
# AVG_SPEED = 20
# Termination = 100
# Rider_arrival_rate = 1/0.0289
# Driver_arrival_rate = 1/0.2109

# def bounded_weibull(scale, shape, loc, lb=0, ub=20):
#     while True:
#         x = random.weibullvariate(scale, shape) + loc
#         if lb <= x <= ub:
#             return x

# #########Random Simulation
# #Classes
# class Rider:
#     def __init__(self, r_id, time):
#         self.id = r_id
#         self.request_time = time
#         self.origin = (bounded_weibull(10.5845, 2.3530, -1.0192), bounded_weibull(22.7562, 5.9193, -8.7511))
#         self.destination = (bounded_weibull(18.8784, 4.3608, -5.9380), bounded_weibull(47.6629, 13.4425, -32.5667))
#         self.pickup_time = None
#         self.dropoff_time = None
#         self.patience_deadline = time + random.expovariate(Rider_patience_rate)

# class Driver:
#     def __init__(self, d_id, time):
#         self.id = d_id
#         self.location = (bounded_weibull(13.8762, 3.1566, -2.4330), bounded_weibull(19.2088, 4.6815, -6.0312))
#         # self.online_time = time
#         self.offline_time = time + random.uniform(5,8)
#         self.available = True
#         self.income = 0
#         self.arrival_time = time
#         self.busy_time = 0
#         # self.busy_start = None

# #Helper Functions
# def distance(a, b):
#     return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# def travel_time(dist):
#     mean_time = dist / AVG_SPEED
#     return random.uniform(0.8 * mean_time, 1.2 * mean_time)

# #Matching function
# def attempt_match():
#     global idle_drivers, waiting_riders, TNOW
#     while idle_drivers and waiting_riders:
#         #FIFO
#         rider = waiting_riders.pop(0)
#         B1[rider.id] = 0  # mark as matched
#         #Find closest driver
#         driver = min(idle_drivers, key=lambda d: distance(d.location, rider.origin))
#         idle_drivers.remove(driver)
#         driver.available = False
#         # driver.busy_start = TNOW
#         B2[driver.id] = 0  # mark as matched
#         #Travel distance to pickup
#         d = distance(driver.location, rider.origin)
#         pickup_time = TNOW + travel_time(d)
#         EC[3].append((pickup_time, rider.id, driver.id))
#         match[rider.id] = driver.id

# #System State
# TNOW = 0
# Q =0

# drivers= {}
# riders = {}

# X1=[]   #X coordinate of customers
# Y1=[]   #Y coordinate of customers
# X2=[]   #X coordinate of drivers
# Y2=[]   #Y coordinate of drivers

# #Indices of which taxis/customers are looking for a match
# B1=[]   #Customers
# B2=[]   #Taxis

# #indices of taxis corresponding to each customer
# #index in the i_th place is the taxi for the i_th customer
# match=[]

# idle_drivers = []
# waiting_riders = []

# next_driver_id = 0
# next_rider_id = 0

# #Times and total riders currently in the system
# system_rider_times=[]
# system_rider_counts=[]
# current_riders=0

# #Times and total riders in the system who left due to impatience
# rider_abandonments_times=[]
# rider_abandonments_counts=[]
# current_abandonments=0

# #Times and total drivers currently in the system
# system_driver_times=[]
# system_driver_counts=[]
# current_drivers=0

# #Times each rider was waiting
# waiting_times=[]

# #Times each driver was resting
# resting_times = []

# #Event calendar
# # EC[0] = next rider arrival
# # EC[1] = list of rider impatience times
# # EC[2] = next driver arrival
# # EC[3] = list of pickup times
# # EC[4] = list of dropoff times
# # EC[5] = list of driver offline times
# # EC[6] = termination time
# EC = [0, [], 0, [], [], [], Termination]
# EC[0] = random.expovariate(Rider_arrival_rate)
# EC[2] = random.expovariate(Driver_arrival_rate)



# #Simulation Loop
# while TNOW < Termination:
#     #Identify next event
#     TNEXT = EC[0]
#     event  = 'rider_arrival'
    
#     if EC[1] and min(EC[1])[0] < TNEXT:
#         TNEXT = min(EC[1])[0]
#         event  = 'abandon'

#     if EC[2] < TNEXT:
#         TNEXT = EC[2]
#         event  = 'driver_arrival'    

#     if EC[3] and min(EC[3])[0] < TNEXT:
#         TNEXT = min(EC[3])[0]
#         event  = 'pickup'

#     if EC[4] and min(EC[4])[0] < TNEXT:
#         TNEXT = min(EC[4])[0]
#         event  = 'dropoff'

#     if EC[5] and min(EC[5])[0] < TNEXT:
#         TNEXT = min(EC[5])[0]
#         event  = 'driver_offline'

#     if EC[6] < TNEXT:
#         TNEXT = EC[6]
#         event  = 'termination'

#     TNOW = TNEXT

#     #Event handling
#     if event == 'rider_arrival':
#         #Creating the rider
#         r = Rider(next_rider_id, TNOW)
#         riders[next_rider_id] = r
#         waiting_riders.append(r)
#         #Starting location
#         X1.append(r.origin[0])
#         Y1.append(r.origin[1])
#         B1.append(1)
#         match.append(None)
#         #Abandonment time
#         EC[1].append((r.patience_deadline, next_rider_id))
#         #Updating the EC
#         next_rider_id += 1
#         EC[0] = TNOW + random.expovariate(Rider_arrival_rate)
#         attempt_match()

#         current_riders += 1
#         system_rider_times.append(TNOW)
#         system_rider_counts.append(current_riders)
    
#     elif event == "abandon":
#         event = min(EC[1])
#         EC[1].remove(event)
#         #Assinging time and rider to event
#         _, r_id = event
#         #If pickup time is not at TNOW
#         if any(r.id == r_id for r in waiting_riders):
#                 B1[r_id] = 0
#                 #Removing abandoning rider from the waiting list
#                 waiting_riders = [r for r in waiting_riders if r.id != r_id]
            
#                 current_riders -= 1
#                 system_rider_times.append(TNOW)
#                 system_rider_counts.append(current_riders)
                
#                 current_abandonments += 1
#                 rider_abandonments_times.append(TNOW)
#                 rider_abandonments_counts.append(current_abandonments)

#     elif event == "driver_arrival":
#         #Creating the driver
#         d = Driver(next_driver_id, TNOW)
#         drivers[next_driver_id] = d
#         #Starting location
#         X2.append(d.location[0])
#         Y2.append(d.location[1])
#         B2.append(1)
#         #Adding to idle list
#         idle_drivers.append(d)
#         #Adding their offline time
#         EC[5].append((d.offline_time, next_driver_id))
#         next_driver_id += 1
#         Q += 1
#         #Updating the event calendar
#         EC[2] = TNOW + random.expovariate(Driver_arrival_rate)
#         attempt_match()

#         current_drivers += 1
#         system_driver_times.append(TNOW)
#         system_driver_counts.append(current_drivers)

#     elif event == "pickup":
#         event = min(EC[3])
#         EC[3].remove(event)
#         #Assinging the correct driver and rider to the event
#         _, r_id, d_id = event
#         r = riders[r_id]
#         d = drivers[d_id]
#         r.pickup_time = TNOW
#         #Setting the trip distance
#         trip_dist = distance(r.origin, r.destination)
#         t_dropoff = TNOW + travel_time(trip_dist)
#         #Updating the event calendar
#         EC[4].append((t_dropoff, r_id, d_id, trip_dist))

#         waiting_times.append(TNOW - r.request_time)
    
#     elif event == "dropoff":
#         event = min(EC[4])
#         EC[4].remove(event)
#         #Matching ids, time and distance to the event
#         _, r_id, d_id, dist = event
#         r = riders[r_id]
#         d = drivers[d_id]
#         r.dropoff_time = TNOW
#         d.busy_time+=TNOW-r.pickup_time
#         #Calculating financials
#         fare = 3 + 2*dist
#         cost = 0.2*dist
#         d.income += (fare - cost)
#         #Updating driver status and location
#         d.location = r.destination
#         B2[d_id] = 1
#         # d.busy_time += TNOW - d.busy_start
#         # d.busy_start = None
#         idle_drivers.append(d)
#         attempt_match()

#         current_riders -= 1
#         system_rider_times.append(TNOW)
#         system_rider_counts.append(current_riders)

#     elif event == 'driver_offline':
#         #Taking the first event in the list of driver offline times
#         event = min(EC[5])
#         EC[5].remove(event)
#         _, d_id = event
#         #Updating driver status
#         B2[d_id] = 0
#         #Remving driver from idle list if they are in it
#         idle_drivers = [drv for drv in idle_drivers if drv.id != d_id]

#         current_drivers -= 1
#         system_driver_times.append(TNOW)
#         system_driver_counts.append(current_drivers)

#     elif event == "termination":
#         break

# #Results
# #Calculating which riders were served and which abandoned based on pickup and dropoff times
# served = [r for r in riders.values() if r.dropoff_time]
# abandoned = [r for r in riders.values() if r.pickup_time is None]

# # Rider financials
# total_revenue = 0
# for r in served:
#     trip_dist = distance(r.origin, r.destination)
#     fare = 3 + 2*trip_dist
#     total_revenue += fare
# avg_revenue_per_rider = total_revenue / len(served) if served else 0

# # rider time stats
# total_system_t = 0
# total_waiting_t = 0
# for r in riders.values():
#     if r.pickup_time is None:
#         total_system_t += r.patience_deadline - r.request_time
#         total_waiting_t += r.patience_deadline - r.request_time
#     elif r.dropoff_time is None:
#         total_system_t += Termination - r.request_time
#         total_waiting_t += r.pickup_time - r.request_time
#     else:
#         total_system_t += r.dropoff_time - r.request_time
#         total_waiting_t += r.pickup_time - r.request_time
# rider_satisfaction_score = 100 * (1 - (total_waiting_t/total_system_t))

# # Driver financials
# total_driver_income = sum(d.income for d in drivers.values())
# avg_net_income_per_driver = total_driver_income / len(drivers) if drivers else 0
# total_driver_worktime = sum(d.offline_time - d.online_time for d in drivers.values())
# avg_hourly_driver_income = np.mean([d.income / (d.offline_time - d.online_time) for d in drivers.values()])
# range_hourly_driver_income = max(d.income / (d.offline_time - d.online_time) for d in drivers.values()) - min(d.income / (d.offline_time - d.online_time) for d in drivers.values())
# avg_break_time = np.mean([
#     (d.offline_time - d.online_time - d.busy_time) /
#     (d.offline_time - d.online_time)
#     for d in drivers.values()
# ])
# driver_satisfaction_score = avg_hourly_driver_income + (avg_hourly_driver_income * avg_break_time) - range_hourly_driver_income
# # Additional metrics
# abandonment_rate = len(abandoned)/len(riders) if riders else 0
# revenue_per_hour = total_revenue / Termination

# print("\n----- Input Analyzed Random Simulation -----")
# print("Total Riders:", len(riders))
# print("Served Riders:", len(served))
# print("Abandoned Riders:", len(abandoned))
# print(f"Rider abandonment rate: {abandonment_rate*100:.2f}%")
# print(f"Total revenue: £{total_revenue:.2f}")
# print(f"Average revenue per served rider: £{avg_revenue_per_rider:.2f}")
# print(f"Total driver income: £{total_driver_income:.2f}")
# print(f"Average net income per driver: £{avg_net_income_per_driver:.2f}")
# print(f"Revenue per hour of simulation: £{revenue_per_hour:.2f}")
# print(f"Rider Satisfaction Score {rider_satisfaction_score:.3f}")
# print(f"Driver Satisfaction Score: {driver_satisfaction_score:.3f}")
# print(f"Avg Driver Income/hr: £{avg_hourly_driver_income}")
# print(f"Max Driver Income/hr: £{max(d.income / (d.offline_time - d.online_time) for d in drivers.values())}")
# print(f"Min Driver Income/hr: £{min(d.income / (d.offline_time - d.online_time) for d in drivers.values())}")
# print(f"Avg Driver Break Time: {avg_break_time}")

# #Make plots
# plt.figure()
# plt.step(system_rider_times, system_rider_counts, where='post')
# plt.xlabel("Time")
# plt.ylabel("Number of Customers in System")
# plt.title("Adjusted Customers in System Over Time")
# plt.savefig('adjusted_customers_in_system.png')
# plt.show()

# plt.figure()
# plt.step(rider_abandonments_times, rider_abandonments_counts, where='post')
# plt.xlabel("Time")
# plt.ylabel("Number of Customers who abandon")
# plt.title("Adjusted Abandonments from the System Over Time")
# plt.savefig('adjusted_abandonments.png')
# plt.show()

# plt.figure()
# plt.hist(waiting_times, bins=50)
# plt.xlabel("Rider Waiting Time for Pickup")
# plt.ylabel("Number of Riders")
# plt.title("Adjusted Distribution of Rider Waiting Times")
# plt.savefig('adjusted_waiting_times.png')
# plt.show()

# plt.figure()
# plt.step(system_driver_times, system_driver_counts, where='post')
# plt.xlabel("Time")
# plt.ylabel("Number of Drivers in System")
# plt.title("Adjusted Drivers in System Over Time")
# plt.savefig('adjusted_drivers_in_system.png')
# plt.show()

# driver_incomes = [d.income for d in drivers.values()]
# plt.figure()
# plt.hist(driver_incomes, bins=len(driver_incomes))
# plt.xlabel("Driver Net Income (£)")
# plt.ylabel("Number of Drivers")
# plt.title("Adjusted Number of Drivers by Income Level")
# plt.savefig('adjusted_driver_incomes.png')
# plt.show()

# for d in drivers.values():
#     active_time=d.offline_time-d.arrival_time
#     rest_time=active_time-d.busy_time
#     if rest_time>=0:
#         resting_times.append(rest_time)
        
# plt.figure()
# plt.hist(resting_times, bins=50)
# plt.xlabel("Driver Resting Time")
# plt.ylabel("Number of Drivers")
# plt.title("Adjusted Distribution of Driver Resting Time")
# plt.savefig('adjusted_resting_times.png')
# plt.show()