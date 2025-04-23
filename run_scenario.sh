#!/bin/bash

# Script eseguito DENTRO il container Docker
SCENARIO_NAME=$1

# Avvia lo scenario runner sul file .xosc
python3 /app/scenario_runner/scenario_runner.py /app/data/carla_scenarios/"$SCENARIO_NAME".xosc