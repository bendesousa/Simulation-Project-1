import pandas as pd
import scipy as sp
import numpy as np
"""
EXTRACTION
"""
rider_df  = pd.read_excel("riders.xlsx")
driver_df = pd.read_excel("drivers.xlsx")

driver_df[["Spawn X", "Spawn Y"]] = (
    driver_df["initial_location"]
        .str.strip("()")        # remove parentheses
        .str.split(",", expand=True)  # split into two columns
        .astype(float)          # convert to floats
)

driver_df["Online Time"] = (
    (driver_df["offline_datetime"] - driver_df["arrival_datetime"]).dt.total_seconds()
) / 3600

rider_df[["Spawn X", "Spawn Y"]] = (
    rider_df["pickup_location"]
        .str.strip("()")        # remove parentheses
        .str.split(",", expand=True)  # split into two columns
        .astype(float)          # convert to floats
)
rider_df[["Destination X", "Destination Y"]] = (
    rider_df["dropoff_location"]
        .str.strip("()")        # remove parentheses
        .str.split(",", expand=True)  # split into two columns
        .astype(float)          # convert to floats
)
rider_df["Interarrival"] = rider_df["request_time"].diff()

dx0 = np.array(driver_df["Spawn X"])
dy0 = np.array(driver_df["Spawn Y"])
dt = np.array(driver_df["Online Time"])

rx0 = np.array(rider_df["Spawn X"])
ry0 = np.array(rider_df["Spawn Y"])
rxf = np.array(rider_df["Destination X"])
ryf = np.array(rider_df["Destination Y"])
rt = np.array(rider_df["Interarrival"])

"""
*****TO-DO*****
run fit on the given distrs and bounds to get plots
run fit on the given distrs to get bounds
run fit on distrs that might work and see if better
"""