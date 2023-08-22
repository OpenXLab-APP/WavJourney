FROM python:3.11

# Install miniconda
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
	https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
	&& bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 \
	&& rm -f Miniconda3-latest-Linux-x86_64.sh

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Add conda binary to PATH variable
ENV HOME=/home/user \
	PATH=/opt/miniconda3/bin:/home/user/.local/bin:$PATH \
	CONDA_PREFIX=/opt/miniconda3/envs

# Setup conda envs
WORKDIR $HOME/app
COPY --chown=user . $HOME/app

# Conda envs setup 
RUN bash ./scripts/EnvsSetup.sh

# pre-download all models
RUN conda run --live-stream -n WavJourney python scripts/download_models.py
RUN mkdir $HOME/app/services_logs

# Env settings to get docker images to work on HF Spaces
ENV PYTHONPATH=${HOME}/app \
    PYTHONUNBUFFERED=1 \
    GRADIO_ALLOW_FLAGGING=never \
    GRADIO_NUM_PORTS=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_THEME=huggingface \
    SYSTEM=spaces

# entrypoint
ENTRYPOINT bash /home/user/app/scripts/start_service_and_ui.sh