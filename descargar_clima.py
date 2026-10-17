import requests
import pandas as pd

URL = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 48.78,
    "longitude": 2.29,
    "start_date": "2006-12-01",
    "end_date": "2011-03-31",
    "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
    "timezone": "Europe/Paris",
}

r = requests.get(URL, params=params, timeout=120)
r.raise_for_status()
daily = r.json()["daily"]

df = pd.DataFrame({
    "date": pd.to_datetime(daily["time"]),
    "temp_max": daily["temperature_2m_max"],
    "temp_min": daily["temperature_2m_min"],
    "temp_mean": daily["temperature_2m_mean"],
})

out = r"C:\Users\romin\Desktop\tpintegrador\datos\clima_sceaux.csv"
df.to_csv(out, index=False)
print(df.shape)
print(df.head())
print(df.tail())
