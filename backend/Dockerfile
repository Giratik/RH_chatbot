FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
ENV TIKTOKEN_CACHE_DIR=/app/tiktoken_cache 

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu118

COPY requirements_backend.txt .
RUN pip install --no-cache-dir -r requirements_backend.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]