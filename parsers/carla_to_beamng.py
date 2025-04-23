# parsers/carla_to_beamng.py

import os
import json
from lxml import etree
from features.extractor import OpenScenarioExtractor

def convert_carla_to_beamng(xosc_file, output_dir):
    tree = etree.parse(xosc_file)
    full_extractor = OpenScenarioExtractor(xosc_file)
    scenario_data = full_extractor.extract()

    # Aggiunta dati extra ispirati da script LUA/BeamNG
    scenario_data["weather_script"] = {
        "cloud_state": tree.xpath("string(//Weather/@cloudState)"),
        "sun_intensity": tree.xpath("string(//Sun/@intensity)"),
        "fog": tree.xpath("string(//Fog/@visualRange)"),
        "precipitation": tree.xpath("string(//Precipitation/@intensity)")
    }

    traffic_rule = tree.xpath("//TrafficSignalController")
    if traffic_rule:
        scenario_data["traffic_script"] = {
            "speed_limit": 50,  # valore fittizio, da aggiornare se disponibile
            "controller_id": traffic_rule[0].get("name")
        }

    # Waypoints esempio
    waypoints = tree.xpath("//LanePosition")
    scenario_data["waypoints"] = [{"s": w.get("s"), "lane_id": w.get("laneId")} for w in waypoints]

    scenario_data["vehicles_count"] = len(tree.xpath("//Vehicle"))
    scenario_data["pedestrians_count"] = len(tree.xpath("//Pedestrian"))
    scenario_data["traffic_lights_count"] = len(tree.xpath("//TrafficLight"))
    scenario_data["has_weather"] = bool(tree.xpath("//EnvironmentAction/Environment/Weather"))
    scenario_data["time_of_day"] = tree.xpath("string(//TimeOfDay/@dateTime)")
    scenario_data["maneuvers_count"] = len(tree.xpath("//Maneuver"))
    scenario_data["acts_count"] = len(tree.xpath("//Act"))

    # Estrazione dettagliata dei veicoli
    scenario_name = os.path.splitext(os.path.basename(xosc_file))[0]
    scenario_data["vehicles"] = []
    for vehicle in tree.xpath("//Vehicle"):
        vehicle_data = {
            "type": "file_header",
            "scenario_name": scenario_name,
            "name": vehicle.get("name"),
            "category": vehicle.get("vehicleCategory"),
            "maxSpeed": vehicle.xpath("string(Performance/@maxSpeed)"),
            "maxAcceleration": vehicle.xpath("string(Performance/@maxAcceleration)"),
            "maxDeceleration": vehicle.xpath("string(Performance/@maxDeceleration)"),
            "color": None,
            "initial_position": None,
            "cloudState": tree.xpath("string(//Weather/@cloudState)"),
            "sun_intensity": tree.xpath("string(//Sun/@intensity)"),
            "sun_azimuth": tree.xpath("string(//Sun/@azimuth)"),
            "sun_elevation": tree.xpath("string(//Sun/@elevation)"),
            "fog_visual_range": tree.xpath("string(//Fog/@visualRange)"),
            "precipitation_type": tree.xpath("string(//Precipitation/@precipitationType)"),
            "precipitation_intensity": tree.xpath("string(//Precipitation/@intensity)"),
            "source": "CARLA",
            "location": None
        }
        # Colore (opzionale)
        color_prop = vehicle.xpath("Properties/Property[@name='color']/@value")
        if color_prop:
            vehicle_data["color"] = color_prop[0]

        # Posizione (opzionale)
        pos_s = vehicle.xpath("ObjectController/Position/RoadPosition/@s")
        if pos_s:
            vehicle_data["initial_position"] = pos_s[0]

        scenario_data["vehicles"].append(vehicle_data)

    # Nome del file senza estensione
    filename = os.path.splitext(os.path.basename(xosc_file))[0]
    output_path = os.path.join(output_dir, f"{filename}.json")

    with open(output_path, "w") as f:
        json.dump(scenario_data, f, indent=2)

    print(f"✅ Convertito: {xosc_file} → {output_path}")

def convert_all_carla(carla_dir, beamng_output_dir):
    for file in os.listdir(carla_dir):
        if file.endswith(".xosc"):
            xosc_path = os.path.join(carla_dir, file)
            convert_carla_to_beamng(xosc_path, beamng_output_dir)

if __name__ == "__main__":
    # Percorsi predefiniti relativi al progetto
    carla_dir = os.path.join("data", "carla_scenarios")
    beamng_dir = os.path.join("data", "beamng_scenarios")

    # Assicurati che la cartella di output esista
    os.makedirs(beamng_dir, exist_ok=True)

    print("🚀 Inizio conversione degli scenari CARLA...")
    convert_all_carla(carla_dir, beamng_dir)
    print("✅ Tutti gli scenari convertiti con successo.")