FROM ubuntu:20.04

# Impostazioni base
ENV DEBIAN_FRONTEND=noninteractive

# Aggiorna e installa pacchetti base
RUN apt-get update && apt-get install -y \
    wget gnupg2 lsb-release software-properties-common \
    python3-dev python3-pip python3-venv git curl unzip libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Crea utente non root per sicurezza
RUN useradd -ms /bin/bash carlauser
USER carlauser
WORKDIR /home/carlauser

# Scarica CARLA 0.9.13
RUN wget https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.13.tar.gz && \
    tar -xvzf CARLA_0.9.13.tar.gz && rm CARLA_0.9.13.tar.gz

# Clona ScenarioRunner
RUN git clone https://github.com/carla-simulator/scenario_runner.git && \
    cd scenario_runner && git checkout 0.9.13

# Installa dipendenze Python
RUN python3 -m pip install --upgrade pip && \
    pip3 install -r scenario_runner/requirements.txt

# Porta esposta per CARLA
EXPOSE 2000-2002

# Comando default: avvia CARLA headless
CMD ["./CARLA_0.9.13/CarlaUE4.sh", "-opengl", "-nosound", "-carla-server"]