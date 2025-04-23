import os
import json
from parsers.parser_carla import parse_carla_scenario
from parsers.parser_beamng import parse_beamng_scenario
import pandas as pd
from lxml import etree


def extract_carla_features(xosc_file):
    tree = etree.parse(xosc_file)
    root = tree.getroot()

    features = []

    from features.extractor import OpenScenarioExtractor
    full_extractor = OpenScenarioExtractor(xosc_file)
    header_and_storyboard = full_extractor.extract()
    # Separa header, entities e storyboard
    header = header_and_storyboard.get("File Header", {})
    entities = header_and_storyboard.get("Entities", {})
    storyboard = header_and_storyboard.get("Storyboard", {})

    features.append({"type": "file_header", **header})

    for name, entity in entities.items():
        entity_flat = {"type": "entity", "entity_name": name}
        for key, value in entity.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, dict):
                        for subsubkey, subsubvalue in subvalue.items():
                            entity_flat[f"{key}_{subkey}_{subsubkey}"] = subsubvalue
                    else:
                        entity_flat[f"{key}_{subkey}"] = subvalue
            else:
                entity_flat[key] = value
        features.append(entity_flat)

    for act_name, maneuvers in storyboard.items():
        for maneuver in maneuvers:
            sb_entry = {"type": "storyboard", "act": act_name, "maneuver": maneuver.get("Maneuver Name")}
            for event in maneuver.get("Events", []):
                sb_event = sb_entry.copy()
                sb_event["event"] = event.get("Event Name")
                for action in event.get("Actions", []):
                    for k, v in action.items():
                        if isinstance(v, dict):
                            for subk, subv in v.items():
                                sb_event[f"{k}_{subk}"] = subv
                        else:
                            sb_event[k] = v
                    features.append(sb_event)

    scenario_name = os.path.basename(xosc_file).replace(".xosc", "")  # Estrai il nome del file senza estensione

    # Estrai i veicoli e le loro proprietà
    for vehicle in root.xpath("//Vehicle"):
        vehicle_data = {
            "scenario_name": scenario_name,  # Aggiungi il nome dello scenario
            "name": vehicle.get("name"),
            "category": vehicle.get("vehicleCategory"),
            "maxSpeed": vehicle.xpath("Performance/@maxSpeed")[0],
            "maxAcceleration": vehicle.xpath("Performance/@maxAcceleration")[0],
            "maxDeceleration": vehicle.xpath("Performance/@maxDeceleration")[0],
            "color": None  # Imposta un valore di default
        }

        # Aggiungi un controllo per la proprietà "color"
        color_property = vehicle.xpath("Properties/Property[@name='color']/@value")
        if color_property:
            vehicle_data["color"] = color_property[0]  # Assegna il colore se trovato

        features.append(vehicle_data)

    # Estrai la posizione iniziale dei veicoli
    for teleport in root.xpath("//TeleportAction"):
        positions = teleport.xpath("Position/RoadPosition/@s")
        if positions:
            position = positions[0]
            features[-1]["initial_position"] = position
        else:
            features[-1]["initial_position"] = None

    # Estrai le informazioni su pedoni (se presenti)
    for pedestrian in root.xpath("//Pedestrian"):
        pedestrian_data = {
            "name": pedestrian.get("name"),
            "location": pedestrian.xpath("Position/@x")[0] if pedestrian.xpath("Position/@x") else None
        }
        features.append(pedestrian_data)

    # Estrai informazioni sui semafori (se presenti)
    for traffic_light in root.xpath("//TrafficLight"):
        traffic_light_data = {
            "name": traffic_light.get("name"),
            "state": traffic_light.xpath("State/@state")[0] if traffic_light.xpath("State/@state") else None
        }
        features.append(traffic_light_data)

    # Estrai informazioni su telecamere (se presenti)
    for camera in root.xpath("//Camera"):
        camera_data = {
            "name": camera.get("name"),
            "fov": camera.xpath("Properties/Property[@name='fov']/@value")[0] if camera.xpath("Properties/Property[@name='fov']/@value") else None
        }
        features.append(camera_data)

    # Estrai le caratteristiche meteo e la loro variazione
    for environment_action in root.xpath("//EnvironmentAction"):
        weather_data = {}
        weather = environment_action.xpath(".//Weather")
        if weather:
            cloud_state = weather[0].get("cloudState")
            sun_intensity = weather[0].xpath(".//Sun/@intensity")[0] if weather[0].xpath(".//Sun/@intensity") else None
            sun_azimuth = weather[0].xpath(".//Sun/@azimuth")[0] if weather[0].xpath(".//Sun/@azimuth") else None
            sun_elevation = weather[0].xpath(".//Sun/@elevation")[0] if weather[0].xpath(".//Sun/@elevation") else None
            fog_visual_range = weather[0].xpath(".//Fog/@visualRange")[0] if weather[0].xpath(".//Fog/@visualRange") else None
            precipitation_type = weather[0].xpath(".//Precipitation/@precipitationType")[0] if weather[0].xpath(".//Precipitation/@precipitationType") else None
            precipitation_intensity = weather[0].xpath(".//Precipitation/@intensity")[0] if weather[0].xpath(".//Precipitation/@intensity") else None

            weather_data = {
                "cloudState": cloud_state,
                "sun_intensity": sun_intensity,
                "sun_azimuth": sun_azimuth,
                "sun_elevation": sun_elevation,
                "fog_visual_range": fog_visual_range,
                "precipitation_type": precipitation_type,
                "precipitation_intensity": precipitation_intensity
            }
            features[-1].update(weather_data)

    return features


def extract_all_features(carla_dir, beamng_dir, output_dir):
    carla_dfs = []
    beamng_dfs = []

    # Parsing CARLA .xosc
    for file in os.listdir(carla_dir):
        if file.endswith(".xosc"):
            path = os.path.join(carla_dir, file)
            features = extract_carla_features(path)
            if not features:
                print(f"⚠️  Nessuna caratteristica estratta da {path}")
                continue
            # Separa il contenuto avanzato (header e storyboard) per salvataggi JSON
            extra_data = [f for f in features if f.get("type") == "file_header"]
            #features = [f for f in features if f.get("type") != "file_header"]

            df = pd.DataFrame(features)
            df["source"] = "CARLA"
            carla_dfs.append(df)

            # Esempi fittizi: in futuro sostituire con dati reali ottenuti da simulazione
            execution_time = 10.0  # in secondi
            criticality_score = 0.7  # tra 0 e 1
            diversity_vector = df.iloc[0].to_dict()  # oppure un array di feature rilevanti

            json_data = {
                "scenario": file,
                "execution_time": execution_time,
                "criticality": criticality_score,
                "diversity": diversity_vector
            }

            # Salvataggio dei singoli JSON
            base_filename = os.path.splitext(file)[0]
            with open(os.path.join(output_dir, f"{base_filename}_execution.json"), "w") as f:
                json.dump({"execution_time": execution_time}, f, indent=2)

            with open(os.path.join(output_dir, f"{base_filename}_criticality.json"), "w") as f:
                json.dump({"criticality": criticality_score}, f, indent=2)

            with open(os.path.join(output_dir, f"{base_filename}_diversity.json"), "w") as f:
                json.dump({"diversity": diversity_vector}, f, indent=2)

            # Salvataggio di header e storyboard completi
            if extra_data:
                with open(os.path.join(output_dir, f"{base_filename}_full_metadata.json"), "w") as f:
                    json.dump(extra_data[0], f, indent=2)

    # Parsing BeamNG .json
    for file in os.listdir(beamng_dir):
        if file.endswith(".json"):
            path = os.path.join(beamng_dir, file)
            df = parse_beamng_scenario(path)
            df["source"] = "BeamNG"
            beamng_dfs.append(df)

    # Unione e salvataggio
    all_df = pd.concat(carla_dfs + beamng_dfs, ignore_index=True)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "all_features.csv")
    all_df.to_csv(output_path, index=False)
    print(f"✅ Dataset salvato in: {output_path}")


def main():
    # Percorsi delle cartelle (modifica con i tuoi percorsi effettivi)
    carla_dir = '/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/data/carla_scenarios'  # Modifica con il percorso della cartella CARLA
    beamng_dir = '/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/data/beamng_scenarios'  # Modifica con il percorso della cartella BeamNG
    output_dir = '/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/output'  # Modifica con il percorso della cartella di output

    # Chiamata alla funzione per estrarre le caratteristiche e salvare il CSV
    extract_all_features(carla_dir, beamng_dir, output_dir)


if __name__ == "__main__":
    main()