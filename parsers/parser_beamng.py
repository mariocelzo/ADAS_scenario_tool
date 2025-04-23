import json
import pandas as pd

def parse_beamng_scenario(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    rows = []

    # Estrai i veicoli
    for v in data.get("vehicles", []):
        v["type"] = "vehicle"
        v["scenario_name"] = data.get("name", file_path.split("/")[-1].replace(".json", ""))
        rows.append(v)

    # Estrai dati meteo
    if "weather_script" in data:
        weather = data["weather_script"]
        weather["type"] = "weather"
        weather["scenario_name"] = data.get("name", file_path.split("/")[-1].replace(".json", ""))
        rows.append(weather)

    # Estrai regole di traffico
    if "traffic_script" in data:
        traffic = data["traffic_script"]
        traffic["type"] = "traffic"
        traffic["scenario_name"] = data.get("name", file_path.split("/")[-1].replace(".json", ""))
        rows.append(traffic)

    # Estrai waypoints
    for w in data.get("waypoints", []):
        w["type"] = "waypoint"
        w["scenario_name"] = data.get("name", file_path.split("/")[-1].replace(".json", ""))
        rows.append(w)

    return pd.DataFrame(rows)