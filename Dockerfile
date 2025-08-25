FROM python:3.13.5

RUN apt-get update && apt-get install -y \
    curl ca-certificates chromium chromium-driver \
    libnss3 libgconf-2-4 libxi6 libxcursor1 libxrandr2 \
    libxcomposite1 libasound2 libpangocairo-1.0-0 \
    libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y curl ca-certificates && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# RUN echo '[project]\nname = "retainai"\nversion = "0.1.0"\ndependencies = []' > pyproject.toml
COPY pyproject.toml /app/pyproject.toml
# RUN uv add -r requirements.txt

COPY . .

ENV TF_ENABLE_ONEDNN_OPTS=0
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uv", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]