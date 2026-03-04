import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# =========================
# DATA LOADING
# =========================

rider_df  = pd.read_excel("riders.xlsx")
driver_df = pd.read_excel("drivers.xlsx")

# Ensure datetime columns are datetime
driver_df["arrival_datetime"] = pd.to_datetime(driver_df["arrival_datetime"])
driver_df["offline_datetime"] = pd.to_datetime(driver_df["offline_datetime"])


# =========================
# HELPER: Split "(x, y)" columns
# =========================

def split_xy(df, col, new_cols):
    df[new_cols] = (
        df[col]
        .str.strip("()")
        .str.split(",", expand=True)
        .astype(float)
    )

# =========================
# FEATURE ENGINEERING
# =========================

# Driver spawn locations ~ Uniform(0,20)
split_xy(driver_df, "initial_location", ["Spawn X", "Spawn Y"])

# Driver online time ~ Uniform(6,8) hours
driver_df["Online Time"] = (
    (driver_df["offline_datetime"] - driver_df["arrival_datetime"])
    .dt.total_seconds() / 3600
)

# Driver interarrival ~ Exp(3/hour)
driver_df = driver_df.sort_values("arrival_datetime")
driver_df["Interarrival"] = (
    driver_df["arrival_datetime"]
    .diff()
    .dt.total_seconds() / 3600
)

# Rider pickup and dropoff locations ~ Uniform(0,20)
split_xy(rider_df, "pickup_location", ["Spawn X", "Spawn Y"])
split_xy(rider_df, "dropoff_location", ["Destination X", "Destination Y"])

# Rider interarrival ~ Exp(30/hour)
rider_df = rider_df.sort_values("request_time")
rider_df["Interarrival"] = (
    rider_df["request_time"]
    .diff() / 60
)


# =========================
# FITTING FUNCTION
# =========================

def fit_and_plot(data, dist, bounds=None, title=""):
    data = data.dropna()

    if bounds:
        result = stats.fit(dist, data, bounds)
    else:
        result = stats.fit(dist, data)

    print(f"\n--- {title} ---")
    print(result)

    result.plot()
    plt.title(title)
    plt.show()

    return result


# =========================
# TODO 1: Fit with GIVEN bounds
# =========================

fit_and_plot(driver_df["Spawn X"], stats.uniform,
             [(0, 0), (20, 20)],
             "Driver Spawn X ~ Uniform(0,20)")

fit_and_plot(driver_df["Spawn Y"], stats.uniform,
             [(0, 0), (20, 20)],
             "Driver Spawn Y ~ Uniform(0,20)")

fit_and_plot(driver_df["Online Time"], stats.uniform,
             [(6, 6), (2, 2)],  # loc=6, scale=2
             "Driver Online Time ~ Uniform(6,8)")

fit_and_plot(driver_df["Interarrival"], stats.expon,
             [(0, 0), (1/3, 1/3)],  # scale = 1/lambda
             "Driver Interarrival ~ Exp(3/hour)")

fit_and_plot(rider_df["Spawn X"], stats.uniform,
             [(0, 0), (20, 20)],
             "Rider Spawn X ~ Uniform(0,20)")

fit_and_plot(rider_df["Spawn Y"], stats.uniform,
             [(0, 0), (20, 20)],
             "Rider Spawn Y ~ Uniform(0,20)")

fit_and_plot(rider_df["Destination X"], stats.uniform,
             [(0, 0), (20, 20)],
             "Rider Destination X ~ Uniform(0,20)")

fit_and_plot(rider_df["Destination Y"], stats.uniform,
             [(0, 0), (20, 20)],
             "Rider Destination Y ~ Uniform(0,20)")

fit_and_plot(rider_df["Interarrival"], stats.expon,
             [(0, 0), (1/30, 1/30)],
             "Rider Interarrival ~ Exp(3/hour)")


# =========================
# TODO 2: Fit WITHOUT bounds (estimate parameters)
# =========================

fit_and_plot(driver_df["Spawn X"], stats.uniform,
             title="Driver Spawn X (Estimated Uniform)")

fit_and_plot(driver_df["Spawn Y"], stats.uniform,
             title="Driver Spawn Y (Estimated Uniform)")

fit_and_plot(driver_df["Online Time"], stats.uniform,
             title="Driver Online Time (Estimated Uniform)")

fit_and_plot(driver_df["Interarrival"], stats.expon,
             title="Driver Interarrival (Estimated Exponential)")

fit_and_plot(rider_df["Interarrival"], stats.expon,
             title="Rider Interarrival (Estimated Exponential)")

fit_and_plot(rider_df["Spawn X"], stats.uniform,
             title="Rider Spawn X (Estimated Uniform)")

fit_and_plot(rider_df["Spawn Y"], stats.uniform,
             title="Rider Spawn Y (Estimated Uniform)")

fit_and_plot(rider_df["Destination X"], stats.uniform,
             title="Rider Destination X (Estimated Uniform)")

fit_and_plot(rider_df["Destination Y"], stats.uniform,
             title="Rider Destination Y (Estimated Uniform)")