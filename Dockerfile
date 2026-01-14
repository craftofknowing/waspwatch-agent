# syntax=docker/dockerfile:1

FROM python:3.10-slim

# System deps for playwright / VisualWebArena / WASP
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget build-essential \
    libglib2.0-0 libnss3 libx11-6 libxcomposite1 libxrandr2 \
    libxdamage1 libxfixes3 libatk1.0-0 libatk-bridge2.0-0 \
    libxkbcommon0 libpango-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libasound2 libgbm-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy app code
COPY app ./app
COPY requirements.txt ./requirements.txt
COPY start.sh ./start.sh
RUN chmod +x start.sh

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Clone WASP benchmark (facebookresearch/wasp)
RUN git clone https://github.com/facebookresearch/wasp.git /app/wasp \
    && cd /app/wasp \
    && git submodule update --init --recursive \
    && cd /app/wasp/webarena_prompt_injections \
    && bash setup.sh

# Playwright install (needed by VisualWebArena)
RUN python -m playwright install --with-deps

# Environment defaults for WASP / VisualWebArena
ENV DATASET=webarena_prompt_injections
# In production, REDDIT and GITLAB will be set by scenario/docker-compose [web:37][web:40]
ENV REDDIT="reddit:9999"
ENV GITLAB="gitlab:8023"

# Expose controller port
EXPOSE 8000

# Main entrypoint: run the FastAPI controller
CMD ["./start.sh"]

