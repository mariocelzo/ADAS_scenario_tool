import os
from parsers.parser_carla import parse_carla_scenario
from parsers.parser_beamng import parse_beamng_scenario
import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET


def extract_carla_features(xosc_file):
    tree = etree.parse(xosc_file)
    from extractor import OpenScenarioExtractor
    full_extractor = OpenScenarioExtractor(xosc_file)
    header_and_storyboard = full_extractor.extract()

    root = tree.getroot()

    features = []
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

    features.append({"file_header_and_storyboard": header_and_storyboard})

    return features

class OpenScenarioExtractor:
    def __init__(self, filename):
        self.filename = filename
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()

    def extract(self):
        header = self.extract_header()
        entities = self.extract_entities()
        storyboard = self.extract_storyboard()
        return {
            "header": header,
            "entities": entities,
            "storyboard": storyboard
        }

    def extract_header(self):
        header = {}
        header_element = self.root.find('FileHeader')
        if header_element is not None:
            header['revMajor'] = header_element.get('revMajor')
            header['revMinor'] = header_element.get('revMinor')
            header['date'] = header_element.get('date')
            header['description'] = header_element.get('description')
        return header

    def extract_entities(self):
        entities = []
        entities_element = self.root.find('Entities')
        if entities_element is not None:
            for entity in entities_element.findall('ScenarioObject'):
                entity_data = {
                    'name': entity.get('name'),
                    'catalogReference': entity.find('CatalogReference').get('catalogName') if entity.find('CatalogReference') is not None else None,
                    'parameters': []
                }
                for param in entity.findall('ParameterDeclarations/ParameterDeclaration'):
                    param_data = {
                        'name': param.get('name'),
                        'type': param.get('type'),
                        'value': param.get('value')
                    }
                    entity_data['parameters'].append(param_data)
                entities.append(entity_data)
        return entities

    def extract_storyboard(self):
        storyboard = []
        storyboard_element = self.root.find('Storyboard')
        if storyboard_element is not None:
            for act in storyboard_element.findall('Act'):
                act_data = {
                    'name': act.get('name'),
                    'maneuvers': []
                }
                for maneuver_group in act.findall('ManeuverGroup'):
                    mg_data = {
                        'entityRef': maneuver_group.get('entityRef'),
                        'maneuvers': []
                    }
                    for maneuver in maneuver_group.findall('Maneuver'):
                        m_data = {
                            'name': maneuver.get('name'),
                            'events': []
                        }
                        for event in maneuver.findall('Event'):
                            e_data = {
                                'name': event.get('name'),
                                'actions': []
                            }
                            for action in event.findall('Action'):
                                a_data = {
                                    'type': action.tag,
                                    'parameters': {}
                                }
                                for param in action:
                                    a_data['parameters'][param.tag] = param.text
                                e_data['actions'].append(a_data)
                            m_data['events'].append(e_data)
                        mg_data['maneuvers'].append(m_data)
                    act_data['maneuvers'].append(mg_data)
                storyboard.append(act_data)
        return storyboard