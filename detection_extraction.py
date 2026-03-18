import pandas as pd
from datetime import datetime

# Load history file
df = pd.read_csv("current_data.csv")
df["last_changed"] = pd.to_datetime(df["last_changed"], dayfirst = True, errors="coerce")
# Change time zone (not required if changed in HomeAssistant)
df["last_changed"] = df["last_changed"] + pd.Timedelta(hours=1)
# Define sensors
PIRsensor = "binary_sensor.tz1800_fcdjzz3s_ty0202"
MWsensor = "binary_sensor.sonoff_snzb_06p"

# Keep only motion detection events
df = df[df["entity_id"].isin([PIRsensor, MWsensor])]
df = df[df["state"] == "on"]

print(df)

experiments = pd.read_csv("experiments.csv")

# Combine Date + StartTime
experiments["StartDateTime"] = pd.to_datetime(
    "2026-03-07"  + " " + experiments["StartTime"],# experiments["Date"] + " " + experiments["StartTime"],
    dayfirst=True, # nformatting
    errors="coerce",
    utc=True
)

# Combine Date + EndTime
experiments["EndDateTime"] = pd.to_datetime(
    "2026-03-07" + " " + experiments["EndTime"],# experiments["Date"] + " " + experiments["EndTime"],
    dayfirst=True,
    errors="coerce",
    utc = True
)

# Sort by start time
experiments = experiments.sort_values("StartDateTime").reset_index(drop=True)

print(experiments[["StartDateTime", "EndDateTime"]])

# get the first detection for a certain sensor
def get_first_detection(sensor_id):
    results = []
    for _, exp in experiments.iterrows():
        mask = (
            (df["entity_id"] == sensor_id) &
            (df["last_changed"] >= exp["StartDateTime"]) &
            (df["last_changed"] <= exp["EndDateTime"])
        )
        first_detection = df.loc[mask, "last_changed"].min()
        if pd.notna(first_detection):
            results.append({
                "Trial": exp["Trial"],
                "Time": first_detection.time()  # drop date
            })
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values("Time").reset_index(drop=True)
    return results_df

# retrieve results
PIRsensor_df = get_first_detection(PIRsensor)
MWsensor_df = get_first_detection(MWsensor)

# save results
PIRsensor_df.to_csv("PIRsensor_first_detection_times.csv", index=False)
MWsensor_df.to_csv("MWsensor_first_detection_times.csv", index=False)

print("Saved CSVs with Trial number and time, sorted by time.")