import subprocess
import time
import json
import os
import glob
from collections import defaultdict

SCENARIO_RUNNER_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "ScenarioRunner", "results")

# Crea dizionari globali per i 3 obiettivi
execution_time_summary = {}
criticality_summary = {}
diversity_summary = defaultdict(lambda: 0.0)  # placeholder per ora

def run_scenario(file_path, output_dir):
    scenario_name = os.path.basename(file_path)
    base_name = scenario_name.replace('.xosc', '')

    start = time.time()
    result = subprocess.run(
        f"python3 scenario_runner/scenario_runner.py --openscenario '{file_path}' --reloadWorld --agent srunner/autoagents/basic_agent.py",
        shell=True
    )
    end = time.time()

    execution_time = round(end - start, 2)

    criticality = 0.0
    # Prova a leggere da metrics.json
    json_log = os.path.join(SCENARIO_RUNNER_RESULTS_DIR, base_name, "metrics.json")
    if os.path.exists(json_log):
        with open(json_log) as jl:
            data = json.load(jl)
            criticality = data.get("critical_events", 0)
    else:
        # Fallback su log.txt
        text_log = os.path.join(SCENARIO_RUNNER_RESULTS_DIR, f"{base_name}_results.txt")
        if os.path.exists(text_log):
            with open(text_log) as log:
                for line in log:
                    if "Collision" in line:
                        criticality += 0.5

    # Salva risultati singoli
    results = {
        "scenario": scenario_name,
        "execution_time": execution_time,
        "criticality": criticality
    }

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{base_name}_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    log_path = os.path.join(output_dir, f"{base_name}_log.txt")
    with open(log_path, "w") as log_file:
        log_file.write(f"Scenario completato: {scenario_name}\n")
        log_file.write(f"Tempo di esecuzione: {execution_time}s\n")
        log_file.write(f"Criticità: {criticality}\n")

    # Aggiungi ai dizionari cumulativi
    execution_time_summary[scenario_name] = execution_time
    criticality_summary[scenario_name] = criticality

if __name__ == "__main__":
    SCENARIO_DIR = "/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/data/carla_scenarios"
    OUTPUT_DIR = "/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/output"

    for file_path in glob.glob(os.path.join(SCENARIO_DIR, "*.xosc")):
        run_scenario(file_path, OUTPUT_DIR)

    # Alla fine: salva i 3 JSON globali
    with open(os.path.join(OUTPUT_DIR, "execution_time.json"), "w") as f:
        json.dump(execution_time_summary, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "criticality_score.json"), "w") as f:
        json.dump(criticality_summary, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "diversity_score.json"), "w") as f:
        json.dump(diversity_summary, f, indent=2)