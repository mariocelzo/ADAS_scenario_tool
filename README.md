ADAS Tool - Advanced Driver Assistance Systems

📌 Descrizione

ADAS_scenario_tool è un progetto sviluppato nell'ambito di un tirocinio e di una tesi universitaria, con l'obiettivo di ottimizzare la selezione e l'analisi di scenari di test per sistemi ADAS (Advanced Driver Assistance Systems). Questo strumento si basa sull'integrazione avanzata dei simulatori CARLA e BeamNG, due ambienti di simulazione di riferimento nel campo della guida autonoma.Il progetto si propone di risolvere alcune delle principali problematiche legate alla generazione e all'analisi di scenari di test, come la scarsa disponibilità di dataset eterogenei e la difficoltà nel confrontare scenari complessi su piattaforme diverse. ADAS Tool permette di:

-Effettuare parsing avanzato degli scenari definiti in OpenSCENARIO (.xosc) per CARLA e in JSON per BeamNG;

-Calcolare metriche di criticità, diversità e tempi di esecuzione per ogni scenario;

-Convertire automaticamente scenari da CARLA a BeamNG, ampliando la compatibilità tra simulatori;

-Estrarre feature dinamiche e statiche utili per processi di ottimizzazione e selezione degli scenari.

Grazie a queste caratteristiche, ADAS Tool rappresenta un passo avanti nell'automatizzazione e nell'efficienza della validazione di sistemi ADAS, semplificando il processo di analisi comparativa tra i due ambienti di simulazione e migliorando la robustezza dei test eseguiti.


🚀 Installazione

1️⃣ Clonazione del repository

git clone https://github.com/tuo-username/adas-tool.git
cd adas-tool

2️⃣ Creazione dell’ambiente virtuale

Si consiglia l’utilizzo di un ambiente virtuale per isolare le dipendenze del progetto:

python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux

Per Windows:

.venv\\Scripts\\activate

3️⃣ Installazione delle dipendenze

All’interno dell’ambiente virtuale, eseguire:

pip install --upgrade pip
pip install -r requirements.txt

4️⃣ Docker (per CARLA) Passaggio da eseguire solo se si utilizza MacOS, se si è su macchine Windows passare allo step 5.

Per eseguire CARLA in un ambiente Docker:

docker run -p 2000-2002:2000-2002 --gpus all --rm -it carlasim/carla:0.9.14

Assicurarsi di avere Docker correttamente installato e configurato.

5️⃣ Download di ScenarioRunner

ScenarioRunner è richiesto per il lancio degli scenari:

git clone --branch 0.9.14 https://github.com/carla-simulator/scenario_runner.git
pip install -r scenario_runner/requirements.txt


⸻

🔄 Esecuzione dei test

✅ 1. Avviare CARLA (anche in questo caso nel caso di windows passare al secondo passaggio)

docker run -p 2000-2002:2000-2002 --gpus all --rm -it carlasim/carla:0.9.14

✅ 2. Eseguire gli script di test

Lanciare lo script principale per eseguire e loggare gli scenari:

python3 run_and_log_scenarios.py

I risultati saranno salvati nella cartella output/.

⸻

📂 Struttura del progetto

├── data
│   ├── carla_scenarios
│   └── beamng_scenarios
├── output
│   ├── features
│   ├── logs
│   ├── execution_time.json
│   ├── criticality_score.json
│   └── diversity_score.json
├── parsers
│   ├── parser_carla.py
│   ├── parser_beamng.py
│   └── carla_to_beamng.py
├── requirements.txt
├── run_and_log_scenarios.py
├── scenario_runner
└── README.md


⸻

🛠️ Manutenzione
	•	Per aggiornare le dipendenze:

pip install --upgrade -r requirements.txt


	•	Per aggiornare Docker:

docker pull carlasim/carla:0.9.14



⸻

🤝 Contributi

Contributi e miglioramenti sono ben accetti! Sentiti libero di fare una Pull Request o di aprire una Issue per discutere nuove funzionalità.

⸻

📝 Licenza

Questo progetto è distribuito sotto licenza MIT.

⸻
