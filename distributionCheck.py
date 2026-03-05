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
    .diff()
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

    params = result.params._asdict()

    ks = stats.kstest(data, dist.name, args=tuple(params.values()))

    print("\n--- Goodness of fit (KS Test) ---")
    print(f"KS Statistic: {ks.statistic}")
    print(f"P-value: {ks.pvalue}")

    return result

def find_best_distribution(data, dists, dataset_name="Dataset", top_n=5):

    data = data.dropna()

    results = []

    for dist in dists:

        try:
            params = dist.fit(data)

            # log-likelihood
            loglik = np.sum(dist.logpdf(data, *params))

            k = len(params)
            aic = 2*k - 2*loglik

            results.append((dist, aic, params))

        except Exception:
            continue

    results.sort(key=lambda x: x[1])

    print("\n" + "="*60)
    print(f"Distribution Fit Results for: {dataset_name}")
    print("="*60)

    for i, (dist, aic, params) in enumerate(results[:top_n], start=1):

        # Separate shape parameters from loc/scale
        shapes = params[:-2] if len(params) > 2 else []
        loc = params[-2] if len(params) >= 2 else None
        scale = params[-1] if len(params) >= 1 else None

        print(f"\n{i}. {dist.name}")
        print(f"   AIC: {aic:.2f}")

        if shapes:
            for j, s in enumerate(shapes):
                print(f"   shape{j+1}: {s:.4f}")

        if loc is not None:
            print(f"   loc:   {loc:.4f}")

        if scale is not None:
            print(f"   scale: {scale:.4f}")

    print("\n(Lower AIC = better fit)")

    return results

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
             [(5, 5), (3, 3)],  # loc=5, scale=3 -> (5, 8)
             "Driver Online Time ~ Uniform(5,8)")

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
             "Rider Interarrival ~ Exp(30/hour)")

# =========================
# TODO 2: Fit WITHOUT bounds (estimate parameters)
# =========================

fit_and_plot(driver_df["Spawn X"], stats.uniform, [(0, 20), (0, 20)],
             title="Driver Spawn X (Estimated Uniform)")

fit_and_plot(driver_df["Spawn Y"], stats.uniform, [(0, 20), (0, 20)],
             title="Driver Spawn Y (Estimated Uniform)")

fit_and_plot(driver_df["Online Time"], stats.uniform, [(0, 1000), (0, 1000)],
             title="Driver Online Time (Estimated Uniform)")

fit_and_plot(driver_df["Interarrival"], stats.expon, [(0, 1), (0, 1)],
             title="Driver Interarrival (Estimated Exponential)")

fit_and_plot(rider_df["Interarrival"], stats.expon, [(0, 1), (0, 1)],
             title="Rider Interarrival (Estimated Exponential)")

fit_and_plot(rider_df["Spawn X"], stats.uniform, [(0, 20), (0, 20)],
             title="Rider Spawn X (Estimated Uniform)")

fit_and_plot(rider_df["Spawn Y"], stats.uniform, [(0, 20), (0, 20)],
             title="Rider Spawn Y (Estimated Uniform)")

fit_and_plot(rider_df["Destination X"], stats.uniform, [(0, 20), (0, 20)],
             title="Rider Destination X (Estimated Uniform)")

fit_and_plot(rider_df["Destination Y"], stats.uniform, [(0, 20), (0, 20)],
             title="Rider Destination Y (Estimated Uniform)")

# =========================
# TODO 3: Test common distrs
# =========================
candidates = [
    stats.expon,
    stats.gamma,
    stats.weibull_min,
    stats.lognorm,
    stats.norm,
    stats.uniform
]

find_best_distribution(driver_df["Spawn X"], candidates, dataset_name="Driver Spawn X")

find_best_distribution(driver_df["Spawn Y"], candidates, dataset_name="Driver Spawn Y")

find_best_distribution(driver_df["Online Time"], candidates, dataset_name="Driver Online Time")

find_best_distribution(driver_df["Interarrival"], candidates, dataset_name="Driver Interarrival")

find_best_distribution(rider_df["Interarrival"], candidates, dataset_name="Rider Interarrival")

find_best_distribution(rider_df["Spawn X"], candidates, dataset_name="Rider Spawn X")

find_best_distribution(rider_df["Spawn Y"], candidates, dataset_name="Rider Spawn Y")

find_best_distribution(rider_df["Destination X"], candidates, dataset_name="Rider Destination X")

find_best_distribution(rider_df["Destination Y"], candidates, dataset_name="Rider Destination Y")