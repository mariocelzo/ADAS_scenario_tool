#!/bin/bash

# Avvia CARLA in modalità headless
/opt/CARLA_0.9.13/CarlaUE4.sh -carla-server -nosound -RenderOffScreen &
sleep 10

# Se è stato passato uno scenario come argomento, lo lancia
if [ -n "$1" ]; then
    python3 /opt/scenario_runner/scenario_runner.py /data/"$1".xosc
else
    tail -f /dev/null
fi

