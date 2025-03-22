FROM python:3.11.3-slim

WORKDIR /app

# 安装依赖
RUN apt-get update && \
    apt-get install -y openssl && \
    rm -rf /var/lib/apt/lists/*

RUN COPY requirements.txt .
RUN pip install -r requirements.txt

COPY proxy.py .

EXPOSE 5000

CMD ["python", "proxy.py"]