import xml.etree.ElementTree as ET
import pandas as pd


def parse_carla_scenario(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    scenario_data = {
        "scenario_name": [],
        "num_entities": [],
        "weather": [],
        "road_type": [],
    }

    for entity in root.findall(".//Entities/ScenarioObject"):
        scenario_data["num_entities"].append(entity.get("name"))

    scenario_data["scenario_name"].append(root.get("name") or file_path.split("/")[-1])

    # Esempio di metadati da OpenSCENARIO
    weather = root.find(".//Weather")
    if weather is not None:
        scenario_data["weather"].append(weather.findtext("Precipitation/type", "unknown"))
    else:
        scenario_data["weather"].append("unknown")

    road = root.find(".//RoadNetwork")
    if road is not None:
        scenario_data["road_type"].append("custom")
    else:
        scenario_data["road_type"].append("default")

    scenario_data["num_entities"] = [len(scenario_data["num_entities"])]

    return pd.DataFrame(scenario_data)