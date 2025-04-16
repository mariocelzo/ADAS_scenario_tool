import subprocess
import time
import json
import os
import glob

SCENARIO_RUNNER_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "ScenarioRunner", "results")

def run_scenario(file_path, output_dir):
    scenario_name = os.path.basename(file_path)
    base_name = scenario_name.replace('.xosc', '')

    start = time.time()
    result = subprocess.run([
        "python3", "scenario_runner.py",
        "--openscenario", file_path,
        "--reloadWorld",
        "--agent", "srunner/autoagents/basic_agent.py"
    ])
    end = time.time()

    execution_time = round(end - start, 2)

    criticality = 0.0
    # Try to read criticality from ScenarioRunner JSON
    json_log = os.path.join(SCENARIO_RUNNER_RESULTS_DIR, base_name, "metrics.json")
    if os.path.exists(json_log):
        with open(json_log) as jl:
            data = json.load(jl)
            criticality = data.get("critical_events", 0)  # or whichever key holds incidents count
    else:
        # Fallback to old text log
        text_log = os.path.join(SCENARIO_RUNNER_RESULTS_DIR, f"{base_name}_results.txt")
        if os.path.exists(text_log):
            with open(text_log) as log:
                for line in log:
                    if "Collision" in line:
                        criticality += 0.5  # oppure somma in base alla gravità

    results = {
        "scenario": scenario_name,
        "execution_time": execution_time,
        "criticality": criticality  # Use parsed criticality value
    }

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{base_name}_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    log_path = os.path.join(output_dir, f"{base_name}_log.txt")
    with open(log_path, "w") as log_file:
        log_file.write(f"Scenario completato: {scenario_name}\n")
        log_file.write(f"Tempo di esecuzione: {execution_time}s\n")
        log_file.write(f"Criticità: {criticality}\n")  # Updated to reflect parsed criticality

if __name__ == "__main__":
    SCENARIO_DIR = "/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/data/carla_scenarios"
    OUTPUT_DIR = "/Users/mariocelzo/Downloads/UNIVERSITA/TIROCINIO/ADAS_tool/output"

    for file_path in glob.glob(os.path.join(SCENARIO_DIR, "*.xosc")):
        run_scenario(file_path, OUTPUT_DIR)