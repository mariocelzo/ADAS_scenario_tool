#!/bin/bash

# 1. Avvia CARLA in background
docker run -d \
  --name carla-server \
  --rm \
  -p 2000-2002:2000-2002 \
  --platform linux/amd64 \
  -e XDG_RUNTIME_DIR=/tmp \
  carlasim/carla:0.9.14

# Attendi qualche secondo per far partire il server
echo "Aspetto che CARLA si avvii..."
sleep 10

# 2. Costruisci il container con ScenarioRunner
docker build -t carla-scenario-runner .

# 3. Esegui lo script Python passando lo scenario
docker run --rm \
  --platform linux/amd64 \
  --network host \
  carla-scenario-runner \
  /workspace/Scenari/VehicleLateralDistance.xosc

# 4. Ferma CARLA
docker stop carla-server