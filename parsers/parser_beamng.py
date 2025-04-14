import json
import pandas as pd

def parse_beamng_scenario(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    scenario_data = {
        "scenario_name": data.get("name", file_path.split("/")[-1]),
        "num_vehicles": len(data.get("vehicles", {})),
        "map": data.get("map", "unknown"),
        "description": data.get("description", "none"),
    }

    return pd.DataFrame([scenario_data])