# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Clone WASP benchmark (unchanged)
RUN git clone --depth 1 https://github.com/facebookresearch/wasp.git /app/wasp && \
    cd /app/wasp && \
    git submodule update --init --recursive --depth 1 && \
    cd /app/wasp/visualwebarena && \
    pip install --no-cache-dir --root-user-action=ignore -e . && \
    cd /app/wasp/webarena_prompt_injections && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt && \
    rm -rf /app/wasp/.git*

# Copy app + tests
COPY app ./app
COPY tests ./tests
COPY start.sh ./start.sh
RUN chmod +x start.sh

# Fix permissions
RUN chmod -R 755 /app/wasp/webarena_prompt_injections/configs || true
RUN mkdir -p /app/wasp/webarena_prompt_injections/configs && \
    chmod 777 /app/wasp/webarena_prompt_injections/configs || true

# AgentBeats env vars
ENV DATASET=webarena_prompt_injections
ENV REDDIT="reddit:9999"
ENV GITLAB="gitlab:8023"
EXPOSE 8000

USER pwuser
CMD ["./start.sh"]

